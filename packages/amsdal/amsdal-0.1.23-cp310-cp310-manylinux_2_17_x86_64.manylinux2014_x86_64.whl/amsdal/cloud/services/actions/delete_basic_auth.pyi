from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class DeleteBasicAuthAction(CloudActionBase):
    def action(self, env_name: str, application_name: str | None = None, application_uuid: str | None = None) -> bool: ...
