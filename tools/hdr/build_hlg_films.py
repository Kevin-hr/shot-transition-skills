# -*- coding: utf-8 -*-
"""
build_hlg_films.py — 《她的一天》HDR(HLG) 故事线渲染器（流水线 · 第 3 步）

在 NVIDIA GPU（RTX 5060Ti 实测）上用 hevc_nvenc main10 批量渲染 HLG 竖屏短片：
  - 全部原生 HLG 素材（按 manifest 的 is_hlg=1 自选），SDR 旅行批不用（转换后画面偏平）
  - 方向三模式（按 manifest 自动判定，关键经验，不能只看单帧 JPG）：
      auto : 带旋转标签（rotation!=0）→ 让 ffmpeg 自动旋转，烘焙像素并清标签，只 scale
      crop : 真横屏编码（rotation=0 且 coded w>h）→ -noautorotate + 中心 9:16 裁切
      port : 真竖屏编码（rotation=0 且 coded h>=w）→ 不旋转，直接 cover 缩放
  - SDR 标题卡：PIL 黑底白字 → 显式 rgb24 → zscale 单步写全 in/out 参数转 HLG
  - 每段统一 2160x3840 / 30fps / hevc main10 / HLG(bt2020, arib-std-b67, bt2020nc, tv)
  - 卡片必须带静音音轨，否则 concat 丢音频
  - 最终 concat 必须重编码（-c copy 会在接缝产生 non-monotonic DTS），同参数 NVENC + CFR

用法：
  set HDR_LIBRARY=D:\\my_library
  python scan_manifest.py          # 先出 manifest.csv
  python build_hlg_films.py        # 渲染全部 5 条
  python build_hlg_films.py 02_school_day    # 只渲染一条

依赖：FFmpeg 8.x（含 zscale、hevc_nvenc）、NVIDIA GPU、Pillow。
目录：
  <library>/edits/R###_*.mp4
  <library>/scan/manifest.csv
  <library>/scan/hdr_build/<key>/...   （中间段，可重跑）
  <library>/scan/output/<key>_HDR.mp4
"""
import argparse
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from storylines import FILMS

# ---------- 路径（可用环境变量 HDR_LIBRARY 覆盖） ----------
LIBRARY = Path(os.environ.get("HDR_LIBRARY", str(Path.cwd() / "library")))
SOURCES = LIBRARY / "edits"
SCAN = LIBRARY / "scan"
BUILD = SCAN / "hdr_build"
OUTDIR = SCAN / "output"

W, H = 2160, 3840
FPS = 30
VOL = 0.72  # 线性音量；注意 ffmpeg 会吞掉 -6dB 这种负数写法，故用 0.72

M = {r["rid"]: r for r in csv.DictReader(open(SCAN / "manifest.csv", encoding="utf-8"))}


def run(args, log=None):
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if log:
        Path(log).write_text(p.stderr or "", encoding="utf-8")
    if p.returncode:
        raise RuntimeError(" ".join(map(str, args[:6])) + "\n" + (p.stderr or "")[-2500:])
    return p.stdout


def probe(path):
    return json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                           "-of", "json", str(path)]))


def has_audio(path):
    try:
        return any(s["codec_type"] == "audio" for s in probe(path)["streams"])
    except Exception:
        return False


def src_of(rid):
    return next(SOURCES.glob(rid + "_*"))


def mode_of(rid):
    """方向模式：rotation!=0 走 auto；rotation=0 时横屏 crop、竖屏 port。"""
    r = M[rid]
    rot = int(r["rotation"])
    w, h = int(r["width"]), int(r["height"])
    if rot != 0:
        return "auto"
    return "crop" if w > h else "port"


def find_font():
    for p in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
              r"/System/Library/Fonts/PingFang.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return p
    return None


FP = find_font()

# ---------- 标题卡（SDR 黑底白字 → zscale 单步转 HLG） ----------
def card_jpg(text, sub, jpg_path, title=True):
    img = Image.new("RGB", (W, H), "black")
    d = ImageDraw.Draw(img)
    if title:
        fm = ImageFont.truetype(FP, 180)
        fs = ImageFont.truetype(FP, 72)
    else:
        fm = ImageFont.truetype(FP, 150)
        fs = ImageFont.truetype(FP, 66)
    b = d.textbbox((0, 0), text, font=fm)
    tw, th = b[2] - b[0], b[3] - b[1]
    d.text(((W - tw) // 2, H // 2 - th // 2 - 120), text, fill="white", font=fm)
    if sub:
        b2 = d.textbbox((0, 0), sub, font=fs)
        sw = b2[2] - b2[0]
        d.text(((W - sw) // 2, H // 2 + 160), sub, fill=(178, 178, 178), font=fs)
    img.save(jpg_path, quality=95)


def make_card(text, sub, out_path, dur, title=True):
    if out_path.exists():
        return
    jpg = out_path.with_suffix(".jpg")
    card_jpg(text, sub, jpg, title)
    # 关键：先显式 rgb24，再 zscale 单步同时写全输入/输出参数；NVENC 收 p010le
    vf = (f"scale={W}:{H}:flags=lanczos,format=rgb24,format=gbrpf32le,"
          f"zscale=primariesin=bt709:transferin=iec61966-2-1:primaries=bt2020:"
          f"transfer=arib-std-b67:matrix=bt2020nc:npl=100:rangein=pc:range=tv,format=p010le")
    run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", str(jpg),
         "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",   # 卡片必须有静音音轨
         "-t", str(dur), "-r", str(FPS), "-vf", vf,
         "-c:v", "hevc_nvenc", "-preset", "p5", "-tune", "hq", "-profile:v", "main10",
         "-rc", "vbr", "-cq", "21", "-b:v", "0",
         "-color_primaries", "bt2020", "-color_trc", "arib-std-b67",
         "-colorspace", "bt2020nc", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
         "-shortest", str(out_path)], out_path.with_suffix(".log"))


# ---------- 视频段 ----------
def render_clip(seg_dir, idx, rid, use, frac):
    src = src_of(rid)
    srcdur = float(M[rid]["duration"])
    mode = mode_of(rid)
    out = seg_dir / f"seg{idx:02d}_{rid}.mp4"
    if out.exists():
        return out

    use = min(use, srcdur - 0.25)
    if use <= 0.4:
        start = 0.1
        use = max(0.3, srcdur - 0.2)
    else:
        start = max(0.15, min(srcdur * frac - use / 2, srcdur - use - 0.15))

    fo = 0.30
    fe = max(0.0, use - 0.40)
    vf = []
    if mode == "crop":
        # 真横屏中心 9:16（3840x2160 即中心 1215x2160）；偶数对齐
        vf.append("crop=trunc(ih*9/16/2)*2:ih:(iw-trunc(ih*9/16/2)*2)/2:0")
    vf.append(f"scale={W}:{H}:flags=lanczos:force_original_aspect_ratio=increase,crop={W}:{H}")
    vf.append(f"fps={FPS}")
    vf.append(f"fade=t=in:st=0:d={fo},fade=t=out:st={fe:.2f}:d=0.4")
    vf.append("format=p010le")
    af = f"volume={VOL},afade=t=in:st=0:d={fo},afade=t=out:st={fe:.2f}:d=0.4"

    args = ["ffmpeg", "-v", "warning", "-nostdin", "-y"]
    if mode == "crop":
        args.append("-noautorotate")
    args += ["-ss", f"{start:.2f}", "-i", str(src)]
    if has_audio(src):
        args += ["-map", "0:v:0", "-map", "0:a:0", "-t", f"{use:.2f}", "-af", af]
    else:
        args += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                 "-map", "0:v:0", "-map", "1:a:0", "-t", f"{use:.2f}"]
    args += ["-vf", ",".join(vf),
             "-c:v", "hevc_nvenc", "-preset", "p5", "-tune", "hq", "-profile:v", "main10",
             "-rc", "vbr", "-cq", "21", "-b:v", "0",
             "-color_primaries", "bt2020", "-color_trc", "arib-std-b67",
             "-colorspace", "bt2020nc", "-color_range", "tv",
             "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart", str(out)]
    print(f"  seg{idx:02d} {rid} {mode:4s} {start:5.2f}+{use:.1f}s", flush=True)
    run(args, out.with_suffix(".log"))
    return out


ENDS = {
    "02_school_day": ("毕业快乐", "愿她一路生花"),
    "03_chasing_wind": ("追风的女孩", "风，会追上她"),
    "04_holding_hands": ("牵着你的手", "陪她慢慢长大"),
    "05_fairy_tale": ("她的童话", "愿她永远做自己的公主"),
    "06_see_the_world": ("一起去看世界", "去更远的地方"),
}


def build_film(film):
    key = film["key"]
    seg_dir = BUILD / key
    seg_dir.mkdir(parents=True, exist_ok=True)
    print(f"=== {key} ===", flush=True)

    files = []
    open_card = seg_dir / "00_open.mp4"
    make_card(film["title"], film["sub"], open_card, 2.6, title=True)
    files.append(open_card)

    idx = 1
    for ci, (ch, clips) in enumerate(film["chapters"]):
        cc = seg_dir / f"c{ci:02d}_{ch}.mp4"
        make_card(ch, "", cc, 1.7, title=False)
        files.append(cc)
        for rid, use, frac in clips:
            files.append(render_clip(seg_dir, idx, rid, use, frac))
            idx += 1

    et, es = ENDS[key]
    end_card = seg_dir / "99_end.mp4"
    make_card(et, es, end_card, 2.8, title=True)
    files.append(end_card)

    concat = seg_dir / "concat.txt"
    lines = []
    for f in files:
        d = probe(f)
        durn = float(next(s for s in d["streams"] if s["codec_type"] == "video")["duration"])
        lines.append(f"file '{f.name}'\nduration {durn:.3f}\n")
    concat.write_text("".join(lines), encoding="utf-8")

    out = OUTDIR / f"{key}_HDR.mp4"
    OUTDIR.mkdir(parents=True, exist_ok=True)
    print(f"  concat {len(files)} segments -> {out.name}", flush=True)
    # 关键：concat 必须重编码出连续时间线，避免 -c copy 的 DTS 重复（抖音/严格 muxer 会挑）
    run(["ffmpeg", "-v", "warning", "-nostdin", "-y", "-noautorotate",
         "-f", "concat", "-safe", "0", "-i", str(concat),
         "-r", str(FPS), "-vsync", "cfr",
         "-c:v", "hevc_nvenc", "-preset", "p5", "-tune", "hq", "-profile:v", "main10",
         "-rc", "vbr", "-cq", "21", "-b:v", "0",
         "-color_primaries", "bt2020", "-color_trc", "arib-std-b67",
         "-colorspace", "bt2020nc", "-color_range", "tv",
         "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", str(out)], seg_dir / "concat.log")

    v = next(s for s in probe(out)["streams"] if s["codec_type"] == "video")
    a = next((s for s in probe(out)["streams"] if s["codec_type"] == "audio"), None)
    print(f"  DONE {out.name} {float(v['duration']):.1f}s "
          f"{v['pix_fmt']}/{v['color_transfer']} audio={'Y' if a else 'N'} "
          f"{out.stat().st_size / 1e6:.0f}MB", flush=True)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="?", default=None, help="只渲染指定 key")
    args = ap.parse_args()
    BUILD.mkdir(parents=True, exist_ok=True)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    for film in FILMS:
        if args.only and film["key"] != args.only:
            continue
        build_film(film)
    print("ALL DONE")
