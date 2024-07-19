import base64
import os
import time
from typing import List, Optional

import soundfile
from cochl_sense_api import ApiClient, Configuration
from cochl_sense_api.api.audio_session_api import AudioSessionApi, SessionResult
from cochl_sense_api.model.audio_chunk import AudioChunk
from cochl_sense_api.model.audio_type import AudioType
from cochl_sense_api.model.create_session import CreateSession
from cochl_sense_api.model.default_sensitivity import DefaultSensitivity
from cochl_sense_api.model.tags_sensitivity import TagsSensitivity
from cochl_sense_api.model.window_hop import WindowHop as ClientWindowHop

from . import config
from .exceptions import CochlSenseException, TimeoutError
from .result import FileResult, SoundTag, WindowResult
from .version import check_latest_lib_version

_supported_formats = ["mp3", "wav", "ogg"]


class FileClient:
    """FileClient is used to predict an audio file with Cochl.Sense."""

    def __init__(
        self,
        api_project_key: str,
        api_config: config.APIConfig = None,
    ):
        if not api_project_key:
            raise ValueError(f"invalid project key '{api_project_key}'")
        if api_config is None:
            api_config = config.APIConfig()  # use default APIConfig

        self.project_key = api_project_key
        self.api_config = api_config
        self.internal_client = None

        # check client library version
        check_latest_lib_version(self.api_config.get_host())

    def predict(self, file_path: str, timeout: Optional[float] = None) -> FileResult:
        """Predicts the given file.

        Args:
            file_path: Path to the file. For example, "/Users/user/file.mp3"
            timeout: Maximum amount of seconds to wait until prediction of the given file is done.
        """

        if not os.path.exists(file_path):
            raise FileNotFoundError(file_path)

        self.internal_client = self._create_internal_client()

        # create Session
        session_id = self._create_session(file_path)

        # upload file chunks
        with open(file_path, "rb") as file:
            chunk_sequence = 0
            while True:
                chunk = file.read(self.api_config.chunk_size.value)
                if not chunk:
                    # all bytes of the file has been processed
                    break

                self._upload_chunk(session_id, chunk_sequence, chunk)

                chunk_sequence += 1

        # get results
        results = self._get_all_results(session_id, timeout)

        return results

    def _create_internal_client(self) -> AudioSessionApi:
        if self.api_config and self.api_config.host:
            configuration = Configuration(host=self.api_config.host)
        else:
            configuration = Configuration()
        configuration.api_key["API_Key"] = self.project_key
        return AudioSessionApi(ApiClient(configuration))

    def _create_session(self, file_path: str) -> str:
        """
        Returns:
            str: ID of the created session
        """
        file_name = os.path.basename(file_path)
        file_size = os.stat(file_path).st_size
        file_format = self._get_file_format(file_path)
        file_length = self._get_file_length(file_path)

        content_type = f"audio/{file_format.lower()}"

        window_hop = ClientWindowHop(self.api_config.window_hop.str_value)
        default_sensitivity = DefaultSensitivity(self.api_config.sensitivity.default.value)
        tags_sensitivity = {}
        for tag_name, scale in self.api_config.sensitivity.by_tags.items():
            tags_sensitivity[tag_name] = scale.value

        resp = self.internal_client.create_session(
            CreateSession(
                type=AudioType("file"),
                total_size=file_size,
                content_type=content_type,
                file_name=file_name,
                file_length=file_length,
                window_hop=window_hop,
                default_sensitivity=default_sensitivity,
                tags_sensitivity=TagsSensitivity(**tags_sensitivity),
            )
        )
        return resp.session_id

    def _upload_chunk(self, session_id: str, chunk_sequence: int, chunk: bytes):
        encoded = base64.b64encode(chunk).decode("utf-8")

        _resp = self.internal_client.upload_chunk(
            session_id=session_id,
            chunk_sequence=chunk_sequence,
            audio_chunk=AudioChunk(encoded),
        )

    def _get_all_results(self, session_id: str, timeout: Optional[float] = None) -> FileResult:
        retry_count = 0
        data_count = 0
        frame_results: List[WindowResult] = []
        start_time = time.time()
        while True:
            # check if this whole funtion behaviour not complete within the given timeout
            if timeout is not None:
                if time.time() - start_time > timeout:
                    raise TimeoutError(session_id, timeout)

            response = self.internal_client.get_results(
                session_id=session_id,
                offset=data_count,
                limit=1024,
            )

            state = response.get("state", None)
            has_more = response.get("has_more", None)
            if (state is None) or (has_more is None) or (type(has_more) is not bool):
                raise CochlSenseException(f"invalid Get Result API response: {response}")

            if state == "error":
                error_msg = response.get("error", None)
                if not error_msg:
                    error_msg = "Unexpected error occured."
                raise CochlSenseException(error_msg)

            elif state == "pending" or state == "in-progress":
                # retry after interval
                time.sleep(self._caculate_retry_interval(retry_count))
                continue

            elif state == "done":
                retrieved = self._to_frame_results(response)
                frame_results.extend(retrieved)
                data_count += len(retrieved)

                # the loop continues only if the result is paginated
                if not has_more:
                    return FileResult(
                        session_id=session_id,
                        window_results=frame_results,
                        window_hop=self.api_config.window_hop,
                    )

            else:
                raise CochlSenseException(f"invalid Get Result API response state: {state}")

            # update loop conditions
            retry_count += 1

        return FileResult(
            session_id=session_id,
            window_results=frame_results,
            window_hop=self.api_config.window_hop,
        )

    def _get_results(self, session_id: str, offset: int, limit: int):
        response = self.internal_client.get_results(
            session_id=session_id,
            offset=offset,
            limit=limit,
        )
        return response

    @classmethod
    def _to_frame_results(cls, response: SessionResult) -> List[WindowResult]:
        frame_results = []

        for item in response.data:
            sound_tags = [
                SoundTag(
                    name=tag.name,
                    probability=tag.probability,
                )
                for tag in item.tags
            ]
            frame_results.append(
                WindowResult(
                    start_time=item.start_time,
                    end_time=item.end_time,
                    sound_tags=sound_tags,
                )
            )

        return frame_results

    @classmethod
    def _caculate_retry_interval(cls, retry_count: int) -> float:
        return min(1.1**retry_count, 4.0)

    @classmethod
    def _get_file_format(cls, file_path: str) -> str:
        """
        Returns:
            str: File format in str ("mp3", "wav", "ogg")
        """
        try:
            info = soundfile.info(file_path)
            file_format = info.format.lower()
        except Exception as _e:
            raise ValueError(f"invalid file format '{file_path}', supported formats: {_supported_formats}")

        return file_format

    @classmethod
    def _get_file_length(cls, file_path: str) -> float:
        """Get the float seconds of the given file.

        Returns:
            float: Length of the file in second.
        """
        try:
            with soundfile.SoundFile(file_path) as f:
                num_frames = len(f)
                duration_seconds = num_frames / f.samplerate
                return duration_seconds
        except Exception as _e:
            raise ValueError(f"invalid file format '{file_path}', supported formats: {_supported_formats}")
