"""Measure per-shot motion on an ACTUAL cut file (proxy or final).

Metric: extract at fps=6, scale=640, Farneback, centre-crop median dx / mag,
then average over the shot's safe zone. Measuring the cut itself (not the
source windows) is the whole point -- a per-shot mean computed on source
windows does not necessarily hold on the exported file.

usage: python measure_cut.py <video> [label] [durations]

  durations  镜头时长（秒，逗号分隔），默认 "7,4,3,3,3,6,7"
"""
import glob
import os
import shutil
import subprocess
import sys
import tempfile

import cv2
import numpy as np

FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FP = os.environ.get("FFPROBE") or shutil.which("ffprobe") or "ffprobe"
WORK = os.environ.get("STS_WORK") or os.path.join(tempfile.gettempdir(), "sts-work")
os.makedirs(WORK, exist_ok=True)

DURS = [float(x) for x in
        (sys.argv[3] if len(sys.argv) > 3 else "7,4,3,3,3,6,7").split(",")]
INSET = 0.2

video = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(video)

bounds = []
t = 0.0
for d in DURS:
    bounds.append((t, t + d))
    t += d
TOTAL = t

# duration / frame count
p = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries",
                    "stream=nb_frames,duration,r_frame_rate,width,height",
                    "-of", "default=noprint_wrappers=1", video],
                   capture_output=True, text=True)
print(f"=== {label} ===")
print(video)
print(p.stdout.strip())
print(f"expected total {TOTAL:.3f}s")


def clip_flow(a, b, tag):
    d = os.path.join(WORK, "measure", tag)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error",
                    "-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", video,
                    "-vf", "fps=6,scale=640:-2", "-q:v", "3", "-y",
                    os.path.join(d, "f_%03d.jpg")], check=True, capture_output=True)
    files = sorted(glob.glob(os.path.join(d, "f_*.jpg")))
    prev = cv2.imread(files[0], cv2.IMREAD_GRAYSCALE)
    dxs, mags = [], []
    for f in files[1:]:
        cur = cv2.imread(f, cv2.IMREAD_GRAYSCALE)
        fl = cv2.calcOpticalFlowFarneback(prev, cur, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        h, w = fl.shape[:2]
        c = fl[h // 5:h * 4 // 5, w // 5:w * 4 // 5]
        dxs.append(float(np.median(c[..., 0])))
        mags.append(float(np.median(np.sqrt((c ** 2).sum(axis=2)))))
        prev = cur
    return float(np.mean(dxs)), float(np.mean(mags)), len(files)


data = []
for i, (a, b) in enumerate(bounds):
    dx, mag, n = clip_flow(a + INSET, b - INSET, f"C{i+1}")
    data.append((f"C{i+1}", dx, mag))
    print(f"  C{i+1}  cut[{a:.1f}-{b:.1f}]  dx={dx:6.2f}  mag={mag:6.2f}  ({n} frames)")


def lab(d):
    return "weak/vert" if abs(d) < 0.6 else ("<- left" if d < 0 else "-> right")


print("\nadjacent speed ratio (measured on this cut):")
bad = 0
for i in range(len(data) - 1):
    m1, m2 = data[i][2], data[i + 1][2]
    diff = abs(m1 - m2) / max(m1, m2) * 100
    flag = "OK" if diff <= 30 else ("WARN(30-50%)" if diff <= 50 else "!! FAIL(>50%) !!")
    if diff > 30:
        bad += 1
    print(f"  {data[i][0]}->{data[i+1][0]}  {m1:.2f} -> {m2:.2f}   {diff:5.1f}%  {flag}")
print(f"-> over 30%: {bad}/6")

print("\nadjacent direction (measured on this cut):")
conf = 0
for i in range(len(data) - 1):
    l1, l2 = lab(data[i][1]), lab(data[i + 1][1])
    bad_dir = (l1 != l2) and ("weak" not in l1) and ("weak" not in l2)
    if bad_dir:
        conf += 1
    print(f"  {data[i][0]}->{data[i+1][0]}  {l1} -> {l2}   {'!! OPPOSITE !!' if bad_dir else 'OK'}")
print(f"-> direction conflicts: {conf}/6")
