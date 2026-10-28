# Gemma4 12B Q8：同一旧 100 词日文语义复核对照（2026-10-27）

测试完成。Gemma4 Q8 在同一冻结的 100 词上，补试后**检出 1/4 处已知错误、漏放 3 处、误报 17 个正确字段，剩余 unavailable 为 0**。Qwen 同样检出 1/4，但误报 21 个、unavailable 6 个；Mistral 检出 0/4，误报 24 个、unavailable 4 个。Gemma 本次误报和可用性表现更好，尚不足以独立承担全库自动语义验收。

本次总计 107 个实际模型请求。首个记录开始至最后补试记录结束为 **5,107.290595 秒，即 1 小时 25 分 7.29 秒**。正式词库 230 个受监测输入没有漂移，默认复核模型没有切换；运行结束后 Gemma 内存已释放，下载的权重保留。

## 同一输入与计分分母

使用先前 Qwen、Mistral 的同一旧组 **100 词、825 个翻译字段**。冻结 gold-v2 为 **818 正确、4 错误、3 待定**，可评分分母是 822。三个 gold 待定项始终排除，不能算作正确或模型通过。该组保留此前七处修正采用前的日译，属于已知样本回归，不是当前正式译文，也不是新盲集。

- [测试计划](../.local/ja-gemma4-q8-test-2026-10-27/test-plan.json)、[输入绑定](../.local/ja-gemma4-q8-test-2026-10-27/pre-inference-bindings.json)
- [同一 selection](../.local/ja-semantic-holdout-2026-10-26/selection.json)：文件 SHA `f3a1a3692b5034253bcce17169ff3248dd8227951e77c9f206fe84d03cb4ea68`
- [同一旧快照](../.local/ja-semantic-review-2026-10-26/snapshot.json)：文件 SHA `aa024c1a0ff313e050a1e44760ef20f9d4f3ff34fe8d93a13b62e32f420a2c43`
- [同一 gold-v2](../.local/ja-semantic-holdout-2026-10-26/gold-v2.json)：文件 SHA `ecf3a41ca139e2ef5cccb044dac0b35ebcd08f9fa6b73723eab4fb3de4626b13`

旧 gold 的独立源文审查过程和局限见[原报告](ja-semantic-holdout-review-2026-10-26.md)。gold 来自逐字段 Codex 源文审查，不能称为专业人工译审认证；本次没有按 Gemma 输出改分。源文审查 v2 的历史接触边界见[基线审计](../.local/ja-gemma4-q8-test-2026-10-27/baseline-audit.json)。

## 本地模型与相同任务设置

本机实际核验 `gemma4:12b-it-q8_0`，家族 gemma4、GGUF、11.9B、Q8_0，模型包大小 **12,844,772,074 bytes**。完整 digest 为 `41c402fdddc2a87e40a4391caa400961e93786383fbb92a88fc764c333c25322`。参数量和量化标记与[Ollama 官方标签](https://ollama.com/library/gemma4:12b-it-q8_0)一致。本地细节见[核验记录](../.local/ja-gemma4-q8-test-2026-10-27/model-verification.json)。环境为 Apple M1 Pro、32 GiB 统一内存、Ollama 0.32.1，每次仅一个模型驻留。

```json
{"num_ctx":8192,"num_predict":4096,"presence_penalty":0.0,"repeat_penalty":1.0,"seed":42,"temperature":0.1,"top_k":40,"top_p":0.95}
```

任务的 messages、JSON schema（format）、options、stream=true、keep_alive=5m 均与历史请求相同；首轮 100/100 个真实请求已分别与 Qwen、Mistral 核对。Gemma 与 Qwen 显式 `think:false`，Mistral 无 think 字段。Gemma 包内 temperature=1、top_k=64 的默认值被以上固定任务参数覆盖。这是相同设置下的对照，不代表各模型分别调优后的最佳效果。

Gemma 本机 `/api/show` 没有 thinking values 元数据，但含 thinking capability；精确模板为 `{{ .Prompt }}`，由本机原生渲染机制处理，不替换其 tokenizer。Ollama 的思考控制随模型而变，参见[官方说明](https://docs.ollama.com/capabilities/thinking)。模型家族、规模、量化与原生渲染不同，因此本轮不是纯 4-bit / 8-bit 量化消融。

## 必要兼容改动及验证

仅修改本地传输适配器：Gemma4 显式关闭思考；完整、为空的原生 thought 前缀允许规范化，非空、异常或截断通道脱敏后 HOLD。私有思考正文不保存、不显示。此次 107 个调用的 thinking_chars 和 inline_thinking_chars 均为 0，也未发生空前缀规范化。

Adapter SHA 从 `0c64f941694c8a6f09bdd2f9394a493d516e0b8961939f94e804ea27bcb91351` 变为 `50840a64e10e6db156a7b9fef33ecdb75adde0f0b9812e058d99b24416fb532c`。其余三个冻结检测/核心/守卫文件逐字未变；提示词、schema、判定解析与抽样配置未调。离线旧 100 词新旧请求比对也确认 Qwen、Mistral、TranslateGemma 原有请求不变。

**18 项针对性测试和完整 135 项 harness 测试均通过**，前者包含于后者，不能相加。证据含[兼容改动与测试](../.local/ja-gemma4-q8-test-2026-10-27/transport-compatibility-tests.json)、[精确补丁](../.local/ja-gemma4-q8-test-2026-10-27/transport-compatibility.patch)、[首词真实请求核对](../.local/ja-gemma4-q8-test-2026-10-27/actual-input-fairness-smoke.json)。完整首轮与补试审计分别见[initial](../.local/ja-gemma4-q8-test-2026-10-27/initial-run-audit.json)、[retry](../.local/ja-gemma4-q8-test-2026-10-27/retry-run-audit.json)。

## 首轮与一次有限补试

表中“漏放”指 gold error 获准 pass，“误报”指 gold pass 判为 error。“model”是结构及准确引句校验后保留的模型判断；“guarded”另外应用确定性守卫，HOLD 不算检错。全部计数限定 822 个可评分字段，missing 均为 0。

| 模型 / 阶段 | 视图 | 检出 / 4 | 漏放 | 误报 / 818 | 正确 pass | uncertain | unavailable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Qwen 9B Q8 初轮 | model | 0 | 3 | 20 | 784 | 0 | 15 |
| Qwen 9B Q8 初轮 | guarded | 0 | 3 | 20 | 782 | 2 | 15 |
| Qwen 9B Q8 补试后 | model | 1 | 3 | 21 | 791 | 0 | 6 |
| Qwen 9B Q8 补试后 | guarded | 1 | 3 | 21 | 789 | 2 | 6 |
| Mistral 24B Q4 初轮 | model | 0 | 4 | 23 | 782 | 1 | 12 |
| Mistral 24B Q4 初轮 | guarded | 0 | 4 | 23 | 780 | 3 | 12 |
| Mistral 24B Q4 补试后 | model | 0 | 4 | 24 | 789 | 1 | 4 |
| Mistral 24B Q4 补试后 | guarded | 0 | 4 | 24 | 787 | 3 | 4 |
| Gemma4 12B Q8 初轮 | model | 1 | 3 | 15 | 795 | 0 | 8 |
| Gemma4 12B Q8 初轮 | guarded | 1 | 3 | 15 | 793 | 2 | 8 |
| Gemma4 12B Q8 补试后 | model | 1 | 3 | 17 | 801 | 0 | 0 |
| Gemma4 12B Q8 补试后 | guarded | 1 | 3 | 17 | 799 | 2 | 0 |

首轮有 8 个字段的 targetQuote 不匹配原日译，因此未取得有效判断。只对这 8 字段、7 词补试一次；**817 个已有有效字段判定逐字保留**。补试恢复全部 8 字段：6 个正确 pass、2 个新增误报。未对有效 pass/error/uncertain 重新采样，也没有从程序已丢弃的回答中回收分数。范围见[补试清单](../.local/ja-gemma4-q8-test-2026-10-27/retry-scope.json)。

Gemma 最终召回为 1/4=25%，报错精度为 1/18≈5.56%，正确字段误报率 17/818≈2.08%。model 对 822 个可评分字段均有明确判断，**明确判断完整不等于判断正确**。guarded 仍保留 2 个 uncertain。三个独立 gold 待定项未解决，所以校准报告仍为 `status=incomplete`、`passed=false`；运行完成与语义验收通过分开记录。

[Gemma 初轮指标](../.local/ja-gemma4-q8-test-2026-10-27/metrics-regression-initial.json)、[补试后对 Qwen](../.local/ja-gemma4-q8-test-2026-10-27/metrics-regression-after-retry.json)、[补试后对 Mistral](../.local/ja-gemma4-q8-test-2026-10-27/metrics-vs-mistral-after-retry.json)、[三模型逐字段对照](../.local/ja-gemma4-q8-test-2026-10-27/paired-field-comparison.json)。历史指标经[独立重算](../.local/ja-gemma4-q8-test-2026-10-27/baseline-audit.json)，结果与原报告一致。

## 检错理由与仍然漏放的错误

| 原译字段及确认差异 | Gemma | Qwen | Mistral |
| --- | --- | --- | --- |
| impulse.tip：后接动作的语法形式误成继续行为 | error | pass | pass |
| workmanship.tip：中性做工增加“好”的评价 | pass | error | pass |
| saving.ex.0：遗漏 monthly 的一个月期限 | pass | pass | pass |
| bespectacled.ex.0：help find 找到结果变成协助寻找过程 | pass | pass | pass |

[四处源文与公开理由复核](../.local/ja-gemma4-q8-test-2026-10-27/known-error-review-initial.json)确认 Gemma 的 impulse 检错确实指向该语法关系，属于有效命中；其余三处未识别对应源义。四条均是有效判定，按补试规则原样保留。Gemma 和 Qwen 的检出位置不同；三模型都批准 saving 与 bespectacled，不能把模型一致当作正确性证明。

首轮 15 项误报已经逐项对照源文与完整日译复核，未发现可信的 gold challenge。诊断分为术语断言 3 项、多义与词条语境 6 项、构文或文风偏好 4 项、忽略目标已存在内容 2 项。例如 `site.senses.2` 已同时译出「置く；建てる」，模型仍称漏译 place；`weather.ex.1` 句末已有「可能性がある」，模型只看句中「妨げ、」便声称漏译 can。

见[首轮 15 项公开理由诊断](../.local/ja-gemma4-q8-test-2026-10-27/false-report-review-initial.json)。这是揭盲后的源文诊断，不是重新定义 gold，也不能改成模型自行通过验收。

补试新增的 `impose.ex.1` 与 `review.ex.0` 两项也已对照完整源译独立诊断，均不支持模型的报错，未提出可信的 gold challenge。前者将「ことがあります」绝对限定为习惯频率，后者忽略句中「書評を読んで」已有的外部促因。见[新增 2 项复核](../.local/ja-gemma4-q8-test-2026-10-27/false-report-review-retry-extra.json)。全部 17 项均已覆盖，gold 与主指标保持原状。

## 实测耗时与资源口径

| 口径 | Gemma4 Q8 实测 |
| --- | ---: |
| 首轮真实请求 / 记录 | 100 / 100 |
| 首轮记录跨度 | 4,986.477948 秒，约 1 小时 23 分 6.48 秒 |
| 补试真实请求 / 含复用的记录 | 7 / 100 |
| 补试记录跨度 | 93.164781 秒 |
| 首条开始到最后补试结束 | 5,107.290595 秒，约 1 小时 25 分 7.29 秒 |
| 实际请求 wall latency 合计 | 5,068.040849209 秒 |
| 首轮生成 tokens / eval 耗时 | 53,568 / 4,517.449609 秒 |
| 首轮生成吞吐 | 11.8580 tokens/s |

同口径历史 Qwen 为 1 小时 28 分 47.95 秒，Mistral 为 2 小时 38 分 20.14 秒。记录跨度包括加载与中间间隔，不包括下载和事前适配工作；不能把它当成纯计算耗时。模型输出长度、tokenizer 与桌面环境也不同，不能根据单次运行外推全库时间。

[运行中单时点快照](../.local/ja-gemma4-q8-test-2026-10-27/runtime-initial-running.json)记录只有 Gemma 驻留、context=8192，Ollama size/size_vram 同为 13,339,711,240 bytes。统一内存下它们不能相加，也不是峰值或完整进程 RSS；全局交换空间不能归因于本测试。结束状态见[执行摘要](../.local/ja-gemma4-q8-test-2026-10-27/execution-summary.json)。

## 采用边界

本组 Gemma 在相同检出数下少 4 个误报，且补试后没有 unavailable；这支持把它视为一个有用的复核候选。它依然批准了 3/4 处确认错误，不能独立自动放行全库。默认模型及正式词库保持原状，本次未启动新 100 词或全库推理。

只有 4 个确认错误，单个判定就改变召回 25 个百分点，且没有 critical 样本。旧组已经参与诊断，模型来源不同不代表独立真值；本结果不能外推全库准确率，也不能代替新材料上的独立源文复审。

最终数据链、指标重算及证据审计见[独立结果审计](../.local/ja-gemma4-q8-test-2026-10-27/result-audit.json)。完整性审计通过不等于模型语义验收通过。
