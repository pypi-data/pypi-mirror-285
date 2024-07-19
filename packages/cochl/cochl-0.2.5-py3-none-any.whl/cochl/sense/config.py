from enum import Enum
from typing import Dict


class WindowHop(Enum):
    """WindowHop represents the gap between consecutive audio windows.

    When WindowHop is smaller than WindowSize, audio windows overlap.
    The overlap makes inferences slower but reduces possibility of missing sounds between two different windows.

    For example, when WindowSize=1.0s and WindowHop=1.0s, audio windows are like below.
      - Window #0 (0.0s ~ 1.0s)
      - Window #1 (1.0s ~ 2.0s)
    If any important sound happened between the two windows (0.9s ~ 1.1s),
    it may not be detected because the sound is separated into two different windows.

    When WindowSize=1.0s and WindowHop=0.5s, audio windows are like below.
      - Window #0 (0.0s ~ 1.0s)
      - Window #1 (0.5s ~ 1.5s)
      - Window #2 (1.0s ~ 2.0s)
    Windows are overlapping, but less probability missing sound in between.

    """

    HOP_500ms = ("0.5s", 0.5)
    HOP_1s = ("1s", 1.0)

    def __init__(self, str_val: str, second_val: int):
        self.str_val = str_val
        self.second_val = second_val

    @property
    def str_value(self) -> str:
        """str: WindowHop Enum in string value."""
        return self.str_val

    @property
    def second(self) -> float:
        """float: WindowHop Enum in float second-unit value."""
        return self.second_val


class SensitivityScale(Enum):
    """SensitivityScale represents how sensitive a sound tag should be detected.
    High sensitivity means low threshold.
    It means that Cochl.Sense API determines a sound tag is detected even though its confidence is low.
    """

    VERY_HIGH = -2
    HIGH = -1
    MEDIUM = 0
    LOW = 1
    VERY_LOW = 2


class SensitivityConfig:
    """SensitivityConfig represents how sensitive each tag will be detected.

    Attributes:
        default (SensitivityScale): Default sensitivity applied to all tags not managed in `by_tags` attribute.
        by_tags (Dict[str, SensitivityScale]): Sensitivity of each tag. For example, {"Gunshot": SensitivityScale.LOW}
    """

    def __init__(self, default: SensitivityScale, by_tags: Dict[str, SensitivityScale]):
        self.default = default
        self.by_tags = by_tags
        if self.by_tags is None:
            self.by_tags = {}


class ChunkSize(Enum):
    """ChunkSize represents how small a file is to be split when it is uploaded.
    A file is split into multiple chunks before it is uploaded to Cochl.Sense cloud.

    For example, when a 13MB file is uploaded with 5MB ChunkSize,
    two 5MB chunks and one 3MB chunk are uploaded to server.

    """

    SIZE_5MB = 5 * 10**6


class APIConfig:
    def __init__(
        self,
        window_hop: WindowHop = WindowHop.HOP_500ms,
        chunk_size: ChunkSize = ChunkSize.SIZE_5MB,
        sensitivity: SensitivityConfig = None,
        host: str = None,
    ):
        """
        Args:
            window_hop: WindowHop to apply in Cochl.Sense API Client.
            sensitivity: SensitivityConfig to apply in Cochl.Sense API Client.
        """
        self.window_hop = window_hop
        self.chunk_size = chunk_size
        self.sensitivity = sensitivity
        if self.sensitivity is None:
            self.sensitivity = SensitivityConfig(SensitivityScale.MEDIUM, {})

        self.host = host

    def get_host(self) -> str:
        return "https://api.cochl.ai/sense/api/v1" if self.host is None else self.host
