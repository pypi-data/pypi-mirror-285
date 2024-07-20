from uuid import UUID

from sempy.fabric._token_provider import SynapseTokenProvider
from sempy.fabric._client import WorkspaceClient
from sempy.fabric._client._fabric_rest_api import _FabricRestAPI
from typing import Dict, Optional, Union


_workspace_clients: Dict[Optional[Union[str, UUID]], WorkspaceClient] = dict()
_fabric_rest_api: Optional[_FabricRestAPI] = None


def _get_or_create_workspace_client(workspace_name: Optional[Union[str, UUID]]) -> WorkspaceClient:
    global _workspace_clients

    client = _workspace_clients.get(workspace_name)
    if client is None:
        client = WorkspaceClient(workspace_name)
        _workspace_clients[workspace_name] = client

    return client


def _get_fabric_rest_api() -> _FabricRestAPI:
    global _fabric_rest_api

    # cache FabricRestAPI client to re-use HTTP socket
    if _fabric_rest_api is None:
        _fabric_rest_api = _FabricRestAPI(SynapseTokenProvider())

    return _fabric_rest_api
