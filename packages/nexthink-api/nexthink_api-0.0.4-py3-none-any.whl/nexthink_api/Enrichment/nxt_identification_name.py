""" List of allowed values for identification fields """

from enum import Enum

__all__ = ["NxtIdentificationName"]


class NxtIdentificationName(str, Enum):
    DEVICE_DEVICE_NAME = "device/device/name"
    DEVICE_DEVICE_UID = "device/device/uid"
    USER_USER_SID = "user/user/sid"
    USER_USER_UID = "user/user/uid"
    USER_USER_UPN = "user/user/upn"
    BINARY_BINARY_UID = "binary/binary/uid"
    PACKAGE_PACKAGE_UID = "package/package/uid"
