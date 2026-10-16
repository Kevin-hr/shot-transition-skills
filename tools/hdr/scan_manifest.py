# -*- coding: utf-8 -*-
"""
scan_manifest.py — 素材库一次性盘点（《她的一天》HDR 流水线 · 第 1 步）

对素材目录里的每个 mp4/mov，用 ffprobe 探测：
  rid, file, width, height, rotation, duration, size,
  pix_fmt, transfer, primaries, is_hlg
并输出一份 manifest.csv，供 contact_sheets.py / build_hlg_films.py 读取。

为什么要先盘点：
  - 决定方向处理模式（auto / crop / port），必须读 rotation + 编码宽高，不能只看一帧；
  - 判定真 HDR：color_transfer == arib-std-b67（HLG），不能把 SDR 旅行批当 HDR 用；
  - 统计时长（<2s 的片段先剔除），避免后期才发现素材不可用。

用法：
  set HDR_LIBRARY=D:\\my_library        # 库根目录（含 edits/）
  python scan_manifest.py               # 输出到 %HDR_LIBRARY%\\scan\\manifest.csv
  python scan_manifest.py --src D:\\src --out D:\\scan\\manifest.csv

预期目录：
  <library>/edits/R###_*.mp4|.mov       # 源素材，文件名以 R 三位编号开头
"""
import argparse
import csv
import json
import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


def probe(path: Path):
    """返回 (rid,file,w,h,rotation,duration,size,pix_fmt,transfer,primaries,is_hlg)。"""
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
            capture_output=True, text=True, timeout=60,
        )
        d = json.loads(r.stdout)
        v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
        if not v:
            return None

        rotation = 0
        tags = v.get("tags", {}) or {}
        rotation = int(float(tags.get("rotate", 0) or 0))
        for sd in v.get("side_data_list", []) or []:
            if "rotation" in sd:
                rotation = int(sd["rotation"])

        w = int(v.get("width", 0))
        h = int(v.get("height", 0))
        duration = float(v.get("duration") or d.get("format", {}).get("duration") or 0)
        pix_fmt = v.get("pix_fmt", "")
        transfer = v.get("color_transfer", "")
        primaries = v.get("color_primaries", "")
        is_hlg = "1" if transfer == "arib-std-b67" else "0"

        m = re.match(r"(R\d{3})", path.stem)
        rid = m.group(1) if m else path.stem[:4]
        return (rid, path.name, w, h, rotation, round(duration, 3), path.stat().st_size,
                pix_fmt, transfer, primaries, is_hlg)
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    library = Path(os.environ.get("HDR_LIBRARY", str(Path.cwd() / "library")))
    ap.add_argument("--src", type=Path, default=library / "edits", help="源素材目录")
    ap.add_argument("--out", type=Path, default=library / "scan" / "manifest.csv", help="输出 CSV")
    ap.add_argument("--workers", type=int, default=12)
    args = ap.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in args.src.iterdir() if p.suffix.lower() in (".mp4", ".mov"))
    print(f"probing {len(files)} files in {args.src} ...", flush=True)

    rows = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(probe, p): p for p in files}
        for i, f in enumerate(as_completed(futs)):
            r = f.result()
            if r:
                rows.append(r)
            if (i + 1) % 100 == 0:
                print(f"  {i + 1}/{len(files)}", flush=True)

    rows.sort(key=lambda x: int(x[0][1:]))
    with open(args.out, "w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["rid", "file", "width", "height", "rotation", "duration",
                    "size", "pix_fmt", "transfer", "primaries", "is_hlg"])
        w.writerows(rows)

    hlg = [r for r in rows if r[10] == "1"]
    short = [r for r in rows if r[5] < 2]
    durs = [r[5] for r in rows]
    print(f"saved {len(rows)} rows -> {args.out}")
    print(f"HLG: {len(hlg)}   SDR: {len(rows) - len(hlg)}   <2s clips: {len(short)}")
    if durs:
        print(f"duration min/max: {min(durs):.1f}/{max(durs):.1f}s")


if __name__ == "__main__":
    main()
