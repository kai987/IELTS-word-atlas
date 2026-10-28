# Gemma4 Q8 复核优化：旧 100 词联合调优回归（2026-10-27）

测试完成，**本轮候选未改善，不采用**。一次有限补试后，检出仍是 1/4、全部未检出仍是 3 处，误报从旧 Gemma 的 17 增至 21。新版消除 5 个旧误报，却新增 9 个；没有通过事前约定的联合筛选，默认配置保持原状。

本轮冻结一个 `gemma-audit-v1` prompt 与采样参数的联合候选，再测同一旧 100 词。样本及诊断已揭盲；这是开发回归，不是新盲测。源码和候选作为可复现实验保留，不自动启用该 preset。正式词库未修改，运行结束已释放模型内存。

依据：[测试计划](../.local/ja-gemma4-optimized-test-2026-10-27/test-plan.json)、[推理前冻结证据](../.local/ja-gemma4-optimized-test-2026-10-27/pre-inference-bindings.json)、[参数依据](../.local/ja-gemma4-optimized-test-2026-10-27/parameter-rationale.json)、[离线一致性审计](../.local/ja-gemma4-optimized-test-2026-10-27/offline-prompt-parity.json)。候选在首次生成前已冻结，运行中未根据分数调参；原草稿仅使用基线与输入证据，最终数值来自完整推理记录。

## 固定输入与候选

沿用[旧 selection](../.local/ja-semantic-holdout-2026-10-26/selection.json)、[旧源文及日文 snapshot](../.local/ja-semantic-review-2026-10-26/snapshot.json)和[冻结 gold-v2](../.local/ja-semantic-holdout-2026-10-26/gold-v2.json)：100 词、825 个翻译字段，818 pass、4 error、3 uncertain。评分分母为 **822**；3 个独立审查仍存疑的 gold 字段单列，不计为正确或错误，不因模型结果修改原标签。

[模型身份核验](../.local/ja-gemma4-optimized-test-2026-10-27/model-verification.json)记录 `gemma4:12b-it-q8_0`、11.9B、Q8_0、Ollama 0.32.1；权重与原生模板均和旧 Gemma 基线相同。模型 digest 为 `41c402fdddc2a87e40a4391caa400961e93786383fbb92a88fc764c333c25322`。初轮 lane 为 `detect-gemma4-q8-optimized-v1-20261027`，唯一重试 lane 为 `detect-gemma4-q8-optimized-v1-retry-20261027`。

## 改动及保持一致的部分

新 system prompt 使用通用源文审查原则：先读完整源句与完整译句，再检查全部重要信息；按词性和词条语境消歧；保留时间、数量、边界、否定、情态、过程与结果及语法说明的关系；容许自然日语省略、惯用表达和简短词典义；报错必须指出实际丢失、矛盾或擅加的含义。引句必须是同字段的连续原文子串，uncertain 必须说明具体未决歧义，不能替代可确认的 error。实现见[模型适配与 prompt](../scripts/atlas/ja_review_models.py)。

| 参数 | 旧 Gemma 基线 | `gemma-audit-v1` |
| --- | --- | --- |
| temperature | 0.1 | 1.0 |
| top_k | 40 | 64 |
| top_p | 0.95 | 0.95 |
| min_p / frequency_penalty | 未显式设置 | 0.0 / 0.0 |
| presence_penalty / repeat_penalty / seed | 0.0 / 1.0 / 42 | 相同 |
| num_ctx / num_predict | 8192 / 4096 | 相同 |
| think / keep_alive / stream | false / 5m / true | 相同 |

新的 temperature、top_p、top_k 采用 Google 的一般采样建议，作为待验证候选；中性惩罚和预算保持见[参数依据](../.local/ja-gemma4-optimized-test-2026-10-27/parameter-rationale.json)。官方通用建议不证明适合本任务，较高温度也可能增加判断波动；Ollama 对结构化输出另建议较低温度以提高确定性，结构稳定与语义准确需要分别测量。[Gemma 4 官方模型卡](https://ai.google.dev/gemma/docs/core/model_card_4)、[Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)

**user 内容、六键 JSON schema、parser、精确引句校验、guard 和通道隐私处理不变；不新增模型 severity 输出。** 离线审计逐一核对全部 100 词，确认旧默认 messages/schema 未改，新候选的 user/schema 也与旧版一致；默认 Qwen、TranslateGemma、Mistral 路径及历史 presets 保持原行为。共 155 项离线测试通过，见[冻结记录](../.local/ja-gemma4-optimized-test-2026-10-27/pre-inference-bindings.json)和[测试日志](../.local/ja-gemma4-optimized-test-2026-10-27/final-harness-tests.log)。这些检查证明构建与隔离，不证明模型遵守指令或语义质量提高。

审计未发现样本 ID 分支、目标答案或 gold 状态注入；prompt 是静态常量。设计受已揭盲诊断启发，静态检查不能排除概念上的过拟合。prompt 从 1801 增至 3719 字符；首轮实际单请求最大输入 1,194 tokens、最大输出 663 tokens、同次输入输出合计最大 1,853 tokens，均未触及预算。字符数和 backend token 数不能代替运行峰值内存。

## 冻结与一次重试

[CLI 协议绑定](../scripts/atlas/review-ja-corpus.py)仅对新 preset 生效：冻结 system 散列、schema builder 源码、四个相关脚本、实际 profile/options、模型 digest、原生模板、snapshot 及有序选择集；初轮与重试以同一 `inferenceContractSha256` 绑定。重试只处理 unavailable，已有有效 pass/error/uncertain 保留；禁止混入旧基线、改另一集合、从重试继续重试或另建第二个重试 lane。恢复已终结的重试词条不会发第二次请求，重试 error 也不追加补试。

推理前冻结的关键散列如下；canonical JSON 字符串散列与原始 UTF-8 散列刻意分开标示，完整证据见[bindings](../.local/ja-gemma4-optimized-test-2026-10-27/pre-inference-bindings.json)。

| 项目 | SHA-256 |
| --- | --- |
| 测试计划原始文件 | `3d2c457c05b4cd11edc9749b35f5924b586bd9fa3e472a97a75a2b7d7fa55786` |
| system 原始 UTF-8 | `e01bf247ce188b4fb7cd6bcb96af7bd260165d232c9a3712c320ff8bb6d9943d` |
| system canonical JSON 字符串 | `7e7b1924942157326a5a092acc719464174d62bee3742a4db4ef84196908bc3a` |
| CLI 原始文件 | `0acf9807ebd00c30cc3a9abfc508e112e0fdb785c81aa2fbc4410f79ed94b8b6` |
| models 原始文件 | `ca654e29860a2f41687b718156bd8aa4d8fa94ff9101b282f27c953130c0bae0` |

## 基线与优化版成绩

下表限 822 个可评分字段。“漏放”是 gold error 被判 pass；“全部未检出”是 `4−TP`，包括判为 uncertain/unavailable 的错误，不能只报漏放来美化召回。model 指通过结构及引句校验后保留的模型判断，guarded 指程序规则介入后的判断，HOLD 不算模型检出。

| 配置 / 阶段 | 视图 | TP / 4 | 全部未检出 | 漏放 | 误报 / 818 | 真通过 | uncertain | unavailable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 旧 Gemma 初轮 | model | 1 | 3 | 3 | 15 | 795 | 0 | 8 |
| 旧 Gemma 重试后 | model | 1 | 3 | 3 | 17 | 801 | 0 | 0 |
| 旧 Gemma 初轮 | guarded | 1 | 3 | 3 | 15 | 793 | 2 | 8 |
| 旧 Gemma 重试后 | guarded | 1 | 3 | 3 | 17 | 799 | 2 | 0 |
| 优化版初轮 | model | 1 | 3 | 3 | 19 | 796 | 0 | 3 |
| 优化版重试后 | model | 1 | 3 | 3 | 21 | 797 | 0 | 0 |
| 优化版初轮 | guarded | 1 | 3 | 3 | 19 | 794 | 2 | 3 |
| 优化版重试后 | guarded | 1 | 3 | 3 | 21 | 795 | 2 | 0 |

基线依据：[初轮指标](../.local/ja-gemma4-q8-test-2026-10-27/metrics-regression-initial.json)、[重试后指标](../.local/ja-gemma4-q8-test-2026-10-27/metrics-regression-after-retry.json)、[旧 Gemma 完整报告](ja-gemma4-q8-evaluation-2026-10-27.md)。基线最终没有 unavailable，但仍漏放 3 个已知错误并误报 17 个正确字段；完整输出不能替代语义验收。

## 预先约定的联合改进筛选

在完整覆盖、协议与输入审计通过后，最终 **model** 视图须同时满足：TP ≥ 2、误报 ≤ 16、漏放 ≤ 2、可评分字段 uncertain = 0、unavailable = 0。门槛来自推理前[计划](../.local/ja-gemma4-optimized-test-2026-10-27/test-plan.json)，不随结果调整。这只是开发候选筛选，不是统计显著性或全库验收线。

须配对查看每字段的状态转移：正确字段的 error→pass 才是误报恢复，error→uncertain 是 HOLD；错误字段转为 uncertain/unavailable 仍未检出。新增 error 理由需逐项对准原源文差异，不能把同字段上的无关理由算作已知错误的解释命中。重大/轻微漏检分组只取冻结 gold 的 severity，不能当成模型预测等级；可信 gold 疑点另列，原测量口径保持不动。

## 运行证据、状态转移与采用结论

[首轮完整输入审计](../.local/ja-gemma4-optimized-test-2026-10-27/initial-run-audit.json)和[补试审计](../.local/ja-gemma4-optimized-test-2026-10-27/retry-run-audit.json)均通过：100 个首轮请求的词条 user 内容及 schema 与旧版相同，实际 system/options 对应冻结候选，同一权重与原生模板；私有通道仅保留数量，103 次调用记录的 thinking 与 inline-thinking 字符数均为 0。完整性通过不等于模型质量通过。

首轮 3 个引句校验失败字段仅补试一次，实际增加 3 个请求；**全部 825 个翻译字段中，822 个既有有效 assessment 对象逐字保留**，其中包含 3 个 gold 待定字段；对应可计分的保留字段是 819。它与最终可计分分母 822 含义不同。3 字段恢复为 1 个正确 pass、2 个误报，没有剩余 uncertain 或 unavailable（model 视图）。补试生成 100 条检查点，其中 97 条没有调用模型，不能误算为 100 次补试。

根据[逐字段配对分析](../.local/ja-gemma4-optimized-test-2026-10-27/paired-analysis.json)：

| 旧 Gemma 补试后 → 本候选补试后 | 字段数 |
| --- | ---: |
| 旧 17 个误报中的 error→pass | 5 |
| 旧误报转 uncertain / unavailable | 0 / 0 |
| 旧误报仍为 error | 12 |
| 原先正确 pass 新增 error | 9 |
| 已知错误 error→error / pass→pass | 1 / 3 |

因此最终误报为 `17−5+9=21`，净增 4，未用 HOLD 隐藏误报。最终检错召回仍为 `1/4=25%`；报错精度从 `1/18≈5.56%` 降为 `1/22≈4.55%`；正确字段误报率从 `17/818≈2.08%` 升为 `21/818≈2.57%`。三处确认错误依旧判 pass，所有未检出不能因输出完整而忽略。

按冻结 gold 的 severity 分组，major 3 处中仅检出 1 处、漏放 2 处；minor 1 处未检出。等级仅来自独立 gold，不是模型预测。四处逐项[源文理由确认](../.local/ja-gemma4-optimized-test-2026-10-27/known-error-review-initial.json)表明，候选仍仅指出 `impulse.tip` 的语法关系差异；`saving.ex.0` 的月度期限、`workmanship.tip` 的评价极性、`bespectacled.ex.0` 的结果/过程差异仍未指出。分类计数与公开理由命中保持分开核验。

[初轮 19 项误报诊断](../.local/ja-gemma4-optimized-test-2026-10-27/false-report-review-initial.json)和[补试新增 2 项诊断](../.local/ja-gemma4-optimized-test-2026-10-27/false-report-review-retry-extra.json)已覆盖全部 21 个最终误报，未提出可信的 gold challenge。这里的“补试新增”指本轮从 unavailable 恢复为 error，并不等于全部是相对旧版本新生的误报。

`quarterly.ex.1`、`driving.ex.1` 的公开解释甚至承认可判 pass，status 却仍是 error；按既有结构化契约保留原始状态计分，没有根据解释事后改成 pass 或 HOLD。源文诊断说明仍有局部取义、强加典型属性、术语或构文偏好等误报来源。

[恢复为 pass 的 5 项源文确认](../.local/ja-gemma4-optimized-test-2026-10-27/recovered-false-report-review.json)也全部完成，均为忠实恢复，并且完整保留首轮有效判定。所有这些分析都在调优和揭盲后进行，独立于生成阶段，但不是新盲评；原 gold、原判断及主指标均未改。

联合筛选实测为：TP 1 未达到 ≥2，误报 21 未达到 ≤16，漏放 3 未达到 ≤2；model uncertain=0 和 unavailable=0 两项符合。**三项质量条件失败，候选判定 REJECTED。** 原[初轮指标](../.local/ja-gemma4-optimized-test-2026-10-27/metrics-initial.json)、[补试后指标](../.local/ja-gemma4-optimized-test-2026-10-27/metrics-after-retry.json)均保留，没有变更 gold 或事后放宽门槛。

## 耗时、资源及结束状态

| 时间或调用口径 | 实测 |
| --- | ---: |
| 首轮记录跨度 / 真实请求 | 4,847.702431 秒 / 100 |
| 补试记录跨度 / 真实请求 | 38.454312 秒 / 3 |
| 首条开始至最后补试结束 | **4,925.266515 秒，1 小时 22 分 5.27 秒** |
| 实际请求 wall latency 合计 | 4,862.836401869 秒 |
| 首轮生成 tokens / 生成耗时 | 51,905 / 4,355.562556 秒 |
| 首轮生成吞吐 | 11.9169 tokens/s |

旧 Gemma 同口径为 1 小时 25 分 7.29 秒。记录跨度包括加载及中间间隔，不包括事前编码和离线验证；tokenizer、输出长度与桌面环境影响速度，不能根据这次差异推算全库时间或认定某个参数使模型更快。[单时点运行快照](../.local/ja-gemma4-optimized-test-2026-10-27/runtime-running.json)不是峰值内存记录，全局 swap 不能归因于本次测试。

[执行摘要](../.local/ja-gemma4-optimized-test-2026-10-27/execution-summary.json)记录 103 次实际请求、模型内存已释放、权重保留，230 个正式输入文件没有漂移，旧基线、snapshot、selection 和 gold 的绑定散列均未改。最终校准仍为 `incomplete`、`passed=false`，另有 3 个 gold uncertain 未解决；完整运行和模型判断覆盖率不等于语义验收。

prompt 与参数同时改变，差异只能归于整个联合候选，不能单独归因“更长 prompt”或“更高温度”。本轮失败不证明官方通用采样建议在所有任务中无效；它只表明这套组合在本次同组回归上没有达到目标。保留原配置，候选仅供复现研究；本次未启动新盲集或全库推理。

4 个确认错误不足以外推全库准确率或残余错误量；gold 是独立 Codex 源文审查，非专业人工认证。即使将来开发回归的数值改善，也仍需在未参与调优的新材料上独立检验。

最终证据审计见[独立结果审计](../.local/ja-gemma4-optimized-test-2026-10-27/final-result-audit.json)。
