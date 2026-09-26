# Glossary Extractor 产出

来源: 老登的视频日记《0基础保姆级教程，13分钟彻底学会镜头组接逻辑！》转写文本

## 关键术语词典

```yaml
- id: g01
  term: 视觉变量
  type: term
  source_chapter: 00:03:08-00:03:45
  author_definition: |
    "大家可以把屏幕想象成车窗，当车在行驶时，窗外的景物飞速后移，
    这时车窗范围内所有让你眼睛感到这画面变了的内容就是视觉变量。"
  key_distinction: |
    ≠ "摄影机是否运动" — 固定镜头中人物奔跑也是"动"
    ≠ "动作镜头/固定镜头" — 这是摄影机层面的分类
    = 画面内所有变化源的综合感知量（主体运动+运镜+光影变化等）
    作者用"大/小/无"三级量化，替代了传统的二分法
  why_it_matters: |
    "视觉变量"是作者最核心的独创概念。所有关于"动接动静接近"的规则
    都基于此概念。如果沿用传统"动作镜头/固定镜头"分类，
    所有skill的判断逻辑都会出错。
  tags: [term, core-concept, visual-perception]

- id: g02
  term: 组接逻辑
  type: term
  source_chapter: 视频简介
  author_definition: |
    "组接逻辑"指两个镜头放在一起"为什么不跳"的原理，
    涉及空间（30°/180°）、速度（速度匹配）、方向（方向匹配）三个维度。
  key_distinction: |
    ≠ "剪辑"（泛指一切操作）
    ≠ "剪辑点选择"（切哪一帧）
    = 两个镜头之间的逻辑合理性（为什么顺/不顺）
    作者刻意将其与"时长"和"剪辑点选择"分开
  why_it_matters: |
    "组接逻辑"是本系列视频的核心主题。如果与时长/剪辑点混在一起，
    学习者无法分辨"跳"的原因，也就无法对症下药。
  tags: [term, core-concept, composition]

- id: g03
  term: 镜头时长
  type: term
  source_chapter: 00:09:06-00:09:12
  author_definition: |
    "剪辑就是人文的控制，观众读取信息的节奏，镜头时长就等于你选择让观众读多久。"
  key_distinction: |
    ≠ "镜头有多少秒"（技术参数）
    = 创作者对观众信息获取节奏的控制权（创作意图）
    强调"选择"而非"测量"
  why_it_matters: |
    如果把镜头时长理解为纯技术参数，就会机械地按规则设定时长。
    理解为"控制权"后，时长决策才有策略层面的思考。
  tags: [term, duration, audience-control]

- id: g04
  term: 剪辑点
  type: term
  source_chapter: 00:09:16-00:09:25
  author_definition: |
    "当两个画面组合在一起，到底切哪一帧最合适"——剪辑点就是具体的切断位置。
  key_distinction: |
    ≠ "切换"（泛指镜头变换）
    = 两个镜头衔接时具体选择哪一帧切断
    作者强调剪辑点应对齐"观众心理预期"
  why_it_matters: |
    剪辑点是"组接逻辑"的微观实现。同一组镜头在不同帧切换，
    效果可能完全不同。如果理解为泛泛的"切换"，
    就无法精确操作。
  tags: [term, cut-point, precision]

- id: g05
  term: 动/静
  type: term
  source_chapter: 00:03:28-00:03:41
  author_definition: |
    "视觉变量大的——奔跑、快速运镜、跳跃、甩头、挥拳、舞蹈——叫做动；
    视觉变量小的——呼吸、缓慢运镜、微笑、发呆、眨眼、风景——叫做静；
    完全没有视觉变量的就是定格。"
  key_distinction: |
    ≠ "动作镜头/固定镜头"（摄影机是否运动）
    ≠ "动态/静态"（主体的物理状态）
    = 画面内视觉变化量的大小级别
    固定镜头中人物奔跑="动"；运动镜头中缓慢平移="静"
  why_it_matters: |
    "动接动静接近"是剪辑最基础的规则之一。如果按传统理解，
    就会把固定镜头接运动镜头视为"静接动"→错误判断。
  tags: [term, core-concept, dynamic-static]

- id: g06
  term: 结束点
  type: term
  source_chapter: 00:10:45-00:10:48
  author_definition: |
    "当动作结束或者主体消失的时候，观众潜意识里就知道画面该切换了。"
  key_distinction: |
    ≠ "动作的终点"（物理意义上的完成）
    = "观众潜意识认为该切换了"的心理节点
    一个复合动作可以分解为多个子动作，每个子动作都有自己的结束点
  why_it_matters: |
    如果把"结束点"理解为物理终点，就会在动作完全停止后才切换，
    错过最佳切换时机。理解为心理节点后，
    可以在动作即将完成的瞬间切换，更丝滑。
  tags: [term, cut-point, psychology, ending]

- id: g07
  term: 消失点
  type: term
  source_chapter: 00:11:16-00:11:22
  author_definition: |
    "遮挡点又或是出画点，那归根结底就是主体的消失点。"
  key_distinction: |
    ≠ "画面边缘"（物理位置）
    = "观众注意力失去附着对象"的心理节点
    包括：主体出画、被遮挡、被替换等
  why_it_matters: |
    在消失点切换=观众注意力正好没有附着对象=不会注意到切换=剪辑痕迹被忽略。
    如果理解为物理位置，就会在主体刚好到边缘时切换，
    但此时观众注意力还在追着主体走。
  tags: [term, cut-point, psychology, disappearance]

- id: g08
  term: 越轴
  type: term
  source_chapter: 00:01:26-00:01:40
  author_definition: |
    "电影镜头调度中确保空间方向一致性的基本原则，
    要求摄影机在拍摄同一场景时要保持在轴线一侧的180度范围内。"
  key_distinction: |
    ≠ "角度太大"（30°原则的违反）
    = 穿过了场景轴线→主体左右位置突变
    30°原则管"变化够不够"，180°原则管"方向对不对"
  why_it_matters: |
    越轴和角度不足是两种不同的"跳"，需要不同的修复方式。
    如果混淆，会用错误的方法修复。
  tags: [term, spatial, axis, 180-degree]

- id: g09
  term: 出势接作
  type: term
  source_chapter: 00:10:03-00:10:07
  author_definition: |
    "一个镜头负责出动势，一个镜头负责接动作。"
  key_distinction: |
    ≠ "3:7比例"（具体数值，只是表象）
    ≠ "动作完整性"（不是要展示完整动作）
    = 功能分工：前镜头=制造动势（启动/蓄力），后镜头=承接动作（完成/释放）
  why_it_matters: |
    如果迷信比例数值，面对不同动作时会不知所措。
    理解"出势接作"后，可以灵活应对任何动作类型。
  tags: [term, core-concept, action-cutting, principle]

- id: g10
  term: 剪辑痕迹
  type: term
  source_chapter: 00:12:12-00:12:16
  author_definition: |
    剪辑时画面切换的"存在感"——观众是否意识到"这里被切了一刀"。
  key_distinction: |
    ≠ "剪辑错误"（痕迹可以是有意为之的）
    = 切换点的可见度
    弱化痕迹=让观众忽略切换（顺滑叙事）
    利用痕迹=让观众注意到切换（跳切/鬼畜等效果）
  why_it_matters: |
    "剪辑痕迹"是元策略的决策依据。如果不区分"弱化"和"利用"两条路线，
    就会在需要跳切时还在追求顺滑，或在需要顺滑时制造跳切。
  tags: [term, meta-concept, cut-traces]
```
