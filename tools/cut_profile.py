"""Classify each join as hard cut vs dissolve from the frame-difference profile.

A dissolve spreads the change over many frames (e.g. 0.5s worth) as a smooth
bump: many frames carry a moderate difference. A hard cut puts the whole change
in ONE frame pair. So count how many frame pairs carry >=40% of the peak.

usage: python cut_profile.py <video> [durations]

  durations  镜头时长（秒，逗号分隔），默认 "7,4,3,3,3,6,7"
"""
import os
import shutil
import subprocess
import sys
import tempfile

import cv2
import numpy as np

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
WORK = os.environ.get("STS_WORK") or os.path.join(tempfile.gettempdir(), "sts-work")
os.makedirs(WORK, exist_ok=True)
DURS = [float(x) for x in
        (sys.argv[2] if len(sys.argv) > 2 else "7,4,3,3,3,6,7").split(",")]

video = sys.argv[1]
cuts = []
t = 0.0
for d in DURS[:-1]:
    t += d
    cuts.append(t)

print(f"=== join profile :: {os.path.basename(video)} ===")
print("(hard cut => exactly 1 frame pair carries the change)")
for i, T in enumerate(cuts, 1):
    d = os.path.join(WORK, "cutprof", f"c{i}")
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error",
                    "-ss", f"{T-0.20:.4f}", "-t", "0.40", "-i", video,
                    "-vf", "fps=120,scale=320:-2", "-q:v", "2", "-y",
                    os.path.join(d, "f_%04d.jpg")], check=True, capture_output=True)
    fs = sorted(os.listdir(d))
    prev = cv2.imread(os.path.join(d, fs[0]), cv2.IMREAD_GRAYSCALE)
    diffs = []
    for f in fs[1:]:
        cur = cv2.imread(os.path.join(d, f), cv2.IMREAD_GRAYSCALE)
        diffs.append(float(np.mean(np.abs(cur.astype(np.float32)
                                        - prev.astype(np.float32)))))
        prev = cur
    diffs = np.array(diffs)
    peak = diffs.max()
    k = int(np.argmax(diffs))
    big = int((diffs >= 0.4 * peak).sum())
    # frames spanned by the change: contiguous run around the peak
    lo = k
    while lo > 0 and diffs[lo - 1] >= 0.4 * peak:
        lo -= 1
    hi = k
    while hi < len(diffs) - 1 and diffs[hi + 1] >= 0.4 * peak:
        hi += 1
    span_ms = (hi - lo + 1) / 120.0 * 1000.0
    verdict = ("HARD CUT" if big <= 2
               else f"SPREAD over {span_ms:.0f}ms -> dissolve-like")
    print(f"  cut{i} @{T:5.1f}s  peak={peak:6.2f}  pairs>=40%peak={big:3d}  "
          f"span={span_ms:5.1f}ms  {verdict}")
