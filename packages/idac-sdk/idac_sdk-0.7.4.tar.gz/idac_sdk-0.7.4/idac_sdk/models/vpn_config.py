from pydantic import BaseModel, Extra
from enum import Enum
from typing import Optional


class VPNType(str, Enum):
    none = "none"
    vpod = "vpod"
    explicit = "explicit"
    request = "request"
    secure_repo = "secure_repo"


class VPNParameters(BaseModel, extra=Extra.allow):
    # for type set explicit or request
    host: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

    # for type set secure_repo
    secure_repo_space: Optional[str] = None
    secure_repo_file: Optional[str] = None
    secure_repo_block: Optional[str] = None
    secure_repo_key: Optional[str] = None


class VPNConfig(BaseModel, extra=Extra.allow):
    type: VPNType = VPNType.none
    params: VPNParameters = VPNParameters()
