# Mistral Small 3.2 Q4_K_M 日文语义复核评测（2026-10-27）

Mistral 已完成旧组 **100 词的首轮回归及一次有限重试**。在 822 个可计分字段中，四处确认错误仍全部获准 pass，检出为 **0/4**，最终误报 **24 个正确字段**，另有 1 个模型 uncertain、4 个 unavailable。首轮至最后重试记录的跨度为 **2 小时 38 分 20.14 秒**。结果不满足事前运行门槛，**新 100 词的 Mistral / Qwen 配对推理未启动，两者均为 0 请求**。

本文记录冻结输入、公平性约束、独立源文 gold、分轮实测与路由依据。100 个运行记录完成不等于语义判断完整或评测通过；有限重试后仍有 unavailable、模型 uncertain 及独立 gold 待定项。

本轮只评测检测能力，不向正式词库写入译文。新 gold 是 Codex 代理的源文审查标签，不是专业人工译审认证；分层选取的 100 词也不能用于推算全库准确率。

## 两组材料与计分分母

| 材料 | 词数 / 译文字段 | 原译 gold：正确 / 错误 / 待定 | 可计分字段 | 用途 |
| --- | ---: | ---: | ---: | --- |
| 旧 100 词 | 100 / 825 | 818 / 4 / 3 | 822 | 在昨日同一冻结、修正前的源文和日译上做回归筛选 |
| 新 100 词 | 100 / 830 | 823 / 2 / 5 | 825 | 通过运行门槛后，供 Mistral 与 Qwen 在同一新材料上配对比较 |

旧组复用 [旧 selection](../.local/ja-semantic-holdout-2026-10-26/selection.json)、[修正前快照](../.local/ja-semantic-review-2026-10-26/snapshot.json) 和 [gold-v2](../.local/ja-semantic-holdout-2026-10-26/gold-v2.json)。它不使用已经采用七处修订的当前日文，也不能称为新的未见集。历史采用记录与原译评测标签保持分开，详见[昨日批次报告](ja-semantic-holdout-review-2026-10-26.md)。

新组基于七处修订后的[快照](../.local/ja-semantic-review-post-holdout-2026-10-26/snapshot.json)，按 CEFR 配额、稀有主题优先和种子 `20261027` 选取，覆盖 A1–C2 和 19 个主题。排除旧量化基准 100 词、昨日 holdout 100 词和开发用 8 词；**排除集合去重后为 202 词**，不能机械相加为 208。规则、实际 ID 和覆盖分布见[新 selection](../.local/ja-semantic-holdout-mistral-2026-10-27/selection.json)。这里的“未见”指未参与这些既有评测或开发材料，不是对模型预训练内容的保证。

字段仅指 `mode=translate` 的词义、例句、搭配、中文提示等。英文保留项和空字段不混入语义计分分母。Gold 的 `uncertain` 从语义计分中排除，不能当作正确；模型自身的 `uncertain`、`unavailable`、`missing` 则保留为未完成判断，不能改算通过。旧组的 822 与新组的 825 是不同分母。

| 冻结标识 | SHA-256 |
| --- | --- |
| 旧 selection，规范 JSON | `9348d382fd1071e3f7549b13d0c65bee835acc43b363d78a0db828387902de75` |
| 旧快照，精确文件字节 | `aa024c1a0ff313e050a1e44760ef20f9d4f3ff34fe8d93a13b62e32f420a2c43` |
| 新 selection，规范 JSON | `55c5e9d33d1bbe16e96ddb14e378a5abb45ad89b123ccc76d3ec23994979e7ef` |
| 新快照，精确文件字节 | `9744b810d613c2159ddb0e92b457eb152618afefab53100a7747618b14a83bf3` |
| 新 gold，精确文件字节 | `7f1da09020938014b519b1704504ae0469316f485615b82d3dd975a7c6332672` |
| 新 gold，规范 JSON | `633f24b95352a68362cc5b3cf264d911f2fb4e96358ae08ce700084ce7d10733` |

规范 JSON 使用 `ja_review_core.sha` 的 UTF-8、排序键和紧凑分隔符编码；文件字节哈希包含原文件序列化及换行。两种哈希口径不能互换。

## 新 gold 的独立源文流程

三个 Codex 审查代理先分包逐字段审查，再交换此前未负责的包进行第二遍完整审查。两遍各覆盖 830 字段，共 1,660 条字段审查记录；九个争议项随后交由第三位审查者对照源文裁决。英文是中英并存字段的权威，中文用于消歧；中文独有提示直接按中文核对。合理日语省略、同义表达和标准的简短词典释义不自动算错，无法确定的读法保留待定。

最终[源文裁决记录](../.local/ja-semantic-holdout-mistral-2026-10-27/independent-review/source-adjudications.json)与[新 gold](../.local/ja-semantic-holdout-mistral-2026-10-27/gold.json)已由[锁定记录](../.local/ja-semantic-holdout-mistral-2026-10-27/independent-review/gold-lock.json)绑定。锁定时间为 **2026-10-27 00:39:07 JST**，记录中的 UTC 时间为 `2026-10-26T15:39:07.167463+00:00`。

已完成的[gold 链路审计](../.local/ja-semantic-holdout-mistral-2026-10-27/independent-review/gold-chain-audit.json)记录为 `pass`，核对覆盖、引句、排除集合及锁定绑定；它不是模型成绩。

锁定记录声明：锁前未启动新 holdout 的模型推理，也未查看本轮模型逐字段判定或语义汇总成绩。锁前观察到的旧回归信息限于完成进度、运行时间、实际请求输入匹配和结构校验计数。源文 gold 先锁定，再做新材料上的模型测量；不能根据模型输出改标签来提高成绩。

| 新 gold 状态 | 字段 |
| --- | --- |
| 确认错误，2 项 | `internet.col.1`、`sidewalk.col.1` |
| 待定，5 项 | `keyboard.ex.1`、`plantation.ex.0`、`adopt.ex.1`、`territory.tip`、`tune.ex.1` |

这些是**冻结原译**的标签；保守候选建议不等于已证明原译错误。本轮文档和评测不采用候选、不改正式词库。共享 rubric 以及代理之间可能的共同偏差仍是限度，不能把代理双遍审查称为专业人工认证。

## 模型、硬件与任务配置

本地核验的模型为 [`mistral-small3.2:24b-instruct-2506-q4_K_M`](https://ollama.com/library/mistral-small3.2:24b-instruct-2506-q4_K_M)。Ollama 官方 tag 列出 24B、Q4_K_M，与[本地模型核验](../.local/ja-mistral-test-2026-10-27/model-verification.json)一致。原模型卡由 [Mistral AI](https://huggingface.co/mistralai/Mistral-Small-3.2-24B-Instruct-2506)发布；其通用基准或宣传性改进不代替本项目的日文复核实测。

| 核验项 | 值 |
| --- | --- |
| 模型家族 / 格式 / 量化 | `mistral3` / GGUF / `Q4_K_M` |
| 参数规模 | 标记 `24.0B`；模型元数据 `24,011,361,280` 参数 |
| 本地模型大小 | `15,177,384,862` bytes，约 **15.177 GB**；不等于运行时峰值内存 |
| Ollama 模型 digest | `5a408ab55df5c1b5cf46533c368813b30bf9e4d8fc39263bf2a3338cfa3b895b` |
| 原生模板 SHA-256 | `a05d05f28442185a99d6a1a9b3d59f903321f7cd6745c8150e72a94b1e959a87` |
| 运行环境 | Apple M1 Pro，32 GB 统一内存；Ollama `0.32.1` |
| 执行方式 | 单模型驻留，模型和批次串行执行 |
| 对照模型 | `qwen3.5:9b-q8_0` |

一次[运行环境快照](../.local/ja-mistral-test-2026-10-27/runtime-snapshot.json)在 **2026-10-27 01:09:41 JST** 开始的短读取窗口中记录：Ollama `/api/ps` 仅有一个驻留模型 Mistral，上下文为 8192 tokens；`size` 与 `size_vram` 均为 **15,687,472,906 bytes，约 14.61 GiB**，与上表模型文件大小的口径不同。整机物理内存为 **32 GiB**，系统压缩器物理占用约 **7.26 GiB**，全局已用交换空间约 **27.07 GiB**，供电为 **AC**。

这些是单时点观测，不是峰值、均值或当前换页速率；全局交换空间和压缩占用不能归因于本测试，也不能据此认定它们造成了某次耗时。Mac 使用统一内存，`size_vram` 不是应再加到 RAM 或 `size` 上的另一份独立显存，也不是完整进程 RSS。速度测量应注明属于这一桌面运行环境，不据单次快照推算全库耗时。

[原测试计划](../.local/ja-mistral-test-2026-10-27/test-plan.json)固定任务参数如下。模型包内原生默认 temperature 为 `0.15`，本实验请求明确覆盖为 `0.1`。

| 任务参数 | 值 |
| --- | ---: |
| `num_ctx` | 8192 |
| `num_predict` | 4096 |
| `temperature` / `seed` | 0.1 / 42 |
| `top_k` / `top_p` | 40 / 0.95 |
| `repeat_penalty` / `presence_penalty` | 1.0 / 0.0 |

Mistral 不接收关闭思考的 `think` 字段；Qwen 显式接收 `think=false`。二者保留各自原生模板和 tokenizer。**这是不同家族、不同参数规模及不同量化模型的任务比较，不是纯粹的 4-bit 与 8-bit 量化消融实验。**

## 检测代码与实际输入公平性

以下四个文件的当前精确字节哈希与[昨日 Qwen 检测协议](../.local/ja-semantic-review-2026-10-26/protocols/detect-holdout-20261026.json)及其冻结源码副本一致。它们覆盖检测器、核心数据绑定、模型适配和既有守卫；此次文档编写未修改代码。

| 文件 | 精确字节 SHA-256 |
| --- | --- |
| `ja_review_core.py` | `6451166e82c0ed71a7e70924cbf7faa619226f346e97aa5a89831b07d721c3ce` |
| `ja_review_models.py` | `0c64f941694c8a6f09bdd2f9394a493d516e0b8961939f94e804ea27bcb91351` |
| `review-ja-corpus.py` | `8c6597c290e1272a0ad3ce884cb1337d100e7ba1e61efaf702780ba40bdc4722` |
| `translate-ja-local.py` | `80aaa8a03094634f104ad222a2ec51390a75166bd6b33915d2a8b280d74bda6a` |

[实际请求公平性记录](../.local/ja-mistral-test-2026-10-27/actual-input-fairness.json)对 `blog` 的一次实际请求核验显示，`messages`、`format`、`options`、`keep_alive`、`stream` 五部分一致，未读取语义判定。其请求哈希分别为：

- Mistral：`d7882b594842712562d5ac6d746828b7b2498e13d7dd9a836f91f32de0a79bb6`
- Qwen：`26cc8b406d612dc5abbf92ba1d04d29fac179f0204cf717770e0b335dd33f319`

模型名及上述 `think` 差异属于预期差异，所以完整请求哈希不同。该项核验范围限于 `blog` 的任务级 payload，不代表原生模板渲染后的 token 序列相同。

随后完成的[首轮运行审计](../.local/ja-mistral-test-2026-10-27/initial-run-audit.json)已核对整批 **100 个实际请求**：`messages`、`format`、`options`、`keep_alive`、`stream` 五部分各有 100/100 与昨日 Qwen 首轮匹配；源文和日文词条哈希均对应旧冻结快照，四个检测源码文件仍逐字节一致，实验期间没有词库文件漂移，新 gold 未变。Mistral 首轮[协议](../.local/ja-semantic-review-2026-10-26/protocols/detect-mistral-q4-regression-20261027.json)的规范 JSON 哈希为 `ad564c286f8b5e6ee8ff0159e05e593ccf280703ac44f11f191be74922e28550`。

## 旧 Qwen 参考结果：首轮和有限重试分开

下表只复述[旧首轮指标](../.local/ja-semantic-holdout-2026-10-26/metrics-initial.json)和[旧重试后指标](../.local/ja-semantic-holdout-2026-10-26/metrics-after-retry.json)，**不包含 Mistral 的任何成绩**。旧组计分分母为 822，其中确认错误 4 个、正确字段 818 个；3 个独立 gold 待定项排除。

| Qwen 阶段 / 视图 | 真检出 / 4 | 错误获准 pass / 4 | 正确字段误报 / 818 | 正确 pass | uncertain | unavailable | 明确判断 / 822 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 首轮 / model | 0 | 3 | 20 | 784 | 0 | 15 | 807 |
| 一次重试后 / model | 1 | 3 | 21 | 791 | 0 | 6 | 816 |
| 首轮 / guarded | 0 | 3 | 20 | 782 | 2 | 15 | 805 |
| 一次重试后 / guarded | 1 | 3 | 21 | 789 | 2 | 6 | 814 |

重试范围精确限定为首轮的 **15 个 unavailable 字段、14 个词条**，最多增加一次重试；已有有效 pass、error、uncertain 判定保持不变。实际恢复 9 个字段，重试后仍有 6 个 unavailable。范围见 [retry-scope.json](../.local/ja-semantic-holdout-2026-10-26/retry-scope.json)。

重试后 model 视图的错误检出召回为 `1/4 = 25%`，报错精度为 `1/22 ≈ 4.55%`，正确字段误报率为 `21/818 ≈ 2.57%`，错误误放率为 `3/4 = 75%`。获准 pass 中的原译残错为 `3/794 ≈ 0.378%`；这不是全库翻译错误率。明确判断覆盖为 `816/822 ≈ 99.27%`。Guarded 额外保留的 2 个 uncertain 是守卫后的 HOLD，既不算检错，也不算语义通过。

旧组记录仍为 `incomplete`、`passed=false`，包含独立 gold 未解决项。只有四个确认错误，任何一项检出变化就会改变召回 25 个百分点，不能据此给出稳定的全库能力保证。

## 同一旧组的首轮与有限重试对照

[Mistral 首轮指标](../.local/ja-mistral-test-2026-10-27/metrics-regression-initial.json)与上面的旧 Qwen 首轮使用同一修正前快照、同一 100 词 / 825 字段及 gold-v2，计分分母同为 **822 = 818 正确 + 4 错误**。以下首轮对照均尚未使用额外重试。

| 模型 / 首轮视图 | 真检出 / 4 | 错误获准 pass / 4 | 正确字段误报 / 818 | 正确 pass | uncertain | unavailable | 明确判断 / 822 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen / model | 0 | 3 | 20 | 784 | 0 | 15 | 807 |
| Mistral / model | 0 | 4 | 23 | 782 | 1 | 12 | 809 |
| Qwen / guarded | 0 | 3 | 20 | 782 | 2 | 15 | 805 |
| Mistral / guarded | 0 | 4 | 23 | 780 | 3 | 12 | 807 |

Mistral model 视图的首轮召回为 `0/4 = 0%`，报错精度为 `0/23 = 0%`，错误误放率为 `4/4 = 100%`，正确字段误报率为 `23/818 ≈ 2.81%`。获准 pass 中原译残错为 `4/786 ≈ 0.509%`；明确判断覆盖为 `809/822 ≈ 98.42%`。Guarded 视图额外把两个正确字段保留为 uncertain，没有阻止四处已知错误的误放。首轮 `missing=0`，`status=incomplete`、`passed=false`。

Mistral 比 Qwen 首轮少 3 个 unavailable，同时误放和误报均增加；可用性计数改善不能替代语义检错能力。这里的“model”是结构与源译引句校验后保留的模型判断，不是未解析的原始文本；“guarded”是确定性守卫后的结果，二者分开报告。

Mistral 随后只对首轮 12 个 unavailable 字段、10 个词条补试一次。根据[最终指标](../.local/ja-mistral-test-2026-10-27/metrics-regression-after-retry.json)和[重试审计](../.local/ja-mistral-test-2026-10-27/retry-run-audit.json)，8 个字段恢复有效判断：7 个正确 pass、1 个新增误报 `pilferage.ex.1`；4 个仍为 unavailable。825 个选定译文字段中，其余 **813 个既有语义判定逐字保持不变**。

| 模型 / 一次有限重试后视图 | 真检出 / 4 | 错误获准 pass / 4 | 正确字段误报 / 818 | 正确 pass | uncertain | unavailable | 明确判断 / 822 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen / model | 1 | 3 | 21 | 791 | 0 | 6 | 816 |
| Mistral / model | 0 | 4 | 24 | 789 | 1 | 4 | 817 |
| Qwen / guarded | 1 | 3 | 21 | 789 | 2 | 6 | 814 |
| Mistral / guarded | 0 | 4 | 24 | 787 | 3 | 4 | 815 |

Mistral 最终 model 视图的召回为 `0/4 = 0%`，报错精度为 `0/24 = 0%`，错误误放率为 `4/4 = 100%`，正确字段误报率为 `24/818 ≈ 2.93%`。获准 pass 中原译残错为 `4/793 ≈ 0.504%`；明确判断覆盖为 `817/822 ≈ 99.39%`。Guarded 视图对应为 `4/791 ≈ 0.506%` 残错、`815/822 ≈ 99.15%` 明确判断覆盖。两个视图的 `missing=0`，最终仍为 `incomplete`、`passed=false`；3 个独立 gold 待定项仍不参与计分。

| 最终仍 unavailable 的字段 | 校验结果 |
| --- | --- |
| `applaud.ex.1` | `targetQuote` 不是对应日译字段的准确引句 |
| `title.tip` | `sourceQuote` 不是对应源文字段的准确引句 |
| `versus.senses.0` | 输出重复该字段路径，没有选取竞争判定 |
| `versus.tip` | 没有提供可用字段判定 |

这些记录既未算作语义通过，也未算作检错；没有回收程序已丢弃的判定来补分。重试协议规范 JSON 哈希为 `5d4cd065d0bc1284b836ae6a83597085406edd06b388f4a1fa0707f72f1a7ca4`。

## 实际运行耗时与结束状态

| Mistral 首轮时间口径 | 实测 |
| --- | ---: |
| 完成的运行记录 / 模型请求 | 100 / 100 |
| 最早请求开始至最后记录完成的跨度 | **9,282.744575 秒，约 2 小时 34 分 42.7 秒** |
| 各请求 wall latency 合计 | **9,183.802638124 秒** |
| 总生成 tokens / 总生成耗时 | 64,663 / 8,206.114395998 秒 |
| 生成阶段速度：总 tokens 除以总生成耗时 | **7.879856 tokens/秒** |

首轮跨度为 2026-10-27 **00:12:10 至 02:46:53 JST**。根据[运行审计](../.local/ja-mistral-test-2026-10-27/initial-run-audit.json)，跨度包含单词冒烟测试后的恢复间隔与加载；请求耗时合计、生成耗时和整段跨度是不同口径，不能相加或互换。速度属于上文记录的桌面环境，不能据此作纯量化速度比较或全库耗时保证。

| 有限重试及完整跨度口径 | 实测 |
| --- | ---: |
| 重试模型请求 / 目标字段 | 10 / 12 |
| 重试开始至最后重试记录完成 | **166.391435 秒** |
| 重试各请求 wall latency 合计 | **166.207467583 秒** |
| 首轮最早记录至最后重试完成，含阶段间隔 | **9,500.142685 秒，约 2 小时 38 分 20.14 秒** |

重试窗口为 2026-10-27 **02:47:44 至 02:50:30 JST**。不能把两个阶段跨度直接相加当作包含阶段间隔的总跨度。[重试审计](../.local/ja-mistral-test-2026-10-27/retry-run-audit.json)记录结束检查的驻留模型列表为空、已安装模型保留，Mistral digest 仍为 `5a408ab55df5c1b5cf46533c368813b30bf9e4d8fc39263bf2a3338cfa3b895b`；旧快照绑定有效、正式词库文件零漂移，新 gold 未修改。

## 四处已知错误与模型一致性的限度

[known-error-regression-check.json](../.local/ja-mistral-test-2026-10-27/known-error-regression-check.json)在旧组运行过程中单独捕获了四个已完成的已知错误字段，分别保存模型判断（MA）与程序守卫。四项在两个视图中均为 pass，均没有触发验证 HOLD，理由也未指出已锁定的源译差异。该窄检查本身不评估整批完成或全量误报；整批首轮完成及上表计数另由首轮审计和指标文件证明。

| 冻结旧译字段 | 源文语言 / gold 严重度 | 确认差异 | Qwen 一次重试后 / model | Mistral 首轮 MA / guarded |
| --- | --- | --- | --- | --- |
| `saving.ex.0` | 英文 / major | `monthly pass` 的一个月期限被泛称“定期券”遗漏 | pass | pass / pass |
| `impulse.tip` | 中文 / major | “后接动作”的语法接续被误作继续某个行为 | pass | pass / pass |
| `bespectacled.ex.0` | 英文 / major | `find` 的找到结果被弱化为帮忙寻找 | pass | pass / pass |
| `workmanship.tip` | 中文 / minor | 中性的“做工”被加上质量好的限定 | error | pass / pass |

因此，在这批已知案例中，**不同家族的 Qwen 与 Mistral 一致放过了三处 major 错误**。不同模型一致判 pass 并不能证明译文正确；源文逐项核对和冻结 gold 仍不可被一致率代替。本表比较的是各自注明阶段的同一冻结字段，不把 Qwen 重试后结果冒称首轮。

## 误报的揭盲后源文诊断

首轮 23 个“模型报错、旧 gold 正确”的字段分为两包，由两位独立于模型生成的 Codex 审查代理核对模型理由、冻结源译及同词语境：[诊断 1](../.local/ja-mistral-test-2026-10-27/false-report-review-1.json)覆盖 12 字段，[诊断 2](../.local/ja-mistral-test-2026-10-27/false-report-review-2.json)覆盖 11 字段。两份记录均未建立可信的 gold 漏错挑战，也没有修改 gold、成绩或正式数据。

这些是 **POST_UNBLINDING** 诊断，审查者已见模型意见，不能冒充新盲审 gold。诊断中包括要求短词典简释逐字展开所有属性、拒绝合理译词或正常句式、忽略译文已表达的特征等问题；本次没有据这些模型意见追改 gold 或调参重测。两份首轮记录的结论仅覆盖这 23 个案例，不证明整个 gold 无误。

重试新增的 `pilferage.ex.1` 计入最终第 24 个误报，另有[重试新增项独立诊断](../.local/ja-mistral-test-2026-10-27/false-report-review-retry-extra.json)。模型把 `can reduce` 与 `減らせます` 分成“可能性”与“许可或能力”，但独立诊断指出：两句均用改善库存监控和安全保管作为减损手段，日语可能形保持了在这些条件下的可行性，没有增加许可主体、必然性或已发生的结果。该记录也未形成可信 gold 挑战，没有改动 gold 或成绩。三份揭盲后诊断合计覆盖最终 24 个误报字段，仍不构成新的盲审或整个 gold 正确性的证明。

## 事前运行门槛与已确定路由

在查看 Mistral 语义判断前，已通过[运行门槛修订](../.local/ja-mistral-test-2026-10-27/test-plan-amendment-runtime-gate.json)将原先三批直接顺序运行改为条件推进。该修订绑定原计划文件 SHA-256 `9da904e131462b11f879f1c9d85f876d26087ff575faf953f7c7a693540c5b25`。

修订依据是首次调用耗时 **110.77 秒**，生成 **624 tokens**，其中生成阶段 **81.27 秒**。这只是单次测量，不是稳定的每词耗时，也不能保证翻译或复核完整 7,298 词所需的时间。批次长度、输出量、失败重试和加载等开销仍须单独记录。

1. 先完成 Mistral 的旧组回归，在同一修正前快照、同一 gold-v2 上评测。
2. 首轮与最多一次 unavailable-only 重试分别报告；主要路由比较使用相同重试预算后的 model 视图，并同时保留 guarded 结果。
3. 只有真检出增加、错误误放减少或正确字段误报减少中至少一项出现有用改善，且其他语义错误指标及 unavailable 数均不恶化，才继续新组的配对推理。对应 Qwen 重试后参考计数为：真检出 1、错误误放 3、正确字段误报 21、unavailable 6。
4. 满足门槛后，Mistral、Qwen 按计划串行运行同一新组、同一冻结 gold。未满足时停止扩大新模型推理，报告已完成的回归和新 gold 就绪状态，不启动新组模型运行。

这只是决定是否继续投入运行时间的筛选，不是统计显著性结论或词库验收。不得用旧回归调过提示词或模型后再称其为未见测试。无论是否继续推理，新组的独立源文审查与锁定记录均保留。

**最终路由：不扩展到新 100 词的双模型推理。**[本轮重试范围](../.local/ja-mistral-test-2026-10-27/retry-scope.json)仅含 12 个 unavailable 字段、10 个词条，且全部属于 gold 正确字段。四处已知错误的有效 pass 和首轮 23 处有效误报均未被覆盖；重试另增加 1 个误报。与相同有限重试预算后的 Qwen 相比，Mistral 真检出 **0 < 1**，错误误放 **4 > 3**，正确字段误报 **24 > 21**。Unavailable 虽为 **4 < 6**，仍不能抵消其他语义指标恶化。

最终[scope-decision.json](../.local/ja-mistral-test-2026-10-27/scope-decision.json)将 `screenPassed` 记为 `false`，新组 Mistral 和 Qwen 请求数均为 0；没有切换默认复核模型，没有词库文件写入。有限重试已按原预算结束，不再扩展重试或启动新的调参实验。此次停止扩展不改变旧 Qwen 流程此前未通过验收的结论。

## 最终运行状态

| 项目 | 状态 / 实测结果 |
| --- | --- |
| Mistral 旧组首轮 | 100 个记录完成；model / guarded 首轮指标和耗时见上文；语义评分仍 incomplete |
| Mistral 一次有限重试 | 12 字段 / 10 请求；恢复 8 字段，其中 7 正确 pass、1 新增误报；4 仍 unavailable，最终分视图计数见上文 |
| 有限重试及最终总跨度 | 重试 166.391435 秒；最早首轮记录至最后重试 9,500.142685 秒，含阶段间隔 |
| 运行门槛与路由 | 不满足；不启动新组双模型推理 |
| 新组 Mistral 推理 | 未运行，0 请求；召回等模型成绩未测量 |
| 新组 Qwen 配对推理 | 未运行，0 请求；召回等模型成绩未测量 |
| 新组配对模型比较 | 未执行，无胜负结论；830 字段的独立源文 gold 保留 |

本报告保留 selected / scorable 分母、分轮计数和分口径耗时。模型输出可解析、结构守卫通过或运行 exit 0，均不能单独写成语义评测通过。**新组零请求不是 `0/2` 的召回率；它没有模型测量结果。**新组的两个源文确认错误只是已锁 gold 的组成，不能冒充模型漏检数。

## 核心本地证据

[最终结果审计](../.local/ja-mistral-test-2026-10-27/result-audit.json)独立重算了两个阶段的 model / guarded 计数及指标，核对全部 100 次实际请求、813 个保留判断、限定重试、模型与代码摘要、gold 和 230 个正式输入文件，未发现异常。审计通过表示记录与计算一致，Mistral 的语义质量门槛仍然失败。[完整执行汇总](../.local/ja-mistral-test-2026-10-27/execution-summary.json)及[逐字段配对记录](../.local/ja-mistral-test-2026-10-27/paired-field-comparison.json)保留实际范围和各自模型判定。

- [原测试计划](../.local/ja-mistral-test-2026-10-27/test-plan.json)、[运行门槛修订](../.local/ja-mistral-test-2026-10-27/test-plan-amendment-runtime-gate.json)
- [模型核验](../.local/ja-mistral-test-2026-10-27/model-verification.json)、[实际请求公平性](../.local/ja-mistral-test-2026-10-27/actual-input-fairness.json)
- [Mistral 首轮指标](../.local/ja-mistral-test-2026-10-27/metrics-regression-initial.json)、[首轮完整运行与输入审计](../.local/ja-mistral-test-2026-10-27/initial-run-audit.json)、[四处已知错误检查](../.local/ja-mistral-test-2026-10-27/known-error-regression-check.json)、[本轮有限重试范围](../.local/ja-mistral-test-2026-10-27/retry-scope.json)
- [Mistral 最终重试后指标](../.local/ja-mistral-test-2026-10-27/metrics-regression-after-retry.json)、[重试审计](../.local/ja-mistral-test-2026-10-27/retry-run-audit.json)、[最终路由决定](../.local/ja-mistral-test-2026-10-27/scope-decision.json)、[首轮误报诊断 1](../.local/ja-mistral-test-2026-10-27/false-report-review-1.json)、[首轮误报诊断 2](../.local/ja-mistral-test-2026-10-27/false-report-review-2.json)
- [重试新增误报诊断](../.local/ja-mistral-test-2026-10-27/false-report-review-retry-extra.json)
- [新 selection](../.local/ja-semantic-holdout-mistral-2026-10-27/selection.json)、[新 gold](../.local/ja-semantic-holdout-mistral-2026-10-27/gold.json)、[gold 锁](../.local/ja-semantic-holdout-mistral-2026-10-27/independent-review/gold-lock.json)、[九项源文裁决](../.local/ja-semantic-holdout-mistral-2026-10-27/independent-review/source-adjudications.json)
- [旧首轮指标](../.local/ja-semantic-holdout-2026-10-26/metrics-initial.json)、[旧重试后指标](../.local/ja-semantic-holdout-2026-10-26/metrics-after-retry.json)、[旧重试范围](../.local/ja-semantic-holdout-2026-10-26/retry-scope.json)

`.local/` 是本机证据目录；这些相对链接不意味着证据已公开随仓库发布。本轮评测和本文不包含正式词库写入，也不构成全库独立复审完成或部署完成的声明。
