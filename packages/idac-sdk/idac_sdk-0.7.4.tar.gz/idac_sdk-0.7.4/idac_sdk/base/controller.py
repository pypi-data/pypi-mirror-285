from typing import Dict, Optional, Tuple, Union
import json
import httpx
from base64 import b64encode
import warnings
from operator import itemgetter
from idac_sdk.lib._helpers import get_worker_hash
from idac_sdk.models.auth import Auth

from idac_sdk.log import logger
from idac_sdk.config import have_config, load_config
from idac_sdk.models.vpn_config import VPNConfig
from idac_sdk.types import IDACAuthType
from idac_sdk.errors import (
    IncorrectControllerProtoError,
    IncorrectControllerURLError,
    NoAuth,
    NoAuthTokenInResponse,
    NoIDACConfig,
    NoIdError,
)

from . import DEFAULT_USER_AGENT


class BaseIDACController:
    proto: str
    url: str
    api_version: str
    auth: Auth
    user_agent: str
    vpn: VPNConfig

    def __init__(
        self,
        proto: Optional[str] = None,
        url: Optional[str] = None,
        api_version: Optional[str] = None,
        auth_type: Optional[IDACAuthType] = None,
        auth: Optional[Union[str, Tuple[str, str]]] = None,
        worker_id: Optional[str] = None,
        worker_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        vpn: Optional[VPNConfig] = None,
    ) -> None:
        """
        Base IDACController Object

        IDACController describes iDAC controller instance.
        Handles generation of API URLs and Auth Headers required for authentication.

        Args:
            proto (str, optional): `http` or `https`.
            url (str, optional): URL of the controller.
            api_version (str, optional): API version.
            auth_type (IDACAuthType, optional): Type of authentication.
            auth (Union[str, Tuple[str, str]], optional): Authentication data. Usually a token. If
                BASIC auth type is set, can be specified as a tuple in format [username, password]
                which will be automatically encoded in base64. Defaults to None.
            user_agent (Optional[str]): User-Agent string.

        Returns:
            None

        Raises:
            IncorrectControllerProtoError: Raised if incorrect proto provided
            IncorrectControllerURLError: Raised if no URL provided
        """
        if not have_config():
            warnings.warn("iDAC config not found", NoIDACConfig)

        cfg = load_config()

        self.proto = proto if proto else cfg.defaults.idac_proto
        if self.proto != "http" and self.proto != "https":
            raise IncorrectControllerProtoError(f"Unsupported proto: {proto}")

        self.url = url if url else cfg.defaults.idac_fqdn
        if not self.url:
            raise IncorrectControllerURLError("Controller URL not provided")

        self.user_agent = user_agent if user_agent else DEFAULT_USER_AGENT
        self.api_version = api_version if api_version else cfg.defaults.api_version

        auth_type = auth_type if auth_type else IDACAuthType[cfg.defaults.auth.type]
        params: dict[str, str] = {}
        if (auth and isinstance(auth, str) and auth_type not in [
                IDACAuthType.DCLOUD_SESSION.name,
                IDACAuthType.NONE.name,
        ]):
            params = {"token": auth}
        elif auth_type == IDACAuthType.BASIC.name:
            if isinstance(auth, list):
                params = {
                    "token": b64encode(bytes(f"{auth[0]}:{auth[1]}", "utf-8")).decode("utf-8")
                }
        elif auth_type == IDACAuthType.WORKER.name:
            if worker_id and worker_secret:
                params = {"secret": worker_secret, "client_id": worker_id}
        else:
            params = {}
        self.auth = Auth(type=auth_type.name, params=params)
        self.vpn = vpn or cfg.defaults.vpn

    def api_string(self, api: str) -> str:
        """Generate full URL for an API

        Args:
          api (str): API

        Returns:
          str: Full API URL
        """
        result = f"{self.proto}://{self.url}"
        if not result.endswith("/"):
            result = result + "/"
        return result + f"api/v{self.api_version}/{api}"

    def auth_headers(self) -> Dict[str, str]:
        """Generates Authorization headers required for APIs

        Returns:
          Dict[str, str]: Headers
        """
        if not self.auth or self.auth.type == IDACAuthType.NONE.name:
            return {}

        if not self.auth.params or not "token" in self.auth.params:
            raise NoAuth("No authentication data")

        if self.auth.type == IDACAuthType.BASIC.name:
            return {"Authorization": f"Basic {self.auth.params['token']}"}

        return {"Authorization": f"Bearer {self.auth.params['token']}"}

    def with_auth(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Adds auth headers to `headers` param. Also returns that dictionary.

        Example:
        ```
        h = {"Accept": "application/json"}
        idac_controller.with_auth(h)
        ```

        Args:
          headers (Dict[str, str]): Dictionary where headers should be added

        Returns:
          Dict[str, str]: Updated dictionary
        """
        if self.auth.type == IDACAuthType.NONE.name:
            return headers

        if not isinstance(headers, dict):
            raise Exception("Headers not provided")

        headers.update(self.auth_headers())
        return headers

    def api_create_stateless(self) -> Tuple[str, str]:
        """Generate URL for "Create Stateless Request" API

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        return self.api_string("request/stateless/0"), "GET"

    def api_create_stateful(self) -> Tuple[str, str]:
        """Generate URL for "Create Stateful Request" API

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        return self.api_string("request/stateful/0"), "GET"

    def api_create(self) -> Tuple[str, str]:
        """Generate URL for "Create Request" API

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        return self.api_string("request/0"), "POST"

    def api_get_state(self, id: str) -> Tuple[str, str]:
        """Generate URL for "Get Request State" API

        Args:
          id (str): ID of a request

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        if not id:
            raise NoIdError("No ID provided for API")
        return self.api_string(f"request/{id}"), "GET"

    def api_restart(self, id: str) -> Tuple[str, str]:
        """Generate URL for "Restart Request" API

        Args:
          id (str): ID of a request

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        if not id:
            raise NoIdError("No ID provided for API")
        return self.api_string(f"request/restart/{id}"), "POST"

    def api_cleanup(self, id: str) -> Tuple[str, str]:
        """Generate URL for "Cleanup Request" API

        Args:
          id (str): ID of a request

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        if not id:
            raise NoIdError("No ID provided for API")
        return self.api_string(f"request/cleanup/{id}"), "POST"

    def api_extend(self, id: str, minutes: int) -> Tuple[str, str]:
        """Generate URL to extend request by `minutes` minutes

        Args:
            id (str): ID of a request
            minutes (int): amount of minutes

        Raises:
            NoIdError: Raised if no ID provided

        Returns:
            Tuple[str, str]: [URL, method]
        """
        if not id:
            raise NoIdError("No ID provided for API")
        return self.api_string(f"request/extend/{minutes}/{id}"), "POST"

    def api_force_cleanup(self, id: str) -> Tuple[str, str]:
        """Generate URL for "Force Cleanup Request" API

        Args:
          id (str): ID of a request

        Returns:
          Tuple[str, str]: [URL, Method]
        """
        if not id:
            raise NoIdError("No ID provided for API")
        return self.api_string(f"request/forcecleanup/{id}"), "POST"

    def drop_auth(self) -> None:
        """Resets Auth"""
        if self.auth and self.auth.params and "token" in self.auth.params:
            del self.auth.params["token"]

    def get_auth_token_pre(
            self,
            creds: str = "",
            datacenter: str = "") -> Union[str, Tuple[str, dict[str, str], dict[str, str]]]:
        if not self.auth:
            raise NoAuth("No Auth defined")

        logger.debug("Getting auth")
        if self.auth and self.auth.params and "token" in self.auth.params:
            return self.auth.params["token"]

        logger.debug("Requesting auth token")
        api = self.api_string("auth/token")
        headers = {"Content-Type": "application/json"}
        if self.auth.type == IDACAuthType.DCLOUD_SESSION.name:
            data = {"token": creds, "datacenter": datacenter, "type": "dcloud"}
        elif self.auth.type == IDACAuthType.WORKER.name:
            client_id, secret = itemgetter("client_id", "secret")(self.auth.params)
            data = {"token": get_worker_hash(client_id, secret), "type": "worker"}
        else:
            raise NoAuth("Auth type has no authentication request process defined")
        logger.debug(f"With data: {data}")

        return api, headers, data

    def verify_auth_response(self, response: httpx.Response, use_as_auth: bool) -> str:
        logger.debug(f"Got response: {response.status_code} {response.reason_phrase}")
        if response.status_code == 404:
            # old controller, no support for auth/token API, ignore :)
            logger.debug("Looks like controller doesn't support authentication. Ignoring")
            if use_as_auth:
                self.auth.params["token"] = "empty_token"
            return "empty_token"
        response.raise_for_status()
        json_body = json.loads(response.text)
        if isinstance(json_body, dict) and json_body.get("token", None):
            if use_as_auth:
                logger.debug("Saving token for future authentications")
                self.auth.params["token"] = json_body["token"]
            return json_body["token"]
        raise NoAuthTokenInResponse("Didn't receive auth token from controller")
