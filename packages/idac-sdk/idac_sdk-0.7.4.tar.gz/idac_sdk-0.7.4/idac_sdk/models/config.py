from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Extra

from idac_sdk.models.auth import Auth
from idac_sdk.models.vpn_config import VPNConfig


class Defaults(BaseModel, extra=Extra.allow):
    idac_fqdn: str
    idac_proto: str
    auth: Auth
    api_version: str
    vpn: VPNConfig = VPNConfig()


class iDACConfig(BaseModel, extra=Extra.allow):
    version: str
    defaults: Defaults
