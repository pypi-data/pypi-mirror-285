from enum import Enum


class ClipPreviewStatus(Enum):
    UPDATING = "UPDATING"
    ERROR_UPDATING = "ERROR_UPDATING"
    UPDATED = "UPDATED"
