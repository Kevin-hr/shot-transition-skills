# 测试结果 — visual-variation-judgment

> 测试模式: **Fallback 主流程自测** (无独立 sub-agent 盲测)
> 可信度: 中 (低于独立盲测)
> 测试时间: 2026-09-20

---

## 通过率: 8/8 (100%)

| ID | 类型 | 预期 | 实际 | 结果 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 触发：固定微笑+缓慢平移=静接静 | description含"动接动静接近"+"固定镜头接运动镜头"→触发 | ✅ |
| should-trigger-02 | should_trigger | 触发：固定跑步=动，缓慢推拉=静 | description含"固定镜头拍运动主体"+"动接静"→触发 | ✅ |
| should-trigger-03 | should_trigger | 触发：跑步=动，呼吸=静 | description含"两个画面接在一起为什么跳"→触发 | ✅ |
| should-trigger-04 | should_trigger | 触发：打太极+流水=静接静 | description含"怎么判断画面是动还是静"→触发 | ✅ |
| should-not-trigger-01 | should_not_trigger | 不触发（应触发shot-composition-spatial-rules） | 提示含"机位角度"→description匹配空间规则而非视觉变量→不触发 | ✅ |
| should-not-trigger-02 | should_not_trigger | 不触发（纯信息查询） | 提示是知识查询，description明确排除"纯信息查询"→不触发 | ✅ |
| edge-01 | edge_case | 触发但应转向cut-trace-dual-strategy | description含"刻意制造跳"→B段排除跳切场景 | ✅ |
| edge-02 | edge_case | 触发：光影变化纳入视觉变量 | description未明确排除光影→应触发并纳入判断 | ✅ |

---

## 分析

### 优势
- description 中"动接动静接近"和"固定镜头接运动镜头"等 trigger 信号覆盖了核心场景
- "不适用于纯信息查询"明确排除了知识查询类提示

### 潜在风险
- should-not-trigger-01（机位角度问题）与 visual-variation-judgment 的边界需要靠"机位角度"vs"视觉变量"关键词区分，实际部署中可能出现混淆
- edge-02（光影变化）的判断依赖 description 是否包含"光影"——当前未明确提及，建议在 E 段补充

### 建议
- 考虑在 description 中补充"光影变化也计入视觉变量"以覆盖 edge-02
- 跨 skill 诱饵 should-not-trigger-01 在实际使用中可能误触发，建议在"不适用于"段补充"机位角度问题→用 shot-composition-spatial-rules"
