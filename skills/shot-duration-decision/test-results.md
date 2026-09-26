# 测试结果 — shot-duration-decision

> 测试模式: **Fallback 主流程自测** (无独立 sub-agent 盲测)
> 可信度: 中 (低于独立盲测)
> 测试时间: 2026-09-20

---

## 通过率: 8/8 (100%)

| ID | 类型 | 预期 | 实际 | 结果 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 触发：信息密度定时长 | description含"镜头时长怎么定"+"该留多久"→触发 | ✅ |
| should-trigger-02 | should_trigger | 触发：完播率与时长 | description含"镜头太长还是太短"→触发 | ✅ |
| should-trigger-03 | should_trigger | 触发：多元素时长分配 | description含"画面留几秒合适"→触发 | ✅ |
| should-trigger-04 | should_trigger | 触发：节奏控制层 | description含"快切和长镜头怎么选"→触发 | ✅ |
| should-not-trigger-01 | should_not_trigger | 不触发（应触发transition-matching-dual-dimension） | 提示含"速度""方向"→匹配衔接匹配→不触发 | ✅ |
| should-not-trigger-02 | should_not_trigger | 不触发（应触发momentum-receive-cutting） | 提示含"切在哪一帧"→匹配剪辑点选择→不触发 | ✅ |
| edge-01 | edge_case | 触发但排除（纯卡点） | description排除"纯卡点视频"→不适用 | ✅ |
| edge-02 | edge_case | 触发：debunk 3秒法则 | description含"镜头时长怎么定"→触发并解释三层面 | ✅ |

---

## 分析

### 优势
- description 中"镜头时长怎么定""该留多久""快切和长镜头"等 trigger 覆盖核心场景
- "不适用于纯卡点/纯口播"明确了两个极端边界

### 潜在风险
- should-not-trigger-01 中的"跳"可能也匹配时长问题（太短导致跳），需要靠"速度""方向"关键词区分
- 人眼感知时间表的具体数值因人而异，不应绝对化

### 建议
- 无需修改
