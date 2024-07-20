from sempy.fabric._token_provider import create_on_access_token_expired_callback, TokenProvider


class AdomdConnection:
    """
    Cached wrapper of Microsoft.AnalysisServices AdomdConnection object, designed to be used with python context manager.

    Parameters
    ----------
    dax_connection_string : str
        Adomd connection string.
    token_provider : TokenProvider
        Dataset client token provider (used for token refresh)
    """

    def __init__(self, dax_connection_string: str, token_provider: TokenProvider):
        self.adomd_connection = None
        self.dax_connection_string = dax_connection_string
        self.token_provider = token_provider

    def __enter__(self):
        """
        Create a new Microsoft.AnalysisServices.AdomdClient.AdomdConnection object, or get from existing cache.
        """
        return self.get_or_create_connection()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """
        Handles clearing the cached connection only if an exception is thrown (exception will still be raised).
        """
        if exc_type is not None:
            self.close_and_dispose_connection()

    def get_or_create_connection(self):
        """
        If connection is not already created, creates a new Microsoft.AnalysisServices.AdomdClient.AdomdConnection object.
        Connection is opened and has token refresh callback.
        """
        if self.adomd_connection is None:
            from Microsoft.AnalysisServices.AdomdClient import AdomdConnection
            from Microsoft.AnalysisServices import AccessToken
            from System import Func

            self.adomd_connection = AdomdConnection(self.dax_connection_string)
            get_access_token = create_on_access_token_expired_callback(self.token_provider)
            self.adomd_connection.AccessToken = get_access_token(self.adomd_connection.AccessToken)
            self.adomd_connection.OnAccessTokenExpired = Func[AccessToken, AccessToken](get_access_token)
            self.adomd_connection.Open()

        return self.adomd_connection

    def close_and_dispose_connection(self):
        """
        If a connection is cached, close and dispose of it and reset cache to None.
        """
        from System import NotSupportedException
        if self.adomd_connection is not None:
            try:
                # for some unknown reason, closing the connection throws an exception for larger datasets
                self.adomd_connection.Close()
                self.adomd_connection.Dispose()
            except NotSupportedException:
                # ignore for now, open issue we investigate
                pass

            self.adomd_connection = None
