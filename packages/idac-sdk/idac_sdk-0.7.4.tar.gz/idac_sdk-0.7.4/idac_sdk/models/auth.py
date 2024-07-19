from pydantic import BaseModel, Extra


class Auth(BaseModel, extra=Extra.allow):
    type: str
    params: dict[str, str]
