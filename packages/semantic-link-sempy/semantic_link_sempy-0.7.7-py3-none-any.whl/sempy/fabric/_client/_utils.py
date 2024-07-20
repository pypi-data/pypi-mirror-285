import os
import sys
from pathlib import Path
from typing import Optional

from sempy.fabric._token_provider import create_on_access_token_expired_callback, TokenProvider
from sempy._utils._log import log_xmla


_analysis_services_initialized = False


def _init_analysis_services() -> None:
    global _analysis_services_initialized
    if _analysis_services_initialized:
        return

    from clr_loader import get_coreclr
    from pythonnet import set_runtime

    my_path = Path(__file__).parent

    rt = get_coreclr(runtime_config=os.fspath(my_path / ".." / ".." / "dotnet.runtime.config.json"))
    set_runtime(rt)

    import clr
    assembly_path = my_path / ".." / ".." / "lib"

    sys.path.append(os.fspath(assembly_path))
    clr.AddReference(os.fspath(assembly_path / "Microsoft.AnalysisServices.Tabular.dll"))
    clr.AddReference(os.fspath(assembly_path / "Microsoft.AnalysisServices.AdomdClient.dll"))
    clr.AddReference(os.fspath(assembly_path / "Microsoft.Fabric.SemanticLink.XmlaTools.dll"))

    _analysis_services_initialized = True


@log_xmla
def _create_tom_server(connection_string: str, token_provider: TokenProvider):
    import Microsoft.AnalysisServices.Tabular as TOM
    from Microsoft.AnalysisServices import AccessToken
    from System import Func

    tom_server = TOM.Server()

    get_access_token = create_on_access_token_expired_callback(token_provider)

    tom_server.AccessToken = get_access_token(None)
    tom_server.OnAccessTokenExpired = Func[AccessToken, AccessToken](get_access_token)

    tom_server.Connect(connection_string)

    return tom_server


def _odata_quote(s: str) -> str:
    # https://stackoverflow.com/questions/4229054/how-are-special-characters-handled-in-an-odata-query

    return (s.replace("'", "''")
             .replace("%", "%25")
             .replace("+", "%2B")
             .replace("/", "%2F")
             .replace("?", "%3F")
             .replace("#", "%23")
             .replace("&", "%26"))


def _build_adomd_connection_string(datasource: str, initial_catalog: Optional[str] = None, readonly: bool = True) -> str:
    """
    Build ADOMD Connection string

    Parameters
    ----------
    datasource : str
        The data source string (e.g. a workspace url).
    initial_catalog : str
        Optional initial catalog (e.g. the dataset name).
    readonly : bool
        If true the connection is read-only and can connect to read-only replicas. Default to true.
    """

    # build datasource
    if readonly:
        datasource += "?readonly"

    # escape data source
    datasource = datasource.replace('"', '""')

    connection_str = f'DataSource="{datasource}"'

    if initial_catalog is not None:
        initial_catalog = initial_catalog.replace('"', '""')

        connection_str += f';Initial Catalog="{initial_catalog}"'

    connection_str += ";Application Name=SemPy"

    return connection_str
