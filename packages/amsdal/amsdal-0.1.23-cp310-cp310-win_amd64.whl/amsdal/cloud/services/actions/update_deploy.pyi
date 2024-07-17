from amsdal.cloud.models.base import UpdateDeployStatusResponse as UpdateDeployStatusResponse
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class UpdateDeployAction(CloudActionBase):
    def action(self, deployment_id: str) -> UpdateDeployStatusResponse: ...
