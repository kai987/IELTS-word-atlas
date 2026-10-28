# 全库日译逐条语义复审

2026-10-27 已完成全库复审及全部 120 个疑点字段的独立二审：7,298 词条、60,387 个翻译字段均已覆盖，未审 0。最终判定 62 个确认错误（6 个重大、56 个轻微）、47 个仍存疑、11 个初审疑点排除。正式词库未修改，230 个冻结源文／日文文件无漂移。[完整汇总与逐项日文建议](ja-full-semantic-review-results-2026-10-27.md) 已保存；可机器读取的结果在运行目录 `final-report/` 中。

本轮检查 7,298 个词条中的 60,387 个日译字段。结果保存在 `.local/ja-full-semantic-review-2026-10-27/`，当前覆盖量以该目录的 `PROGRESS.md` / `progress.json` 为准。运行开始不代表全库已经审完，发现问题也不自动改写生产词库。

有英文的词义、例句、搭配以英文为准，中文作为辅助语境；只有中文的学习提示和说明按中文核查。英文原样保留项和空字段只做完整性检查，其 29,625 项不计入语义审查分母。

可复用的历史结论来自独立源文审查。只有整条源文对象、整条日译对象、字段路径和语言等绑定全部一致，才可复用。此次符合条件的 201 词条 / 1,664 字段包括 1,655 个通过、4 个已知问题、5 个存疑。源文、译文或同条语境变动的旧结论失效；7 个已修订词条的 58 个字段重新进入审查。

其余 7,097 个词条 / 58,723 个日译字段分为 284 个冻结批次，由 Codex 审查者逐字段阅读对照。审查独立于先前被测的 Qwen、Gemma 等本地模型，并不代表专业人工认证或不同模型家族间的独立性。本轮未使用本地模型生成的 `pass` 作为已审依据。

每批结果必须声明实际完整比较了该批所有译文字段，并列出有序词条列表及具体疑点。缺批、缺词、源文/日译/语境变化、引用不属于同一字段或绑定失效时，不记为完成。阅读回执仅证明文本曾被输出，不能单独证明语义审查。

疑点进入独立重点复核队列，保存源文、当前日译、整条语境、初审结论和写回位置。另一位审查者可将其判为通过、问题或继续存疑；原结论始终保留。日常叙事中自然的省略、补足和日语惯用表达需结合上下文判断，不仅凭形式逻辑作重大误译结论。确认的实质差异与无法确定的范围边界分开记录。

继续运行时使用以下命令汇总已有真实审查结果。这些命令只校验和汇总，不会自行产生源文审查结论，也不调用模型或改写词库。

```sh
python3 scripts/atlas/full_ja_semantic_review.py assemble --run .local/ja-full-semantic-review-2026-10-27
python3 scripts/atlas/adjudicate_ja_full_review.py prepare --run .local/ja-full-semantic-review-2026-10-27
python3 scripts/atlas/adjudicate_ja_full_review.py assemble --run .local/ja-full-semantic-review-2026-10-27
python3 .local/ja-full-semantic-review-2026-10-27/render-progress.py
```

`source-ledger/status.json` 保留初审分类；`focus-review/` 保留二审；`progress.json` 只将与当前初审绑定完全一致的二审结论合入进度展示。未审字段始终保留 `not_reviewed`，遍历完成与全部问题处理完毕分别统计。

本轮另使用 Ollama 官方删除命令移除了 `mistral-small3.2:24b-instruct-2506-q4_K_M`。目标清单和六个未共享权重块均已消失；Gemma 4、Qwen3.5、TranslateGemma 三个 Q8 模型的摘要保持一致。删除专用服务已经停止，证据保存在运行目录的 `model-removal-result.json`。
