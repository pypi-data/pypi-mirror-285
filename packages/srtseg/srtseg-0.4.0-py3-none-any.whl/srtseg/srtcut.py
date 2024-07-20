from srtseg import SRTSeg
import os


def ffmpegcmd(src="", dst="", inputcmd="", outputcmd="", use_temp=True):
    """Run ffmpeg command"""
    if os.path.exists(dst):
        return dst

    if src != dst:
        tpf = temp_file(dst)
        dst_str = f'"{tpf}" && mv "{tpf}" "{dst}"' if use_temp else f'"{dst}"'
        cmd = f'ffmpeg -hide_banner -threads 16 {inputcmd} -i "{src}" '
        cmd += f"{outputcmd} {dst_str}"
        lprint(f"[+] RUNNING {cmd}", src)
        run_as_subprocess(cmd, src)
        if not os.path.exists(dst):
            raise FileNotFoundError(f"[-]ffmpeg生成失败src: {src} cmd: {cmd}")
    return dst


def cut(src, srt_file=None):
    """把videofile按照它的字幕文件分割成很多小块
    Args:
        src 视频文件名。
        srt_file: If not provided, it implies the srt file is at
            the same location with the video file
    Returns:
        dst: The first file path of the cut segment
    """

    # 准备好文件名
    title, ext = os.path.splitext(src)
    if not srt_file:
        srt_file = title + ".srt"

    segs = SRTSeg(srt_file).segs()

    # 所有ts文件放在同名文件夹里面
    os.makedirs(title, 0o777, exist_ok=True)

    times = []
    for seg in segs:
        start = seg.start.total_seconds()
        if start == 0:
            continue
        times.append(str(start))

    last = len(times) - 1
    beacon_file = f"{title}/{last}.ts"
    print(f"[+] 寻找缓存标志文件 {beacon_file}")
    if os.path.exists(beacon_file):
        print("[*] 找到切分好的缓存文件，跳过此步骤 100%")
        return f"{title}/0.ts"

    timesstr = ",".join(times)
    options = f' -vf "scale=480:-2,fps=24" -crf 19 -c:v h264 -c:a aac  \
     -pix_fmt yuv420p  -ac 2 \
     -map 0:v:0 -map 0:a:0 \
     -segment_format mpegts \
     -segment_list "{title}/index.m3u8" \
     -segment_list_type m3u8\
     -sc_threshold 0'
    outputcmd = (
        f"-f segment -force_key_frames {timesstr} "
        f" -segment_times {timesstr} {options} "
        " -segment_time_delta 0.05 -max_muxing_queue_size 1024 "
    )
    dst = f"{title}/%d.ts"

    # There is only one sentence. Simply convert
    if len(times) < 1:
        outputcmd = options
        dst = f"{title}/0.ts"

    common.ffmpegcmd(
        src=src, dst=dst, inputcmd="-y", outputcmd=outputcmd, use_temp=False
    )

    return f"{title}/0.ts"


if __name__ == "__main__":
    cut()
