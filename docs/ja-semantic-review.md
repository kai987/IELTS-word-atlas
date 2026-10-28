# 正式日文词库的独立语义复审

本流程直接检查网页最终使用的日文，不先重新生成整库初译。`translate-ja-local.py` 和旧量化实验保留原用途，新入口为 `review-ja-corpus.py`。

## 冻结对象与覆盖

`prepare` 冻结 `public/atlas/ja/entries/` 的最终译文、权威中英文原文、原始索引、基础日文、全部 reviewed 覆盖修订及其摘要。当前共 7,298 条、230 个输入文件；最终译文与基础日文有 49 条不同。审查和修正绑定最终版本，变更包记录实际生效的覆盖层位置，避免只改基础文件后被覆盖回去。

全库包含三种不同分母：

| 类型 | 数量 | 检查方式 |
| --- | ---: | --- |
| 非空日文译文 | 60,387 | 逐字段源文语义对照，包含中文相关词 |
| 空来源备注 | 7,261 | 保持空白，不得添加内容 |
| 英文相关词 | 22,364 | 与源文逐字一致 |

合计 90,012 个检查槽位。结构完整性、模型已检查和独立语义通过分别统计，不能互相替代。搜索索引为派生显示数据，不重复算作独立语义审查。

```sh
python3 scripts/atlas/review-ja-corpus.py prepare --run .local/ja-semantic-review
python3 scripts/atlas/review-ja-corpus.py status --run .local/ja-semantic-review
```

已有快照和输入不符时拒绝覆盖；修改源文或添加覆盖文件会使变更导出暂停。输出禁止放入正式 `data/`、`public/` 或 `.git/`。

## 检错、参考、修正、二次核查

Qwen 必须为每个译文字段给出 `pass / error / uncertain / unavailable`、错误类别、匹配的源文及译文引句和简短事实说明。检查义项、遗漏、添加、否定、可能性及义务、数值和范围、时间、年龄性别关系、专业术语与语法条件。没有补丁不代表通过。空白和英文保留项由程序单独检查，模型不能覆盖这些结果。

TranslateGemma 仅为疑点字段生成独立参考。每次只翻译一个字段，ID 由程序绑定；输入不包含现有日文或之前的批准结论。英中成对字段以英文为权威，只有中文的提示、备注、相关词从中文译日。参考译文不是裁决，英文/IPA 术语丢失会保留失败记录。

修正为独立请求，要求精确原译文、源文证据和最小修正。语言回退、占位符、术语丢失等进入拦截状态。二次核查另发新请求，只提供源文与修正前后文本，不提供前次判定或自评批准。使用同一 Qwen 的二次核查仍然是模型信号，不能充当独立最终裁决。

下面用明确 ID 做小规模运行；全库运行需显式使用 `--all`，也可用 `--selection` 指定冻结的校准清单。每个阶段结束释放所用模型，若发现其他模型驻留会停止，不强行卸载它。

```sh
python3 scripts/atlas/review-ja-corpus.py detect --run .local/ja-semantic-review --ids library,sister
python3 scripts/atlas/review-ja-corpus.py reference --run .local/ja-semantic-review --ids library,sister
python3 scripts/atlas/review-ja-corpus.py repair --run .local/ja-semantic-review --ids library,sister
python3 scripts/atlas/review-ja-corpus.py crosscheck --run .local/ja-semantic-review --ids library,sister
```

默认使用已安装的 `qwen3.5:9b-q8_0` 和 `translategemma:12b-it-q8_0`，不自动下载模型。两模型及不同任务分别配置参数，避免将 Qwen 的采样设置套给翻译模型。`--preset baseline / official-instruct / official-thinking` 为 Qwen 提供校准对照；通用官方配置不是本任务的准确率保证。可用 `--num-ctx`、`--num-predict` 等覆盖设置，参数变化必须使用新 `--lane`。

TranslateGemma 的单字段输入遵循其[官方专用翻译模板](https://huggingface.co/google/translategemma-12b-it)的任务结构；Qwen 对照参数依据[官方模型卡](https://huggingface.co/Qwen/Qwen3.5-9B)。

## 恢复、失败与原始证据

每条以独立原子文件记录 `attempt-000001.json`，包括版本、模型摘要、实际请求、原始响应、费用无关的耗时/令牌统计和逐字段状态。代码按哈希归档。模型私有 thinking 不落盘；输出耗尽令牌、格式不完整、引句不符及 HTTP 错误均保留证据，不按通过处理。

重复运行跳过所有已结束的尝试，包括失败和待裁决。只有显式 `--retry` 才创建新尝试，旧记录继续保留；参考翻译、修正中的成功字段可以复用，只重试失败部分。检测中的坏引句、缺失或重复字段仅把对应字段记为 `unavailable`，其余已验证字段保留。使用 `detect --retry --from-lane 原lane --lane 新lane` 可在新版本中仅请求这些不可检查字段；已有 pass、error、uncertain 不自动重跑。首次模型调用前就写入带快照绑定的检查点。进程中断后的 running 会记录为 interrupted，不会自动重新生成。

重复的错误类别标签可做不改变判定或译文的去重，并记录 normalization；重复字段路径或无效引句不能通过。`reparse` 在新 lane 对原始完整响应重新执行程序校验，不调用模型、不改原始输出，结果明确绑定旧请求与新解析版本。

## 自然留出集和受控探针

```sh
python3 scripts/atlas/calibrate-ja-review.py prepare --run .local/ja-semantic-review --out .local/ja-semantic-holdout
```

默认另抽 100 条，排除旧评测 100 词；按 CEFR 与主题分层，当前为 825 个译文字段，覆盖 6 个 CEFR 与 19 个主题。`gold-template.json` 初始完全待标注，不会假定现有译文正确。必须独立对照源文填写标签及审查来源；`--exclude-selection` 可继续排除已经用于调优的其他样本。

冻结提示词后，以指定清单运行 `detect`，再测量：

```sh
python3 scripts/atlas/review-ja-corpus.py detect --run .local/ja-semantic-review --selection .local/ja-semantic-holdout/selection.json
python3 scripts/atlas/calibrate-ja-review.py evaluate --selection .local/ja-semantic-holdout/selection.json --gold .local/ja-semantic-holdout/gold-template.json --records .local/ja-semantic-review --out .local/ja-semantic-holdout/metrics.json
```

标注不完整、版本不匹配或缺少独立标注来源时，不产生可验收的准确率结果。指标单列错误检出、误报、错误被批准、未检出、存疑、不可检查和缺失。最新失败不会回捞旧成功。不同参数使用不同 lane，通过 `evaluate --stage ... --compare ... --compare-stage ...` 比较。`--view model / guarded` 选择主要视图，每份报告同时保存两种视图；model 是通过格式/引句校验后的原模型判断，guarded 是再经过程序风险门禁的状态，不能把 HOLD 算成模型检出。

独立审查完成后仍有解释分歧时，可显式使用 `--allow-unresolved-gold` 测量已裁决的子集。只有带说明的 `reviewStatus: uncertain`、`expectedStatus: null` 才可排除出计分分母；报告保留全部选中字段数、可计分字段数及待定清单，状态仍为 `incomplete`、`passed: false`。空白模板、漏标、未知标签、版本不符仍不产生指标。此选项用于如实报告部分测量，不表示校准通过，也不将待定项算作正确。

程序对原文未给出的兄弟姐妹年龄、男性备选、午前/午後、最高级，以及双自/他动词义框架等少量风险做保守 HOLD。原模型判定保存在 `modelAssessment`，程序只把有风险的 pass 降为 uncertain，不把存疑或失败升为通过。正确的复杂义项也可能被 HOLD，必须独立检查；这些规则不覆盖所有语义问题。

另外提供 `ja-semantic-probes.json`：24 个原创受控案例、12 对最小差异，共 26 字段，由另一工作单元独立对照源文核验，包含 14 个正确标签及 12 个明确错误标签。它们只测受控检错能力，不能用于估计自然词库准确率，也不能导出为正式词库变更。

```sh
python3 scripts/atlas/review-ja-corpus.py prepare --run .local/ja-semantic-probes --probes scripts/atlas/ja-semantic-probes.json
python3 scripts/atlas/review-ja-corpus.py detect --run .local/ja-semantic-probes --all --lane detect-baseline
python3 scripts/atlas/calibrate-ja-review.py evaluate --selection .local/ja-semantic-probes/selection.json --gold .local/ja-semantic-probes/gold.json --records .local/ja-semantic-probes --stage detect-baseline --out .local/ja-semantic-probes/metrics.json
```

修正质量另行独立标注，不能由二次核查自动填 gold：

```sh
python3 scripts/atlas/calibrate-ja-review.py repair-template --run .local/ja-semantic-review --stage repair --out .local/ja-semantic-review/repair-gold.json
python3 scripts/atlas/calibrate-ja-review.py repair-evaluate --run .local/ja-semantic-review --stage repair --gold .local/ja-semantic-review/repair-gold.json --out .local/ja-semantic-review/repair-metrics.json
```

报告分别统计真正修复、正确字段被改坏、仍然错误、严重度增加和仅文风改写，并区分全部提议与通过机器门禁的提议。提议、快照或 attempt 内容变化会使旧独立标签失效。

## 独立最终裁决和变更包

```sh
python3 scripts/atlas/review-ja-corpus.py decision-template --run .local/ja-semantic-review --all --out .local/ja-semantic-review/independent-decisions.json
python3 scripts/atlas/review-ja-corpus.py export --run .local/ja-semantic-review --decisions .local/ja-semantic-review/independent-decisions.json --out .local/ja-semantic-review/reviewed-changes.json
```

模板逐字段提供源文及修正前后文本，初始全部存疑；审查者需独立核对源文并填写真实来源、决定、引句和说明。`pass` 绑定原日文的哈希；`accept` 绑定具体修正提议及新日文的哈希；`reject / uncertain` 不导出修改。模板不能直接当作已审结论，模型 crosscheck 文件也不能直接充当独立裁决文件。

导出只生成可审阅变更包，包含实际覆盖层位置、原译文、修正、证据和输入摘要，不修改正式词库。采用修正时须更新实际生效的数据层，重新组装并执行 `npm run check:japanese`；完成前分别报告未审、通过、修复和未决数量。

## 本轮验证记录

本机冻结全量位于 `.local/ja-semantic-review-2026-10-26/`；100 词留出材料、原空白模板及版本化审查记录位于 `.local/ja-semantic-holdout-2026-10-26/`。受控参数对照和全阶段样本位于 `.local/ja-semantic-probes-2026-10-26/`。以下记录为流程初次验证，后续自然 100 词的执行、独立审查和采用状态见[本批报告](ja-semantic-holdout-review-2026-10-26.md)。任何小样本通过都不代表全库已完成语义复审。

2026-10-26 的受控结果：

| 检测配置 | 已知错误 12 个中的检出数 | 正确字段 14 个中的误报数 | 引句无效／不可检查 |
| --- | ---: | ---: | ---: |
| 低温基线 | 10 | 1 | 0 |
| 官方非思考通用参数 | 9 | 1 | 3 |

每配置均生成 24 次原始响应。重复类别标签只做无损去重，旧请求、原响应及早期严格解析失败均保留，新解析结果另存 lane；官方配置中 3 个字段的无效引句仍为不可检查。基线漏检的 2 个错误经过通用事实门禁转为 uncertain，模型检出数仍是 10，不能宣称模型检出了全部错误。本轮保留低温基线，不能据此认定它对全部文本最优。

参考翻译共 11 个字段，均完成；修正环节发现本机后端无法初始化原先过大的字符串 grammar，已将 schema/解析器一致限制为 1,600 字符。旧 HTTP 400 及后端诊断保留，新 lane 运行 11 次生成，其中 8 个形成有效结构的提议，另 3 个因 before 或源文证据不匹配而保留失败。另一个工作单元只依据 source/before/after 独立复评 8 个提议：6 个真正修复、1 个仍错、1 个仅文风改写。没有把结构接收或模型二次核查当作修正正确率。

真实正式译文的开发试审为 8 词、67 个语义字段，与新的 100 词留出集无重叠。独立源文标注确认 65 个正确、2 个错误。模型漏掉这两个错误并误报三个正确字段；部分引句失败后，保留其他已审字段，仅用两次额外请求重试五个不可检查字段。最终 model 视图仍为 0/2 检出、2/2 错误获批，guarded 视图将两个漏检和一个正确但复杂的义项留作 uncertain。这个结果证明仍需独立最终裁决，不支持将 Qwen 自评用于正式验收。

同一 Qwen 的普通二次核查在 8 个提议中接受了 2 个，其中 1 个是独立复评确认仍错的材料提纯义项。另对 3 个争议例使用官方思考参数、16,384 上下文和 4,096 生成令牌预算诊断：1 个正确修正获接受，2 个耗尽预算而未形成可用裁决。思考文本不保存，预算耗尽保持失败。样本不足以支持全库启用思考模式；两种模式均不能代替独立最终裁决。

流程初次验证时，100 词留出集尚未运行模型、未填写金标，工具正确返回 incomplete 和空验收指标；准备完成并不等于已验证。该阶段未改动正式译文。初次验证包括 85 项语义流程测试、原 36 项复核测试、25 项网站测试，以及全量日文自动校验（7,298 词、67,649 个既有检查槽位，0 错误、0 语言警告）；这些自动测试不等于译文语义零错误。后续测试数量和正式译文状态以本批报告为准。
