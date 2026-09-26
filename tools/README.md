# 工具集 (`tools/`)

这些脚本不是"演示代码"，而是本项目真实剪辑里**实际跑过、并据以下结论**的验收工具。
它们回答的是同一个问题：**成片到底达没达标？**（而不是"源素材看起来如何"）

> **铁律**：结论必须来自最终产物。这些工具全部直接读**成片文件**（或成片的低分辨率代理），
> 不读源素材取样窗口。详见根目录 [CONTRIBUTING.md](../CONTRIBUTING.md)。

---

## 依赖

| 依赖 | 说明 |
|---|---|
| FFmpeg / ffprobe | 需在 `PATH` 中；或用环境变量 `FFMPEG` / `FFPROBE` 指定完整路径 |
| Python 3 | `numpy`、`opencv-python`（`pip install numpy opencv-python`） |

环境变量：

| 变量 | 作用 | 默认 |
|---|---|---|
| `FFMPEG` | ffmpeg 可执行文件路径 | 从 `PATH` 查找 |
| `FFPROBE` | ffprobe 可执行文件路径 | 从 `PATH` 查找 |
| `STS_WORK` | 中间产物（抽帧、profile、音频 raw）的工作目录 | 系统临时目录下的 `sts-work` |

所有脚本的"镜头时长"参数默认值为 `7,4,3,3,3,6,7`（共 33s）。
换素材时把它改成你自己的时长序列即可。

---

## 一、选镜阶段（源片 → 选镜方案）

| 脚本 | 用途 | 调用 |
|---|---|---|
| `scan_profile.py` | 全片 6fps 光流扫描，产出逐帧 `dx`/`mag` 时间序列 | `python scan_profile.py <source> [fps]` |
| `select_shots.py` | 在硬约束（速度差≤R、边界方向不相反、源间隔≥G、mag≤上限）下用 DP 选镜 | `python select_shots.py [durations] [src_end] [edge_w]` |

`select_shots.py` 的输出 `selection_w<edge_w>.json` 给出每个镜头的 `src_start` / `dur` /
是否 `hflip`，可直接喂给 `render_hardcut.ps1` 的 `-Starts` 与 `-Durations`。

> **量法必须一致**：`scan_profile.py`、`select_shots.py`、`measure_boundary.py` 三者的
> 采样帧率与裁剪窗口是**刻意对齐**的（`fps=6` → `scale=640` → Farneback → 中心裁剪中位数），
> 否则"选镜时的预测值"和"成片的实测值"不是同一把尺子。改一处就要改三处。

## 二、渲染

| 脚本 | 用途 | 调用 |
|---|---|---|
| `render_hardcut.ps1` | 硬切拼接渲染：`concat` 无 xfade、帧/样本精确截断、切点两侧 8ms 音频淡变 | 见下 |

```powershell
.\render_hardcut.ps1 -Source <src> -Out <out.mp4> `
                     -Starts 3.0,67.0,102.5,125.5,148.5,175.0,216.5 `
                     -Durations 7,4,3,3,3,6,7
```

`-Durations` 驱动一切：总时长、每段的 `trim=end_frame` / `atrim=end_sample` 计数、淡变偏移。
默认按 HDR/HLG 规格输出；SDR 交付传空串关闭色彩标签，例如
`-ColorPrimaries "" -ColorTrc "" -ColorSpace "" -ColorRange ""`。

> **4K 渲染很贵**：先渲 640px 代理跑完整验收，通过后再付 4K 的渲染成本。
> 代理与 4K 的实测结论在本项目里高度一致。

## 三、成片验收（成片 → 结论）

| 脚本 | 验的是什么 | 调用 |
|---|---|---|
| `measure_cut.py` | 逐镜运动速度（成片实测速度差是否 ≤30%） | `python measure_cut.py <video> [label] [durations]` |
| `measure_boundary.py` | **剪辑点两侧**的运动方向（是否越轴/方向冲突） | `python measure_boundary.py <video> [label] [durations]` |
| `cut_profile.py` | 每个接缝是硬切还是叠化 | `python cut_profile.py <video> [durations]` |
| `cut_diff.py` | 跳切风险（切点两侧画面是否"差得不够"） | `python cut_diff.py <video> [durations]` |
| `audio_cut_check.py` | 切点音频咔哒声（波形阶跃 vs 局部 p99.9） | `python audio_cut_check.py <video> [durations]` |
| `verify_delivery.py` | 规格总检：时长/帧数、色彩标签 vs 源片、黑帧/冻结/静音、音视频流等长 | `python verify_delivery.py <final> [source] [durations] [fps]` |

### 判读标准（本仓库采用的阈值）

| 指标 | 达标 |
|---|---|
| 相邻镜速度差 | ≤ 30% |
| 剪辑点两侧方向 | 不相反（`|dx| ≤ 0.8` 视为无明确方向，不算冲突） |
| 接缝形态 | 硬切：变化集中在 1 个帧对（约 1/帧率，如 60fps 约 16.7ms） |
| 跳切差异 | 切点两侧画面平均绝对差 ≥ ~15（越高越"像新镜头"） |
| 音频咔哒声 | 切点跳变 ≤ 局部 p99.9 |
| 黑帧 / 冻结帧 / 静音 | 0 段 |

---

## 一次完整的验收串

```bash
python scan_profile.py  "<source.mov>"
python select_shots.py                       # 产出 selection_w3.0.json
# 渲染代理 → 4K（render_hardcut.ps1）
python measure_cut.py       "<final.mp4>"
python measure_boundary.py  "<final.mp4>"
python cut_profile.py       "<final.mp4>"
python cut_diff.py          "<final.mp4>"
python audio_cut_check.py   "<final.mp4>"
python verify_delivery.py   "<final.mp4>" "<source.mov>"
```

跑完后把每个脚本的结论与 [案例 01 的决策报告](../cases/01-shot-transition-17s/decision-report.md)
里的实测表对照，看阈值判读是否符合预期。