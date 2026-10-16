# -*- coding: utf-8 -*-
"""
build_sdr_day.py — 《她的一天》张艺谋风格 SDR 叙事短片（参考实现 / HDR 之前的基线）

这是 HLG 流水线之前的 SDR 版本（libx264 / yuv420p / 竖屏 2160x3840），保留它有两个用途：
  1. 方向三模式的最早实现：auto / crop / hold（混合片段横屏部分单独处理）；
  2. 作为对照：HDR 版本（build_hlg_films.py）是在这套方向处理经验之上，
     换成 NVENC main10 + zscale 转 HLG 得到的。

方向处理（与 HDR 版一致的关键经验）：
  auto 普通旋转段：ffmpeg 自动旋转（烘焙像素 + 清标签），只 scale
  crop 真横屏(rot=0)：-noautorotate + 中心 9:16 裁切
  hold 混合片段：横屏段落用 -noautorotate + 中心裁切，避免被二次旋转
  最终合并统一 -noautorotate，防止 hold 段的 -90 标签再被转一次

用法：
  set HDR_LIBRARY=D:\\my_library
  python build_sdr_day.py
输出：<library>/scan/sdr_day/her-day-shortfilm.mp4（SDR，HDR 版不使用此输出）
"""
import json
import os
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

LIBRARY = Path(os.environ.get("HDR_LIBRARY", str(Path.cwd() / "library")))
SOURCES = LIBRARY / "edits"
SEGDIR = LIBRARY / "scan" / "sdr_day"
OUT = SEGDIR / "her-day-shortfilm.mp4"
SEGDIR.mkdir(parents=True, exist_ok=True)

# (rid, start, dur, chapter, mode, note)
# mode: auto=自动旋转(竖屏素材)  crop=真横屏中心裁切  hold=混合片段横屏部分(-noautorotate+crop)
SEGMENTS = [
    ("R058", 0.0, 3.0, "晨", "auto", "清晨车窗外日出"),
    ("R044", 0.0, 4.0, None, "auto", "床上跳舞窗光"),
    ("R045", 0.0, 4.0, None, "auto", "客厅对电视跳舞"),
    ("R064", 0.0, 4.0, "学", "auto", "书桌前翻书"),
    ("R066", 1.0, 4.0, None, "crop", "沙发看书笑"),
    ("R047", 1.0, 4.0, None, "auto", "拼积木"),
    ("R052", 0.0, 3.5, None, "auto", "剪纸"),
    ("R051", 1.0, 3.0, "食", "auto", "餐桌空碗"),
    ("R055", 0.0, 3.5, None, "auto", "街边吃烤串"),
    ("R021", 1.0, 4.0, "行", "auto", "小巷跟拍"),
    ("R042", 2.0, 3.0, None, "auto", "草地走路"),
    ("R029", 2.0, 4.0, None, "auto", "林荫道骑车"),
    ("R036", 0.0, 3.5, None, "auto", "骑车带长颈鹿"),
    ("R025", 2.0, 4.0, None, "auto", "步道回头笑"),
    ("R034", 1.0, 6.0, "沙", "auto", "日落沙滩红衣"),
    ("R020", 0.0, 3.5, None, "auto", "红铲装沙"),
    ("R069", 2.0, 3.5, None, "auto", "蹲沙地玩沙"),
    ("R046", 0.0, 3.0, "暮", "crop", "黄昏城市空镜"),
    ("R024", 1.0, 4.0, None, "auto", "夜广场跑步"),
    ("R030", 1.0, 4.0, None, "auto", "夜滑板车灯火"),
    ("R013", 3.5, 2.0, "情", "auto", "奶奶厨房背影"),
    ("R013", 8.0, 4.5, None, "hold", "奶奶拥抱长镜"),
    ("R043", 1.0, 3.5, None, "auto", "爸爸跳绳"),
    ("R022", 2.0, 4.5, None, "auto", "红衣男孩到红包"),
    ("R033", 1.0, 5.0, "夜", "auto", "幼儿园夜演"),
    ("R041", 0.0, 3.0, None, "auto", "荧光棒特写"),
    ("R019", 0.0, 3.0, None, "crop", "荧光棒群像"),
    ("R015", 0.0, 7.0, None, "crop", "生日烛光"),
    ("R065", 0.0, 3.5, "别", "crop", "车窗外挥手"),
    ("R062", 1.0, 3.0, None, "crop", "夜景大桥收尾"),
]


def run(args, log=None):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if log:
        Path(log).write_text(p.stderr, encoding="utf-8")
    if p.returncode:
        raise RuntimeError(p.stderr[-2500:])
    return p.stdout


def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                           "-of", "json", str(path)]))


def get_src(rid):
    return next(SOURCES.glob(rid + "_*"))


def find_font():
    for p in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
              r"C:\Windows\Fonts\simsun.ttc", r"/System/Library/Fonts/PingFang.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return p
    return None


def make_title_card(text, sub, out_path, duration=2.0):
    W, H = 2160, 3840
    img = Image.new("RGB", (W, H), "black")
    d = ImageDraw.Draw(img)
    fp = find_font()
    fm = ImageFont.truetype(fp, 200) if fp else ImageFont.load_default()
    fs = ImageFont.truetype(fp, 80) if fp else ImageFont.load_default()
    b = d.textbbox((0, 0), text, font=fm)
    tw, th = b[2] - b[0], b[3] - b[1]
    d.text(((W - tw) // 2, H // 2 - th // 2 - 150), text, fill="white", font=fm)
    if sub:
        b2 = d.textbbox((0, 0), sub, font=fs)
        sw = b2[2] - b2[0]
        d.text(((W - sw) // 2, H // 2 + 180), sub, fill=(180, 180, 180), font=fs)
    jpg = out_path.with_suffix(".jpg")
    img.save(jpg, quality=95)
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(jpg),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
         "-t", str(duration), "-r", "30", "-vf", f"scale={W}:{H}",
         "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-shortest", str(out_path)])


def render_segment(idx, rid, start, dur, mode, note):
    src = get_src(rid)
    seg_path = SEGDIR / f"seg{idx:02d}_{rid}.mp4"
    if seg_path.exists():
        return seg_path

    vf = []
    if mode in ("hold", "crop"):
        vf.append("crop=1215:2160:iw/2-607:0")
        vf.append("scale=2160:3840:flags=lanczos")
    else:
        vf.append("scale=2160:3840:flags=lanczos")
    vf.append("fps=30")
    vf.append(f"fade=t=in:st=0:d=0.3,fade=t=out:st={max(0, dur - 0.4):.2f}:d=0.4")

    # R015 烛光段源片电平偏高（0dB 削波），线性降到 0.5（约 -6dB）
    gain = "volume=0.5," if rid == "R015" else ""
    af = f"{gain}afade=t=in:st=0:d=0.3,afade=t=out:st={max(0, dur - 0.4):.2f}:d=0.4"

    args = ["ffmpeg", "-v", "warning", "-nostdin", "-y"]
    if mode == "hold":
        args.append("-noautorotate")
    args += ["-ss", str(start), "-i", str(src),
             "-map", "0:v:0", "-map", "0:a:0", "-t", str(dur),
             "-vf", ",".join(vf),
             "-c:v", "libx264", "-preset", "fast",
             "-b:v", "12000k", "-maxrate", "14000k", "-bufsize", "12000k",
             "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
             "-af", af, "-movflags", "+faststart", str(seg_path)]
    print(f"seg{idx:02d} {rid} {mode:4s} {note} ({dur}s)", flush=True)
    run(args, SEGDIR / f"seg{idx:02d}.log")
    return seg_path


def main():
    seg_files = []
    for i, (rid, start, dur, chapter, mode, note) in enumerate(SEGMENTS):
        if chapter:
            card = SEGDIR / f"card_{i:02d}_{chapter}.mp4"
            if not card.exists():
                make_title_card(chapter, "", card, 1.8)
            seg_files.append(card)
        seg_files.append(render_segment(i, rid, start, dur, mode, note))

    open_card = SEGDIR / "card_open.mp4"
    if not open_card.exists():
        make_title_card("她的一天", "从清晨到夜晚", open_card, 2.5)
    end_card = SEGDIR / "card_end.mp4"
    if not end_card.exists():
        make_title_card("晚安", "Goodnight", end_card, 2.5)

    all_files = [open_card] + seg_files + [end_card]
    concat = SEGDIR / "concat.txt"
    lines = []
    for f in all_files:
        d = probe(f)
        dur_f = float(d["streams"][0]["duration"])
        lines.append(f"file '{f.name}'\nduration {dur_f:.3f}\n")
    concat.write_text("".join(lines), encoding="utf-8")

    merged = SEGDIR / "merged_sdr.mp4"
    print("concat merging...", flush=True)
    run(["ffmpeg", "-v", "warning", "-nostdin", "-y", "-noautorotate",
         "-f", "concat", "-safe", "0", "-i", str(concat),
         "-c:v", "libx264", "-preset", "medium", "-b:v", "12000k",
         "-pix_fmt", "yuv420p", "-r", "30",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
         "-movflags", "+faststart", str(merged)], SEGDIR / "merge.log")

    v = next(s for s in probe(merged)["streams"] if s["codec_type"] == "video")
    print(f"Merged: {float(v['duration']):.1f}s", flush=True)

    run(["ffmpeg", "-v", "warning", "-nostdin", "-y", "-noautorotate", "-i", str(merged),
         "-c", "copy", "-movflags", "+faststart", str(OUT)])
    v2 = next(s for s in probe(OUT)["streams"] if s["codec_type"] == "video")
    print(f"Done: {OUT.name} {float(v2['duration']):.1f}s {OUT.stat().st_size / 1e6:.1f}MB",
          flush=True)


if __name__ == "__main__":
    main()
