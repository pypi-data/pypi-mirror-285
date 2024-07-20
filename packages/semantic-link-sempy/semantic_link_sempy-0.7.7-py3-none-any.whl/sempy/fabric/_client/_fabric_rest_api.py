import base64
import json
from urllib.parse import quote
from dataclasses import dataclass

from sempy.fabric._client._rest_client import FabricRestClient, OperationStart
from sempy.fabric.exceptions import FabricHTTPException
from sempy.fabric._token_provider import TokenProvider
from typing import Optional, Union


@dataclass
class JobStatus:
    status: str
    retry_after: int


class _FabricRestAPI():
    _rest_client: FabricRestClient

    def __init__(self, token_provider: Optional[TokenProvider] = None):
        self._rest_client = FabricRestClient(token_provider)

    def get_my_workspace_id(self) -> str:
        # TODO: we should align on a single API to retrieve workspaces using a single API,
        #       but we need to wait until the API support filtering and paging
        # Using new Fabric REST endpoints
        payload = self.list_workspaces()

        workspaces = [ws for ws in payload if ws["type"] == 'Personal']

        if len(workspaces) != 1:
            raise ValueError(f"Unable to resolve My workspace ID. Zero or more than one workspaces found ({len(workspaces)})")

        return workspaces[0]['id']

    def create_workspace(self, display_name: str, capacity_id: Optional[str] = None, description: Optional[str] = None) -> str:
        payload = {"displayName": display_name}

        if capacity_id is not None:
            payload["capacityId"] = capacity_id

        if description is not None:
            payload["description"] = description

        response = self._rest_client.post("v1/workspaces", json=payload)
        if response.status_code != 201:
            raise FabricHTTPException(response)

        return response.json()["id"]

    def delete_workspace(self, workspace_id: str):
        response = self._rest_client.delete(f"v1/workspaces/{workspace_id}")
        if response.status_code != 200:
            raise FabricHTTPException(response)

    def create_item(self, workspace_id: str, payload, lro_max_attempts: int, lro_operation_name: str) -> str:
        path = f"v1/workspaces/{workspace_id}/items"

        response = self._rest_client.post(path,
                                          json=payload,
                                          headers={'Content-Type': 'application/json'},
                                          lro_wait=True,
                                          lro_max_attempts=lro_max_attempts,
                                          lro_operation_name=lro_operation_name)

        if response.status_code in [200, 201]:
            return response.json()["id"]
        else:
            raise FabricHTTPException(response)

    def create_lakehouse(self,
                         workspace_id: str,
                         display_name: str,
                         description: Optional[str] = None,
                         lro_max_attempts: int = 10) -> str:
        payload = {
            "displayName": display_name,
            "type": "Lakehouse"
        }

        if description is not None:
            payload["description"] = description

        return self.create_item(workspace_id, payload, lro_max_attempts, "create lakehouse")

    def delete_item(self, workspace_id: str, artifact_id: str):
        path = f"v1/workspaces/{workspace_id}/items/{artifact_id}"

        response = self._rest_client.delete(path)

        if response.status_code != 200:
            raise FabricHTTPException(response)

    def create_notebook(self,
                        workspace_id: str,
                        display_name: str,
                        description: Optional[str] = None,
                        content: Optional[str] = None,
                        lro_max_attempts: int = 10) -> str:
        payload: dict[str, Union[str, dict]] = {
            "displayName": display_name,
            "type": "Notebook"
        }

        if description is not None:
            payload["description"] = description

        if content is not None:
            payload["definition"] = {
                "format": "ipynb",
                "parts": [
                    {
                        "path": "artifact.content.ipynb",
                        "payload": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                        "payloadType": "InlineBase64"
                    }
                ]
            }

        return self.create_item(workspace_id, payload, lro_max_attempts, "create notebook")

    def run_item_job(self, workspace_id: str, item_id: str, jobType: str, executionData: Optional[dict] = None) -> OperationStart:
        response = self._rest_client.post(
            f"v1/workspaces/{workspace_id}/items/{item_id}/jobs/instances?jobType={jobType}",
            data=json.dumps({"executionData": {}},),
            headers={'Content-Type': 'application/json'}
        )

        return OperationStart(response)

    def run_notebook_job(self, workspace_id: str, notebook_id: str) -> OperationStart:
        return self.run_item_job(workspace_id, notebook_id, "RunNotebook")

    def get_job_status(self, workspace_id: str, item_id: str, run_id: str) -> JobStatus:
        response = self._rest_client.get(
            f"v1/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{run_id}",
            headers={'Content-Type': 'application/json'})

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return JobStatus(response.json()['status'],
                         response.headers.get("Retry-After", 2))

    def list_items(self, workspace_id: str, type: Optional[str] = None) -> list:
        path = f"v1/workspaces/{workspace_id}/items"

        if type is not None:
            path += f"?type={quote(type)}"

        return self._rest_client.get_paged(path)

    def list_workspaces(self) -> list:
        return self._rest_client.get_paged("v1/workspaces")

    def list_capacities(self):
        return self._rest_client.get_paged("v1/capacities")
