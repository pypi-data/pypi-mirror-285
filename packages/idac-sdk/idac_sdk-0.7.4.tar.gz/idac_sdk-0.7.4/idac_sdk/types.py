from enum import Enum, unique


@unique
class IDACRequestType(Enum):
    """iDAC request types"""

    SIMPLE = 0
    STATELESS = 1
    STATEFUL = 2


@unique
class IDACRequestStatus(Enum):
    """iDAC request statuses"""

    active = "active"
    queued = "queued"
    toBeDeleted = "toBeDeleted"
    update = "update"
    extend = "extend"
    scheduled = "scheduled"
    starting = "starting"
    cleaning = "cleaning"
    error = "error"
    cancelled = "cancelled"
    onboardError = "onboardError"
    complete = "complete"
    executed = "executed"
    deleted = "deleted"


@unique
class IDACAuthType(Enum):
    """iDAC authentication types"""

    NONE = 0
    BASIC = 1
    BEARER = 2
    DCLOUD_SESSION = 3
    WORKER = 4
