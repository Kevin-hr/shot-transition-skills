# Counter-Example Extractor 产出

来源: 老登的视频日记《0基础保姆级教程，13分钟彻底学会镜头组接逻辑！》转写文本

## 候选反例/失败模式

```yaml
- id: ce01
  title: 混淆组接逻辑/时长/剪辑点选择
  type: counter-example
  source_chapter: 视频简介
  source_quote: |
    "很多人讲两个镜头组接的时候会把组接逻辑、时长、剪辑点选择混在一起讲，
    倒不是说是有什么问题，而是到了最后不好落地，都变成了靠感觉了。"
  failure_mode: |
    将三个独立维度混在一起学习，导致每个维度都没学透，
    最终无法落地为可操作规则，只能依赖"感觉"。
  mechanism: |
    三个维度各有独立的判断标准：组接逻辑看空间/速度/方向，
    时长看信息密度/情绪/节奏，剪辑点看动作结构/心理预期。
    混在一起时，无法分辨"跳"是因为组接逻辑问题还是时长问题还是剪辑点问题。
  warning_signs:
    - 剪辑时总觉得"不对劲"但说不清哪里不对
    - 同样的操作有时顺有时跳，找不到规律
    - 剪辑完全依赖直觉，无法向他人解释决策
  bound_to:
    - "三维度分离学习原则"
    - 所有剪辑skill的适用范围
  tags: [counter-example, methodology, confusion]

- id: ce02
  title: 越轴导致空间感错乱
  type: counter-example
  source_chapter: 00:01:08-00:01:26
  source_quote: |
    "原本在画面右侧的小龙突然跑到了左边，虽然机位角度已经大于了30度，
    但主体左右直接调换，大脑的空间感完全错乱了。"
  failure_mode: |
    虽然满足了30°原则（角度变化>30°），但越过了轴线，
    导致主体左右位置突变，观众空间感错乱。
  mechanism: |
    大脑通过连续镜头建立空间模型，越轴=模型中的主体位置突然翻转，
    大脑需要重新构建空间模型，产生认知负荷，表现为"跳"的感觉。
  warning_signs:
    - 剪辑后主体突然从画面一侧跳到另一侧
    - 观众反馈"方向乱了"
    - 多机位拍摄时未画轴线图
  bound_to:
    - "180°原则（越轴原则）"
    - "30°原则"
  tags: [counter-example, spatial, axis-crossing]

- id: ce03
  title: 混淆"动接动静接近"的传统理解
  type: counter-example
  source_chapter: 00:02:16-00:03:00
  source_quote: |
    "大家都知道动接动静接近，但真正开始组接的时候，却开始究竟怎么都拿捏不准。
    一和四还明显就是用了固定镜头接的运动镜头，所以动接动静接近，
    并不是指影视创作动作镜头语言这块的概念，千万不要搅在一起。"
  failure_mode: |
    将"动接动静接近"误解为"动作镜头接动作镜头，固定镜头接固定镜头"，
    导致在实际组接时无法正确判断哪些镜头该接在一起。
  mechanism: |
    传统教学中的"动作镜头"（摄影机运动）和"固定镜头"（摄影机静止）
    与"画面内视觉变化量"不是同一回事。固定镜头中人物奔跑也是"动"，
    运动镜头中缓慢平移也是"静"。概念混淆导致判断错误。
  warning_signs:
    - 按"摄影机是否运动"分类来组接
    - 组接后仍然觉得不顺畅但找不到原因
    - 把"动作镜头"等同于"动"
  bound_to:
    - "视觉变量判断框架"
  tags: [counter-example, misconception, visual-variation]

- id: ce04
  title: 视觉变量大小不匹配导致跳
  type: counter-example
  source_chapter: 00:03:52-00:04:01
  source_quote: |
    "如果我们把视觉变量大的和视觉变量小的组结在一起，会怎么样呢？
    为了对比更明显，我们选择这两个骑车的镜头来看一下……是不是还蛮明显的。"
  failure_mode: |
    视觉变量大的镜头接视觉变量小的镜头，画面节奏断裂→跳。
    例如快跑接发呆、快速运镜接静止风景。
  mechanism: |
    大视觉变量=大脑处于高信息处理状态；小视觉变量=大脑处于低信息处理状态。
    突然切换=大脑处理模式被迫急速切换=认知负荷=跳的感觉。
  warning_signs:
    - 快节奏镜头突然接慢节奏镜头
    - 观众反馈"突然断了"
    - 两组接在一起画面节奏不统一
  bound_to:
    - "视觉变量判断框架"
    - "速度匹配原则"
  tags: [counter-example, visual-variation, mismatch]

- id: ce05
  title: 主体运动方向相反导致跳
  type: counter-example
  source_chapter: 00:04:31-00:04:50
  source_quote: |
    "一个主体从画面左侧向右移动，一个主体从画面右侧向左移动。
    这就好比你上一秒正在开车直行，下一秒突然180度掉头一样，
    大脑的反应是这违背常理太突兀，中间少了一段。"
  failure_mode: |
    上下镜头主体运动方向相反，大脑认为"违背常理"，产生"中间少了一段"的感觉。
  mechanism: |
    大脑默认连续的运动应有物理因果性（方向不变或渐变）。
    方向突变=违反物理直觉=需要额外信息解释=认知负荷=跳。
  warning_signs:
    - 上下镜头主体运动方向相反
    - 观众觉得"突然转向"或"缺了过渡"
    - 运镜方向或视线方向不一致
  bound_to:
    - "方向匹配原则"
  tags: [counter-example, direction, mismatch]

- id: ce06
  title: 镜头时长失控的两种极端
  type: counter-example
  source_chapter: 00:07:01-00:08:05
  source_quote: |
    "当镜头小于1.5秒快速切换的时候……大脑的逻辑是环境变化得这么快，
    我必须集中精力，不然容易错过危险或者信息。
    当镜头大于3秒甚至更久的时候……大脑进入联想处理信息共情的状态。"
  failure_mode: |
    - 镜头太短（<1.5s）：信息来不及处理，观众焦虑（除非目的是制造紧张）
    - 镜头太长（>6-8s）：注意力衰减，观众无聊想滑走
  mechanism: |
    人眼和大脑处理画面信息有固定时间窗口。太短=信息过载；
    太长=信息已被消化但镜头还在=冗余=注意力衰减。
  warning_signs:
    - 观众完播率低，在某个位置集中退出
    - 画面信息量小但镜头很长
    - 快切段落过多导致观众疲惫
  bound_to:
    - "人眼感知时间表"
    - "镜头时长三层面决策框架"
    - "信息密度决定时长原则"
  tags: [counter-example, duration, attention, too-short, too-long]

- id: ce07
  title: 迷信景别切换规则
  type: counter-example
  source_chapter: 00:01:57-00:02:10
  source_quote: |
    "很多人在教景别切换的时候，讲求全景接中景接中景接特写，
    这种隔离景别的切换方式，但本质上我们没必要完全去追寻这个规则。"
  failure_mode: |
    刻板遵循"全景→中景→特写"的景别切换规则，限制了创作自由。
    实际上只要画面有足够变化+符合逻辑，景别相同也可以切换。
  mechanism: |
    景别切换规则只是保证"画面有足够变化"的一种手段，不是目的。
    迷信手段而忘记目的→在不需要隔离景别时也强制使用→限制表达。
  warning_signs:
    - 所有切换都严格遵循景别递进
    - 创作者自己觉得"被规则束缚"
    - 相同景位的合理切换被否定
  bound_to:
    - "隔离景别非必要原则"
  tags: [counter-example, shot-size, rule-rigidity]

- id: ce08
  title: 迷信剪辑点比例
  type: counter-example
  source_chapter: 00:09:58-00:10:03
  source_quote: |
    "所以大家明白了吗？比例多少，动作是否完整，其实都不是那么重要，
    真正的核心只有一句话，一个镜头负责出动势，一个镜头负责接动作。"
  failure_mode: |
    迷信3:7比例或其他具体数值，忽略"出势接作"的原理。
  mechanism: |
    比例是表象，原理是本质。不同动作的最优比例不同，
    但"出势接作"的逻辑不变。迷信比例=刻舟求剑。
  warning_signs:
    - 每次动作剪辑都机械套用3:7
    - 无法解释为什么选这个比例
    - 面对非常规动作不知如何处理
  bound_to:
    - "出势接作剪辑框架"
  tags: [counter-example, ratio-obsession, surface-level]
```
