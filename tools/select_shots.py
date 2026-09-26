"""Search a 7-shot selection that satisfies the hard constraints on the FINAL cut.

Hard constraints
  1. adjacent per-segment mean |flow| relative difference <= R   (R<=0.30, aim lower)
  2. boundary direction of adjacent shots must not be opposite (flip allowed)
  3. source separation between consecutive picks >= G seconds
  4. segment mean mag <= MAG_CAP (avoid whip-pan / frantic picks)

Objective: minimise R, then maximise G, then minimise hflips, then maximise the
appearance difference between neighbouring picks (visual-variation-judgment).

usage: python select_shots.py [durations] [src_end] [edge_w]

  durations  镜头时长（秒，逗号分隔），默认 "7,4,3,3,3,6,7"
  src_end    可用源片时长上界（秒），默认 224.0
  edge_w     画面差异项的权重，默认 3.0

env:
  STS_WORK   工作目录（须含 scan_profile.py 产出的 profile_6fps.json 与 profile_frames/）；
             未设置时使用系统临时目录

input  (from STS_WORK): profile_6fps.json, profile_frames/f_*.jpg
output (to   STS_WORK): selection_w<edge_w>.json
"""
import glob
import json
import os
import sys
import tempfile

import cv2
import numpy as np

WORK = os.environ.get("STS_WORK") or os.path.join(tempfile.gettempdir(), "sts-work")
FPS = 6.0
PROF = os.path.join(WORK, "profile_6fps.json")
FRAMES = os.path.join(WORK, "profile_frames")

DURS = [float(x) for x in
        (sys.argv[1] if len(sys.argv) > 1 else "7,4,3,3,3,6,7").split(",")]
TOTAL = sum(DURS)
SRC_END = float(sys.argv[2]) if len(sys.argv) > 2 else 224.0
EDGE_W = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0

STEP = 0.5
WEAK = 0.8
EDGE = 0.8
MAG_CAP = 12.0

if not os.path.exists(PROF):
    sys.exit(f"missing {PROF}\n先运行: python scan_profile.py <source>")

rows = json.load(open(PROF))
T = np.array([r["t"] for r in rows])
DX = np.array([r["dx"] for r in rows])
MG = np.array([r["mag"] for r in rows])


def win_mean(arr, a, b):
    lo = np.searchsorted(T, a, side="right")
    hi = np.searchsorted(T, b, side="right")
    if hi <= lo:
        return None
    return float(arr[lo:hi].mean())


_FEAT = None


def feats():
    """Per-profile-frame features: 32x32 gray thumbnail + edge-density scalar.

    Edge density (mean |Sobel| on the 640px frame) is a crude shot-size proxy:
    a wide shot full of small people carries far more edge energy than a close
    shot with a few large blobs.
    """
    global _FEAT
    if _FEAT is None:
        files = sorted(glob.glob(os.path.join(FRAMES, "f_*.jpg")))
        th, ed = [], []
        for p in files:
            g = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
            th.append(cv2.resize(g, (32, 32), interpolation=cv2.INTER_AREA))
            gx = cv2.Sobel(g, cv2.CV_32F, 1, 0, ksize=3)
            gy = cv2.Sobel(g, cv2.CV_32F, 0, 1, ksize=3)
            ed.append((float(np.mean(np.abs(gx))) + float(np.mean(np.abs(gy)))) / 2.0)
        _FEAT = (np.stack(th).astype(np.float32), np.array(ed, np.float32))
    return _FEAT


def feat_at(t):
    th, ed = feats()
    k = max(0, min(len(th) - 1, int(round(t * FPS))))
    return th[k], float(ed[k])


def candidates(i):
    d = DURS[i]
    out = []
    s = 1.0
    while s + d <= SRC_END:
        mag = win_mean(MG, s, s + d)
        if mag is not None and mag <= MAG_CAP:
            th, ed = feat_at(s + d / 2.0)
            out.append({
                "s": round(s, 2), "d": d, "mag": mag,
                "dxL": win_mean(DX, s, s + EDGE),
                "dxR": win_mean(DX, s + d - EDGE, s + d),
                "th": th, "ed": ed,
            })
        s += STEP
    return out


CANDS = [candidates(i) for i in range(len(DURS))]
print("candidates per shot:", [len(c) for c in CANDS])


def conflict(a, b):
    """a,b = signed boundary dx (already flipped). True if clearly opposite."""
    if abs(a) <= WEAK or abs(b) <= WEAK:
        return False
    return (a > 0) != (b > 0)


def solve(R, G):
    """DP over state (candidate, flip). Returns (flips, picks) or None.

    The flip state of a segment must be part of the state: it is needed both to
    test the boundary against the next segment and to charge its penalty.
    """
    INF = float("inf")
    layers = []
    for i, cand in enumerate(CANDS):
        n = len(cand)
        cost = [[INF, INF] for _ in range(n)]
        back = [[None, None] for _ in range(n)]
        if i == 0:
            for j in range(n):
                cost[j][0] = 0.0
                cost[j][1] = 100.0
        else:
            prev_cand, prev_cost, _ = layers[-1]
            for j, c in enumerate(cand):
                for fb in (0, 1):
                    rb = -c["dxL"] if fb else c["dxL"]
                    best, bk, bfa = INF, None, None
                    for k, p in enumerate(prev_cand):
                        if c["s"] < p["s"] + p["d"] + G:
                            continue
                        ratio = abs(c["mag"] - p["mag"]) / max(c["mag"], p["mag"])
                        if ratio > R:
                            continue
                        for fa in (0, 1):
                            if prev_cost[k][fa] == INF:
                                continue
                            ra = -p["dxR"] if fa else p["dxR"]
                            if conflict(ra, rb):
                                continue
                            pen = (1000.0 * fb
                                   - float(np.mean(np.abs(c["th"] - p["th"])))
                                   - EDGE_W * abs(c["ed"] - p["ed"]))
                            tot = prev_cost[k][fa] + pen
                            if tot < best:
                                best, bk, bfa = tot, k, fa
                    if best < INF:
                        cost[j][fb] = best
                        back[j][fb] = (bk, bfa)
        layers.append((cand, cost, back))

    cand, cost, back = layers[-1]
    flat = [(cost[j][f], j, f) for j in range(len(cand)) for f in (0, 1)]
    tot, cur, curf = min(flat)
    if tot == INF:
        return None
    picks = [None] * len(DURS)
    flips = [0] * len(DURS)
    for i in range(len(DURS) - 1, -1, -1):
        picks[i] = layers[i][0][cur]
        flips[i] = curf
        if i > 0:
            cur, curf = layers[i][2][cur][curf]
    return flips, picks


def report(R, G, flips, picks):
    print(f"\n=== R={R:.2f}  G={G}s  flips={sum(flips)} ===")
    print(f"{'#':>2} {'src_s':>7} {'dur':>4} {'mag':>6} {'dxL':>7} {'dxR':>7} "
          f"{'flip':>4}  ratio_to_next")
    for i, (c, f) in enumerate(zip(picks, flips)):
        nxt = ""
        if i + 1 < len(picks):
            r = abs(picks[i + 1]["mag"] - c["mag"]) / max(picks[i + 1]["mag"], c["mag"])
            div = float(np.mean(np.abs(picks[i + 1]["th"] - c["th"])))
            nxt = (f"{r*100:5.1f}%   div={div:5.1f} "
                   f"ed={c['ed']:5.1f}->{picks[i+1]['ed']:5.1f}")
        print(f"{i+1:>2} {c['s']:>7.1f} {c['d']:>4} {c['mag']:>6.2f} "
              f"{c['dxL']:>7.2f} {c['dxR']:>7.2f} {f:>4}  {nxt}")
    print("span:", round(picks[0]["s"], 1), "->", round(picks[-1]["s"] + picks[-1]["d"], 1))
    print("total duration:", TOTAL)


def validate(flips, picks):
    """Independent re-check of the reconstructed path (do not trust the DP)."""
    bad = []
    for i in range(len(picks) - 1):
        a, b = picks[i], picks[i + 1]
        if b["s"] < a["s"] + a["d"] + 5:
            bad.append(f"shot{i+1}->{i+2}: source overlap/gap too small")
        ratio = abs(b["mag"] - a["mag"]) / max(b["mag"], a["mag"])
        if ratio > 0.30:
            bad.append(f"shot{i+1}->{i+2}: speed {ratio*100:.1f}% > 30%")
        ra = -a["dxR"] if flips[i] else a["dxR"]
        rb = -b["dxL"] if flips[i + 1] else b["dxL"]
        if conflict(ra, rb):
            bad.append(f"shot{i+1}->{i+2}: direction conflict {ra:+.2f} vs {rb:+.2f}")
    if picks[0]["s"] < 0.5 or picks[-1]["s"] + picks[-1]["d"] > SRC_END + 0.01:
        bad.append("source bounds exceeded")
    return bad


best = None
for R in [0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22, 0.25, 0.28, 0.30]:
    for G in [20, 16, 12, 8, 5]:
        res = solve(R, G)
        if res:
            best = (R, G, res)
            break
    if best:
        break

if not best:
    print("NO FEASIBLE SOLUTION")
else:
    R, G, (flips, picks) = best
    report(R, G, flips, picks)
    problems = validate(flips, picks)
    print("\nVALIDATION:", "ALL PASS" if not problems else "")
    for p in problems:
        print("  !!", p)
    th = [c["th"] for c in picks]
    ed = [c["ed"] for c in picks]
    pair = [float(np.mean(np.abs(th[i] - th[j])))
            for i in range(len(th)) for j in range(i + 1, len(th))]
    ded = sum(abs(ed[i + 1] - ed[i]) for i in range(len(ed) - 1))
    ratios = [abs(picks[i + 1]["mag"] - picks[i]["mag"])
              / max(picks[i + 1]["mag"], picks[i]["mag"])
              for i in range(len(picks) - 1)]
    print(f"METRICS edge_w={EDGE_W} maxSpd={max(ratios)*100:.1f}% "
          f"minPairSim={min(pair):.1f} sumdEd={ded:.1f} "
          f"edRange={max(ed)-min(ed):.1f}")
    json.dump({"R": R, "G": G, "edge_w": EDGE_W, "flips": flips,
               "max_speed_ratio": round(max(ratios), 4),
               "min_pair_sim": round(min(pair), 2),
               "sum_delta_edge": round(ded, 2),
               "picks": [{"src_start": c["s"], "dur": c["d"],
                          "pred_mag": round(c["mag"], 3),
                          "pred_dxL": round(c["dxL"], 3),
                          "pred_dxR": round(c["dxR"], 3),
                          "edge": round(c["ed"], 2)} for c in picks]},
              open(os.path.join(WORK, f"selection_w{EDGE_W}.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"\nsaved -> selection_w{EDGE_W}.json")