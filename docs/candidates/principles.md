# Principle Extractor 产出

来源: 老登的视频日记《0基础保姆级教程，13分钟彻底学会镜头组接逻辑！》转写文本

## 候选原则/规则

```yaml
- id: p01
  title: 30°原则
  type: principle
  source_chapter: 00:00:47-00:00:56
  source_quote: |
    "这就是影视行业中的30度原则，指的就是当摄影机在拍摄同一人物或物体的、
    连续镜头时，镜头之间的角度变化应至少为30度，否则观众可能会感到不自然，
    从而分散对剧情的注意力。"
  summary: |
    同一主体的连续镜头，机位角度变化≥30°。否则大脑认为没换镜头但主体变了→跳。
    但角度变化也不能太大到越轴（见180°原则）。
  tags: [editing, spatial-rule, 30-degree]

- id: p02
  title: 180°原则（越轴原则）
  type: principle
  source_chapter: 00:01:25-00:01:40
  source_quote: |
    "这就是大家常说的180度原则，也就是越轴。指的就是电影镜头调度中，
    确保空间方向一致性的基本原则，它要求摄影机在拍摄同一场景时，
    要保持在轴线一侧的180度范围内。"
  summary: |
    机位须保持在轴线一侧180°范围内。否则主体左右位置突变→大脑空间感错乱。
    与30°原则配合使用：角度变化≥30°但≤180°（不越轴）。
  tags: [editing, spatial-rule, 180-degree, axis]

- id: p03
  title: 速度匹配原则
  type: principle
  source_chapter: 00:04:15-00:04:24
  source_quote: |
    "这就是大家常说的速度匹配，指的就是上下两个镜头衔接时，
    主体速度、镜头运动速率、整体画面节奏保持一致，让过度更丝滑，画面更流畅。"
  summary: |
    上下镜头衔接时，主体速度、运镜速率、画面节奏须保持一致。
    可通过加速/减速某一段来实现匹配。
  tags: [editing, matching, speed, rhythm]

- id: p04
  title: 方向匹配原则
  type: principle
  source_chapter: 00:04:57-00:05:04
  source_quote: |
    "这就是大家常说的方向匹配，指的就是上下镜头衔接时，
    主体运动方向、镜头运动方向、画面视线方向保持一致，让画面逻辑连贯。"
  summary: |
    上下镜头衔接时，主体运动方向、运镜方向、视线方向须保持一致。
    方向相反=违背常理→跳。
  tags: [editing, matching, direction, logic]

- id: p05
  title: 结束点/消失点剪辑原则
  type: principle
  source_chapter: 00:10:42-00:10:52
  source_quote: |
    "在结束点和消失点剪辑。原理也特别简单，就是当动作结束或者主体消失的时候，
    观众潜意识里就知道画面该切换了，在这个点去切换镜头，是符合观众心理预期的。"
  summary: |
    在动作结束或主体消失处切换镜头=符合观众心理预期=剪辑痕迹被忽略。
    结束点：动作完成的那一帧（钥匙插完、挥拳到顶等）。
    消失点：主体从画面消失（出画、被遮挡等）。
  tags: [editing, cut-point, psychology, expectation]

- id: p06
  title: Murch眨眼原则
  type: principle
  source_chapter: 00:11:48-00:12:16
  source_quote: |
    "默奇认为虽然我们好像是不间断地看着周围的一切，但实际上每次闭上眼睛，
    本质上都经历了一次剪辑。当注意力切换、想法结束、情绪告一段落的时候，
    我们会自然而然地眨一下眼睛……所以在画面中人物眨眼的时候切换镜头，
    剪辑痕迹就很容易被忽略。"
  summary: |
    人物眨眼=注意力天然切换点=最佳剪辑时机。
    来源于Walter Murch的剪辑理论。眨眼分割上一段画面、开启下一段视线。
  tags: [editing, cut-point, murch, blink, attention]

- id: p07
  title: 三维度分离学习原则
  type: principle
  source_chapter: 视频简介
  source_quote: |
    "很多人讲两个镜头组接的时候会把组接逻辑、时长、剪辑点选择混在一起讲，
    倒不是说是有什么问题，而是到了最后不好落地，都变成了靠感觉了。
    我之所以分开讲，是想除了靠感觉外，尽可能找一些方法、技巧去确定如何组接两个镜头。"
  summary: |
    组接逻辑（为什么跳/不跳）、镜头时长（放多久）、剪辑点选择（切哪帧）是三个独立维度。
    混在一起教→不好落地→变成靠感觉。分开学→每个维度都有可操作规则。
  tags: [editing, methodology, separation, pedagogy]

- id: p08
  title: 信息密度决定时长原则
  type: principle
  source_chapter: 00:06:35-00:06:55
  source_quote: |
    "信息杂乱细节多的画面，时长需要留长一点；而主题突出重点清晰的画面，
    可以适当地缩短时长。总结一句话就是，能够完整表达一个内容的最短时长，
    就是那个合适的时长。"
  summary: |
    画面信息密度高→需要更长时间让大脑处理；信息密度低→可缩短。
    判定标准："能够完整表达一个内容的最短时长就是合适的时长。"
  tags: [editing, duration, information-density]

- id: p09
  title: 隔离景别非必要原则
  type: principle
  source_chapter: 00:01:57-00:02:10
  source_quote: |
    "很多人在教景别切换的时候，讲求全景接中景接中景接特写，
    这种隔离景别的切换方式，但本质上我们没必要完全去追寻这个规则，
    因为只要画面有足够的变化，告诉大脑我们已经切换镜头了，
    这是一个新的视角，而且符合逻辑，基本上就没有跳的问题。"
  summary: |
    传统教学中"全景→中景→特写"的隔离景别切换不是必须遵守的规则。
    只要画面有足够变化+符合逻辑，景别相同也可以切换。
  tags: [editing, shot-size, flexibility, debunking]

- id: p10
  title: 镜头时长=观众信息节奏控制原则
  type: principle
  source_chapter: 00:09:06-00:09:12
  source_quote: |
    "剪辑就是人文的控制，观众读取信息的节奏，镜头时长就等于你选择让观众读多久。"
  summary: |
    镜头时长不是技术参数，而是创作者对观众信息获取节奏的控制权。
    选择时长=选择让观众读多久。
  tags: [editing, duration, audience-control, philosophy]
```
