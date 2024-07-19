from typing import Any, Generic, List, Optional, TypeVar, Union, Type, cast
from functools import wraps
from httpx import URL

from idac_sdk.base.controller import BaseIDACController
from idac_sdk.asynced.controller import IDACController as AsyncController
from idac_sdk.synced.controller import IDACController as SyncController
from idac_sdk.models.vpn_config import VPNConfig, VPNType
from idac_sdk.types import IDACAuthType, IDACRequestStatus
from idac_sdk.log import logger
from idac_sdk.errors import IncorrectWantedStateError, NoControllerError, UnknownVPNType
from idac_sdk.session_data import SessionData
from . import DEFAULT_USER_AGENT


def check_controller(method):

    @wraps(method)
    def wrapper(self, *method_args, **method_kwargs):
        if not isinstance(self.controller, BaseIDACController):
            raise NoControllerError("iDAC controller not provided")
        if (hasattr(self, "wanted_controller_type") and self.wanted_controller_type and
                not isinstance(self.controller, self.wanted_controller_type)):
            raise NoControllerError("Incorrect iDAC controller provided")
        return method(self, *method_args, **method_kwargs)

    return wrapper


T = TypeVar("T", AsyncController, SyncController)


class BaseIDACRequest(Generic[T]):
    session_data: Optional[SessionData]
    controller: T
    uuid: Optional[str]
    user_agent: str
    vpn: VPNConfig
    wanted_controller_type: Optional[Type[T]]
    max_redirects = 10

    def __init__(
        self,
        uuid: Optional[str] = None,
        session_data: Optional[SessionData] = None,
        controller: Optional[T] = None,
        user_agent: Optional[str] = None,
        vpn: Optional[VPNConfig] = None,
        wanted_controller_type: Optional[Type[T]] = None,
    ) -> None:
        """
        Base IDACRequest Object

        IDACRequest describes iDAC request object.
        Handles all operations with requests: create, cleanup, restart.

        Args:
            uuid (Optional[str], optional): Request UUID. Should be provided to work with existing
                requests Defaults to None.
            session_data (Optional[SessionData], optional): SessionData object. Will be send to iDAC
                controller Defaults to None.
            controller (Optional[IDACController], optional): IDACCOntroller object.
                Defaults to None.
            user_agent (Optional[str], optional): User-Agent string. Defaults to None.
            vpn (Optional[VPNConfig], optional): VPN options
        """
        if not uuid:
            # no UUID -> new request, need to set session_data and controller
            self.uuid = None
        else:
            # UUID provided -> existing request
            self.uuid = uuid

        self.session_data = SessionData() if not session_data else session_data

        self.user_agent = user_agent if user_agent else DEFAULT_USER_AGENT
        self.wanted_controller_type = wanted_controller_type

        if not controller and controller is not False:
            if not self.wanted_controller_type:
                raise NoControllerError("iDAC controller not provided")
            if isinstance(self.session_data, SessionData) and self.session_data.has("creds"):
                self.controller = self.wanted_controller_type(
                    auth_type=IDACAuthType.DCLOUD_SESSION,
                    auth=self.session_data.get("creds"),
                )
            else:
                self.controller = self.wanted_controller_type()
        else:
            self.controller = controller

        self.vpn = vpn or self.controller.vpn

    def add_vpn(self, where: dict[str, Any]) -> dict[str, Any]:
        """Adds VPN parameters to request

        Args:
            where (dict[str, Any]): Where VPN params should be added

        Raises:
            UnknownVPNType: Raised if unknown VPN type configured

        Returns:
            dict[str, Any]: updated dictionary with VPN parameters
        """
        logger.debug("Adding VPN parameters: %s", self.vpn)
        if ("idacVpn" in where) or (self.vpn.type == VPNType.none):
            return where

        if self.vpn.type == VPNType.vpod:
            # adding params for vPod VPN. `datacenter`, `vpod` and `anycpwd` should be loaded from session.xml
            where.update({"idacVpn": "dcloud-vpod"})
        elif self.vpn.type == VPNType.request or self.vpn.type == VPNType.explicit:
            # adding params for `request` - explicit VPN settings
            where.update({
                "idacVpn": "request",
                "idacVpnHost": self.vpn.params.host,
                "idacVpnUsername": self.vpn.params.username,
                "idacVpnPassword": self.vpn.params.password,
            })
        elif self.vpn.type == VPNType.secure_repo:
            # adding params for `secure_repo` - VPN settings will be loaded from secure repo
            where.update({
                "idacVpn": "secureRepo",
                "idacVpnSecureRepoSpace": self.vpn.params.secure_repo_space,
                "idacVpnSecureRepoFile": self.vpn.params.secure_repo_file,
                "idacVpnSecureRepoBlock": self.vpn.params.secure_repo_block,
                "idacVpnSecureRepoKey": self.vpn.params.secure_repo_key,
            })
        else:
            raise UnknownVPNType("Unknown VPN type provided")

        return where

    def sanitize_states(
        self, states: Union[List[IDACRequestStatus], List[str], List[Union[IDACRequestStatus, str]]]
    ) -> List[IDACRequestStatus]:
        for idx, val in enumerate(states):
            if isinstance(val, str):
                cast(List[IDACRequestStatus], states)[idx] = IDACRequestStatus(val)
            elif not isinstance(val, IDACRequestStatus):
                raise IncorrectWantedStateError(f"Incorrect wanted state: {val}")

        return cast(List[IDACRequestStatus], states)

    def raise_if_error(self, url: URL | str) -> None:
        err_detect = "notifications/error.php"
        if ((isinstance(url, str) and err_detect in url) or
            (isinstance(url, URL) and err_detect in url.path)):
            u = url if isinstance(url, URL) else URL(url)
            p = u.params
            msg: str = p.get("msg", None)
            if not msg:
                raise Exception(f"Unknown error during request execution for URL {u}")

            parts = msg.split(';')
            raise Exception("; ".join(parts))
