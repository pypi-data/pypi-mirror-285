from amsdal.cloud.models.base import ListSecretsDetails as ListSecretsDetails
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class ListSecretsAction(CloudActionBase):
    def action(self, env_name: str, application_uuid: str | None = None, application_name: str | None = None, *, with_values: bool = False) -> ListSecretsDetails: ...
