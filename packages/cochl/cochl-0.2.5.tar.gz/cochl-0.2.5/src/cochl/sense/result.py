from typing import Dict, List

from .config import WindowHop

TAG_NAME_OTHER = "Others"
DEFAULT_IM = 0


class SoundTag:
    def __init__(self, name: str, probability: float):
        self.name = name
        self.probability = probability

    def __str__(self):
        return str(vars(self))

    def to_dict(self):
        return vars(self).copy()


class WindowResult:
    def __init__(self, start_time: float, end_time: float, sound_tags: List[SoundTag]):
        self.start_time = start_time
        self.end_time = end_time
        self.sound_tags = sound_tags

    def __str__(self):
        v = vars(self).copy()
        v["sound_tags"] = [vars(t) for t in v["sound_tags"]]
        return str(v)

    def to_dict(self):
        v = vars(self).copy()
        v["sound_tags"] = [st.to_dict() for st in self.sound_tags]
        return v


class FileResult:
    def __init__(
        self,
        session_id: str,
        window_results: List[WindowResult],
        window_hop: WindowHop,
    ):
        self.session_id = session_id
        self.window_results = window_results
        self._window_hop = window_hop

    def to_dict(self) -> Dict:
        """
        Get results in form of a dict

        Example:
            >>> results.to_dict()

            {
                'session_id': 'df1637ab-5478-455c-bff8-c7b90ff215c2',
                'window_results': [
                    {
                        'start_time': 0.0,
                        'end_time': 1.0,
                        'sound_tags': [
                            {'name': 'Gunshot', 'probability': 0.578891396522522},
                            {'name': 'Gunshot_single', 'probability': 0.578891396522522},
                        ],
                    },
                    {
                        'start_time': 0.5,
                        'end_time': 1.5,
                        'sound_tags': [
                            {'name': 'Others', 'probability': 0.0}
                        ],
                    },
                    {
                        'start_time': 1.0,
                        'end_time': 2.0,
                        'sound_tags': [
                            {'name': 'Others', 'probability': 0.0}
                        ],
                    },
                ]
            }
        """
        return {
            "session_id": self.session_id,
            "window_results": [wr.to_dict() for wr in self.window_results],
        }

    def to_summarized_result(
        self,
        interval_margin: int = 0,
        by_tags: Dict[str, int] = None,
    ) -> str:
        """
        Used to make your Cochl.Sense results understandable in a glance
        Useful for demo, human testing etc.

        Args:
            hop_size: The hop size that was used for inference
            interval_margin: The default interval margin to apply to every tag that is not specified in "by_tags"
            by_tags: The custom internal margin of each tag

        Raises:
            ValueError: if the provided hop size is not supported

        Example:
            .. code-block:: python

            print(results.to_summarized_result(
                interval_margin=1,
                by_tags={"Speech": 5, "Sing": 3}
            ))
        """
        result_summary = ResultSummary(
            hop_size=self._window_hop,
            default_im=interval_margin,
            tags_im=by_tags,
        )
        summarized_results = result_summary.minimize_details(self.window_results)
        return summarized_results


class ResultSummary:
    """
    Example:

        .. code-block:: python

        result_summary = ResultSummary(
            tags_im={"Speech": 2}
        )
        summary = result_summary.minimize_details(window_results)
    """

    def __init__(
        self,
        default_im=DEFAULT_IM,
        hop_size=WindowHop.HOP_500ms,
        tags_im: Dict[str, int] = None,
    ):
        """
        Args:
            default_im: The default interval margin to apply to every tag that is not specified in "tags_im"
            hop_size: The hop size that was used for inference
            tags_im: The custom internal margin of each tag

        Raises:
            ValueError: if the provided hop size is not supported
        """
        if hop_size != WindowHop.HOP_500ms and hop_size != WindowHop.HOP_1s:
            raise ValueError("Hop size can only be 0.5 or 1")
        self.hop_size = hop_size.second
        self.default_im = default_im
        self.tags_im = tags_im
        self._buffer = {}
        self._file_mode = False
        self._tag_name_other = TAG_NAME_OTHER
        self._min_im = 0
        if default_im == 0 and self.hop_size == WindowHop.HOP_500ms.second:
            self._min_im = -WindowHop.HOP_500ms.second

    def minimize_details(self, results: List[WindowResult] = None):
        """
        Used for file inference to loop over the results and provide a single result summary
        """
        if results is None:
            results = []

        self._file_mode = True
        output = ""

        for window_result in results:
            line = self.minimize_details_window(window_result)
            if not line:
                continue
            output = self._append_line(output, line)

        for tag, (_, from_time, to_time) in self._buffer.items():
            line = f"At {from_time}-{to_time}s, [{tag}] was detected"
            output = self._append_line(output, line)

        self._file_mode = False
        return output

    def minimize_details_window(self, window_result: WindowResult):
        """
        This can be used as you loop over the results
        It will output a merge of the results in ranges
        """
        output = ""
        nb_line = 0

        start_time = window_result.start_time
        end_time = window_result.end_time
        treated_tags = []

        for tag in window_result.sound_tags:
            name = tag.name
            if name == self._tag_name_other:
                continue

            if name in self._buffer:
                (_, from_time, _) = self._buffer[name]
                self._buffer[name] = (self._im(name), from_time, end_time)
            else:
                self._buffer[name] = (self._im(name), start_time, end_time)
            treated_tags.append(name)

        tags_to_remove = []
        for tag, (im, from_time, to_time) in self._buffer.items():
            if tag in treated_tags:
                continue

            im -= self.hop_size
            if im < self._min_im:
                line = f"At {from_time}-{to_time}s, [{tag}] was detected"
                nb_line += 1
                output = self._append_line(output, line)
                tags_to_remove.append(tag)
            else:
                self._buffer[tag] = (im, from_time, to_time)

        for tag in tags_to_remove:
            del self._buffer[tag]

        return output

    def clear_buffer(self):
        self._buffer.clear()

    def _im(self, tag):
        if self.tags_im is None:
            return self.default_im
        return self.tags_im.get(tag, self.default_im)

    @classmethod
    def _append_line(cls, result, line) -> str:
        if not result:
            return line
        return f"{result}\n{line}"
