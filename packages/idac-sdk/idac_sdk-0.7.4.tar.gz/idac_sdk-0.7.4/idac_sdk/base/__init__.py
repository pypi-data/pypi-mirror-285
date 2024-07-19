r"""
Base classes for iDAC Controller & iDAC Request.
Should not be used directly!
"""

import platform
from idac_sdk._version import __version__ as version
from idac_sdk.types import IDACRequestStatus

system = platform.platform()
python = platform.python_implementation() + " " + platform.python_version()

DEFAULT_WAIT_TIMEOUT = 10 * 60  # 10 minutes
DEFAULT_WAIT_INTERVAL = 30  # 30 seconds
DEFAULT_MAX_TRIES = int(DEFAULT_WAIT_TIMEOUT / DEFAULT_WAIT_INTERVAL)
DEFAULT_USER_AGENT = f"iDAC SDK/{version} ({system}; {python})"

REQUEST_ERROR_STATES = [
    IDACRequestStatus.cancelled,
    IDACRequestStatus.error,
    IDACRequestStatus.onboardError,
]
REQUEST_GOOD_STATES = [
    IDACRequestStatus.active,
    IDACRequestStatus.executed,
    IDACRequestStatus.complete,
]
