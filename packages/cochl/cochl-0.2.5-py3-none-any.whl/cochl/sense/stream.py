import base64
import threading
from enum import Enum

from cochl_sense_api import ApiClient, Configuration
from cochl_sense_api.api.audio_session_api import AudioSessionApi
from cochl_sense_api.model.audio_type import AudioType
from cochl_sense_api.model.create_session import CreateSession
from cochl_sense_api.model.default_sensitivity import DefaultSensitivity
from cochl_sense_api.model.tags_sensitivity import TagsSensitivity
from cochl_sense_api.model.predict_request import PredictRequest
from cochl_sense_api.model.window_hop import WindowHop as ClientWindowHop

from . import config
from .result import SoundTag, WindowResult
from .version import check_latest_lib_version

DEFAULT_WINDOW_SIZE = 1  # 1-sec


class AudioDataType(Enum):
    """AudioDataType represents the data type of each PCM audio sample."""

    S16 = ("s16", 2)  # signed 2-byte
    S24 = ("s24", 3)  # signed 3-byte
    S32 = ("s32", 4)  # signed 4-byte
    U16 = ("u16", 2)  # unsigned 2-byte
    U24 = ("u24", 3)  # unsinged 3-byte
    U32 = ("u32", 4)  # unsinged 4-byte
    F32 = ("f32", 4)  # floating-point 4-byte

    def __init__(self, str_val: str, byte_size_val: int):
        self.str_val = str_val
        self.byte_size_val = byte_size_val

    @property
    def str_value(self) -> str:
        return self.str_val

    @property
    def byte_size(self) -> int:
        return self.byte_size_val


class AudioEndian(Enum):
    LITTLE = "le"  # little endian
    BIG = "be"  # big endian


class StreamAudioType:
    def __init__(
        self,
        sample_rate: int,
        data_type: AudioDataType,
        endian: AudioEndian = AudioEndian.LITTLE,
    ):
        self.sample_rate = sample_rate
        self.data_type = data_type
        self.endian = endian

    def get_window_byte_size(self, window_size: int) -> int:
        """
        Returns the number of bytes composing one audio window.
        For example, 1-sec window of 22,050Hz & f32 consists of 1 * 22,050 * 4 = 88,200 bytes.
        """
        return window_size * self.sample_rate * self.data_type.byte_size


class StreamBuffer:
    """StreamBuffer manages raw audio data (not compressed, PCM)
    based on the given audio type and API configguration.
    """

    def __init__(self, audio_type: StreamAudioType, api_config: config.APIConfig):
        self.audio_type = audio_type

        # the number of samples to hop between windows
        self.window_byte_size = audio_type.get_window_byte_size(DEFAULT_WINDOW_SIZE)
        self.window_hop_byte_size = int(self.window_byte_size / DEFAULT_WINDOW_SIZE * api_config.window_hop.second)

        self.lock = threading.Lock()
        self._buffer = bytearray()

    def put(self, data: bytes):
        with self.lock:
            self._buffer.extend(data)

    def pop(self) -> bytes:
        """Returns audio data bytes stored in the buffer.
        Each returned audio data represents audio window based on StreamBuffer's audio type and api config.

        For example, sample_rate=22050hz, data_type=float32, window_size=1s, window_hop=500ms
        First pop returns [0:88200] of the buffer (0.0s ~ 1.0s)
        Second pop returns [44100:132300] of the buffer (0.5s ~ 1.5s)
        """
        with self.lock:
            if not self.is_ready():
                raise Exception("buffer not ready")

            # retrieve data and hop through the buffer
            data = self._buffer[: self.window_byte_size]
            self._buffer = self._buffer[self.window_hop_byte_size :]
            return bytes(data)

    def is_ready(self):
        """
        Returns if the buffer has enough data to make a prediction.
        """
        return self.window_byte_size <= len(self._buffer)


class StreamClient:
    """StreamClient is used to predict audio stream with Cochl.Sense API."""

    def __init__(
        self,
        api_project_key: str,
        audio_type: StreamAudioType,
        api_config: config.APIConfig = None,
    ):
        if not api_project_key:
            raise ValueError(f"invalid project key '{api_project_key}'")
        if audio_type is None:
            raise ValueError("audio_type must be set")
        if api_config is None:
            api_config = config.APIConfig()

        self.project_key = api_project_key
        self.audio_type = audio_type
        self.api_config = api_config

        # prediction must be requested one at a time
        self.predict_lock = threading.Lock()
        self.sequence = 0

        # check client library version
        check_latest_lib_version(self.api_config.get_host())

        # init session
        self.internal_client = self._create_internal_client()
        self.session_id = self._create_session()

    def get_buffer(self) -> StreamBuffer:
        return StreamBuffer(self.audio_type, self.api_config)

    def get_session_id(self) -> str:
        return self.session_id

    def predict(self, audio_data: bytes) -> WindowResult:
        with self.predict_lock:
            encoded = base64.b64encode(audio_data).decode("utf-8")

            resp = self.internal_client.predict(
                self.session_id,
                PredictRequest(
                    sequence=self.sequence,
                    data=encoded,
                ),
            )

            self.sequence = resp.next_sequence  # update sequence

            sound_tags = [
                SoundTag(
                    name=tag.name,
                    probability=tag.probability,
                )
                for tag in resp.data.tags
            ]
            return WindowResult(
                start_time=resp.data.start_time,
                end_time=resp.data.end_time,
                sound_tags=sound_tags,
            )

    def _create_internal_client(self) -> AudioSessionApi:
        if self.api_config and self.api_config.host:
            configuration = Configuration(host=self.api_config.host)
        else:
            configuration = Configuration()
        configuration.api_key["API_Key"] = self.project_key
        return AudioSessionApi(ApiClient(configuration))

    def _create_session(self) -> str:
        content_type = f"audio/x-raw; rate={self.audio_type.sample_rate}; format={self.audio_type.data_type.str_value}"

        window_hop = ClientWindowHop(self.api_config.window_hop.str_value)
        default_sensitivity = DefaultSensitivity(self.api_config.sensitivity.default.value)
        tags_sensitivity = {}
        for tag_name, scale in self.api_config.sensitivity.by_tags.items():
            tags_sensitivity[tag_name] = scale.value

        resp = self.internal_client.create_session(
            CreateSession(
                type=AudioType("stream"),
                content_type=content_type,
                window_hop=window_hop,
                default_sensitivity=default_sensitivity,
                tags_sensitivity=TagsSensitivity(**tags_sensitivity),
            )
        )
        return resp.session_id
