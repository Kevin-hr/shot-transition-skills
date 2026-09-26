"""Direction matching at the CUT BOUNDARY, measured on an actual cut file.

The project lesson: inside a handheld shot the direction drifts, so the whole-shot
average is not what the viewer perceives. What matters is the direction in the
~0.8s on each side of the cut. The selection DP constrained exactly those windows
(dxL / dxR), so this is the check that validates its guarantee.

Frames straddling the cut itself are excluded (that pair is a scene change).

usage: python measure_boundary.py <video> [label] [durations]

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
WORK = os.environ.get("STS_WORK") or os.path.join(tempfile.gettempdir(), "sts-work")
os.makedirs(WORK, exist_ok=True)

DURS = [float(x) for x in
        (sys.argv[3] if len(sys.argv) > 3 else "7,4,3,3,3,6,7").split(",")]
WIN = 0.8          # window on each side of the cut
GAP = 0.05         # skip frames right at the cut
WEAK = 0.8         # below this the shot is treated as having no clear direction
FPS = 6            # MUST match the profile/DP sampling, or the dx scale differs

video = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(video)

cuts = []
t = 0.0
for d in DURS[:-1]:
    t += d
    cuts.append(t)

print(f"=== boundary direction :: {label} ===")


def flow(a, b, tag):
    d = os.path.join(WORK, "measure_b", tag)
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error",
                    "-ss", f"{a:.3f}", "-t", f"{b-a:.3f}", "-i", video,
                    "-vf", f"fps={FPS},scale=640:-2", "-q:v", "3", "-y",
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
    return float(np.mean(dxs)), float(np.mean(mags))


def lab(d):
    return "weak" if abs(d) < WEAK else ("<- left" if d < 0 else "-> right")


conf = 0
for i, T in enumerate(cuts, 1):
    pa, pm = flow(T - GAP - WIN, T - GAP, f"pre{i}")
    na, nm = flow(T + GAP, T + GAP + WIN, f"post{i}")
    l1, l2 = lab(pa), lab(na)
    bad = (l1 != l2) and (l1 != "weak") and (l2 != "weak")
    if bad:
        conf += 1
    print(f"  cut{i} @{T:5.1f}s  pre dx={pa:6.2f} ({l1:<8}) "
          f"post dx={na:6.2f} ({l2:<8})  {'!! OPPOSITE !!' if bad else 'OK'}"
          f"   [mag {pm:.2f} -> {nm:.2f}]")
print(f"-> boundary direction conflicts: {conf}/{len(cuts)}")
