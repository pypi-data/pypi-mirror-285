from amsdal.cloud.models.base import SignupReponseCredentials as SignupReponseCredentials
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class FreeSignupAction(CloudActionBase):
    def action(self, organization_name: str, email: str) -> SignupReponseCredentials: ...
