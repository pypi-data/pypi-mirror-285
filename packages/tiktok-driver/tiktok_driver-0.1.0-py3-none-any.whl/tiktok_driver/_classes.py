from dataclasses import dataclass
from enum import Enum

class DownloadType(Enum):
    VIDEO = 0
    IMAGE = 1

@dataclass
class DownloadInformation:
    url: str
    type: DownloadType