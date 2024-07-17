from amsdal.cloud.models.base import CreateSessionDetails as CreateSessionDetails
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class CreateSessionAction(CloudActionBase):
    def action(self, encrypted_data: bytes) -> CreateSessionDetails: ...
