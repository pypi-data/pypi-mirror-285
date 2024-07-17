from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class DeleteSecretAction(CloudActionBase):
    def action(self, secret_name: str, env_name: str, application_uuid: str | None = None, application_name: str | None = None) -> bool: ...
