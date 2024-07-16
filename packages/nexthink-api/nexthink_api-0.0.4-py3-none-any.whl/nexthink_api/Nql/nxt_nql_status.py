""" NQL Status response state """

from enum import Enum

__all__ = ["NxtNqlStatus"]


class NxtNqlStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"
