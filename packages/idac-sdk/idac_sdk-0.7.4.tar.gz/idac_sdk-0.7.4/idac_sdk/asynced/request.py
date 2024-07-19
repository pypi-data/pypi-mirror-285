from httpx import AsyncClient, Request, ReadTimeout
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Union

from idac_sdk.base import (
    DEFAULT_WAIT_INTERVAL,
    DEFAULT_WAIT_TIMEOUT,
    REQUEST_ERROR_STATES,
    REQUEST_GOOD_STATES,
)
from idac_sdk.base.request import BaseIDACRequest, check_controller
from idac_sdk.types import IDACRequestStatus, IDACRequestType, IDACAuthType
from idac_sdk.log import logger
from idac_sdk.asynced.controller import IDACController as AsyncController
from idac_sdk.errors import (
    IDACRequestStateError,
    IncorrectMinutesValue,
    NoAuth,
    NoIdError,
)
from idac_sdk.models.vpn_config import VPNConfig
from idac_sdk.models.request_state import RequestState
from idac_sdk.session_data import SessionData


class IDACRequest(BaseIDACRequest[AsyncController]):

    def __init__(
        self,
        uuid: Optional[str] = None,
        session_data: Optional[SessionData] = None,
        controller: Optional[AsyncController] = None,
        user_agent: Optional[str] = None,
        vpn: Optional[VPNConfig] = None,
    ) -> None:
        """
        Async IDACRequest Object

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
        super().__init__(
            uuid=uuid,
            session_data=session_data,
            controller=controller,
            user_agent=user_agent,
            vpn=vpn,
            wanted_controller_type=AsyncController,
        )

    @check_controller
    async def check_controller_auth(self) -> None:
        """Tells controller to request auth token if auth type is DCLOUD_SESSION"""
        logger.debug(f"Checking auth. Type is {self.controller.auth.type}")
        if self.controller.auth.type == IDACAuthType.DCLOUD_SESSION.name:
            assert self.session_data, "Session data not set"
            if not self.session_data.has("creds"):
                raise NoAuth("No credentials set for DCLOUD_SESSION authentication.")
            token = await self.controller.get_auth_token(self.session_data.get("creds"),
                                                         self.session_data.get("datacenter"))
            logger.debug(f"dCloud token is: {token}")
        elif self.controller.auth.type == IDACAuthType.WORKER.name:
            token = await self.controller.get_auth_token()
            logger.debug(f"Worker token is: {token}")

    @check_controller
    async def create(
        self,
        request_type: IDACRequestType = IDACRequestType.SIMPLE
    ) -> Tuple[RequestState, Optional[str]]:
        """Sends Create API request. All data taken from session_data

        Args:
            request_type (IDACRequestType, optional): Type of the request.
                Defaults to IDACRequestType.SIMPLE.

        Returns:
            RequestState: State of the new request
        """
        assert self.session_data, "Session data not set"
        await self.check_controller_auth()

        if request_type == IDACRequestType.STATEFUL:
            api, method = self.controller.api_create_stateful()
        elif request_type == IDACRequestType.STATELESS:
            api, method = self.controller.api_create_stateless()
        else:
            api, method = self.controller.api_create()

        headers: Dict[str, str] = {"Accept": "application/json"}
        self.controller.with_auth(headers)
        logger.debug(f"API: {method} to {api}")
        logger.debug(f"Headers are: {headers}")

        # convert SessionData to dict and populate VPN parameters
        data = self.add_vpn(self.session_data.dict(exclude_none=True))

        if method == "POST":
            # put data in body if POST
            kwargs = {"json": data}
            headers.update({"Content-Type": "application/json"})
        else:
            # put data in query string if GET
            kwargs = {"params": data}

        redirect: str | None = None
        st: RequestState | None = None
        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})

            # initial request
            request = Request(method, api, headers=headers, **kwargs)

            redirects = 0
            while redirects < self.max_redirects + 1:
                if redirects == self.max_redirects:
                    raise Exception(f"Exceeded max number of redirects - {self.max_redirects}")
                r = await client.send(request=request)
                logger.debug(f"Got response: {r.status_code} {r.reason_phrase}")
                if r.status_code < 200 or r.status_code > 399:
                    r.raise_for_status()

                json_body: dict
                try:
                    json_body = json.loads(r.text)
                except Exception as e:
                    logger.debug(f"Failed to parse JSON body: {e}")
                    if r.next_request:
                        self.raise_if_error(r.next_request.url)
                        logger.debug(f"Have next request, going there: {r.next_request.url}")
                        # update request and increase redirects counter
                        request = r.next_request
                        redirects += 1
                        continue
                    else:
                        raise e

                st = RequestState(**json_body)
                if st.request:
                    # grab UUID of a new automation
                    self.uuid = st.request.uuid

                if r.status_code >= 300 and r.status_code < 400:
                    # redirected
                    redirect = r.headers.get("location")
                break
            if not st:
                raise Exception("Failed to get request state")

        return st, redirect

    @check_controller
    async def get_state(self) -> RequestState:
        """Loads state of a request from controller

        Raises:
            NoIdError: if no ID/UUID set

        Returns:
            RequestState: State of the request
        """
        if not self.uuid:
            raise NoIdError("No ID/UUID provided for Get State")
        await self.check_controller_auth()

        api, method = self.controller.api_get_state(self.uuid)
        logger.debug(f"API: {method} to {api}")

        headers: Dict[str, str] = {"Accept": "application/json"}
        self.controller.with_auth(headers)

        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})
            r = await client.request(method, api, headers=headers)
            if r.status_code < 200 or r.status_code > 399:
                r.raise_for_status()

            json_body: dict = json.loads(r.text)
            return RequestState(**json_body)

    @check_controller
    async def restart(self) -> None:
        """Restarts request

        Raises:
            NoIdError: if no ID/UUID set
        """
        if not self.uuid:
            raise NoIdError("No ID/UUID provided for Restart")
        await self.check_controller_auth()

        api, method = self.controller.api_restart(self.uuid)
        logger.debug(f"API: {method} to {api}")

        headers: Dict[str, str] = {"Accept": "application/json"}
        self.controller.with_auth(headers)

        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})
            r = await client.request(method, api, headers=headers)
            logger.debug(f"Got response: {r.status_code} {r.reason_phrase}")
            if r.status_code < 200 or r.status_code > 399:
                r.raise_for_status()
            return

    @check_controller
    async def cleanup(self) -> None:
        """Cleans request

        Raises:
            NoIdError: if no ID/UUID set
        """
        if not self.uuid:
            raise NoIdError("No ID/UUID provided for Cleanup")
        await self.check_controller_auth()

        api, method = self.controller.api_cleanup(self.uuid)
        logger.debug(f"API: {method} to {api}")

        headers: Dict[str, str] = {"Accept": "application/json"}
        self.controller.with_auth(headers)

        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})
            r = await client.request(method, api, headers=headers)
            logger.debug(f"Got response: {r.status_code} {r.reason_phrase}")
            if r.status_code < 200 or r.status_code > 399:
                r.raise_for_status()
            return

    @check_controller
    async def force_cleanup(self) -> None:
        """Forcibly cleans request

        Raises:
            NoIdError: if no ID/UUID set
        """
        if not self.uuid:
            raise NoIdError("No ID/UUID provided for Force Cleanup")
        await self.check_controller_auth()

        api, method = self.controller.api_force_cleanup(self.uuid)
        logger.debug(f"API: {method} to {api}")

        headers: Dict[str, str] = {"Accept": "application/json"}
        self.controller.with_auth(headers)

        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})
            r = await client.request(method, api, headers=headers)
            logger.debug(f"Got response: {r.status_code} {r.reason_phrase}")
            if r.status_code < 200 or r.status_code > 399:
                r.raise_for_status()
            return

    @check_controller
    async def extend(self, minutes: int) -> None:
        """Extend a request by `minutes` minutes

        Args:
            minutes (int): amount of minutes

        Raises:
            NoIdError: if no ID provided
            IncorrectMinutesValue: if incorrect amount of minutes provided
        """
        if not self.uuid:
            raise NoIdError("No ID/UUID provided for Extend")
        if not minutes or not isinstance(minutes, int):
            raise IncorrectMinutesValue("Minutes should be an integer")
        await self.check_controller_auth()

        api, method = self.controller.api_extend(self.uuid, minutes=minutes)
        logger.debug(f"API: {method} to {api}")
        headers: Dict[str, str] = {"Accept": "application/json"}
        self.controller.with_auth(headers)

        async with AsyncClient() as client:
            client.headers.update({"User-Agent": self.user_agent})
            r = await client.request(method, api, headers=headers)
            logger.debug(f"Got response: {r.status_code} {r.reason_phrase}")
            if r.status_code < 200 or r.status_code > 399:
                r.raise_for_status()
            return

    @check_controller
    async def wait_for_status(
        self,
        wanted_state: Union[List[IDACRequestStatus], List[str],
                            List[Union[IDACRequestStatus, str]]] = REQUEST_GOOD_STATES,
        stop_on_error: bool = True,
        timeout: Optional[int] = DEFAULT_WAIT_TIMEOUT,
        interval: int = DEFAULT_WAIT_INTERVAL,
    ) -> Union[RequestState, None]:
        """Waits for request to land in one of wanted states by periodically checking it's status

        Args:
            wanted_state (List[Union[IDACRequestStatus, str]], optional): List of wanted statuses.
                Defaults to [ IDACRequestStatus.active, IDACRequestStatus.executed,
                IDACRequestStatus.complete, ].
            stop_on_error (bool, optional): Stop waiting if request errored. Defaults to True.
            timeout (int, optional): Timeout (in seconds). Max amout of time process should wait.
                If set to None will wait forever. Defaults to 10 minutes.
            interval (int, optional): Interval (seconds) between request. Defaults to 30 seconds.

        Raises:
            NoIdError: if no ID/UUID set
            IDACRequestStateError: if request is in errored status
            IncorrectWantedStateError: if incorrect wanted state provided
        """
        if not self.uuid:
            raise NoIdError("No ID/UUID provided for Wait For Status")

        wanted_state = self.sanitize_states(wanted_state)

        async def try_infinite() -> RequestState:
            while True:
                try:
                    st = await self.get_state()
                    status = IDACRequestStatus(st.status)
                    if status in wanted_state:
                        return st
                    if stop_on_error and status in REQUEST_ERROR_STATES:
                        raise IDACRequestStateError(f"Request landed in error state: {status.value}")
                except ReadTimeout as e:
                    pass
                await asyncio.sleep(interval)

        return await asyncio.wait_for(try_infinite(), timeout=timeout)
