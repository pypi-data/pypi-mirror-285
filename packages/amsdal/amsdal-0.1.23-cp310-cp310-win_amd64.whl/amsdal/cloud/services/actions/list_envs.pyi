from amsdal.cloud.models.base import ListEnvsResponse as ListEnvsResponse
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class ListEnvsAction(CloudActionBase):
    def action(self, *, application_name: str | None = None, application_uuid: str | None = None) -> ListEnvsResponse: ...
