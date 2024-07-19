from typing import Optional, Tuple, Union
from httpx import AsyncClient
from idac_sdk.base.controller import BaseIDACController

from idac_sdk.models.vpn_config import VPNConfig
from idac_sdk.types import IDACAuthType


class IDACController(BaseIDACController):
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
        IDACController Object

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
        super().__init__(
            proto=proto,
            url=url,
            api_version=api_version,
            auth_type=auth_type,
            auth=auth,
            worker_id=worker_id,
            worker_secret=worker_secret,
            user_agent=user_agent,
            vpn=vpn,
        )

    async def get_auth_token(
        self, creds: str = "", datacenter: str = "", use_as_auth: bool = True
    ) -> str:
        """Requests auth token from controller. Required for DCLOUD_SESSION and WORKER auth type

        Args:
            creds (str): `creds` token from session.xml dCloud file
            datacenter (str): dCloud datacenter where session runs
            use_as_auth (bool, optional): If True, response will be used as `auth` for
                `auth_headers` & `with_auth` methods. Defaults to True.

        Raises:
            NoAuthTokenInResponse: Raised if no token received in response
            NoAuth: Raised if no authentication provided
        Returns:
            str: Auth token
        """

        prep = self.get_auth_token_pre(creds=creds, datacenter=datacenter)
        if isinstance(prep, str):
            return prep

        # unpack
        (api, headers, data) = prep

        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})
            response = await client.post(api, headers=headers, json=data)
            return self.verify_auth_response(response=response, use_as_auth=use_as_auth)
