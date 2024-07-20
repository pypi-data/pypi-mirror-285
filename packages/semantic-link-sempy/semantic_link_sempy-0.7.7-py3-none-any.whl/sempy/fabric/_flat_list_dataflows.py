import pandas as pd

from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._token_provider import SynapseTokenProvider


def list_dataflows() -> pd.DataFrame:
    """
    List all the Power BI dataflows.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per data flow.
    """
    rest_api = _PBIRestAPI(token_provider=SynapseTokenProvider())

    payload = rest_api.list_dataflows()

    df = rename_and_validate_from_records(payload, [
                               ("id",        "Dataflow Storage Account Id",   "str"),
                               ("name",      "Dataflow Storage Account Name", "str"),
                               ("isEnabled", "Is Enabled",                    "bool")])

    return df
