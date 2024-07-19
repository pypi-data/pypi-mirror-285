from __future__ import annotations

import os
import re
from dataclasses import dataclass
from fractions import Fraction
from typing import TYPE_CHECKING

import numpy as np

from auto_editor import version
from auto_editor.utils.subtitle_tools import convert_ass_to_text
from auto_editor.wavfile import read

if TYPE_CHECKING:
    from fractions import Fraction
    from typing import Any

    from av.filter import FilterContext
    from numpy.typing import NDArray

    from auto_editor.ffwrapper import FileInfo
    from auto_editor.output import Ensure
    from auto_editor.utils.bar import Bar
    from auto_editor.utils.log import Log


@dataclass(slots=True)
class FileSetup:
    src: FileInfo
    ensure: Ensure
    strict: bool
    tb: Fraction
    bar: Bar
    temp: str
    log: Log


class LevelError(Exception):
    pass


def link_nodes(*nodes: FilterContext) -> None:
    for c, n in zip(nodes, nodes[1:]):
        c.link_to(n)


def mut_remove_small(
    arr: NDArray[np.bool_], lim: int, replace: int, with_: int
) -> None:
    start_p = 0
    active = False
    for j, item in enumerate(arr):
        if item == replace:
            if not active:
                start_p = j
                active = True

            if j == len(arr) - 1 and j - start_p < lim:
                arr[start_p:] = with_
        elif active:
            if j - start_p < lim:
                arr[start_p:j] = with_
            active = False


def mut_remove_large(
    arr: NDArray[np.bool_], lim: int, replace: int, with_: int
) -> None:
    start_p = 0
    active = False
    for j, item in enumerate(arr):
        if item == replace:
            if not active:
                start_p = j
                active = True

            if j == len(arr) - 1 and j - start_p >= lim:
                arr[start_p:] = with_
        elif active:
            if j - start_p > lim:
                arr[start_p:j] = with_
            active = False


def obj_tag(tag: str, tb: Fraction, obj: dict[str, Any]) -> str:
    key = f"{tag}:{tb}:"
    for k, v in obj.items():
        key += f"{k}={v},"

    key = key[:-1]  # remove unnecessary char
    return key


@dataclass(slots=True)
class Levels:
    ensure: Ensure
    src: FileInfo
    tb: Fraction
    bar: Bar
    temp: str
    log: Log

    @property
    def media_length(self) -> int:
        if self.src.audios:
            if (arr := self.read_cache("audio", {"stream": 0})) is not None:
                return len(arr)

            sr, samples = read(self.ensure.audio(self.src, 0))
            samp_count = len(samples)
            del samples

            samp_per_ticks = sr / self.tb
            ticks = int(samp_count / samp_per_ticks)
            self.log.debug(f"Audio Length: {ticks}")
            self.log.debug(
                f"... without rounding: {float(samp_count / samp_per_ticks)}"
            )
            return ticks

        # If there's no audio, get length in video metadata.
        import av

        with av.open(f"{self.src.path}") as cn:
            if len(cn.streams.video) < 1:
                self.log.error("Could not get media duration")

            video = cn.streams.video[0]

            if video.duration is None or video.time_base is None:
                dur = 0
            else:
                dur = int(video.duration * video.time_base * self.tb)
            self.log.debug(f"Video duration: {dur}")

        return dur

    def none(self) -> NDArray[np.bool_]:
        return np.ones(self.media_length, dtype=np.bool_)

    def all(self) -> NDArray[np.bool_]:
        return np.zeros(self.media_length, dtype=np.bool_)

    def read_cache(self, tag: str, obj: dict[str, Any]) -> None | np.ndarray:
        workfile = os.path.join(
            os.path.dirname(self.temp), f"ae-{version}", "cache.npz"
        )

        try:
            npzfile = np.load(workfile, allow_pickle=False)
        except Exception as e:
            self.log.debug(e)
            return None

        key = f"{self.src.path}:{obj_tag(tag, self.tb, obj)}"
        if key not in npzfile.files:
            return None

        self.log.debug("Using cache")
        return npzfile[key]

    def cache(self, tag: str, obj: dict[str, Any], arr: np.ndarray) -> np.ndarray:
        workdur = os.path.join(os.path.dirname(self.temp), f"ae-{version}")
        if not os.path.exists(workdur):
            os.mkdir(workdur)

        tag = obj_tag(tag, self.tb, obj)
        np.savez(os.path.join(workdur, "cache.npz"), **{f"{self.src.path}:{tag}": arr})

        return arr

    def audio(self, stream: int) -> NDArray[np.float64]:
        if stream > len(self.src.audios) - 1:
            raise LevelError(f"audio: audio stream '{stream}' does not exist.")

        if (arr := self.read_cache("audio", {"stream": stream})) is not None:
            return arr

        sr, samples = read(self.ensure.audio(self.src, stream))

        if len(samples) == 0:
            raise LevelError(f"audio: stream '{stream}' has no samples.")

        def get_max_volume(s: np.ndarray) -> float:
            return max(float(np.max(s)), -float(np.min(s)))

        max_volume = get_max_volume(samples)
        self.log.debug(f"Max volume: {max_volume}")

        samp_count = samples.shape[0]
        samp_per_ticks = sr / self.tb

        if samp_per_ticks < 1:
            self.log.error(
                f"audio: stream '{stream}'\n  Samplerate ({sr}) must be greater than "
                f"or equal to timebase ({self.tb})\n"
                "  Try `-fps 30` and/or `--sample-rate 48000`"
            )

        audio_ticks = int(samp_count / samp_per_ticks)
        self.log.debug(
            f"analyze: audio length: {audio_ticks} ({float(samp_count / samp_per_ticks)})"
        )
        self.bar.start(audio_ticks, "Analyzing audio volume")

        threshold_list = np.zeros((audio_ticks), dtype=np.float64)

        if max_volume == 0:  # Prevent dividing by zero
            return threshold_list

        # Determine when audio is silent or loud.
        for i in range(audio_ticks):
            if i % 500 == 0:
                self.bar.tick(i)

            start = int(i * samp_per_ticks)
            end = min(int((i + 1) * samp_per_ticks), samp_count)

            threshold_list[i] = get_max_volume(samples[start:end]) / max_volume

        self.bar.end()
        return self.cache("audio", {"stream": stream}, threshold_list)

    def subtitle(
        self,
        pattern: str,
        stream: int,
        ignore_case: bool,
        max_count: int | None,
    ) -> NDArray[np.bool_]:
        if stream >= len(self.src.subtitles):
            raise LevelError(f"subtitle: subtitle stream '{stream}' does not exist.")

        try:
            flags = re.IGNORECASE if ignore_case else 0
            re_pattern = re.compile(pattern, flags)
        except re.error as e:
            self.log.error(e)

        import av
        from av.subtitles.subtitle import AssSubtitle, TextSubtitle

        try:
            container = av.open(self.src.path, "r")
            subtitle_stream = container.streams.subtitles[stream]
            assert isinstance(subtitle_stream.time_base, Fraction)
        except Exception as e:
            self.log.error(e)

        # Get the length of the subtitle stream.
        sub_length = 0
        for packet in container.demux(subtitle_stream):
            if packet.pts is None or packet.duration is None:
                continue
            for subset in packet.decode():
                # See definition of `AVSubtitle`
                # in: https://ffmpeg.org/doxygen/trunk/avcodec_8h_source.html
                start = float(packet.pts * subtitle_stream.time_base)
                dur = float(packet.duration * subtitle_stream.time_base)

                end = round((start + dur) * self.tb)
                sub_length = max(sub_length, end)

        result = np.zeros((sub_length), dtype=np.bool_)
        del sub_length

        count = 0
        early_exit = False
        container.seek(0)
        for packet in container.demux(subtitle_stream):
            if packet.pts is None or packet.duration is None:
                continue
            if early_exit:
                break
            for subset in packet.decode():
                if max_count is not None and count >= max_count:
                    early_exit = True
                    break

                start = float(packet.pts * subtitle_stream.time_base)
                dur = float(packet.duration * subtitle_stream.time_base)

                san_start = round(start * self.tb)
                san_end = round((start + dur) * self.tb)

                for sub in subset:
                    if isinstance(sub, AssSubtitle):
                        line = convert_ass_to_text(sub.ass.decode(errors="ignore"))
                    elif isinstance(sub, TextSubtitle):
                        line = sub.text.decode(errors="ignore")
                    else:
                        continue

                    if line and re.search(re_pattern, line):
                        result[san_start:san_end] = 1
                        count += 1

        container.close()

        return result

    def motion(self, stream: int, blur: int, width: int) -> NDArray[np.float64]:
        import av

        if stream >= len(self.src.videos):
            raise LevelError(f"motion: video stream '{stream}' does not exist.")

        mobj = {"stream": stream, "width": width, "blur": blur}
        if (arr := self.read_cache("motion", mobj)) is not None:
            return arr

        container = av.open(f"{self.src.path}", "r")

        video = container.streams.video[stream]
        video.thread_type = "AUTO"

        inaccurate_dur = 1 if video.duration is None else video.duration
        self.bar.start(inaccurate_dur, "Analyzing motion")

        prev_frame = None
        current_frame = None
        total_pixels = self.src.videos[0].width * self.src.videos[0].height
        index = 0

        graph = av.filter.Graph()
        link_nodes(
            graph.add_buffer(template=video),
            graph.add("scale", f"{width}:-1"),
            graph.add("format", "gray"),
            graph.add("gblur", f"sigma={blur}"),
            graph.add("buffersink"),
        )
        graph.configure()

        threshold_list = np.zeros((1024), dtype=np.float64)

        for unframe in container.decode(video):
            graph.push(unframe)
            frame = graph.pull()

            # Showing progress ...
            assert frame.time is not None
            index = int(frame.time * self.tb)
            if frame.pts is not None:
                self.bar.tick(frame.pts)

            current_frame = frame.to_ndarray()

            if index > len(threshold_list) - 1:
                threshold_list = np.concatenate(
                    (threshold_list, np.zeros((len(threshold_list)), dtype=np.float64)),
                    axis=0,
                )

            if prev_frame is not None:
                # Use `int16` to avoid underflow with `uint8` datatype
                diff = np.abs(
                    prev_frame.astype(np.int16) - current_frame.astype(np.int16)
                )
                threshold_list[index] = np.count_nonzero(diff) / total_pixels

            prev_frame = current_frame

        self.bar.end()
        return self.cache("motion", mobj, threshold_list[:index])
