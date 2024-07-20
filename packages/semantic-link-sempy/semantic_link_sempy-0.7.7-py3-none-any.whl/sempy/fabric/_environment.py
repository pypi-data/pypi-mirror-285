import os
from typing import Optional, Dict, Any
from urllib.parse import quote, urlparse

fs_client: Optional[Any] = None
environment: Optional[str] = None
on_fabric: Optional[bool] = None
on_jupyter: Optional[bool] = None
on_aiskill: Optional[bool] = None
jupyter_config: Optional[Dict[str, str]] = None

# FIXME: we need a proper API to get base URL from spark config, which currently doesn't seem to exist
# the current hack aligns with https://dev.azure.com/powerbi/Embedded/_git/BugbashTool?path=/PowerBIEmbedded/PowerBIEmbedded/App.config&_a=contents&version=GBmaster
# sovereign clouds are skipped for now.
SUPPORTED_ENVIRONMENTS = {
    "onebox": "onebox-redirect.analysis.windows-int.net/",
    "daily":  "dailyapi.powerbi.com/",
    "edog":   "powerbiapi.analysis-df.windows.net/",
    "dxt":    "powerbistagingapi.analysis.windows.net/",
    "msit":   "df-msit-scus-redirect.analysis.windows.net/",
    "prod":   "api.powerbi.com/",
}

# https://dev.azure.com/powerbi/Trident/_wiki/wikis/Trident.wiki/46148/Environments
SUPPORTED_FABRIC_REST_ENVIRONMENTS = {
    "onebox": "analysis.windows-int.net/powerbi/api/",
    "daily":  "dailyapi.fabric.microsoft.com/",
    "edog":   "powerbiapi.analysis-df.windows.net/",
    "dxt":    "dxtapi.fabric.microsoft.com/",
    "msit":   "msitapi.fabric.microsoft.com/",
    "prod":   "api.fabric.microsoft.com/",
}


def get_workspace_id() -> str:
    """
    Return workspace id or default Lakehouse's workspace id.

    Returns
    -------
    str
        Workspace id guid if no default Lakehouse is set; otherwise, the default Lakehouse's workspace id guid.
    """
    if _get_fabric_context("defaultLakehouseId"):
        return _get_fabric_context_or_config("defaultLakehouseWorkspaceId", "trident.workspace.id")
    return _get_fabric_context_or_config("currentWorkspaceId", "trident.workspace.id")


def get_lakehouse_id() -> str:
    """
    Return lakehouse id of the lakehouse that is connected to the workspace.

    Returns
    -------
    str
        Lakehouse id guid.
    """
    return _get_fabric_context_or_config("defaultLakehouseId", "trident.lakehouse.id")


def get_notebook_workspace_id() -> str:
    """
    Return notebook workspace id.

    Returns
    -------
    str
        Workspace id guid.
    """
    return _get_fabric_context_or_config("currentWorkspaceId", "trident.artifact.workspace.id")


def get_artifact_id() -> str:
    """
    Return artifact id.

    Returns
    -------
    str
        Artifact (most commonly notebook) id guid.
    """
    return _get_fabric_context_or_config("currentNotebookId", "trident.artifact.id")


def _get_artifact_type() -> str:
    """
    Return artifact type.

    Returns
    -------
    str
        Artifact type e.g. "SynapseNotebook".
    """
    return _get_trident_config('trident.artifact.type')


def _get_onelake_endpoint() -> str:
    """
    Return onelake endpoint for the lakehouse.

    Returns
    -------
    str
        Onelake endpoint.
    """
    # e.g. abfss://<workspaceid>@<hostname>/
    domain = urlparse(_get_trident_config("fs.defaultFS")).netloc
    return domain.split("@")[-1]


def _get_fabric_context(key: str) -> str:
    """
    Retrieves the value from the Fabric context.

    Parameters
    ----------
    key : str
        The key for the Fabric context value.

    Returns
    -------
    str
        The retrieved value associated with the given key
    """
    if not _on_fabric():
        return ""

    try:
        from synapse.ml.internal_utils.session_utils import get_fabric_context
        return get_fabric_context().get(key)
    except (ImportError, AttributeError):
        return ""


def _get_trident_config(key: str) -> str:
    """
    Retrieves the value from the Spark/Jupyter runtime configurations.

    For Spark runtime, this function first retrieves from the SparkConf. If no value is found, it then retrieves from
    the Hadoop configurations.

    For Jupyter runtime, this function first retrieves from the `~/.trident-context` file. If no value is found, it then
    retrieves from the file `/opt/spark/conf/spark-defaults.conf`.

    Parameters
    ----------
    key : str
        The key for the Spark/Jupyter config value.

    Returns
    -------
    str
        The retrieved value associated with the given key
    """
    if _on_fabric():
        global jupyter_config
        if jupyter_config is None:
            from synapse.ml.internal_utils.session_utils import get_fabric_context
            jupyter_config = get_fabric_context()
        return jupyter_config.get(key, "")
    else:
        return "local"


def _get_fabric_context_or_config(context_key: str, config_key: str) -> str:
    """
    Retrieves the value from the Fabric context or Spark/Jupyter configurations.

    This function first attempts to fetch the value with `context_key` from the Fabric context. If no value is found,
    it then retrieves the value using `config_key` from the Spark/Jupyter runtime configurations.

    Parameters
    ----------
    context_key : str
        The key for the Fabric context value.
    config_key : str
        The key for the Spark/Jupyter config value.

    Returns
    -------
    str
        The retrieved value associated with the given keys, preferring `context_key`
    """
    value = _get_fabric_context(context_key)
    if value:
        return value
    return _get_trident_config(config_key)


def _get_synapse_endpoint() -> str:
    return f"https://{SUPPORTED_ENVIRONMENTS[_get_environment()]}"


def _get_pbi_uri() -> str:
    return f"powerbi://{SUPPORTED_ENVIRONMENTS[_get_environment()]}"


def _get_fabric_rest_endpoint() -> str:
    return f"https://{SUPPORTED_FABRIC_REST_ENVIRONMENTS[_get_environment()]}"


def _get_workspace_url(workspace: str) -> str:
    url = f"{_get_pbi_uri()}v1.0/myorg/"
    if workspace == "My workspace":
        return url
    else:
        return f"{url}{quote(workspace)}"


def _get_workspace_path(workspace_name: str, workspace_id: str):
    if workspace_name == "My workspace":
        # retrieving datasets from "My workspace" (does not have a group GUID) requires a different query
        return "v1.0/myorg/"
    else:
        return f"v1.0/myorg/groups/{workspace_id}/"


def _get_environment() -> str:

    global environment

    if environment is None:

        if _on_fabric():
            environment = _get_trident_config("spark.trident.pbienv")

        if not environment:
            environment = 'msit'

        environment = environment.lower().strip()

        if environment not in SUPPORTED_ENVIRONMENTS:
            raise ValueError(f"Unsupported environment '{environment}'. We support {list(SUPPORTED_ENVIRONMENTS.keys())}")

    return environment


def _on_fabric() -> bool:
    """True if running on Fabric (spark or jupyter or ai skill)"""
    global on_fabric
    if on_fabric is None:
        on_fabric = "AZURE_SERVICE" in os.environ or _on_jupyter() or _on_aiskill()
    return on_fabric


def _on_jupyter() -> bool:
    global on_jupyter
    if on_jupyter is None:
        on_jupyter = os.environ.get("MSNOTEBOOKUTILS_RUNTIME_TYPE", "").lower() == "jupyter"
    return on_jupyter


def _on_aiskill() -> bool:
    global on_aiskill
    if on_aiskill is None:
        on_aiskill = os.environ.get("trident.aiskill.env", "").lower() == "true"
    return on_aiskill
