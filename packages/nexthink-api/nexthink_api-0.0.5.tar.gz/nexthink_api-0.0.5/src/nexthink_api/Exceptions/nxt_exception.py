""" Nexthink base Exception """

import json


class NxtException(Exception):
    __slots__ = ('_data', '_text', '_status', '_message', '_code')

    def __init__(self, message=None, data=None):
        super().__init__(message)
        self._data = data
        # noinspection PyBroadException
        try:
            self._text = json.loads(self._data.text)
            self._status = self._text["status"]
            self._message = self._text["errors"][0]["errors"][0]["message"]
            self._code = self._text["errors"][0]["errors"][0]["code"]
        except Exception:  # pylint: disable=broad-except
            self._message = data
            self._code = None
            self._status = None

    @property
    def status_code(self) -> int:
        return self._data["status_code"]

    @property
    def nexthink_code(self) -> str:
        return self._code

    @property
    def nexthink_message(self) -> str:
        return self._message

    @property
    def nexthink_status(self) -> str:
        return self._status
