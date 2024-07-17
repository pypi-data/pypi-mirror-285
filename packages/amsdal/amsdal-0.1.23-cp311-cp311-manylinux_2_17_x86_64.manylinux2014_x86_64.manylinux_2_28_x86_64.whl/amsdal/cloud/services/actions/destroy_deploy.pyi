from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class DestroyDeployAction(CloudActionBase):
    def action(self, deployment_id: str) -> bool: ...
