# Gemma4 Q8：新版提示词与旧参数对照回归（2026-10-27）

本轮只测试一个冻结候选：**新版提示词＋旧版八键参数**。目的在于补齐已有两组之间的受控比较，查看新版提示词在旧参数下的表现。C 组已完成 100 词及一次有限补试，最终 **TP 1/4、全部未检出 3、误报 21、model uncertain/unavailable 0/0**。其误报仍比 A 多 4，与 B 总数相同，但 B/C 的 6 个可评分字段状态不同。**候选未通过改进筛选，不切换默认配置；目前这组证据支持继续保留 A。**

此前 A 组“旧提示词＋旧参数”补试后检出 1/4、误报 17；B 组“新提示词＋新参数”检出仍为 1/4、误报增至 21，联合候选已拒绝。本轮不修改新版提示词、gold、schema、parser、guard 或正式词库，也不在同组上反复调到通过。

依据：[本轮计划](../.local/ja-gemma4-prompt-only-test-2026-10-27/test-plan.json)、[推理前绑定](../.local/ja-gemma4-prompt-only-test-2026-10-27/pre-inference-bindings.json)、[A 组报告](ja-gemma4-q8-evaluation-2026-10-27.md)、[B 组报告](ja-gemma4-optimized-evaluation-2026-10-27.md)。

## 三组设置与比较口径

| 组别 | system prompt | 参数 | 补试后 model TP / 4 | 全部未检出 | FP / 818 | model uncertain / unavailable |
| --- | --- | --- | ---: | ---: | ---: | --- |
| A | 旧版 | 旧版 | 1 | 3 | 17 | 0 / 0 |
| B | 新版 `gemma-audit-v1` | 新版 | 1 | 3 | 21 | 0 / 0 |
| C，本轮 | 与 B 相同 | 与 A 精确相同 | 1 | 3 | 21 | 0 / 0 |

**主比较为 C vs A**：固定旧参数，比较 system prompt。**次比较为 C vs B**：固定新版 prompt，比较采样参数组合。A vs B 同时改变提示词和参数。实际归档请求和实现约束审计均已通过：C/A 只有 system 不同，C/B messages/schema 相同，八键参数与 A 完全一致。该结论由真实请求支持。

缺少“旧提示词＋新参数”第四格，因此不能估计完整的提示词与参数交互，也不能从 C vs B 单独归因 temperature。固定 seed 的单次运行提供同组开发证据，不能证明稳定的总体因果效应。

## 相同输入与分母

三组沿用同一[旧 selection](../.local/ja-semantic-holdout-2026-10-26/selection.json)、[修正前 snapshot](../.local/ja-semantic-review-2026-10-26/snapshot.json)及[gold-v2](../.local/ja-semantic-holdout-2026-10-26/gold-v2.json)：**100 词、825 个翻译字段，818 个 gold pass、4 个 error、3 个 uncertain；可评分分母为 822**。3 个独立存疑 gold 始终排除，不算作正确、错误或模型通过。

该快照保留此前修正采用前的日译，与当前正式词库不同。这组材料及诊断已揭盲，是开发回归；不能称为新盲评、全库准确率估计或专业人工译审认证。4 处确认错误含 3 处 major、1 处 minor，没有 critical 样本。严重度只来自冻结 gold，不增加模型 severity 输出。

## 本轮冻结配置

C 使用独立采样 preset `gemma-audit-v1-baseline`，共享 prompt variant 仍为 `gemma-audit-v1`。两者在计划和协议中分列，保留 B 的 preset，不覆盖历史配置。模型固定为 `gemma4:12b-it-q8_0`、11.9B、Q8_0；权重、原生模板及 Ollama 0.32.1 与前两组相同，见[本轮模型核验](../.local/ja-gemma4-prompt-only-test-2026-10-27/model-verification.json)。

请求顶层保持 `think:false`、`stream:true`、`keep_alive:"5m"`。C 的 `options` 精确复用 A 的八键：

```json
{"num_ctx":8192,"num_predict":4096,"presence_penalty":0.0,"repeat_penalty":1.0,"seed":42,"temperature":0.1,"top_k":40,"top_p":0.95}
```

`min_p` 与 `frequency_penalty` 均不出现在 C 的请求 options 中。B 的 temperature=1.0、top_k=64，并显式设置这两个零值参数；其余上述设置相同。本轮比较的是预先固定的参数组合，不单独检验某一个参数。

新版 system 的原始 UTF-8 SHA 保持 `e01bf247ce188b4fb7cd6bcb96af7bd260165d232c9a3712c320ff8bb6d9943d`，canonical JSON 字符串 SHA 为 `7e7b1924942157326a5a092acc719464174d62bee3742a4db4ef84196908bc3a`。它与 B 完全相同，没有本轮新增例题、词条规则或目标答案。保存 prompt 文件的 SHA 另记，包含文件末尾换行，不与上述字符串散列混用。

| 冻结项目 | SHA-256 |
| --- | --- |
| 测试计划原始文件 | `2857671dce94c31ff67c634d9585d3e382f2bd00cab5f27929b50a6541515e6c` |
| C / A 八键 options，canonical JSON | `29b97ba70d3835d5a5d7908541b6272dba1380e9e9e12e454dcd199193622353` |
| 保存的 prompt 原始文件 | `dd9cd3bd34b0b1cb9a032f43e6be5390c26f607626ef1bacf5b9454a5c7fee59` |
| CLI 原始文件 | `2e4e0224f059f5e769aebd85ca0786460caf6ff86397aebf7f9f20c46e8ab357` |
| models 原始文件 | `626277fcf298a03d8c569bfee30eab364db93319195c53f41ed06ffe266ad95e` |

[推理前绑定](../.local/ja-gemma4-prompt-only-test-2026-10-27/pre-inference-bindings.json)记录：全部 100 词的构造 payload 与 A 只在 system 不同；与 B 的 messages、schema 相同；覆盖 825 个翻译字段。user 内容、六键 schema、parser、精确引句校验、guard 及隐私处理保持原行为。161 项离线测试通过；这些验证证明构造与配置隔离，不证明模型遵守提示词或语义质量改善。C 的 100 个首轮实际归档请求逐项核对通过，见[首轮审计](../.local/ja-gemma4-prompt-only-test-2026-10-27/initial-run-audit.json)和[首词请求证据](../.local/ja-gemma4-prompt-only-test-2026-10-27/actual-input-fairness-smoke.json)。

## 一次有限补试与审计约束

初轮 lane 为 `detect-gemma4-q8-prompt-only-20261027`，唯一补试 lane 为 `detect-gemma4-q8-prompt-only-retry-20261027`。每轮绑定同一完整有序选择集、同一权重、prompt、profile、源码和推理合同；只允许一次 unavailable-only 补试。已有有效 pass/error/uncertain 的完整 assessment 对象必须原样保留，不因新一轮请求而改变解释、引句或判断。

初轮对初轮、补试后对补试后比较，model 与 guarded 分列。模型请求数与复制检查点分开，补试 lane 的 100 条记录不能自动算作 100 次推理。缺记录、合同漂移、有效判定丢失、私有正文泄露或生产文件漂移，应拒绝完整性审计；不能为得到可用结果放松门槛。终态未齐 100 词前不产完整报告。

[补试审计](../.local/ja-gemma4-prompt-only-test-2026-10-27/retry-run-audit.json)通过。首轮 2 个字段未通过准确引句校验，按[范围清单](../.local/ja-gemma4-prompt-only-test-2026-10-27/retry-scope.json)补试 2 次，均恢复为误报。全部 825 个翻译字段中的 **823 个既有有效 assessment 对象逐字保留**，包含 820 个可评分字段及 3 个 gold 待定字段；不能把 823 与评分分母 822 混用。补试 100 条检查点中 98 条没有模型请求，实际共 102 次调用。保留档案中 thinking/inline-thinking 字符数均为 0。旧 artifacts/gold 及 230 个正式输入文件散列均未漂移。正式词库与默认复核配置的任何采用变更均不属于本次自动操作范围。

## 首轮与补试后成绩

下表均限 822 个可评分字段。TP 为 gold error 判 error；“全部未检出”为 `4−TP`，包括 pass、uncertain、unavailable；“漏放”仅指 gold error 被判 pass。误报分母为 818 个 gold pass。HOLD 不计为检错，不能用总体真通过数掩盖错误漏检。

| 组别 / 阶段 | 视图 | TP / 4 | 全部未检出 | 漏放 | FP / 818 | 真通过 | uncertain | unavailable |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A 初轮 | model | 1 | 3 | 3 | 15 | 795 | 0 | 8 |
| A 补试后 | model | 1 | 3 | 3 | 17 | 801 | 0 | 0 |
| A 初轮 | guarded | 1 | 3 | 3 | 15 | 793 | 2 | 8 |
| A 补试后 | guarded | 1 | 3 | 3 | 17 | 799 | 2 | 0 |
| B 初轮 | model | 1 | 3 | 3 | 19 | 796 | 0 | 3 |
| B 补试后 | model | 1 | 3 | 3 | 21 | 797 | 0 | 0 |
| B 初轮 | guarded | 1 | 3 | 3 | 19 | 794 | 2 | 3 |
| B 补试后 | guarded | 1 | 3 | 3 | 21 | 795 | 2 | 0 |
| C 初轮 | model | 1 | 3 | 3 | 19 | 797 | 0 | 2 |
| C 补试后 | model | 1 | 3 | 3 | 21 | 797 | 0 | 0 |
| C 初轮 | guarded | 1 | 3 | 3 | 19 | 795 | 2 | 2 |
| C 补试后 | guarded | 1 | 3 | 3 | 21 | 795 | 2 | 0 |

基线来源：[A 初轮](../.local/ja-gemma4-q8-test-2026-10-27/metrics-regression-initial.json)、[A 补试后](../.local/ja-gemma4-q8-test-2026-10-27/metrics-regression-after-retry.json)、[B 初轮](../.local/ja-gemma4-optimized-test-2026-10-27/metrics-initial.json)、[B 补试后](../.local/ja-gemma4-optimized-test-2026-10-27/metrics-after-retry.json)。A、B 最终均只检出 `impulse.tip`；其余三处仍判 pass。C 的完整生成结果和[四处公开理由确认](../.local/ja-gemma4-prompt-only-test-2026-10-27/known-error-review-initial.json)也相同：仅 `impulse.tip` 的理由准确指出语法关系错义；月度期限、做工评价极性、找到结果与寻找过程三个差异仍未识别。

C 的召回为 `1/4=25%`，报错精度 `1/22≈4.55%`，正确字段误报率 `21/818≈2.57%`；A 对应为 25%、约 5.56%、约 2.08%。major 3 处只检出 1 处、漏放 2 处；minor 1 处仍漏放。model 对正确 gold 的 uncertain/unavailable 均为 0，guarded 仍有 2 个 uncertain。完整指标见[初轮](../.local/ja-gemma4-prompt-only-test-2026-10-27/metrics-initial.json)、[补试后对 A](../.local/ja-gemma4-prompt-only-test-2026-10-27/metrics-after-retry.json)、[补试后对 B](../.local/ja-gemma4-prompt-only-test-2026-10-27/metrics-vs-joint-after-retry.json)。3 个 gold uncertain 仍排除，所以校准为 incomplete/passed=false；运行完成与语义验收分开。

## 预先约定的筛选与源文确认

主采用筛选仍相对于 A：完整性审计通过后，补试后 **model** 必须同时满足 **TP ≥ 2、FP ≤ 16、错误放行 ≤ 2、可评分 uncertain = 0、unavailable = 0**。门槛与上一轮相同，不根据 C 的分数调整。这是开发候选筛选，不是统计显著性或全库验收线。

数值 TP 与公开理由是否指出原 gold 差异分别记录。新增检错须对照完整源译确认，不能用同字段上的无关问题冒充已知错误命中。类别措辞可以不同，但具体实质差异必须一致。可信 gold 疑点另列，不静默改标签或重算历史指标。

还须分别配对 C vs A、C vs B：列出原误报 error→pass、error→uncertain/HOLD、error→unavailable、仍为 error，以及新增误报。只有 error→pass 算作误报恢复。错误字段转为 uncertain/unavailable 仍属于未检出。[相对 A 的逐字段配对](../.local/ja-gemma4-prompt-only-test-2026-10-27/paired-analysis.json)记录：旧 17 个误报中 3 个恢复为 pass、14 个仍为 error，另新增 7 个误报，`17−3+7=21`，无 error→HOLD 或 unavailable。已知错误仍为 1 个 error、3 个 pass。

[相对 B 的配对](../.local/ja-gemma4-prompt-only-test-2026-10-27/paired-vs-joint-analysis.json)记录：3 个 B 误报恢复为 pass，另 3 个 B 正确字段变成 error，18 个误报保留。因此总误报数同为 21，不能说逐字段判定完全相同，更不能凭相同总分宣称采样没有影响。

[C 初轮 19 项诊断](../.local/ja-gemma4-prompt-only-test-2026-10-27/false-report-review-initial.json)与[补试 2 项诊断](../.local/ja-gemma4-prompt-only-test-2026-10-27/false-report-review-retry-extra.json)覆盖全部 21 个最终误报，均不支持模型报错，未提出可信的 gold challenge。例如 `quarterly.ex.1` 的日译已有「新たな」，模型仍声称未译 emerging；`bespectacled.ex.1` 把日语「の」机械限定为英文 of，忽略了「の」也可表达场所关系。所有原始状态及主指标原样保留。

[恢复项复核](../.local/ja-gemma4-prompt-only-test-2026-10-27/recovered-false-report-review.json)分开确认了相对 A 的 3 项、相对 B 的另 3 项，均忠实于完整源文；六项完整 C assessment 对象均与 C 首轮逐字一致。这些是揭盲后的源文诊断，不是独立新盲测，也没有据此改动 gold。

预定筛选中，C 的 TP 1 未达到 ≥2、FP 21 未达到 ≤16、错误放行 3 未达到 ≤2；model uncertain=0、unavailable=0 两项符合。三项质量条件失败，候选判定 **REJECTED**，未采用为默认。

## 耗时、服务与结束状态

| 口径 | A | B | C |
| --- | ---: | ---: | --- |
| 首轮实际请求 | 100 | 100 | 100 |
| 补试实际请求 | 7 | 3 | 2 |
| 总实际请求 | 107 | 103 | 102 |
| 首轮记录跨度，秒 | 4,986.477948 | 4,847.702431 | 5,100.891978 |
| 补试记录跨度，秒 | 93.164781 | 38.454312 | 29.536528 |
| 首条开始至最后补试结束，秒 | 5,107.290595 | 4,925.266515 | 5,173.732470 |
| 实际请求 wall latency 合计，秒 | 5,068.040849209 | 4,862.836401869 | 5,112.089779792 |
| 首轮生成 tokens | 53,568 | 51,905 | 52,256 |
| 首轮 eval 吞吐，tokens/s | 11.8580 | 11.9169 | 12.1992 |

历史时间来源：[A 执行摘要](../.local/ja-gemma4-q8-test-2026-10-27/execution-summary.json)、[B 执行摘要](../.local/ja-gemma4-optimized-test-2026-10-27/execution-summary.json)。记录跨度、请求 wall latency 和 eval 吞吐口径不同，不能相互替代。

本轮开始时原 Ollama 服务未运行，由任务启动并持有服务（会话 33171），版本仍为 0.32.1。结束时已释放模型并确认 `PS=[]`，随后关闭本轮自启的服务，并验证 127.0.0.1:11434 端口关闭。没有停止用户的其他模型进程；模型权重保留。证据见[结束状态](../.local/ja-gemma4-prompt-only-test-2026-10-27/runtime-after.json)。

服务启动状态、模型加载、调用等待、中间间隔及桌面内存状态可能与 A、B 不同。须按时间戳界定服务启动是否位于各项时间口径内；这里的运行不是纯模型性能基准，也不能单凭跨度变化认定提示词使模型更快、外推全库耗时或把全局 swap 归因于本测试。C 的记录跨度约 **1 小时 26 分 13.73 秒**；[单时点资源快照](../.local/ja-gemma4-prompt-only-test-2026-10-27/runtime-running.json)不是峰值内存，完整结束结果见[执行摘要](../.local/ja-gemma4-prompt-only-test-2026-10-27/execution-summary.json)。

## 本轮结果与采用边界

C 已完成全批及一次 U-only 补试，生成数据链检查通过，双指标改进筛选未通过。旧参数下更换为新版提示词，本组误报从 17 增为 21，漏检保持 3；新版提示词下，两套参数总分相同，但局部判定不同。这个受控对照未显示新版提示词的质量优势，默认保留旧提示词＋旧参数。三套配置及所有原始记录保留用于复现，没有改写正式词库。

即使 C 在该组数值改善，也只能支持已揭盲样本上的开发结果，仍需在未参与调优的新材料上独立检验。三组不是完整因子设计；只有 4 处确认错误，单个判定就改变召回 25 个百分点。本次不启动新盲集或全库推理，不把输出完整或模型一致当作语义正确性证明。

最终独立数据及报告审计见[结果审计](../.local/ja-gemma4-prompt-only-test-2026-10-27/final-result-audit.json)。
