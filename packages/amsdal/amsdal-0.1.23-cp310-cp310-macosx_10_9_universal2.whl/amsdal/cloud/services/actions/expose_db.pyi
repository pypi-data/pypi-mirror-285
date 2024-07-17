from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase
from typing import Any

class ExposeDBAction(CloudActionBase):
    def action(self, env_name: str, application_name: str | None = None, application_uuid: str | None = None, ip_address: str | None = None) -> dict[str, Any]: ...
