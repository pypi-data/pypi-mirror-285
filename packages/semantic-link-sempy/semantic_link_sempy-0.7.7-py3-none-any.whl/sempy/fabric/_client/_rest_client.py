import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
from tqdm.auto import tqdm

from sempy.fabric.exceptions import FabricHTTPException
from requests.adapters import HTTPAdapter, Retry
from requests.sessions import Session
from sempy._utils._log import log_retry, log_rest_response, log_rest_request
from sempy.fabric._token_provider import SynapseTokenProvider, TokenProvider

from sempy.fabric._environment import _get_synapse_endpoint, _get_environment, _get_fabric_rest_endpoint
from typing import Dict, Optional


class RetryWithLogging(Retry):
    @log_retry
    def increment(self, *args, **kwargs):
        return super().increment(*args, **kwargs)


class SessionWithLogging(Session):
    @log_rest_request
    def prepare_request(self, *args, **kwargs):
        return super().prepare_request(*args, **kwargs)


@dataclass
class OperationStatus:
    status: str
    retry_after: int
    percent_complete: int


class OperationStart:
    operation_id: str
    retry_after: int

    def __init__(self, response):
        self.operation_id = response.headers.get("x-ms-operation-id") or response.headers['Location'].split('/')[-1]
        self.retry_after = int(response.headers.get("Retry-After", 2))


class BaseRestClient(ABC):
    """
    REST client to access Fabric and PowerBI endpoints. Authentication tokens are automatically acquired from the execution environment.

    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        Implementation of TokenProvider that can provide auth token
        for access to the PowerBI workspace. Will attempt to acquire token
        from its execution environment if not provided.
    """
    def __init__(self, token_provider: Optional[TokenProvider] = None):
        self.http = SessionWithLogging()

        @log_rest_response
        def validate_rest_response(response, *args, **kwargs):
            if response.status_code >= 400:
                raise FabricHTTPException(response)
        self.http.hooks["response"] = [validate_rest_response]
        retry_strategy = RetryWithLogging(
            total=10,
            allowed_methods=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"],
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1
        )
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http.mount("https://", retry_adapter)

        self.token_provider = token_provider or SynapseTokenProvider()
        self.default_base_url = self._get_default_base_url()

    @abstractmethod
    def _get_default_base_url(self):
        pass

    def _get_headers(self) -> dict:
        # this could be static / a function
        correlation_id = str(uuid.uuid4())
        return {
            'authorization': f'Bearer {self.token_provider()}',
            'Accept': 'application/json',
            'ActivityId': correlation_id
        }

    def request(self, method: str, path_or_url: str, *args, **kwargs):
        """
        Request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        method : str
            HTTP method.
        path_or_url : str
            The path or the url to the resource.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        headers = self._get_headers()
        headers.update(kwargs.get("headers", {}))

        # overwrite url + headers
        if path_or_url.startswith("https://"):
            url = path_or_url
        else:
            url = f"{self.default_base_url}{path_or_url}"

        kwargs["url"] = url
        kwargs["headers"] = headers

        return self.http.request(method, *args, **kwargs)

    def get(self, path_or_url: str, *args, **kwargs):
        """
        GET request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("GET", path_or_url, *args, **kwargs)

    def post(self, path_or_url: str, *args, **kwargs):
        """
        POST request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("POST", path_or_url, *args, **kwargs)

    def delete(self, path_or_url: str, *args, **kwargs):
        """
        DELETE request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("DELETE", path_or_url, *args, **kwargs)

    def head(self, path_or_url: str, *args, **kwargs):
        """
        HEAD request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("HEAD", path_or_url, *args, **kwargs)

    def patch(self, path_or_url: str, *args, **kwargs):
        """
        PATCH request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("PATCH", path_or_url, *args, **kwargs)

    def put(self, path_or_url: str, *args, **kwargs):
        """
        PUT request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("PUT", path_or_url, *args, **kwargs)


class FabricRestClient(BaseRestClient):
    """
    REST client to access Fabric REST endpoints. Authentication tokens are automatically acquired from the execution environment.

    All methods (get, post, ...) have an additional parameter `lro_wait` that can be set to True to wait for the long-running-operation to complete.
    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        Implementation of TokenProvider that can provide auth token
        for access to the PowerBI workspace. Will attempt to acquire token
        from its execution environment if not provided.
    """
    def __init__(self, token_provider: Optional[TokenProvider] = None):
        super().__init__(token_provider)

    def _get_default_base_url(self):
        return _get_fabric_rest_endpoint()

    def request(self,
                method: str,
                path_or_url: str,
                lro_wait: Optional[bool] = False,
                lro_max_attempts: int = 10,
                lro_operation_name: Optional[str] = None,
                *args,
                **kwargs):
        """
        Request to the Fabric REST API.

        Parameters
        ----------
        method : str
            HTTP method.
        path_or_url : str
            The path or the url to the resource.
        lro_wait : bool, default=False
            If True, waits for the long-running-operation to complete.
        lro_max_attempts : int, default=10
            The maximum number of attempts to wait for the long-running-operation to complete.
        lro_operation_name : str, default=None
            The name of the operation to wait for displayed via TQDM.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        response = super().request(method, path_or_url, *args, **kwargs)

        if not lro_wait or response.status_code != 202:
            return response

        return self._wait_for_operation(lro_operation_name or path_or_url,
                                        OperationStart(response),
                                        lro_max_attempts)

    def get_paged(self, path_or_url: str, headers: Optional[Dict] = None, *args, **kwargs) -> list:
        """
        GET request to the Fabric REST API that handles pagination.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        headers : dict, default=None
            Headers to be included in the request.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        list
            The list of rows from the response.
        """

        if headers is None:
            headers = {}

        headers['Content-Type'] = 'application/json'
        response = self.get(path_or_url, *args, headers=headers, **kwargs)

        if response.status_code != 200:
            raise FabricHTTPException(response)

        rows = []
        while True:
            response_json = response.json()
            rows.extend(response_json['value'])

            continuation_uri = response_json.get("continuationUri")
            if continuation_uri is None:
                break

            response = self.get(continuation_uri, headers=headers)
            if response.status_code != 200:
                raise FabricHTTPException(response)

        return rows

    def _get_operation_status(self, operation_id: str) -> OperationStatus:
        response = self.get(
            f"v1/operations/{operation_id}",
            headers={'Content-Type': 'application/json'}
        )
        response_json = response.json()

        return OperationStatus(
            response_json['status'],
            int(response.headers.get("Retry-After", 2)),
            response_json["percentComplete"])

    def _wait_for_operation(self, name, operation: OperationStart, max_attempts: int = 10) -> str:
        bar = tqdm(total=100, desc=f"Waiting {operation.retry_after} seconds for {name} operation to check for status")

        operation_id = operation.operation_id

        for _ in range(max_attempts):
            time.sleep(operation.retry_after)

            op_status = self._get_operation_status(operation_id)
            if op_status.status in ['Failed', 'Undefined']:
                raise RuntimeError(f"Operation {name} {operation_id} failed: {op_status.status}")

            if op_status.status == 'Succeeded':
                bar.set_description(f"Operation {name} successfully completed")
                bar.update(100)

                return self.get(
                    f"v1/operations/{operation_id}/result",
                    headers={'Content-Type': 'application/json'}
                )

            bar.set_description(f"Waiting for {name} to complete: {op_status.status}")
            bar.update(op_status.percent_complete)

        raise TimeoutError("Operation timed out.")


class PowerBIRestClient(BaseRestClient):
    """
    REST client to access PowerBI REST endpoints. Authentication tokens are automatically acquired from the execution environment.

    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        Implementation of TokenProvider that can provide auth token
        for access to the PowerBI workspace. Will attempt to acquire token
        from its execution environment if not provided.
    """
    def __init__(self, token_provider: Optional[TokenProvider] = None):
        super().__init__(token_provider)

    def _get_default_base_url(self):
        # The endpoint api.powerbi.com does not work for REST calls using the "pbi" token due to limited audience
        if _get_environment() in ["prod", "msit"]:
            headers = self._get_headers()
            return self.http.get("https://api.powerbi.com/powerbi/globalservice/v201606/clusterdetails", headers=headers).json()["clusterUrl"] + "/"
        else:
            return _get_synapse_endpoint()
