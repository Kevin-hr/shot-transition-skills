# 测试结果 — transition-matching-dual-dimension

> 测试模式: **Fallback 主流程自测** (无独立 sub-agent 盲测)
> 可信度: 中 (低于独立盲测)
> 测试时间: 2026-09-20

---

## 通过率: 8/8 (100%)

| ID | 类型 | 预期 | 实际 | 结果 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 触发：方向不匹配 | description含"为什么速度差不多还是跳"→触发 | ✅ |
| should-trigger-02 | should_trigger | 触发：速度不匹配 | description含"速度匹配""两个镜头怎么接更顺"→触发 | ✅ |
| should-trigger-03 | should_trigger | 触发：方向相反 | description含"运动方向不一致"+"为什么速度差不多还是跳"→触发 | ✅ |
| should-trigger-04 | should_trigger | 触发：英文关键词 | description含"speed matching""direction matching"→触发 | ✅ |
| should-not-trigger-01 | should_not_trigger | 不触发（应触发shot-composition-spatial-rules） | 提示含"机位角度差""越轴"→匹配空间规则→不触发 | ✅ |
| should-not-trigger-02 | should_not_trigger | 不触发（应触发shot-duration-decision） | 提示含"该留几秒""信息量"→匹配时长决策→不触发 | ✅ |
| edge-01 | edge_case | 触发：运动类型不同 | description含"两个镜头怎么接更顺"→触发并分析方向维度 | ✅ |
| edge-02 | edge_case | 不触发（跳切场景） | description排除"刻意制造不匹配效果的跳切"→不触发 | ✅ |

---

## 分析

### 优势
- description 中"速度匹配""方向匹配"中英双写，覆盖面好
- "不适用于空间规则未检查的场景"明确了前置依赖

### 潜在风险
- edge-01（产品旋转vs水平滑动）的运动类型差异在 description 中未明确区分，依赖 agent 的推理能力
- 速度匹配的"一致"是定性判断，缺乏量化标准

### 建议
- 无需修改
