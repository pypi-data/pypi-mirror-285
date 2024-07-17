from amsdal.cloud.models.base import ListDeployResponse as ListDeployResponse
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class ListDeploysAction(CloudActionBase):
    def action(self, *, list_all: bool = True) -> ListDeployResponse: ...
