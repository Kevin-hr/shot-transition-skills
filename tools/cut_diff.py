"""Jump-cut risk at each cut: how different are the frames on either side?

Too similar (<~15 mean abs diff on the 640px frame) reads as a jump cut -- the
viewer sees a jump in the same framing rather than a new shot. Also verifies the
join is a single hard step, not a dissolve ramp.

usage: python cut_diff.py <video> [durations]

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
os.makedirs(os.path.join(WORK, "cutdiff"), exist_ok=True)


def grab(t, out):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-ss", f"{t:.4f}",
                    "-i", video, "-frames:v", "1", "-vf", "scale=640:-2",
                    "-q:v", "2", "-y", out], check=True, capture_output=True)
    return cv2.imread(out, cv2.IMREAD_GRAYSCALE)


cuts = []
t = 0.0
for d in DURS[:-1]:
    t += d
    cuts.append(t)

print(f"=== cut-point difference :: {os.path.basename(video)} ===")
for i, T in enumerate(cuts, 1):
    pre = grab(T - 0.05, os.path.join(WORK, "cutdiff", f"pre{i}.jpg"))
    post = grab(T + 0.05, os.path.join(WORK, "cutdiff", f"post{i}.jpg"))
    d = float(np.mean(np.abs(pre.astype(np.float32) - post.astype(np.float32))))
    lvl = "too similar (jump-cut risk)" if d < 15 else ("medium" if d < 35 else "clearly different")
    print(f"  cut{i} @{T:5.1f}s  diff={d:6.2f}  -> {lvl}")

# dissolve probe: if there were a crossfade there would be intermediate blends,
# so consecutive frames would differ only slightly for ~0.5s around the cut.
print("\ndissolve probe (mean |frame-to-frame| in a 0.3s window around each cut):")
for i, T in enumerate(cuts, 1):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error",
                    "-ss", f"{T-0.15:.4f}", "-t", "0.3", "-i", video,
                    "-vf", "fps=60,scale=640:-2", "-q:v", "2", "-y",
                    os.path.join(WORK, "cutdiff", f"w{i}_%03d.jpg")],
                   check=True, capture_output=True)
    fs = sorted(f for f in os.listdir(os.path.join(WORK, "cutdiff"))
                if f.startswith(f"w{i}_"))
    prev = cv2.imread(os.path.join(WORK, "cutdiff", fs[0]), cv2.IMREAD_GRAYSCALE)
    diffs = []
    for f in fs[1:]:
        cur = cv2.imread(os.path.join(WORK, "cutdiff", f), cv2.IMREAD_GRAYSCALE)
        diffs.append(float(np.mean(np.abs(cur.astype(np.float32) - prev.astype(np.float32)))))
        prev = cur
    diffs = np.array(diffs)
    # a hard cut = one big spike, everything else small
    spike = diffs.max()
    others = np.sort(diffs)[:-1]
    ratio = spike / max(others.mean(), 1e-6)
    print(f"  cut{i} @{T:5.1f}s  spike={spike:6.2f}  mean(other)={others.mean():5.2f}  "
          f"ratio={ratio:5.1f}  {'HARD CUT' if ratio > 4 else 'smooth ramp (dissolve?)'}")
