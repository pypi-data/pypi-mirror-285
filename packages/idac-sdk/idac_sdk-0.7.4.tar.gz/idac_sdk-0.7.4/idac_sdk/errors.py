class SessionDataFileNotFoundError(FileNotFoundError):
    ...


class SessionDataFileNotFoundWarning(Warning):
    ...


class IncorrectControllerProtoError(Exception):
    ...


class IncorrectControllerURLError(Exception):
    ...


class IncorrectSessionData(Exception):
    ...


class NoIdError(Exception):
    ...


class NoControllerError(Exception):
    ...


class NoAuthTokenInResponse(Exception):
    ...


class NoAuth(Exception):
    ...


class BadXmlFileError(Exception):
    ...


class IDACRequestStateError(Exception):
    ...


class IncorrectWantedStateError(Exception):
    ...


class IncorrectMinutesValue(Exception):
    ...


class NoIDACConfig(Warning):
    ...


class OldConfigFoundException(Exception):
    ...


class OldConfigFoundWarning(Warning):
    ...


class UnknownVPNType(Exception):
    ...
