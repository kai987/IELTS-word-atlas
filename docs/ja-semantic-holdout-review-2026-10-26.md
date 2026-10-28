# 日文词库独立语义审查：100 词冻结批次（2026-10-26）

本批完成了 **100 个词条、825 个译文字段**的两遍源文审查，已采用 **4 处确认错误修复、3 处保守澄清**。冻结原译的 v2 标签仍为 **818 pass、4 error、3 uncertain**，修订后的本批字段另有独立接受记录。Qwen 经一次有限重试只检出 1/4 处确认错误，误报 21 个正确字段，**未达到扩大全库自动复审的质量条件**。

这是一批 Codex 源文语义审查记录，不是专业人工译审认证，也不代表全库复审完成。全库 7,298 词中，**7,198 词、59,562 个语义字段**未纳入本批完整双遍审查及采用记录。不能用本批的少量错误数推算全库准确率。

## 范围与冻结证据

本批按 CEFR 配额、稀有主题优先及固定种子选取，覆盖 A1–C2 六个 CEFR 级别和全部 19 个主题。A1、A2、B1、B2 各 17 词，C1、C2 各 16 词。它是未参与既有基准的分层校准材料，不是用于估算总体错误率的全库简单随机样本。字段也按词条聚集，不能视为 825 个相互独立的统计样本。

审查对象为词义、例句、搭配及中文提示等 `mode=translate` 字段；英文保留项和空字段不计入 825。中英并存时以英文的事实、关系和语气为权威，中文仅作语境；只有中文的提示等字段直接按中文核对。逐项检查错义、遗漏、擅加、否定或情态、数量时间或实体、语法或术语以及未译内容。标准的短词典简释、合理同义表达和日语通常省略不自动算错。

| 冻结标识 | 值 |
| --- | --- |
| 选取种子 | `20261026` |
| 选择内容 SHA-256（规范 JSON 编码） | `9348d382fd1071e3f7549b13d0c65bee835acc43b363d78a0db828387902de75` |
| 快照文件 SHA-256（精确字节） | `aa024c1a0ff313e050a1e44760ef20f9d4f3ff34fe8d93a13b62e32f420a2c43` |

选取规则与覆盖分布见 [selection.json](../.local/ja-semantic-holdout-2026-10-26/selection.json)。逐字段源文、原日文及完整词条语境分别保存在 [packet 1](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-1.json)、[packet 2](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-2.json)、[packet 3](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-3.json)。这些本地证据位于 `.local/`，本报告不意味着它们已经随仓库公开发布。

## 两遍独立审查与盲审限度

三个 Codex 审查代理先各自审查一个包，再交换到此前未负责的包进行完整交叉审查。每个字段都有两位不同 Codex 审查代理的逐项判定、准确源译引句和短说明；两遍各覆盖 825 字段，共 1,650 次字段审查记录。这里的“两位”指两个代理，不是两位专业人工译审，也不代表不同模型家族之间的独立验证。

| 源文包 | 词数 / 字段数 | 第一遍 | 第二遍交叉审查 |
| --- | ---: | --- | --- |
| packet 1 | 34 / 280 | [review-1.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/review-1.json) | [cross-review-3.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/cross-review-3.json) |
| packet 2 | 33 / 273 | [review-2.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/review-2.json) | [cross-review-1.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/cross-review-1.json) |
| packet 3 | 33 / 272 | [review-3.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/review-3.json) | [cross-review-2.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/cross-review-2.json) |

交叉审查阶段不读取前一位的字段评分或 Qwen 预测；争议项之后再做源文裁决。审查代理保持对本地模型预测的盲态，没有调用本地模型代替自身语义审查。共享 rubric、调度说明和源文关注点仍可能形成共同偏差，因此此处的独立性限于逐字段源文判断及对被测模型输出的隔离。

首次 gold v1 在 root 查看任何模型判断前锁定。后来从修订候选的源文核对中发现 `monthly pass` 的明确月份限制被漏译，形成[独立源文发现记录](../.local/ja-semantic-holdout-2026-10-26/independent-review/source-ledger-monthly.json)，继而完成整批交叉审查和版本化裁决。**原 [gold.json](../.local/ja-semantic-holdout-2026-10-26/gold.json) 与 [v1 锁定记录](../.local/ja-semantic-holdout-2026-10-26/independent-review/gold-lock.json) 保留，不覆盖历史标签。**

| 原译 gold 版本 | pass | error | uncertain | 说明 |
| --- | ---: | ---: | ---: | --- |
| v1 | 820 | 3 | 2 | 首次源文裁决后锁定，保留原件 |
| v2 | 818 | 4 | 3 | 完整交叉审查及源文边界裁决后的原快照标签 |

v2 锁定前，root **只查看过一次模型汇总状态，没有查看逐字段模型判定**；完整交叉审查记录在这次汇总接触前已形成。root 因而不能被描述为 v2 全程对模型信息完全盲态。负责源文复核与边界裁决的代理仍未见模型预测。`repertoire.col.2` 最终保留 uncertain，与 root 原先拟定 pass 的预期不同，采用的是盲态代理的独立判断。过程和接触限度见 [gold-lock-v2.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/gold-lock-v2.json)；最终原译标签见 [gold-v2.json](../.local/ja-semantic-holdout-2026-10-26/gold-v2.json)。不能把 v1、v2 差异包装成模型测量后的准确率提升。

## 四处确认错误及三处存疑

以下是 **冻结原译**的四处错误。链接指向包含完整源译文本的源文包，表内引句可直接在对应词条中核对。

| 字段 / 源文证据 | 原译中的问题 | 源文裁决依据 |
| --- | --- | --- |
| [impulse.tip](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-1.json)：`后接动作常用impulse to do` | `行為を続けるには` | 把“后接表示动作的形式”这一语法连接说明，改成了“继续某行为”。 |
| [workmanship.tip](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-2.json)：`强调成品的做工，而非工作态度` | `完成品の作りのよさ` | 中性的成品做工被添加为正面的“做得好”；词条中的好坏做工均应能容纳。 |
| [bespectacled.ex.0](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-3.json)：`helped me find the missing book` | `本を探すのを手伝ってくれました` | 这一具体肯定过去叙事中的找到结果被弱化为仅协助寻找过程；不是把过去时本身等同于完成结果。 |
| [saving.ex.0](../.local/ja-semantic-holdout-2026-10-26/independent-review/packet-1.json)：`Buying a monthly pass gave me a useful saving.` | `定期券を買ったおかげで、かなりの節約になりました。` | `monthly` 的一个月期限没有保留；此明确遗漏与 `useful` 是否被程度强化是两个问题，不靠后者的歧义来判错。 |

三处 uncertain 为 `excite.ex.1` 的 `young` → `幼い` 年龄范围、`impose.senses.0` 的 `徴収する` 税义范围，以及 `repertoire.col.2` 的 `一通り` 完备性读法。它们不计为确认错误，也不硬归为通过。更中性的候选获得认可，并不反证原句必错。

另外，[五项边界裁决](../.local/ja-semantic-holdout-2026-10-26/independent-review/cross-boundary-adjudication.json)逐项说明了 `food`、`horsepower`、`oyster` 的一般效用语境中 `can` 与日语一般句的对应，以及 `headache` 第一人称“需要清静”与 `静かにしていたい` 的自然语用，四项均判 pass；`repertoire` 保留 uncertain。这不是“所有 can 都可以省略”的规则。

## 七处独立认可并已采用的修订

下表为获独立核对接受并已采用的 **after** 文本。4 处属于确认错误修复，3 处属于存疑原句的保守澄清。完整源文、before/after、字段位置、检查者与哈希保存在 [source-reviewed-changes.json](../.local/ja-semantic-holdout-2026-10-26/source-reviewed-changes.json)。该不可覆盖变更包保留生成时的未应用状态，实际采用结果另见 [application-result.json](../.local/ja-semantic-holdout-2026-10-26/application-result.json)。

| 字段 | 用途 | 已认可的 after | 独立候选检查 |
| --- | --- | --- | --- |
| impulse.tip | 确认错误修复 | on impulseは「一時の衝動で」という意味です。動作を表す語を後ろに続けるときは、impulse to doの形をよく使います。 | [correction-check.json](../.local/ja-semantic-holdout-2026-10-26/correction-check.json) |
| workmanship.tip | 确认错误修复 | 不可算名詞で、仕事への態度ではなく、完成品の作りや仕上がりの質を表します。 | [correction-check.json](../.local/ja-semantic-holdout-2026-10-26/correction-check.json) |
| bespectacled.ex.0 | 确认错误修复 | 眼鏡をかけた図書館員の手助けで、見当たらなかった本を見つけることができました。 | [correction-check.json](../.local/ja-semantic-holdout-2026-10-26/correction-check.json) |
| saving.ex.0 | 确认错误修复 | 1か月の定期券を買ったおかげで、出費を抑えられて助かりました。 | [saving-correction-check-v2.json](../.local/ja-semantic-holdout-2026-10-26/saving-correction-check-v2.json) |
| excite.ex.1 | 存疑原句澄清 | 体験型の科学展示は、若い来館者をわくわくさせ、科学的な考えを自ら探究するよう促すことができます。 | [clarification-check.json](../.local/ja-semantic-holdout-2026-10-26/clarification-check.json) |
| impose.senses.0 | 存疑原句澄清 | 課す；施行する；賦課する | [impose-clarification-check.json](../.local/ja-semantic-holdout-2026-10-26/impose-clarification-check.json) |
| repertoire.col.2 | 存疑原句澄清 | 技能の持ち合わせ | [repertoire-clarification-check.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/repertoire-clarification-check.json) |

825 字段的 818/4/3 是冻结原译的标签；采用 after 不改写它。应用前已完成冻结源文件、精确 before、实际生效层和独立证据核验，应用后另记录正式数据及组装结果。

## Qwen 测量与有限重试

本机使用 `qwen3.5:9b-q8_0`（实际模型元数据为 Q8_0、9.0B），Ollama 0.32.1。参数为 temperature 0.1、top_k 40、top_p 0.95、seed 42、presence_penalty 0、repeat_penalty 1、num_ctx 8192、num_predict 4096、think false。请求、模型摘要、代码版本和旧快照均冻结；本批本地模型测量限于 Qwen 检错，不能视为 TranslateGemma 与 Qwen 全流程通过。

首轮 `detect-holdout-20261026` 完成 100 条记录、100 次请求，记录时间跨度为日本时间 21:48:21–23:13:11，约 84 分 51 秒。随后 `detect-holdout-retry-20261026` 仅对 14 词中的 15 个不可检查字段追加 14 次请求，约 2 分 49 秒。其余 810 个语义字段的完整判定逐项保持一致，包括原 pass、error、uncertain；未挑选重跑已判通过或报错的字段。实际请求再次验证使用修正前的冻结日文，即使正式词库已另行修订。证据见 [retry-scope.json](../.local/ja-semantic-holdout-2026-10-26/retry-scope.json) 和 [execution-summary.json](../.local/ja-semantic-holdout-2026-10-26/execution-summary.json)。

计分分母为已裁决的 **822 字段：818 正确、4 错误**。3 个原译 uncertain 排除出计分，保留清单，不算正确或模型通过；选中字段总数仍为 825。

| 版本 / 视图 | 真错误检出 / 4 | 错误被判 pass | 正确字段误报 / 818 | 正确 pass | 程序 HOLD 的正确字段 | 不可检查 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 首轮 model | 0 | 3 | 20 | 784 | 0 | 15 |
| 首轮 guarded | 0 | 3 | 20 | 782 | 2 | 15 |
| 有限重试后 model | 1 | 3 | 21 | 791 | 0 | 6 |
| 有限重试后 guarded | 1 | 3 | 21 | 789 | 2 | 6 |

重试后检出的是 `workmanship.tip`；`saving.ex.0`、`impulse.tip`、`bespectacled.ex.0` 仍被判 pass。程序门禁保留了两个正确字段作 HOLD，没有检出上述漏错。6 个不可检查字段是 `house.tip`、`information.col.3`、`ingot.ex.1`、`motel.senses.0`、`motel.ex.0`、`urban.ex.0`，均因源文或译文引句不匹配而保留失败，不追加无限重试。

原始测量见 [metrics-initial.json](../.local/ja-semantic-holdout-2026-10-26/metrics-initial.json)，有限重试及原始版本对照见 [metrics-after-retry.json](../.local/ja-semantic-holdout-2026-10-26/metrics-after-retry.json)。两份均包含 model 与 guarded 视图。原译仍有 3 个独立待定标签，因此使用显式 `--allow-unresolved-gold` 只报告已裁决子集，工具状态保持 `incomplete`、`passed: false`。6 个模型不可检查字段也没有被算作通过。

揭盲后另检查了首轮前 87 词中的全部 15 个“模型 error / gold pass”案例，诊断见 [post-unblinding-model-diagnostics.json](../.local/ja-semantic-holdout-2026-10-26/independent-review/post-unblinding-model-diagnostics.json)。它是固定局部时点的解释，不是新的盲态评测：包括把カキ误认为其他贝类、声称源文没有 `deep` 但源文实际包含，以及声称漏译 children 但译文有「子ども」等。未据此改写原 gold，也未把这 15 个案例描述为全部 21 个最终误报的新一轮独立认证。

本批错误只有 4 个，不能据此估计全库检出率；但 3 个实错被直接批准的事实已不支持将该模型作为验收者。此次不启动剩余全库的自动扩跑。后续提示词或流程调整需要另抽未见集；已揭盲的本批可作回归材料，不能重新宣称为未见验证。

## 实际采用与版本交接

七处修订由 Codex 对照源文提出，并由另一审查代理逐项认可；没有采用 Qwen 自评批准来替代独立决定。应用前已保存 **6 个 canonical 分块及全部 74 个 public JA JSON 的精确字节备份**，共 80 文件；备份位于 `.local/ja-semantic-holdout-2026-10-26/application-backup/`。

实际变更为 6 个基础分块、6 个 public 对应分块及 1 个派生索引，共 13 文件。全 7,298 个组装对象与仅修改七字段后的预期对象精确一致；`repertoire.col.2` 保留了 `a repertoire of skills｜` 英文前缀，派生索引仅更新 `impose` 的首义显示。76 个英文／中文源文件及其余覆盖输入保持原哈希。计划及应用审计见 [application-plan.json](../.local/ja-semantic-holdout-2026-10-26/application-plan.json)、[应用预审](../.local/ja-semantic-holdout-2026-10-26/independent-review/application-plan-audit.json) 与 [资料链审计](../.local/ja-semantic-holdout-2026-10-26/independent-review/evidence-chain-audit.json)。

另一位未读取模型输出的审查代理完成了[应用后最终审计](../.local/ja-semantic-holdout-2026-10-26/independent-review/post-application-audit.json)：80 份备份、13 文件差异、7 个新目标、源资料、gold、新快照及本地资源全部匹配，0 项失败。两份 gold 的应用前精确字节哈希均可复验；原锁记录的内容及绑定也已核对，但未预存锁文件整体字节哈希，因此不额外声称有锁文件的前后整字节比对证据。

修正后另建 `.local/ja-semantic-review-post-holdout-2026-10-26/`，新快照文件 SHA-256 为 `9744b810d613c2159ddb0e92b457eb152618afefab53100a7747618b14a83bf3`。原模型运行仍绑定旧快照；继续检查正式现状应使用新快照，旧运行与现状的 13 文件差异为已记录的采用结果。修正后的本批 [final-independent-coverage.json](../.local/ja-semantic-holdout-2026-10-26/final-independent-coverage.json) 绑定全部 825 字段的新目标哈希：818 个原样接受、4 个修错、3 个澄清。本批之外的 59,562 个语义字段不计通过。

## 验证与预览

- 126 项 Python 复核工具测试通过。
- 组装后 `npm run check:japanese`：7,298 词、14,596 例句、67,649 个既有检查槽位，0 错误、0 语言警告。
- 全库另外核对 7,261 个空来源字段和 22,364 个保留英文字段，合计 29,625 项确定性检查全部通过；这不是语义正确率。
- `npm test`：25 项网站测试通过。
- 精确对象差异、输入哈希、独立接受证据和回滚备份均已核验；`git -c core.whitespace=cr-at-eol diff --check` 通过，保留既有 CSV 的 CRLF。
- 本地预览最初连接失败，旧失败记录保留于 [local-served-check.json](../.local/ja-semantic-holdout-2026-10-26/local-served-check.json)。恢复 Vite 的 `http://127.0.0.1:5188/` 后，7 个受影响 HTTP 资源均与当前文件精确匹配，见 [恢复后资源检查](../.local/ja-semantic-holdout-2026-10-26/local-served-check-after-restart.json)。这是本地资源验收，不能代替页面交互或线上部署验收。
- 检测及有限重试结束后，Ollama 驻留模型为空；两个已安装的 Q8 模型保留。
