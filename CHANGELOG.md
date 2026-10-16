# 更新日志

本文件记录本项目的所有重要变更，格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [1.1.0] — 2026-10-16

新增案例 02 与 HDR(HLG) 竖屏故事线流水线。

### 新增

- **案例 02 `02-her-day-hdr`**：《她的一天》5 部不同故事线的 4K 竖屏**真 HDR（HLG）**短片
  （上学日 / 追风 / 牵着你的手 / 童话 / 去看世界，84–99s），张艺谋风格；
  114 个去重镜头、与第一版 SDR 零素材重复，全片 decode 错误 0。
  - 含选材剔除清单（画中脸 / 文字模板 / 屏幕录制 / 成人主体等）、逐项验收数据与
    墨菲定律对抗性审查（主动披露未覆盖项）。
- **HDR 工具集 `tools/hdr/`**（在消费级 NVIDIA GPU 上实测）：
  - `scan_manifest.py` — 素材库盘点（时长/分辨率/旋转/位深/色彩/HLG 判定）→ `manifest.csv`
  - `contact_sheets.py` — 全库抽帧（overview）与入选镜头 4 帧复核（deep）
  - `storylines.py` — 5 条故事线数据配置（rid / 时长 / 取点 / 章节），自带去重自检
  - `build_hlg_films.py` — HLG 渲染器：方向三模式（auto/crop/port）+ 标题卡 zscale 转 HLG
    + `hevc_nvenc main10` + concat 重编码
  - `build_sdr_day.py` — 张艺谋风格 SDR 基线（auto/crop/hold 三模式的最早实现，作对照）
  - `manifest.sample.csv` — manifest 字段样例
- **关键工程经验**（见 `tools/hdr/README.md`）：
  - 方向不能只看单帧，须读 `rotation` + 编码宽高，按 auto/crop/port 三模式处理；
  - SDR 标题卡须先 `rgb24` 再 `zscale` 单步写全 in/out 参数转 HLG，NVENC 收 `p010le`；
  - 标题卡必须补静音音轨；concat 必须重编码（`-c copy` 会产生 non-monotonic DTS）；
  - 音量用线性系数（`volume=0.72`），负数 dB 会被吞；
  - 4K 10-bit libx265 约 0.45fps 不可行，NVENC 快约 44 倍；
  - 只用原生 HLG 素材，不混 SDR 旅行批（转换后画面偏平）。

### 变更

- 更新根 `README.md`、`cases/README.md`、`tools/README.md`，加入案例 02 与 `tools/hdr/` 导航。

### 已知限制

- 案例 02 的 4K HDR 成片（单片 170–220MB）**不随仓库分发**，只提供脚本与数据配置。
- HDR 流水线依赖 NVIDIA GPU（NVENC）与带 `zscale` 的 FFmpeg；无 N 卡时需自行替换编码器。
- 案例 02 未做真机 HDR 手机播放与抖音上传后的平台显示验证，结论仅覆盖本地 ffprobe / 解码 / 抽帧。
- 案例 02 中 `R156` 为 1080p 源放大（2.8s），其余为 4K 原生 HLG。

---

## [1.0.0] — 2026-09-26

首次公开发布。

### 新增

- **6 个镜头组接技能**（`skills/`）：把一套公开分享的剪辑方法论结构化为可执行技能，
  每个技能含 `SKILL.md`（R-I-C-E 四段骨架）、测试用例与验证记录。
  - `shot-composition-spatial-rules` — 空间规则（30° / 180° 原则、越轴）
  - `visual-variation-judgment` — 视觉变量判断（动接动静接近）
  - `transition-matching-dual-dimension` — 转场匹配双维度（速度 + 方向）
  - `shot-duration-decision` — 镜头时长决策
  - `momentum-receive-cutting` — 出势接作（剪辑点选择）
  - `cut-trace-dual-strategy` — 剪辑痕迹双策略（弱化 vs 利用）
- **量化验收工具集**（`tools/`）：把“剪得顺不顺”变成可测量的数字——光流测方向与速度、
  剪辑点边界方向、硬切/叠化判定、音频切点爆音检测、音画同步互相关。
- **案例 01 `shot-transition-17s`**：17 秒横版成片的完整决策过程、审计报告与实测指标。
- **拉片教程**（`tutorial/`）：逐镜拉片 + 技能映射的可视化教程。
- 双许可：代码 [MIT](LICENSE) / 内容 [CC BY 4.0](LICENSE-CONTENT.md)，
  第三方引用状况见 [ATTRIBUTION.md](ATTRIBUTION.md)。

### 已知限制

- 案例 01 的 4K 原片体积过大，**不随仓库分发**，仓库内只保留 720p 展示小样与全部报告。
- `tools/` 中的脚本是在 Windows + PowerShell + FFmpeg 环境下开发的，其他平台需自行适配路径。

---

## 开源前的项目沿革（2026-09-20 ~ 2026-09-22）

以下为整理归档时保留的过程记录，非本仓库的版本发布。

### 2026-09-21 ~ 2026-09-22 — 案例 01 完成

- 用 6 个技能剪辑 7 镜头横版短片；审计发现 2 处违规（同场景方向未翻转、节奏单调）。
- 修复后交付 17 秒成片；4K 原片不随仓库分发，仓库内保留 720p 小样。

### 2026-09-20 — 6 个技能蒸馏完成

- 从原视频提炼出 6 个技能，每个技能经测试用例验证后安装使用。
