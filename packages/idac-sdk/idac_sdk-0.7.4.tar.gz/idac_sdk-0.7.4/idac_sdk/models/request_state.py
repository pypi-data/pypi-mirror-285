from __future__ import annotations
from typing import Any, List, Literal, Optional, Union, cast
from pydantic import BaseModel, Extra

from idac_sdk.models.new_request import NewRequest


class LoggerDetails(BaseModel, extra=Extra.allow):
    apiLogToken: Optional[str]
    method: Optional[str]
    api: Optional[str]
    requestId: Optional[str]
    owner: Optional[str]
    recipePath: Optional[str]
    recipeName: Optional[str]


class Vpn(BaseModel):
    username: Optional[str]
    host: Optional[str]
    endpoints: Optional[List[Any]]
    mode: Optional[str]


class Request(NewRequest, extra=Extra.allow):
    api: Optional[str]
    dcloudTimestamp: Optional[str]
    pod: Optional[str]
    uuid: Optional[str]
    cookieLifeHours: Optional[int]
    remote_addr: Optional[str]
    Referer: Optional[str]
    method: Optional[str]
    controller: Optional[str]
    vpn: Optional[Vpn]
    controllerEnv: Optional[str]
    controllerApiUrl: Optional[str]
    user_agent: Optional[str]
    query_string: Optional[str]


class Controller(BaseModel, extra=Extra.allow):
    region: Optional[str]
    webUrl: Optional[str]
    environment: Optional[str]
    extPort: Optional[str]
    location: Optional[str]
    apiUrl: Optional[str]
    cloud: Optional[str]


class Details(BaseModel, extra=Extra.allow):
    language: Optional[str]
    demo: Optional[str]
    name: Optional[str]
    cookieLifeHours: Optional[int]
    notifications: Optional[Any]


class Output(BaseModel, extra=Extra.allow):
    destUrl: Optional[Any]
    loaderPage: Optional[str]
    htmlTemplate: Optional[str]


class Tasks(BaseModel):
    End: Optional[List[Any]]
    Stop: Optional[List[Any]]
    Start: Optional[List[Any]]
    Details: Optional[Details]
    Input: Optional[List[Any]]
    Output: Optional[Output]


class WorkerCode(BaseModel):
    Date: Optional[str]
    Rev: Optional[str]


class Code(BaseModel):
    worker: Optional[WorkerCode]


class Start(BaseModel):
    code: Optional[Code]
    hostname: Optional[str]
    location: Optional[str]


class Worker(BaseModel):
    Start: Optional[Start]


class HistoryItem(BaseModel):
    demo: Optional[str]
    status: Optional[str]
    comments: Optional[str]
    time: Optional[str]


class RequestState(BaseModel, extra=Extra.allow):
    status: Optional[str]
    forcecleanupApi: Optional[str]
    mLoaderUrl: Optional[str]
    loggerDetails: Optional[LoggerDetails]
    workerId: Optional[str]
    registerAction: Optional[str]
    request: Optional[Request]
    loaderUrl: Optional[str]
    comments: Optional[str]
    statusUrl: Optional[str]
    controller: Optional[Controller]
    tasks: Optional[Tasks]
    outputUrl: Optional[str]
    errorUrl: Optional[str]
    cleanupApi: Optional[str]
    restartApi: Optional[str]
    action: Optional[str]
    output: Optional[str]
    vpn: Optional[bool]
    statusApi: Optional[str]
    worker: Optional[Worker]
    history: Optional[List[HistoryItem]]

    def get_task_outputs(
        self, section: Literal["Start", "Stop"], task_name: str
    ) -> Union[dict[str, Any], None]:
        if not hasattr(self.tasks, section):
            raise KeyError(f"No section {section} in tasks")

        for tsk in cast(list, getattr(self.tasks, section)):
            if tsk["name"] == task_name:
                return tsk["output"]

        return None
