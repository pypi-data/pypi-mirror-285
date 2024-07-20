""" SRT Segmentation
The simplest file format is .srt, and it can be handled pretty well with srt lib.
srtseg provides the additional feature on top of srt:
* Get duration of each video (cut in the middle of the space between two subtitle)
* Segment selection
* M3U8 export
* WebVTT export
Author: Jianshuo Wang
Last Modified: 2024-07-13
"""

import json
import math


from copy import copy, deepcopy
from datetime import timedelta

import srt


class Seg:
    """Representation of a segment in video file.
    IMPORTANT:
    -- start/end: Timedelta of the start/end time based on the original video
    -- path: Relative path to the srt file. This is a base to calculate path
    -- selected: Used the mark whehter this seg is included in export
    -- subtitle: srt Subtitle object (which has its start, end, content)
    """

    start = timedelta(0)
    end = timedelta(0)
    subtitle = None
    duration = timedelta(0)
    path = ""
    selected = True

    def __repr__(self):
        """Representation of Seg

        Returns:
            str: string representation
        """
        return (
            f"Seg: {self.subtitle.index} {self.subtitle.start} "
            f"{self.subtitle.end} {self.subtitle.content}"
            f"@{self.path}"
        )


class SRTSeg:
    """Segment the video according to SRT time"""

    def __init__(self, path=None):
        """
        Initial based on srt_file using srt lib
            segements: collection of segments
            path: the SRT File
            subtitles: The subtitle collection
        Args:
            srt_file: the SRT file location
        """
        self.segments = []
        self.path = path

        if path is None:
            return

        def default_filename_func(seg):
            return f"{seg.path.replace('.srt')}/{seg.subtitle.index-1}.ts"

        self.media_url_func = default_filename_func

        subtitles = srt.parse(open(path).read())
        self.from_subtitles(subtitles, path)

    def from_subtitles(self, subtitles, path=None):
        """Build object from subtitles"""
        for sub in subtitles:
            seg = Seg()
            seg.subtitle = sub
            seg.selected = True
            seg.path = path
            self.segments.append(seg)

        self._calculate_times()
        return self

    def subs(self):
        """The subtitles of the video"""
        return [sg.subtitle for sg in self.segs()]

    def __iter__(self):
        return iter(self.segs())

    def segs(self):
        """The segments of the video. Contains subs and more information"""
        start_pointer = timedelta(0)
        results = []
        for seg in self.segments:
            if seg.selected:
                # We don't want to change the original stuff
                sg = deepcopy(seg)
                delta = sg.start - start_pointer
                sg.start -= delta
                sg.end -= delta
                sg.subtitle.start -= delta
                sg.subtitle.end -= delta
                start_pointer += sg.duration
                results.append(sg)

        return results

    def _calculate_times(self):
        segs = self.segments
        for index, _ in enumerate(segs):
            # 第一个和最后一个特殊处理
            if index == 0:
                segs[index].start = timedelta(0)
                segs[index].duration = segs[index].subtitle.end
                continue

            segs[index].start = (
                segs[index].subtitle.start + segs[index - 1].subtitle.end
            ) / 2
            segs[index - 1].end = segs[index].start
            segs[index - 1].duration = segs[index - 1].end - segs[index - 1].start

            if index == len(segs) - 1:
                segs[index].end = segs[index].subtitle.end
                segs[index].duration = segs[index].end - segs[index].start

        return self.segments

    def filter(self, lines=None, exact=True, padding=None, max_duration=None):
        """
        Filter the selected lines in the srt file
        Args:
            lines: The array of lines to be selected ordered by importance
                lines can be content, or the 0 based index of the line
                The order of the lines matters - from most important to least
            exact: Whether the match should be exact (from begining to
                    end) or substring match is OK
            ignore_case: Whether to ignore cases
            max_duration: The maxium duration of video can be returned
            padding: Select surrounding lines. Examples of pading:
                [0]: only the line
                [-1, 0, 1]: the lines before and after the selected line
                [0, 1]: the line and the following line
        Return:
            The same SRTSeg object
        """
        max_duration = max_duration or 60 * 60 * 1
        result = deepcopy(self)

        padding = padding or [0]
        duration = 0
        positives = []

        result.clear_selection()

        if lines is None:  # None lines means select all
            lines = range(len(self.segments))

        for line in lines:
            found = []

            # 支持index方式传入lines
            if isinstance(line, int):
                found.append(line)
            else:
                found = result.match_line(line, exact)

            # 检测连续性。如果数字是连续的，则不建议打断

            for item in found:
                if (
                    duration + result.segments[item].duration.total_seconds()
                    < max_duration
                ):
                    duration += result.segments[item].duration.total_seconds()
                    positives.append(item)
                    result.segments[item].selected = True
        # result.padding(padding, positives, max_duration)
        return result

    def clear_selection(self):
        """Set all segments to unselected before actions like filter"""
        for seg in self.segments:
            seg.selected = False

    def padding(self, padding, positives, max_duration):
        """Padding to include more segs than the key one"""
        duration = 0  # bugbug

        for positive in positives:
            for offset in padding:
                if offset == 0:
                    continue
                if 0 <= positive + offset <= len(self.segments) - 1:
                    duration += self.segments[
                        positive + offset
                    ].duration.total_seconds()
                    if duration > max_duration:
                        return self
                    self.segments[positive + offset].selected = True
        return self

    def selected_index(self):
        """Return selected index"""
        # return [(sg.originalIndex, sg.subtitle.content)
        #         for sg in self.segments if sg.selected]
        return [idx for idx, sg in enumerate(self.segments) if sg.selected]

    def m3u8(self):
        """
        Return m3u8 of the current selected content

        Args:
            usepath: Use the path in the TS file location
            start: When usepath, where is the starting point of rel path
        Returns:
            str: The content of m3u8
        """
        m3u8_infs = ""
        max_duration = 0

        for seg in self.segs():
            duration = round(seg.duration.total_seconds(), 1)
            max_duration = max(duration, max_duration)

            filename = self.media_url_func(seg)

            m3u8_infs += f"""#EXT-X-DISCONTINUITY
#EXTINF:{duration},
{filename}
"""
        m3u8_header = f"""#EXTM3U
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:0
#EXT-X-TARGETDURATION:{math.ceil(max_duration)}
"""
        m3u8_footer = """#EXT-X-ENDLIST\n"""
        return m3u8_header + m3u8_infs + m3u8_footer

    def srtstr(self):
        """Return SRT format string"""
        return srt.compose(list(self.subs()))

    def json(self, base=None):
        """Return json format of subtitles"""
        result = base or {}
        result["subtitles"] = []
        for seg in self.segs():
            result["subtitles"].append(
                {
                    "index": seg.subtitle.index - 1,
                    "start": seg.subtitle.start.total_seconds(),
                    "end": seg.subtitle.end.total_seconds(),
                    "content": seg.subtitle.content,
                    "filename": self.media_url_func(seg),
                }
            )

        return json.dumps(result, indent=2, ensure_ascii=False)

    def __add__(self, other):
        """Append a SRT to the end of the other SRT."""
        assert issubclass(other.__class__, SRTSeg), "Not SRTSeg"
        result = copy(self)
        result.segments = copy(self.segments)

        # For everything in the append, the timestamp in everything
        # should be reset by the delta
        self_seg = list(self.segs())
        prev_end = timedelta(0) if len(self_seg) == 0 else self_seg[-1].end
        new_seg = list(other.segs())
        next_start = timedelta(0) if len(new_seg) == 0 else new_seg[0].start

        # 添加的需要都进行时间移动
        delta = prev_end - next_start
        for seg in other.segs():
            seg.start += delta
            seg.end += delta
            seg.subtitle.start += delta
            seg.subtitle.end += delta
            result.segments.append(seg)

        return result

    def __repr__(self):
        """Representation of SRT Object"""
        return (
            f"{self.__class__.__name__} filename={self.srtfile}"
            f" <{len(self.segs())}/{len(self.segments)}>"
        )
