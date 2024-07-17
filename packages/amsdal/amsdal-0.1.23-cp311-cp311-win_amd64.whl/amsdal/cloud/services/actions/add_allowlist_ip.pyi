from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class AddAllowlistIPAction(CloudActionBase):
    def action(self, env_name: str, ip_address: str | None = None, application_name: str | None = None, application_uuid: str | None = None) -> bool: ...
