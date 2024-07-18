from typing import Required, TypedDict

from dixa.api import DixaResource, DixaVersion
from dixa.exceptions import DixaAPIError
from dixa.model.v1.agent import (
    Agent,
    AgentBulkActionOutcome,
    AgentBulkActionOutcomes,
    AgentPresence,
)
from dixa.model.v1.team import Team


class AgentCreateBody(TypedDict, total=False):
    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    displayName: Required[str]
    email: Required[str]
    firstName: str
    lastName: str
    middleNames: list[str]
    phoneNumber: str


class AgentUpdateBody(TypedDict, total=False):
    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    displayName: Required[str]
    firstName: str
    lastName: str
    middleNames: list[str]
    phoneNumber: str


class AgentUpdateBulkBody(TypedDict, total=False):
    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    displayName: Required[str]
    firstName: str
    id: Required[str]
    lastName: str
    middleNames: list[str]
    phoneNumber: str


class AgentPatchBody(TypedDict, total=False):
    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    displayName: str
    firstName: str
    lastName: str
    middleNames: list[str]
    phoneNumber: str


class AgentPatchBulkBody(TypedDict, total=False):
    additionalEmails: list[str]
    additionalPhoneNumbers: list[str]
    avatarUrl: str
    displayName: str
    firstName: str
    id: Required[str]
    lastName: str
    middleNames: list[str]
    phoneNumber: str


class AgentListQuery(TypedDict, total=False):
    email: str
    phone: str


class AgentResource(DixaResource):
    """
    https://developer.rechargepayments.com/2021-01/addresses
    """

    resource = "agents"
    dixa_version: DixaVersion = "v1"

    def create(self, body: AgentCreateBody) -> Agent:
        """Create an agent.
        https://docs.dixa.io/openapi/dixa-api/beta/tag/Agents/#tag/Agents/operation/postAgents
        """
        data = self.client.post(self._url, body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Agent(**data)

    def create_bulk(self, body: list[AgentCreateBody]) -> list[AgentBulkActionOutcome]:
        """Create agents.
        https://docs.dixa.io/openapi/dixa-api/beta/tag/Agents/#tag/Agents/operation/postAgentsBulk
        """
        data = self.client.post(f"{self._url}/bulk", {"data": body}, list)
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        results = []
        for elem in data:
            for return_cls in AgentBulkActionOutcomes:
                try:
                    results.append(return_cls(**elem))
                    break
                except TypeError:
                    continue
            else:
                raise DixaAPIError(
                    f"Expected one of {AgentBulkActionOutcomes}, got {type(data).__name__}"
                )
        return results

    def get(self, agent_id: str) -> Agent:
        """Get an agent by id.
        https://docs.dixa.io/openapi/dixa-api/beta/tag/Agents/#tag/Agents/operation/getAgentsAgentid
        """
        data = self.client.get(f"{self._url}/{agent_id}")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Agent(**data)

    def update(self, agent_id: str, body: AgentUpdateBody) -> Agent:
        """Update an agent by id.
        https://docs.dixa.io/openapi/dixa-api/beta/tag/Agents/#tag/Agents/operation/putAgentsAgentid
        """
        data = self.client.put(f"{self._url}/{agent_id}", body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Agent(**data)

    def update_bulk(self, body: list[AgentUpdateBody]) -> list[AgentBulkActionOutcome]:
        """Update agents.
        https://docs.dixa.io/openapi/dixa-api/beta/tag/Agents/#tag/Agents/operation/putAgentsBulk
        """
        data = self.client.put(self._url, {"data": body}, list)
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        results = []
        for elem in data:
            for return_cls in AgentBulkActionOutcomes:
                try:
                    results.append(return_cls(**elem))
                    break
                except TypeError:
                    continue
            else:
                raise DixaAPIError(
                    f"Expected one of {AgentBulkActionOutcomes}, got {type(data).__name__}"
                )
        return results

    def delete(self, agent_id: str):
        """Delete an address by ID.
        https://docs.dixa.io/openapi/dixa-api/beta/tag/Agents/#tag/Agents/operation/deleteAgentsAgentid
        """
        return self.client.delete(f"{self._url}/{agent_id}")

    def list_(self, query: AgentListQuery | None = None) -> list[Agent]:
        """List agents.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Agents/#tag/Agents/operation/getAgents
        """
        return self.client.paginate(self._url, query)

    def get_presence(self, agent_id: str) -> AgentPresence:
        """Get agent presence.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Agents/#tag/Agents/operation/getAgentsAgentidPresence
        """
        data = self.client.get(f"{self._url}/{agent_id}/presence")
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return AgentPresence(**data)

    def list_presence(self) -> list[AgentPresence]:
        """List agent presence.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Agents/#tag/Agents/operation/getAgentsPresence
        """
        return self.client.paginate(f"{self._url}/presence")

    def list_teams(self, agent_id: str) -> list[Team]:
        """List teams.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Agents/#tag/Agents/operation/getAgentsAgentidTeams
        """
        return self.client.paginate(f"{self._url}/{agent_id}/teams")

    def patch(self, agent_id: str, body: AgentPatchBody) -> Agent:
        """Patch an agent.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Agents/#tag/Agents/operation/patchAgentsAgentid
        """
        data = self.client.patch(f"{self._url}/{agent_id}", body)
        if not isinstance(data, dict):
            raise DixaAPIError(f"Expected dict, got {type(data).__name__}")
        return Agent(**data)

    def patch_bulk(
        self, body: list[AgentPatchBulkBody]
    ) -> list[AgentBulkActionOutcome]:
        """Patch agents.
        https://docs.dixa.io/openapi/dixa-api/v1/tag/Agents/#tag/Agents/operation/patchAgentsBulk
        """
        data = self.client.patch(self._url, {"data": body}, list)
        if not isinstance(data, list):
            raise DixaAPIError(f"Expected list, got {type(data).__name__}")
        results = []
        for elem in data:
            for return_cls in AgentBulkActionOutcomes:
                try:
                    results.append(return_cls(**elem))
                    break
                except TypeError:
                    continue
            else:
                raise DixaAPIError(
                    f"Expected one of {AgentBulkActionOutcomes}, got {type(data).__name__}"
                )
        return results
