"""Full-source 6fps optical-flow profile.

Metric is deliberately identical to the acceptance-side measurement
(fps=6 -> scale=640 -> Farneback -> center-crop median dx / mag), so that a
per-segment mean computed here is comparable to what gets measured on the cut.

usage: python scan_profile.py <source> [fps]

  fps   采样帧率，默认 6（必须与 select_shots.py / measure_boundary.py 一致）

env:
  FFMPEG     ffmpeg 可执行文件路径；未设置时从 PATH 查找
  STS_WORK   工作目录；未设置时使用系统临时目录

outputs (into STS_WORK):
  profile_frames/f_*.jpg   采样帧
  profile_6fps.json        每帧的 t / dx / mag
"""
import glob
import json
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

SRC = sys.argv[1]
FPS = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
FRAMES = os.path.join(WORK, "profile_frames")
OUT = os.path.join(WORK, f"profile_{int(FPS) if FPS == int(FPS) else FPS}fps.json")

os.makedirs(FRAMES, exist_ok=True)
if not glob.glob(os.path.join(FRAMES, "f_*.jpg")):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-i", SRC,
                    "-an", "-sn", "-dn", "-vf", f"fps={FPS},scale=640:-2",
                    "-q:v", "3", "-y", os.path.join(FRAMES, "f_%05d.jpg")],
                   check=True)

files = sorted(glob.glob(os.path.join(FRAMES, "f_*.jpg")))
prev = cv2.imread(files[0], cv2.IMREAD_GRAYSCALE)
rows = []
for idx, path in enumerate(files[1:], start=1):
    cur = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    flow = cv2.calcOpticalFlowFarneback(prev, cur, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    h, w = flow.shape[:2]
    c = flow[h // 5:h * 4 // 5, w // 5:w * 4 // 5]
    rows.append({
        "t": round(idx / FPS, 4),
        "dx": round(float(np.median(c[..., 0])), 4),
        "mag": round(float(np.median(np.sqrt((c ** 2).sum(axis=2)))), 4),
    })
    prev = cur

json.dump(rows, open(OUT, "w"), ensure_ascii=False)
mags = np.array([r["mag"] for r in rows])
dxs = np.array([r["dx"] for r in rows])
print("pairs:", len(rows), "duration~", rows[-1]["t"])
print("mag  min/p25/med/p75/p90/max:",
      round(mags.min(), 2), round(np.percentile(mags, 25), 2),
      round(np.median(mags), 2), round(np.percentile(mags, 75), 2),
      round(np.percentile(mags, 90), 2), round(mags.max(), 2))
print("dx   min/p25/med/p75/max:",
      round(dxs.min(), 2), round(np.percentile(dxs, 25), 2),
      round(np.median(dxs), 2), round(np.percentile(dxs, 75), 2),
      round(dxs.max(), 2))
print("saved ->", OUT)