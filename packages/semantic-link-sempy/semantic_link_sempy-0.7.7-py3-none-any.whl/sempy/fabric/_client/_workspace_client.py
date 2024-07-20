import datetime
import pandas as pd
from warnings import warn
import time
from tqdm.auto import tqdm

from sempy.fabric._client._dataset_xmla_client import DatasetXmlaClient
from sempy.fabric._client._dataset_rest_client import DatasetRestClient
from sempy.fabric._client._dataset_onelake_import import DatasetOneLakeImportClient
from sempy.fabric._client._connection_mode import ConnectionMode
from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy.fabric._client._fabric_rest_api import _FabricRestAPI, OperationStart
from sempy.fabric._client._utils import _init_analysis_services, _create_tom_server, _build_adomd_connection_string, _odata_quote
from sempy.fabric._environment import get_workspace_id, _get_workspace_url
from sempy.fabric._token_provider import SynapseTokenProvider, TokenProvider
from sempy.fabric._utils import (
    is_valid_uuid,
    dotnet_to_pandas_date,
    collection_to_dataframe,
    get_properties,
)
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric.exceptions import DatasetNotFoundException, WorkspaceNotFoundException

from functools import lru_cache
from uuid import UUID
from typing import List, Optional, Union


class WorkspaceClient:
    """
    Accessor class for a Power BI workspace.

    The workspace can contain multiple Datasets, which can be accessed via
    a PowerBIClient obtained via :meth:`get_dataset_client`.

    The class is a thin wrapper around
    `Microsoft.AnalysisServices.Tabular.Server <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    client that accesses cloud Power BI workspace and its Tabular Object Model (TOM)
    via the XMLA interface. The client caches the connection to the server for faster performance.

    Parameters
    ----------
    workspace : str or UUID
        PowerBI Workspace Name or UUID object containing the workspace ID.
    token_provider : TokenProvider, default=None
        Implementation of :class:`~sempy.fabric._token_provider.TokenProvider` that can provide auth token
        for access to the PowerBI workspace. Will attempt to acquire token
        from its execution environment if not provided.
    """
    def __init__(self, workspace: Optional[Union[str, UUID]] = None, token_provider: Optional[TokenProvider] = None):

        _init_analysis_services()

        # cached TOM server
        self.tom_server_readonly = None

        self.token_provider = token_provider or SynapseTokenProvider()
        self._pbi_rest_api = _PBIRestAPI(token_provider=self.token_provider)
        self._fabric_rest_api = _FabricRestAPI(token_provider=self.token_provider)
        self._cached_dataset_client = lru_cache()(
            lambda dataset_name, ClientClass: ClientClass(
                self,
                dataset_name,
                token_provider=self.token_provider
            )
        )

        self._workspace_id: str
        self._workspace_name: str

        if workspace is None:
            self._workspace_id = get_workspace_id()
            self._workspace_name = self._pbi_rest_api.get_workspace_name_from_id(self._workspace_id)
        elif isinstance(workspace, UUID):
            self._workspace_id = str(workspace)
            self._workspace_name = self._pbi_rest_api.get_workspace_name_from_id(self._workspace_id)
        elif isinstance(workspace, str):
            workspace_id = self.get_workspace_id_from_name(workspace)
            # None if we couldn't find the workspace, so it might be a UUID as string
            if workspace_id is None:
                if is_valid_uuid(workspace):
                    self._workspace_id = workspace
                    self._workspace_name = self._pbi_rest_api.get_workspace_name_from_id(self._workspace_id)
                else:
                    raise WorkspaceNotFoundException(workspace)
            else:
                self._workspace_name = workspace
                self._workspace_id = workspace_id
        else:
            raise TypeError(f"Unexpected type {type(workspace)} for \"workspace\"")

        self.dataset_client_types = {
            ConnectionMode.XMLA: DatasetXmlaClient,
            ConnectionMode.REST: DatasetRestClient,
            ConnectionMode.ONELAKE_IMPORT_DATASET: DatasetOneLakeImportClient,
        }

    def get_workspace_id_from_name(self, workspace_name: str) -> Optional[str]:
        if workspace_name == "My workspace":
            return self._fabric_rest_api.get_my_workspace_id()

        value = self._pbi_rest_api.list_workspaces(f"name eq '{_odata_quote(workspace_name)}'")

        if value is None:
            return None

        return value[0]['id']

    def get_workspace_id(self) -> str:
        """
        Get workspace ID of associated workspace.

        Returns
        -------
        String
            Workspace ID.
        """
        return self._workspace_id

    def get_workspace_name(self) -> str:
        """
        Get name ID of associated workspace.

        Returns
        -------
        String
            Workspace name.
        """
        return self._workspace_name

    def _get_readonly_tom_server(self):
        """
        Connect to PowerBI TOM Server, or returns server if already connected.


        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Server
            XMLA client with a cached connection to a PowerBI Tabular Object Model server.
        """
        if self.tom_server_readonly is None:
            self.tom_server_readonly = self._create_tom_server(readonly=True)

        return self.tom_server_readonly

    def _create_tom_server(self, readonly: bool):
        """
        Creates a TOM server object.

        Parameters
        ----------
        readonly: bool
            Whether the server should be readonly.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Server
            XMLA client with a cached connection to a PowerBI Tabular Object Model server.
        """

        # ?readonly enables connections to read-only replicas (see https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-scale-out-app)
        workspace_url = _get_workspace_url(self.get_workspace_name())
        connection_str = _build_adomd_connection_string(workspace_url, readonly=readonly)

        return _create_tom_server(connection_str, self.token_provider)

    def get_datasets(self, mode: str, additional_xmla_properties: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
        """
        Get a list of datasets in a PowerBI workspace.

        Each dataset is derived from
        `Microsoft.AnalysisServices.Tabular.Database <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.database?view=analysisservices-dotnet>`__

        The dataframe contains the following columns:

        - Dataset Name `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.namedcomponent.name?view=analysisservices-dotnet#microsoft-analysisservices-namedcomponent-name>`__
        - Created Date `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.majorobject.createdtimestamp?view=analysisservices-dotnet#microsoft-analysisservices-majorobject-createdtimestamp>`__
        - ID `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.namedcomponent.id?view=analysisservices-dotnet#microsoft-analysisservices-namedcomponent-id>`__
        - Last Update `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.core.database.lastupdate?view=analysisservices-dotnet#microsoft-analysisservices-core-database-lastupdate>`__

        Returns
        -------
        DataFrame
            Pandas DataFrame listing databases and their attributes.
        """  # noqa: E501
        databases = []

        # Alternative implementation using REST API
        # + returns the most updated dataset list (using XMLA caches the TOM model)
        # + returns default datasets too
        # - these might not work with XMLA client
        # - less metadata

        # REST displays most up-to-date list of datasets, but the discover/read operations in XMLA
        # are cached at the time of initialization and may not know about recently added/deleted datasets.
        # We are choosing XMLA to maintain consistency between what the user sees with list_datasets and
        # read_table operations.

        if mode == "rest":
            dataset_json = self._pbi_rest_api.get_workspace_datasets(self.get_workspace_name(), self.get_workspace_id())

            return rename_and_validate_from_records(dataset_json, [
                ("id",                               "Dataset Id",                           "str"),
                ("name",                             "Dataset Name",                         "str"),
                ("webUrl",                           "Web Url",                              "str"),
                ("addRowsAPIEnabled",                "Add Rows API Enabled",                 "bool"),
                ("configuredBy",                     "Configured By",                        "str"),
                ("isRefreshable",                    "Is Refreshable",                       "bool"),
                ("isEffectiveIdentityRequired",      "Is Effective Identity Required",       "bool"),
                ("isEffectiveIdentityRolesRequired", "Is Effective Identity Roles Required", "bool"),
                ("isOnPremGatewayRequired",          "Is On Prem Gateway Required",          "bool"),
                ("targetStorageMode",                "Target Storage Mode",                  "str"),
                ("createdDate",                      "Created Timestamp",                    "datetime64[ns]"),
                ("createReportEmbedURL",             "Create Report Embed URL",              "str"),
                ("qnaEmbedURL",                      "Qna Embed URL",                        "str"),
                ("upstreamDatasets",                 "Upstream Datasets",                    "object"),
                ("users",                            "Users",                                "object"),
                ("queryScaleOutSettings",            "Query Scale Out Settings",             "object"),
            ])

        elif mode == "xmla":

            # TODO: figure out how to refresh list of TOM databases without re-establishing the connection (costly)
            for item in self._get_readonly_tom_server().Databases:
                # PowerBI is known to throw exceptions on individual attributes e.g. due to Vertipaq load failure
                # Careful with adding additional attributes here, can take a long time to load
                # e.g. EstimatedSize & CompatibilityLevel can be very slow
                try:
                    row = {'Dataset Name': item.Name,
                           'Dataset ID': item.ID,
                           'Created Timestamp': dotnet_to_pandas_date(item.CreatedTimestamp),
                           'Last Update': dotnet_to_pandas_date(item.LastUpdate)}

                    row.update(get_properties(item, additional_xmla_properties))

                    databases.append(row)
                except Exception as ex:
                    databases.append({'Dataset Name': item.Name, 'Error': str(ex)})
        else:
            raise ValueError(f"Unexpected mode {mode}")

        return pd.DataFrame(databases)

    def get_dataset(self, dataset: Union[str, UUID]):
        """
        Get PowerBI dataset for a given dataset_name.

        The dataset is derived from
        `Microsoft.AnalysisServices.Tabular.Database <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.database?view=analysisservices-dotnet>>`_

        Parameters
        ----------
        dataset : str or UUID
            Dataset name UUID object containing the dataset ID.

        Returns
        -------
        Dataset
            PowerBI Dataset represented as TOM Database object.
        """
        client = self.get_dataset_client(dataset)

        for db in self._get_readonly_tom_server().Databases:
            if db.Name == client.resolver.dataset_name:
                return db

        # Executing the following is very unlikely, because an exception should have
        # occured during dataset resolution. The only conceivable way is if the dataset
        # got deleted before we retrieved the list with self.get_connection().Databases.
        raise DatasetNotFoundException(str(dataset), self.get_workspace_name())

    def get_tmsl(self, dataset: Union[str, UUID]) -> str:
        """
        Retrieve the TMSL for a given dataset.

        Parameters
        ----------
        dataset : str or UUID
            Name or UUID of the dataset to list the measures for.

        Returns
        -------
        str
            TMSL for the given dataset.
        """
        tabular_database = self.get_dataset(dataset)

        import Microsoft.AnalysisServices.Tabular as TOM

        return TOM.JsonSerializer.SerializeDatabase(tabular_database)

    def execute_tmsl(self, script: str):
        """
        Executes TMSL script.

        Parameters
        ----------
        script : str
            The TMSL script json
        """
        # always create a new connection to avoid state issues
        server = self._create_tom_server(readonly=False)

        try:
            # deal with Power BI transient errors
            # max. weight <1min
            max_retries = 5
            for retry in range(1, max_retries+1):
                results = server.Execute(script)

                errors = []
                warnings = []
                for res in results:
                    for msg in res.Messages:
                        error_code = msg.GetType().GetProperty("ErrorCode")
                        if error_code is not None:
                            errors.append(f"Error {msg.ErrorCode}: {msg.Description}")
                        else:
                            warnings.append(msg.Description)

                if len(warnings) > 0:
                    warn("\n".join(warnings))

                if len(errors) > 0:
                    msg = "\n".join(errors)

                    if "was routed to wrong node by the Power BI request router. This is usually caused by intermittent issues. Please try again." not in msg \
                       or retry == max_retries:
                        raise RuntimeError(msg)

                    time.sleep(retry * retry)
                else:
                    # no errors, stop retry
                    return
        finally:
            # cleanup (True = drop session)
            server.Disconnect(True)
            server.Dispose()

        assert False, "Retry loop should have returned"

    def refresh_tom_cache(self):
        """
        Refresh the TOM Server (https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet)
        to it's latest state.
        """

        # Note: simply re-establishing the connection is the most stable solution
        # Refreshing can be very slow and also lead to errors
        # Element 'METADATA' with namespace name 'urn:schemas-microsoft-com:xml-analysis:rowset' was not found
        if self.tom_server_readonly is not None:
            # cleanup (True = drop session)
            self.tom_server_readonly.Disconnect(True)
            self.tom_server_readonly.Dispose()

        self.tom_server_readonly = None

    def list_measures(self, dataset: Union[str, UUID], additional_xmla_properties: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
        """
        Retrieve all measures associated with the given dataset.

        Each measure is derived from
        `Microsoft.AnalysisServices.Tabular.Measure <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet>`__

        Parameters
        ----------
        dataset : str or UUID
            Name or UUID of the dataset to list the measures for.
        additional_xmla_properties : str or List[str], default=None
            Additional XMLA `measure <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet>`_
            properties to include in the returned dataframe.

        Returns
        -------
        DataFrame
            Pandas DataFrame listing measures and their attributes.
        """
        client = self.get_dataset_client(dataset)
        database = self.get_dataset(client.resolver.dataset_name)

        # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet
        # (table, measure)
        extraction_def = [
            ("Table Name",               lambda r: r[0].Name,                   "str"),   # noqa: E272
            ("Measure Name",             lambda r: r[1].Name,                   "str"),   # noqa: E272
            ("Measure Expression",       lambda r: r[1].Expression,             "str"),   # noqa: E272
            ("Measure Data Type",        lambda r: r[1].DataType.ToString(),    "str"),   # noqa: E272
            ("Measure Hidden",           lambda r: r[1].IsHidden,               "bool"),  # noqa: E272
            ("Measure Display Folder",   lambda r: r[1].DisplayFolder,          "str"),   # noqa: E272
            ("Measure Description",      lambda r: r[1].Description,            "str"),   # noqa: E272
            ("Format String",            lambda r: r[1].FormatString,           "str"),   # noqa: E272
            ("Data Category",            lambda r: r[1].DataCategory,           "str"),   # noqa: E272
            ("Detail Rows Definition",   lambda r: r[1].DetailRowsDefinition,   "str"),   # noqa: E272
            ("Format String Definition", lambda r: r[1].FormatStringDefinition, "str"),   # noqa: E272
        ]

        collection = [
            (table, measure)
            for table in database.Model.Tables
            for measure in table.Measures
        ]

        return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)

    def get_dataset_client(self, dataset: Union[str, UUID], mode: ConnectionMode = ConnectionMode.REST) -> Union[DatasetRestClient, DatasetXmlaClient]:
        """
        Get PowerBIClient for a given dataset name or GUID.

        The same cached reusable instance is returned for each dataset.

        Parameters
        ----------
        dataset : str or UUID
            Dataset name or UUID object containing the dataset ID.
        mode : ConnectionMode, default=REST
            Which client to use to connect to the dataset.

        Returns
        -------
        DatasetRestClient, DatasetXmlaClient or DatasetOneLakeImportClient
            Client facilitating data retrieval from a specified dataset.
        """

        return self._cached_dataset_client(dataset, self.dataset_client_types[mode])

    def _is_internal(self, table) -> bool:
        if table.IsPrivate:
            return True
        # annotations = list(table.Annotations)
        for annotation in table.Annotations:
            if annotation.Name == "__PBI_LocalDateTable":
                return True
        return False

    def _get_xmla_datetime_utc(self, xmla_datetime) -> datetime.datetime:
        utc_dt_str = xmla_datetime.ToUniversalTime().ToString("s")
        return datetime.datetime.strptime(utc_dt_str, "%Y-%m-%dT%H:%M:%S")

    def __repr__(self):
        return f"PowerBIWorkspace('{self.get_workspace_name()}')"

    def list_reports(self) -> pd.DataFrame:
        """
        Return a list of reports in the specified workspace.

        Returns
        -------
        pandas.DataFrame
            DataFrame with one row per report.
        """

        payload = self._pbi_rest_api.list_reports(self.get_workspace_name(), self.get_workspace_id())

        return rename_and_validate_from_records(payload, [
                                ("id",                 "Id",                   "str"),
                                ("reportType",         "Report Type",          "str"),
                                ("name",               "Name",                 "str"),
                                ("webUrl",             "Web Url",              "str"),
                                ("embedUrl",           "Embed Url",            "str"),
                                ("isFromPbix",         "Is From Pbix",         "bool"),
                                ("isOwnedByMe",        "Is Owned By Me",       "bool"),
                                ("datasetId",          "Dataset Id",           "str"),
                                ("datasetWorkspaceId", "Dataset Workspace Id", "str"),
                                ("users",              "Users",                "object"),
                                ("subscriptions",      "Subscriptions",        "object")])

    def list_items(self, type: Optional[str] = None) -> pd.DataFrame:
        payload = self._fabric_rest_api.list_items(self.get_workspace_id(), type)

        return rename_and_validate_from_records(payload, [
                                ("id",                 "Id",                   "str"),
                                ("displayName",        "Display Name",         "str"),
                                ("description",        "Description",          "str"),
                                ("type",               "Type",                 "str"),
                                ("workspaceId",        "Workspace Id",         "str")])

    def create_lakehouse(self, display_name: str, description: Optional[str] = None, max_attempts: int = 10) -> str:
        return self._fabric_rest_api.create_lakehouse(self.get_workspace_id(), display_name, description, lro_max_attempts=max_attempts)

    def create_workspace(self, display_name: str, description: Optional[str] = None) -> str:
        return self._fabric_rest_api.create_workspace(display_name, description)

    def delete_item(self, item_id: str):
        self._fabric_rest_api.delete_item(self.get_workspace_id(), item_id)

    def delete_workspace(self):
        self._fabric_rest_api.delete_workspace(self.get_workspace_id())

    def create_notebook(self, display_name: str, description: Optional[str] = None, content: Optional[str] = None, max_attempts: int = 10) -> str:
        return self._fabric_rest_api.create_notebook(self.get_workspace_id(), display_name, description, content, max_attempts)

    def resolve_item_id(self, item_name: str, type: Optional[str] = None) -> str:
        df = self.list_items(type=type)
        selected_df = df[df["Display Name"] == item_name]["Id"]
        if selected_df.empty:
            raise ValueError(f"There's no item with the name '{item_name}' in workspace '{self.get_workspace_name()}'")
        return selected_df.values[0]

    def resolve_item_name(self, item_id: Union[str, UUID], type: Optional[str] = None) -> str:
        df = self.list_items(type=type)
        selected_df = df[df["Id"] == str(item_id)]["Display Name"]
        if selected_df.empty:
            raise ValueError(f"There's no item with the ID '{item_id}' in workspace '{self.get_workspace_name()}'")
        return selected_df.values[0]

    def resolve_dataset_id(self, dataset_name: str) -> str:
        return self.get_dataset_client(dataset_name).resolver.dataset_id

    def resolve_dataset_name(self, dataset_id: Union[str, UUID]) -> str:
        return self.get_dataset_client(dataset_id).resolver.dataset_name

    def run_notebook_job(self, notebook_id: str, max_attempts: int = 10) -> str:
        workspace_id = self.get_workspace_id()
        op_start = self._fabric_rest_api.run_notebook_job(workspace_id, notebook_id)

        self._wait_for_job("notebook", workspace_id, notebook_id, op_start, max_attempts)

        return op_start.operation_id

    def _wait_for_job(self, name: str, workspace_id: str, item_id, operation_start: OperationStart, max_attempts: int):
        bar = tqdm(range(max_attempts), desc=f"Waiting {operation_start.retry_after} seconds for {name} job to check for status")

        time.sleep(operation_start.retry_after)

        for _ in bar:
            job_status = self._fabric_rest_api.get_job_status(workspace_id, item_id, operation_start.operation_id)

            if job_status.status in ['Cancelled', 'Deduped', 'Failed']:
                raise RuntimeError(f"{name.capitalize()} job failed: {job_status.status}")

            if job_status.status == 'Completed':
                bar.set_description(f"{name.capitalize()} job successfully completed")

                return

            bar.set_description(f"Waiting {job_status.retry_after} seconds to check for status of {name} job to complete: {job_status.status}")

            time.sleep(job_status.retry_after)

        raise TimeoutError(f"{name.capitalize()} job timed out.")
