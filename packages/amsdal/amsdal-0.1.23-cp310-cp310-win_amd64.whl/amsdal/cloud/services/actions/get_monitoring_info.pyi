from amsdal.cloud.models.base import GetMonitoringInfoResponse as GetMonitoringInfoResponse
from amsdal.cloud.services.actions.base import CloudActionBase as CloudActionBase

class GetMonitoringInfoAction(CloudActionBase):
    def action(self, env_name: str, application_name: str | None = None, application_uuid: str | None = None) -> GetMonitoringInfoResponse: ...
