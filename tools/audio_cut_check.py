"""Check for audio clicks at the hard-cut points.

A cross-faded audio join hides any waveform discontinuity. Hard cuts butt two
unrelated waveforms together, so a step can appear at the join and be heard as a
click. Compare the sample-to-sample jump AT the cut against the local
distribution of jumps around it.

usage: python audio_cut_check.py <video> [durations]

  durations  镜头时长（秒，逗号分隔），默认 "7,4,3,3,3,6,7"

env:
  FFMPEG     ffmpeg 可执行文件路径；未设置时从 PATH 查找
  STS_WORK   工作目录；未设置时使用系统临时目录
"""
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
WORK = os.environ.get("STS_WORK") or os.path.join(tempfile.gettempdir(), "sts-work")
os.makedirs(WORK, exist_ok=True)

DURS = [float(x) for x in
        (sys.argv[2] if len(sys.argv) > 2 else "7,4,3,3,3,6,7").split(",")]
SR = 48000

video = sys.argv[1]
raw = os.path.join(WORK, "audio_check.raw")
subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", video,
                "-vn", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-y", raw],
               check=True, capture_output=True)
x = np.fromfile(raw, dtype=np.int16).astype(np.float32)
print(f"samples={len(x)}  duration={len(x)/SR:.3f}s")

cuts = []
t = 0.0
for d in DURS[:-1]:
    t += d
    cuts.append(t)

d = np.abs(np.diff(x))
worst = 0
for T in cuts:
    n = int(round(T * SR))
    if n <= 0 or n >= len(x):
        continue
    jump = float(np.abs(x[n] - x[n - 1]))
    lo, hi = max(0, n - SR // 2), min(len(d), n + SR // 2)
    local = d[lo:hi]
    p999 = float(np.percentile(local, 99.9))
    p50 = float(np.percentile(local, 50))
    ratio = jump / max(p999, 1e-6)
    flag = "OK" if jump <= p999 else "!! click risk !!"
    if jump > p999:
        worst += 1
    print(f"  cut @{T:5.1f}s  jump={jump:7.1f}  local p50={p50:6.1f} "
          f"p99.9={p999:7.1f}  ratio={ratio:4.2f}  {flag}")
print(f"-> cuts above local p99.9: {worst}/{len(cuts)}")