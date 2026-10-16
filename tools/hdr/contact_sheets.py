# -*- coding: utf-8 -*-
"""
contact_sheets.py — 素材内容人工复核（流水线 · 第 2 步）

方向/内容不能只看单帧缩略图（单帧 JPG 不带旋转标签，会误导），所以在选镜前
把每个候选片段抽帧、自动旋转、拼成 contact sheet，人工快速确认：
  内容是不是想要的、方向正不正、是不是后期二剪模板（画中脸/文字水印/屏幕录制）。

两种模式：
  overview   全库抽帧，每片 1 帧，48 格/张（6 列 x 8 行），用于大面盘点
  deep       对 storylines.py 里每个入选镜头抽 4 帧（15%/40%/65%/90%），
             逐片出图，确认最终取点、内容与方向

用法：
  set HDR_LIBRARY=D:\\my_library
  python contact_sheets.py overview
  python contact_sheets.py deep

输出在 <library>/scan/frames、<library>/scan/deep、<library>/scan/sheet_*.jpg。
依赖：FFmpeg、Pillow。
"""
import argparse
import csv
import math
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from storylines import FILMS

LIBRARY = Path(os.environ.get("HDR_LIBRARY", str(Path.cwd() / "library")))
EDITS = LIBRARY / "edits"
SCAN = LIBRARY / "scan"
FRAMES = SCAN / "frames"
DEEP = SCAN / "deep"


def find_font():
    for p in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf",
              r"/System/Library/Fonts/PingFang.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return p
    return None


FP = find_font()


def load_manifest():
    return {r["rid"]: r for r in csv.DictReader(open(SCAN / "manifest.csv", encoding="utf-8"))}


def overview():
    """全库 R071+ 抽 1 帧，自动旋转，48 格/张。"""
    FRAMES.mkdir(parents=True, exist_ok=True)
    rows = list(load_manifest().values())

    def num(rid):
        return int(rid[1:])

    # 与第一版 SDR 已用 RID 去重（按需修改为你自己的已用集合）
    used = set()
    cand = [r for r in rows if num(r["rid"]) >= 71 and r["rid"] not in used]
    cand = [r for r in cand if float(r["duration"]) >= 1.5]
    print(f"candidates: {len(cand)}", flush=True)

    CELL_W, CELL_H = 240, 426
    COLS, ROWS = 6, 8
    PER = COLS * ROWS

    def extract(r):
        rid = r["rid"]
        dur = float(r["duration"])
        out = FRAMES / f"{rid}.jpg"
        if out.exists():
            return rid
        t = min(2.5, dur * 0.35) if dur > 0 else 0.5
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(EDITS / r["file"]),
               "-frames:v", "1", "-vf",
               f"scale={CELL_W}:{CELL_H}:force_original_aspect_ratio=decrease,"
               f"pad={CELL_W}:{CELL_H}:(ow-iw)/2:(oh-ih)/2:black",
               "-q:v", "3", str(out)]
        subprocess.run(cmd, capture_output=True)
        return rid if out.exists() else None

    done = set()
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(extract, r): r for r in cand}
        for i, f in enumerate(as_completed(futs)):
            if f.result():
                done.add(f.result())
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(cand)}", flush=True)

    cand = [r for r in cand if r["rid"] in done]
    cand.sort(key=lambda r: num(r["rid"]))
    for s in range(math.ceil(len(cand) / PER)):
        batch = cand[s * PER:(s + 1) * PER]
        sheet = Image.new("RGB", (COLS * CELL_W, ROWS * (CELL_H + 26)), "black")
        d = ImageDraw.Draw(sheet)
        font = ImageFont.truetype(FP, 22) if FP else ImageFont.load_default()
        for i, r in enumerate(batch):
            cc, rr = i % COLS, i // COLS
            x, y = cc * CELL_W, rr * (CELL_H + 26)
            try:
                sheet.paste(Image.open(FRAMES / f"{r['rid']}.jpg").convert("RGB"), (x, y + 26))
            except Exception:
                pass
            d.text((x + 4, y + 2), f"{r['rid']} {float(r['duration']):.0f}s",
                   fill="yellow", font=font)
        out = SCAN / f"sheet_{s:02d}_{batch[0]['rid']}-{batch[-1]['rid']}.jpg"
        sheet.save(out, quality=88)
        print("sheet", out.name, f"({len(batch)} clips)", flush=True)


def deep():
    """对 storylines 入选镜头每个抽 4 帧，逐片出 contact sheet。"""
    DEEP.mkdir(parents=True, exist_ok=True)
    M = load_manifest()

    def src_of(rid):
        return EDITS / M[rid]["file"]

    def extract_one(rid, frac, tag):
        out = DEEP / f"{rid}_{tag}.jpg"
        dur = float(M[rid]["duration"])
        t = max(0.2, min(dur - 0.3, dur * frac))
        if out.exists():
            return out
        cmd = ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(src_of(rid)),
               "-frames:v", "1", "-vf", "scale=220:-2", "-q:v", "3", str(out)]
        subprocess.run(cmd, capture_output=True)
        return out

    jobs = []
    for film in FILMS:
        for _, clips in film["chapters"]:
            for rid, _, frac in clips:
                for f2, tag in [(0.15, "a"), (0.4, "b"), (0.65, "c"), (0.9, "d")]:
                    jobs.append((rid, f2, tag))
    jobs = sorted(set(jobs))
    print(f"extracting {len(jobs)} frames...", flush=True)
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(extract_one, *j): j for j in jobs}
        for i, f in enumerate(as_completed(futs)):
            f.result()
            if (i + 1) % 120 == 0:
                print(f"  {i + 1}/{len(jobs)}", flush=True)

    FW, FH = 150, 267
    PERPAGE = 13
    for film in FILMS:
        items = [(rid, ch) for ch, clips in film["chapters"] for rid, _, _ in clips]
        for pg in range(math.ceil(len(items) / PERPAGE)):
            sub = items[pg * PERPAGE:(pg + 1) * PERPAGE]
            sheet = Image.new("RGB", (4 * FW, len(sub) * (FH + 30)), (20, 20, 20))
            d = ImageDraw.Draw(sheet)
            font = ImageFont.truetype(FP, 18) if FP else ImageFont.load_default()
            for i, (rid, ch) in enumerate(sub):
                y = i * (FH + 30)
                d.text((4, y + 2), f"{rid} {float(M[rid]['duration']):.0f}s "
                                    f"r{M[rid]['rotation']} {ch}", fill="yellow", font=font)
                for j, tag in enumerate(["a", "b", "c", "d"]):
                    p = DEEP / f"{rid}_{tag}.jpg"
                    if p.exists():
                        try:
                            im = Image.open(p).convert("RGB")
                            im.thumbnail((FW, FH))
                            sheet.paste(im, (j * FW + (FW - im.width) // 2, y + 30))
                        except Exception:
                            pass
            out = SCAN / f"deep_{film['key']}_p{pg}.jpg"
            sheet.save(out, quality=88)
            print("saved", out.name, f"({len(sub)} clips)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["overview", "deep"])
    a = ap.parse_args()
    overview() if a.mode == "overview" else deep()
