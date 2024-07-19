import platform
import os.path
from warnings import warn
import xmltodict
import json
from typing import Any, Dict, Literal, Optional, Union
from deepmerge import always_merger

from idac_sdk.errors import (
    BadXmlFileError,
    IncorrectSessionData,
    SessionDataFileNotFoundError,
    SessionDataFileNotFoundWarning,
)
from idac_sdk.models.new_request import NewRequest

DEFAULT_SESSION_XML_UNIX = "/dcloud/session.xml"
DEFAULT_SESSION_XML_WIN = "c:\\dcloud\\session.xml"


class SessionData:
    data: NewRequest

    def __init__(
        self,
        session_xml_path: Optional[Union[str, Literal[False]]] = None,
        initial_data: Union[NewRequest, Dict[str, Any], None] = None,
        **kwargs,
    ) -> None:
        """SessionData Object

        Handles data of a session.

        Args:
            session_xml_path (Union[str, bool], optional): Path to session.xml file. If set to None
                will try to load either `c:\\dcloud\\session.xml` if on Windows or
                `/dcloud/session.xml` otherwise. If set to False will not load anything.
                Defaults to None.
            initial_data (Union[NewRequest, Dict[str, Any]], optional): Initial session data.
                If both session_xml_path and initial_data provided, data will be merged and values
                from initial_data will overwrite values from session.xml. Defaults to None.
            **kwargs: Any other named parameter will be considered as a parameter which should be
                added to data

        Raises:
            IncorrectSessionData: if incorrect `initial_data` provided

        Returns:
            None
        """
        if session_xml_path is not False:
            self.load_session_xml(file=session_xml_path)

        if initial_data or kwargs:
            if initial_data and (not isinstance(initial_data, NewRequest) and
                                 not isinstance(initial_data, dict)):
                raise IncorrectSessionData("Incorrect initial data provided")

            # ensure that d is dictionary
            if initial_data:
                d = (initial_data.dict(exclude_unset=True, exclude_none=True) if isinstance(
                    initial_data, NewRequest) else initial_data)
            else:
                d = dict()

            # all other params considered part of initial data as well, merge
            if kwargs:
                d = always_merger.merge(d, kwargs)

            if hasattr(self, "data"):
                # need to merge data
                self.data = NewRequest(**always_merger.merge(
                    self.data.dict(exclude_unset=True, exclude_none=True),
                    d,
                ))
            else:
                self.data = NewRequest(**d)
        else:
            if not hasattr(self, "data"):
                # create empty if not loaded from session.xml
                self.data = NewRequest()

    def load_session_xml(self,
                         file: Optional[Union[str, Literal[False]]] = None,
                         merge: bool = True) -> None:
        """Loads data from a file.
        If file is not specified loads from `c:\\dcloud\\session.xml` if on Windows or from
            `/dcloud/session.xml`

        Args:
            file (str, optional): File to load. Defaults to None
            merge (bool, optional): Tells if loaded data should be merged with existent or not.
                If False, existing data will be replace with loaded. Defaults to True

        Raises:
            SessionDataFileNotFoundError: If file doesn't exist

        Returns:
            None
        """
        xml_guessed = False
        if not file:
            xml_guessed = True
            if platform.system().lower() == "windows":
                file = DEFAULT_SESSION_XML_WIN
            else:
                file = DEFAULT_SESSION_XML_UNIX

        if not os.path.exists(file):
            if not xml_guessed:
                raise SessionDataFileNotFoundError(f"File {file} not found.")
            else:
                warn(f"session.xml not found by path '{file}'.", SessionDataFileNotFoundWarning)
                return

        d = None
        with open(file, "r") as file_handle:
            d = xmltodict.parse(file_handle.read())
            d = json.loads(json.dumps(d))

        if isinstance(d, dict):
            if "session" in d:
                new_data = NewRequest(**d["session"])
            else:
                new_data = NewRequest(**d)

            if hasattr(self, "data"):
                self.data = (NewRequest(**always_merger.merge(
                    self.data.dict(exclude_unset=True, exclude_none=True),
                    new_data.dict(exclude_unset=True, exclude_none=True),
                )) if merge else new_data)
            else:
                self.data = new_data
        else:
            raise BadXmlFileError(f"File {file} is not a useful XML file")

    def set(self, key: str, value: Any) -> None:
        """Adds or updates key/value to session data

        Args:
            key (str): Key to add to the session data
            value (Any): Value of the key

        Returns:
            None
        """
        setattr(self.data, key, value)

    def has(self, key: str) -> bool:
        """Check if `key` exists in session data

        Args:
            key (str): Key name to check

        Returns:
            bool: True if key exists, False otherwise
        """
        return key in self.data.__fields_set__

    def get(self, key: str) -> Any:
        """Returns value of a key. Throws if key doesn't exist

        Args:
            key (str): Key name to get

        Returns:
            Any: Value of the key
        """
        return getattr(self.data, key)

    def delete(self, key: str) -> None:
        """Delete a key from session data

        Args:
            key (str): Key name to delete

        Returns:
            None
        """
        delattr(self.data, key)

    def dict(self, *args, **kwargs) -> dict:
        """Generates dictionary from data

        Returns:
            dict: Data as a dictionary
        """
        return self.data.dict(*args, **kwargs)
