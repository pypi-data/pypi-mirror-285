""" Definition class of field names to be enriched """

from enum import Enum

__all__ = ["NxtFieldName"]


class NxtFieldName(str, Enum):
    DESKTOP_POOL = "device/device/virtualization/desktop_pool"
    HOSTNAME = "device/device/virtualization/hostname"
    HYPERVISOR_NAME = "device/device/virtualization/hypervisor_name"
    TYPE = "device/device/virtualization/type"
    ENVIRONMENT_NAME = "device/device/virtualization/environment_name"
    DESKTOP_BROKER = "device/device/virtualization/desktop_broker"
    DISK_IMAGE = "device/device/virtualization/disk_image"
    LAST_UPDATE = "device/device/virtualization/last_update"
    CUSTOM_DEVICE = "device/device/#{}"
    CUSTOM_USER = "user/user/#{}"
    CUSTOM_BINARY = "binary/binary/#{}"
    CUSTOM_PACKAGE = "package/package/#{}"
