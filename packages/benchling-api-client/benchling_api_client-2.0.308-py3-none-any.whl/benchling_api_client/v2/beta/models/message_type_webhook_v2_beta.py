from enum import Enum
from functools import lru_cache
from typing import cast

from ..extensions import Enums


class MessageTypeWebhookV2Beta(Enums.KnownString):
    V2_BETAASSAYRUNCREATED = "v2-beta.assayRun.created"
    V2_BETAASSAYRUNUPDATEDFIELDS = "v2-beta.assayRun.updated.fields"
    V2_BETAENTITYREGISTERED = "v2-beta.entity.registered"
    V2_BETAENTRYCREATED = "v2-beta.entry.created"
    V2_BETAENTRYUPDATEDFIELDS = "v2-beta.entry.updated.fields"
    V2_BETAENTRYUPDATEDREVIEWRECORD = "v2-beta.entry.updated.reviewRecord"
    V2_BETAREQUESTCREATED = "v2-beta.request.created"
    V2_BETAREQUESTUPDATEDFIELDS = "v2-beta.request.updated.fields"
    V2_BETAREQUESTUPDATEDSTATUS = "v2-beta.request.updated.status"
    V2_BETAWORKFLOWTASKGROUPCREATED = "v2-beta.workflowTaskGroup.created"
    V2_BETAWORKFLOWTASKGROUPUPDATEDWATCHERS = "v2-beta.workflowTaskGroup.updated.watchers"
    V2_BETAWORKFLOWTASKCREATED = "v2-beta.workflowTask.created"
    V2_BETAWORKFLOWTASKUPDATEDASSIGNEE = "v2-beta.workflowTask.updated.assignee"
    V2_BETAWORKFLOWTASKUPDATEDSCHEDULEDON = "v2-beta.workflowTask.updated.scheduledOn"
    V2_BETAWORKFLOWTASKUPDATEDSTATUS = "v2-beta.workflowTask.updated.status"
    V2_BETAWORKFLOWTASKUPDATEDFIELDS = "v2-beta.workflowTask.updated.fields"
    V2_BETAWORKFLOWOUTPUTCREATED = "v2-beta.workflowOutput.created"
    V2_BETAWORKFLOWOUTPUTUPDATEDFIELDS = "v2-beta.workflowOutput.updated.fields"
    V0_BETALIFECYCLEACTIVATEREQUESTED = "v0-beta.lifecycle.activateRequested"
    V0_BETALIFECYCLEDEACTIVATED = "v0-beta.lifecycle.deactivated"
    V2_BETAAPPCONFIGURATIONUPDATED = "v2-beta.app.configuration.updated"

    def __str__(self) -> str:
        return str(self.value)

    @staticmethod
    @lru_cache(maxsize=None)
    def of_unknown(val: str) -> "MessageTypeWebhookV2Beta":
        if not isinstance(val, str):
            raise ValueError(f"Value of MessageTypeWebhookV2Beta must be a string (encountered: {val})")
        newcls = Enum("MessageTypeWebhookV2Beta", {"_UNKNOWN": val}, type=Enums.UnknownString)  # type: ignore
        return cast(MessageTypeWebhookV2Beta, getattr(newcls, "_UNKNOWN"))
