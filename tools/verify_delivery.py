"""Technical acceptance checks on the FINAL hard-cut file.

Covers the things that must survive the 4K/HDR encode: exact duration, stream
frame/sample counts, HDR colour tags vs the source, black/freeze/silence, and
that the audio stream is not shorter than the video stream.

usage: python verify_delivery.py <final.mp4> [source] [durations] [fps]

  source     源片路径，用于逐项对比色彩/编码标签；省略则跳过对比
  durations  镜头时长（秒，逗号分隔），默认 "7,4,3,3,3,6,7"
  fps        成片帧率，用于推算期望帧数，默认 120

env:
  FFMPEG     ffmpeg 可执行文件路径；未设置时从 PATH 查找
  FFPROBE    ffprobe 可执行文件路径；未设置时从 PATH 查找
"""
import os
import shutil
import subprocess
import sys

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FP = os.environ.get("FFPROBE") or shutil.which("ffprobe") or "ffprobe"

final = sys.argv[1]
SRC = sys.argv[2] if len(sys.argv) > 2 else None
DURS = [float(x) for x in
        (sys.argv[3] if len(sys.argv) > 3 else "7,4,3,3,3,6,7").split(",")]
FPS = float(sys.argv[4]) if len(sys.argv) > 4 else 120.0

EXPECT_DUR = sum(DURS)
EXPECT_FRAMES = int(round(EXPECT_DUR * FPS))

print("=" * 74)
print("1) streams")
print("=" * 74)
probes = [("FINAL", final)] + ([("SOURCE", SRC)] if SRC else [])
for label, path in probes:
    out = subprocess.run([FP, "-v", "error", "-show_entries",
                          "stream=index,codec_type,codec_name,width,height,"
                          "r_frame_rate,nb_frames,duration,pix_fmt,color_range,"
                          "color_space,color_transfer,color_primaries,"
                          "bits_per_raw_sample,sample_rate,channels",
                          "-of", "default=noprint_wrappers=1", path],
                         capture_output=True, text=True)
    print(f"--- {label} ---")
    print(out.stdout.strip())

print()
print("=" * 74)
print("2) duration / frame count")
print("=" * 74)
out = subprocess.run([FP, "-v", "error", "-select_streams", "v:0",
                      "-show_entries", "stream=nb_frames,duration",
                      "-of", "default=noprint_wrappers=1", final],
                     capture_output=True, text=True)
print(out.stdout.strip())
print(f"expected: {EXPECT_FRAMES} frames / {EXPECT_DUR:.3f}s")
out = subprocess.run([FP, "-v", "error", "-select_streams", "a:0",
                      "-show_entries", "stream=duration,nb_frames",
                      "-of", "default=noprint_wrappers=1", final],
                     capture_output=True, text=True)
print("audio:", out.stdout.strip())


def scan(name, args):
    r = subprocess.run([FF, "-hide_banner", "-loglevel", "info", "-i", final]
                       + args + ["-f", "null", "-"],
                       capture_output=True, text=True)
    hits = [l.strip() for l in r.stderr.splitlines()
            if name in l]
    print(f"{name}: {len(hits)} hit(s)")
    for l in hits[:6]:
        print("   ", l)


print()
print("=" * 74)
print("3) black / freeze / silence")
print("=" * 74)
scan("black_start", ["-vf", "blackdetect=d=0.1:pix_th=0.10", "-an"])
scan("freeze_start", ["-vf", "freezedetect=n=-60dB:d=0.2", "-an"])
scan("silence_start", ["-af", "silencedetect=n=-45dB:d=0.15", "-vn"])