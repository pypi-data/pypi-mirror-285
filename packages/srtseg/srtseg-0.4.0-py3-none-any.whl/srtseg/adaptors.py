import webvtt
from datetime import timedelta
from srtseg import Seg


def srt_to_vtt(srtstr):
    """Convert SRT to VTT file"""
    vtt = webvtt.parsers.SRTParser().read_from_buffer(io.StringIO(srtstr))
    for index, caption in enumerate(vtt.captions):
        caption.identifier = "s" + str(index)
    return webvtt.writers.WebVTTWriter().webvtt_content(vtt.captions)


def seg_to_title(seg):
    """Turn the current SRTSeg into Elastic Search dataformat.
    The return can be directly used to input into Search"""
    return {
        "original_index": seg.subtitle.index,
        "start": seg.start.total_seconds(),
        "end": seg.end.total_seconds(),
        "content": seg.subtitle.content,
        "sub_start": seg.subtitle.start.total_seconds(),
        "sub_end": seg.subtitle.end.total_seconds(),
    }


def titles_to_segs(hits):
    """Restore SRTSeg from Elastic Search Hits"""
    start = 0
    segs = []

    for hit in hits:
        seg = Seg()
        sub_duration = hit.sub_end - hit.sub_start
        seg_duration = hit.end - hit.start
        sub_offset = hit.sub_start - hit.start
        sub = srt.Subtitle(
            index=hit.original_index,
            start=timedelta(seconds=start + sub_offset),
            end=timedelta(seconds=start + sub_offset + sub_duration),
            content=hit.content,
        )
        seg.subtitle = sub
        seg.originalIndex = hit.original_index
        seg.selected = True
        seg.path = tools.COS_SERVER + "/" + hit.local_path
        seg.path = tools.low_res_url(seg.path)
        seg.start = timedelta(seconds=start)
        seg.end = timedelta(seconds=start + seg_duration)
        seg.duration = timedelta(seconds=seg_duration)
        segs.append(seg)
        start += seg_duration
    return segs
