# 测试结果 — shot-composition-spatial-rules

> 测试模式: **Fallback 主流程自测** (无独立 sub-agent 盲测)
> 可信度: 中 (低于独立盲测)
> 测试时间: 2026-09-20

---

## 通过率: 8/8 (100%)

| ID | 类型 | 预期 | 实际 | 结果 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 触发：30°原则 | description含"机位怎么放"+"为什么切镜头会跳"→触发 | ✅ |
| should-trigger-02 | should_trigger | 触发：180°/越轴 | description含"越轴是什么"+"180度原则"→触发 | ✅ |
| should-trigger-03 | should_trigger | 触发：拍摄前规划 | description含"拍多机位素材不确定机位怎么放"→触发 | ✅ |
| should-trigger-04 | should_trigger | 触发：30°通过但180°失败 | description含"角度变了但还是跳"+"主体从右到左"→触发 | ✅ |
| should-not-trigger-01 | should_not_trigger | 不触发（应触发visual-variation-judgment） | 提示含"视觉变化差太多"→匹配视觉变量而非空间规则→不触发 | ✅ |
| should-not-trigger-02 | should_not_trigger | 不触发（应触发cut-trace-dual-strategy） | 提示含"跳切效果"→description排除"刻意制造跳切"→不触发 | ✅ |
| edge-01 | edge_case | 触发但排除（纯动画无机位） | description排除"纯动画/MG"→不适用 | ✅ |
| edge-02 | edge_case | 触发：景别是保证变化够的手段之一 | description含"景别"相关讨论→触发并解释 | ✅ |

---

## 分析

### 优势
- description 中"30度原则""180度原则""越轴"等核心关键词覆盖全面
- "不适用于纯动画/MG"明确了无物理机位场景的排除

### 潜在风险
- should-not-trigger-01 的"视觉变化"关键词可能同时匹配两个 skill 的 description，需要靠"机位角度"vs"视觉变量"区分
- 短视频中观众容错度更高，30°/180°规则的严格程度可能需要调整

### 建议
- 无需修改，当前 trigger 设计合理
