# HDR(HLG) 竖屏故事线流水线（`tools/hdr/`）

在消费级 NVIDIA GPU（RTX 5060Ti 实测）上，把一批手机拍的**原生 HLG** 家庭素材，
批量剪成多条 **4K 竖屏 HDR 短片**，并保证方向、色彩、时间线、音量全部可验收。

这是 [`案例 02 · 她的一天 五部 HDR 故事线`](../../cases/02-her-day-hdr/README.md)
实际跑通的工具，属于 [`../`](../README.md) 选镜/渲染/验收工具链在 **HDR 竖屏叙事**
场景下的扩展。

> 铁律不变：**任何“达标”结论都要在导出的成片上重算一遍。** 这套工具的每一步
> 都用 ffprobe 回读产物，而不是只看源素材或命令行是否退出码为 0。

---

## 为什么单独做一套

案例 01 的工具链面向“单条横版片 + 光流定量验收”。本场景的新问题是：

1. **真 HDR**：素材是手机 HLG（`arib-std-b67` / bt2020 / 10-bit），不是 SDR；
2. **竖屏**：目标 9:16（2160×3840），而源素材混着横屏、竖屏、带旋转标签的竖屏；
3. **批量故事线**：一次产出 5 条不同叙事，每条 4 个章节 + 标题卡 + 结尾卡；
4. **硬件编码**：4K 10-bit 软编（libx265）只有约 0.45fps，必须走 NVENC。

---

## 三步流水线

```
edits/R###_*.mp4|.mov
        │  ① scan_manifest.py    盘点（时长/分辨率/旋转/色彩/HLG）
        ▼
scan/manifest.csv
        │  ② contact_sheets.py   overview 全库抽帧 + deep 入选镜头 4 帧
        ▼
人工确认内容/方向/剔除脏素材 → 写入 storylines.py
        │  ③ build_hlg_films.py  逐段渲染 + 标题卡 + concat 重编码
        ▼
scan/output/<key>_HDR.mp4   （2160×3840 / HEVC main10 / HLG / 30fps）
```

```bash
# 依赖：FFmpeg（含 zscale、hevc_nvenc）、NVIDIA GPU、Pillow、Python 3
set HDR_LIBRARY=D:\my_library            # 库根（其下有 edits/ 与 scan/）

python scan_manifest.py                  # ① 出 manifest.csv
python contact_sheets.py overview        # ② 全库抽帧盘点
python contact_sheets.py deep            # ② 入选镜头 4 帧复核
# 把选定的 (rid, 时长, 取点) 写进 storylines.py
python build_hlg_films.py                # ③ 渲染全部
python build_hlg_films.py 02_school_day  # ③ 只渲染一条
```

---

## 关键工程经验（每条都踩过坑）

### 1. 方向必须三模式，不能只看单帧

单帧 JPG 不带旋转标签，按缩略图判断方向会被骗。判据必须读 manifest 的
`rotation` + **编码**宽高，再以“视频段编码后抽帧”复核：

| 模式 | 判据 | 处理 |
|---|---|---|
| `auto` | `rotation != 0` | 让 ffmpeg 自动旋转（烘焙像素 + 清标签），只 `scale` |
| `crop` | `rotation==0` 且编码 `w>h`（真横屏） | `-noautorotate` + 中心 9:16 裁切（3840×2160 取中心 1215×2160） |
| `port` | `rotation==0` 且编码 `h>=w`（真竖屏） | 不旋转，直接 cover 缩放 |

中心裁切（偶数对齐）：

```
crop=trunc(ih*9/16/2)*2:ih:(iw-trunc(ih*9/16/2)*2)/2:0
```

### 2. SDR 标题卡转 HLG：先 rgb24，zscale 单步写全参数

PIL 画的黑底白字卡是 sRGB，必须显式转 HLG 才能与 HLG 段统一。滤镜链：

```
scale=W:H:flags=lanczos,format=rgb24,format=gbrpf32le,
zscale=primariesin=bt709:transferin=iec61966-2-1:primaries=bt2020:
      transfer=arib-std-b67:matrix=bt2020nc:npl=100:rangein=pc:range=tv,
format=p010le
```

三个坑：必须先显式 `rgb24`；zscale 要**在一个滤镜里同时写全输入/输出参数**；
NVENC 只收 `p010le`。

### 3. 卡片必须带静音音轨

标题卡用 `anullsrc` 补一条静音 AAC，否则 concat 时整段音频流丢失。

### 4. concat 必须重编码，不能 `-c copy`

段参数一致时看似可以 copy，但 concat demuxer + `-c copy` 会在接缝产生
`non-monotonically increasing DTS`，严格 muxer / 抖音会挑。最终对 concat
**重编码**（同参数 NVENC + `-r 30 -vsync cfr`）后，全片 decode 错误为 0。

### 5. 音量用线性系数，不用负数 dB

`-af volume=-6dB` 这种负数写法会被吞，改用线性 `volume=0.72`（约 -2.8dB），
再叠加 `afade` 进出。源片电平偏高的个别镜头（如烛光段）单独 `volume=0.5`。

### 6. 软编不可行，NVENC 快约 44 倍

4K 10-bit libx265 约 **0.45fps**，不可用；`hevc_nvenc -profile:v main10`
（RTX 5060Ti）实用帧率约为其 44 倍。

### 7. 只用原生 HLG，不混入 SDR

972 条素材中真 HLG 256 条（`is_hlg=1`）。SDR 旅行批转 HLG 后画面发平，
不纳入；宁可只在 HLG 池（R071–R299 段）里选镜头。

---

## 输出规格（5 条一致）

| 项 | 值 |
|---|---|
| 分辨率 | 2160×3840（竖 9:16，无黑边/无变形） |
| 编码 | HEVC `hevc_nvenc`，`-profile:v main10`，`-rc vbr -cq 21 -b:v 0` |
| 位深/格式 | 10-bit，`yuv420p10le` |
| HDR | `bt2020` 色域 / `arib-std-b67`（HLG）/ `bt2020nc` / `range=tv` |
| 帧率 | 30fps CFR |
| 音频 | AAC 160kbps / 48kHz / 立体声 |
| 时长 | 约 84–99s（含标题卡/章节卡/结尾卡） |

逐段编码参数（`build_hlg_films.py` 中为单一事实源）：

```
-c:v hevc_nvenc -preset p5 -tune hq -profile:v main10 -rc vbr -cq 21 -b:v 0
-color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc -color_range tv
```

---

## 文件

| 文件 | 说明 |
|---|---|
| `scan_manifest.py` | 素材库盘点 → `manifest.csv`（含 `is_hlg` 判定） |
| `manifest.sample.csv` | manifest 字段样例（横屏/竖屏/旋转/SDR/1080p/超短片段各一） |
| `contact_sheets.py` | `overview` 全库抽帧 + `deep` 入选镜头 4 帧复核 |
| `storylines.py` | 5 条故事线的数据配置（`rid / 时长 / 取点 / 章节`），带自检 |
| `build_hlg_films.py` | HLG 渲染器（三模式方向 + 卡片转 HLG + concat 重编码） |
| `build_sdr_day.py` | 张艺谋风格 SDR 基线（auto/crop/hold 三模式的最早实现，作对照） |

> 素材与成片均为本人自拍自有家庭影像，4K 原片与成片**不随仓库分发**；
> 这里只提供可复现的脚本、数据配置与字段样例。
