from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class DeleteDepenencyAction(CloudActionBase):
    def action(self, dependency_name: str, env_name: str, application_name: str | None = None, application_uuid: str | None = None) -> bool: ...
