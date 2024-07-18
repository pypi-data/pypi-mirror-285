"""
Documents possible responses from gRPC server for bumblebee client
"""
from dataclasses import dataclass


@dataclass
class StatusResponses:
    """
    status codes paired with their descriptions
    """
    NORMAL = {
        "status": 0,
        "message": "Success"
    }

    MISMATCH = {
        "status": 1,
        "message": "lock_id doesn't match current device lock",
    }

    DEVICE_BUSY = {
        "status": 2,
        "message": "Device currently processing other request"
    }        

@dataclass
class LockManageStatus:
    """
    Statuses and descriptions for acquiring and releasing lock
    """

    SUCCESS = {
        "status": 0,
        "message": "Success"}
    MISMATCH = {
        "status": 1,
        "message": "lock_id does not match current device lock_id",
    }
    BUSY = {
        "status": 2,
        "message": "Lock currently in use unable to perform operation",
    }
