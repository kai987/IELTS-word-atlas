# 日文词库：47处疑点集中复核

完成时间：2026-10-28T18:26:23+09:00。范围为原全库审查保留的47个字段、46个词条。

**结论：15处必须修正（2处重大、13处轻微），28处可选优化，4处可原样保留，0处继续存疑。**

本次只完成复核与修改建议，以下15处新确认错误及28处可选优化均尚未应用。此前已修正的62处保持不变。可选优化不计入错误数，也不要求一律替换。

## 判断方法与证据边界

每个字段均对照完整英中源词条与当前实际发布目录中的日文词条；英中齐备时以英文为准，仅中文提示按中文翻译。47处各有一份不含旧结论的初审及一份独立根审初稿，17份追加交叉审查用于处理分歧。最终逐项裁决，不以多数票自动定案。审阅来自同一Codex模型家族，不等于不同模型交叉认证或人工专家审校。

实质错误包括删掉源文明示关系、增加不获来源支持的事件阶段或条件、错误术语和否定范围变化。已有正常词义、句法或语用读法支持的原译，区别于仅为了清楚度而提出的候选。当前可接受不表示最优，候选更清楚也不证明原译必错。

may的两义、shade与木陰、business与商店等均比较完整句子；词典或其他出版用例只能支持某读法成立，不能证明例句现实场景。技术与语法资料的具体推论写在相应项目中，不据此断言实际法规、食品成分或现实建筑。部分PDF根审采用出版社可检索全文；不把字体缺失的渲染图或抓取失败说成已完整目视阅读。

## 必须修正清单

|编号|词条·字段|级别|当前问题|
|---|---|---|---|
|[U-01](#u-01)|authorize · `ex.1`|轻微|改判两份初稿：may 的词义可有许可与可能性，但不能因此把 only-after 的先后限制移成限制有时适用。选择英文允许且行政批准场景支持的许可义保留条件；这是译句判断，不是任何地方实际法规的断言。|
|[U-04](#u-04)|bounce · `ex.0`|轻微|改判 root 初稿：跳／飛两种表记不能证明表面反弹。反弹方式是本字段已明示的教学信息，必须补回。|
|[U-06](#u-06)|county · `tip`|轻微|改判两份初稿：已给出的中文-only 按中文翻译规则足以决定，现译日语术语事实正确仍不能替换中文译名对比。补明元语言即可，不需要新造编辑授权缺口。|
|[U-08](#u-08)|difficult · `ex.1`|轻微|采纳源文范围分析：缺经验并不等于当年毕业，亦未明说第一份工作。不能用典型招聘情景补出新卒限制。|
|[U-13](#u-13)|expert · `ex.0`|轻微|改判 root 初稿：请求履行是可取消的后续推断，不能写成已经接受检查服务。依頼しました保留事件阶段。|
|[U-16](#u-16)|fresh · `senses.0`|轻微|本项是总定义，不能用两条果蔬例句排除刚制作食品。preserved 不能扩大为一切加工。|
|[U-17](#u-17)|from · `ex.1`|轻微|改判 root 初稿：additional 的 put-with 关系不可只保留为困难程度更大；恢复附加的障碍。|
|[U-20](#u-20)|impost · `col.2`|重大|新增同属西方拱建筑的日本学术资料，明确インポスト上才放拱起点，补足此前仅石桥术语证据的局限。起拱石与支承台石是不同构件，定为 major。|
|[U-23](#u-23)|kill · `tip`|轻微|改判 root 初稿：副词自ら不同于主语自身这一名词性说明；非意志用法仍可带自身致因，不等同中性的死亡。并不宣称现译必然等于自杀。|
|[U-26](#u-26)|mathematical · `ex.1`|轻微|改判 root 初稿：将来可以是一段时期，但没有表达源文明示的随时间推移关系。兼容未来过程不等于翻出了过程。|
|[U-28](#u-28)|nowhere · `ex.1`|轻微|改判 root 初稿：持续有偿就业与按期发薪不是同一个依存关系。候选修饰就业持续性，不擅加正社員或永久合同。|
|[U-29](#u-29)|occurrence · `ex.1`|轻微|urban 是独立明示的限定，人口密集不能自动补回城市属性。需补都市部。|
|[U-31](#u-31)|persistence · `ex.1`|重大|采用 major：不是任何家庭都能保证与任何一家都不能保证的范围差异影响核心命题。语法研究支持どの…も配否定的全否定风险；并未据此宣称增长毫无益处。|
|[U-35](#u-35)|propose · `ex.1`|轻微|more regularly 的比较增量必须保留，不以目的可推知改善代替明示比较级。|
|[U-39](#u-39)|shiny · `col.0`|轻微|独立搭配没有 polished；不得把另一条例句的打磨事件移入通用搭配的状态义。|

优先处理 `impost.col.2` 的建筑构件与 `persistence.ex.1` 的否定范围，其余13处恢复来源中的关系、限定或词义。所有完整替换值见下方逐项对照及机器可读清单。

## 可选优化与保留

28处可选优化：adopt（ex.1）、assembly（ex.0）、comedy（ex.0）、craft（ex.1）、disappointed（ex.1）、diving（ex.0）、embroidery（ex.0）、familiar（ex.1）、farmer（ex.1）、high（ex.1）、integrate（ex.1）、keyboard（ex.1）、kitchen（ex.1）、librarian（ex.0）、medium-sized（ex.1）、officer（ex.0）、pot（col.2）、prominent（ex.0）、replace（ex.1）、sausage（col.1）、sausage（ex.1）、stake（ex.0）、stay（ex.1）、steward（ex.0）、terminable（ex.1）、territory（tip）、thermometer（ex.1）、tiger（ex.0）。

4处原样保留：expect（col.2）、happen（ex.0）、portrait（ex.0）、tune（ex.1）。

此前 `authorize` 的may、`county` 的本地化取舍在初稿中仍存疑；追加审查后可依据整句限制范围及既定中文来源规则裁决，不需为不同理论读法另设阻塞。`authorize` 仍可选许可或一般可能性表达，但都应将“评估后才批准”放在审批行为上。

## 47处完整对照

<a id="u-01"></a>
### U-01 · authorize · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Local authorities may authorize new housing developments only after assessing their likely effects on traffic and public services.

当前日文（完整字段值）：

> 地方当局が新たな住宅開発を許可できるのは、交通と公共サービスに及ぼしそうな影響を評価してからに限られる場合があります。

建议日文（完整字段值）：

> 地方当局は、交通と公共サービスへの予想される影響を評価した後に限り、新たな住宅開発を許可することができます。

判断：may 的许可与可能性读法都真实存在，但这不足以使 only after 的限制任意变成“有些时候限制才成立”。许可义下，英语规定所述审批须先评估；可能义下，不确定的是是否发生带有“评估之后才批准”这一时序的审批。现译的主陈述却是“可批准的条件仅限评估之后”有时成立，把場合があります接在限制成立上，同时保留許可できる这一权限/可行性表述。它不是仅仅选了 may 的一种词义，而是改变了不确定性所修饰的命题。建议采用完整 entry 行政批准场景支持、且英语允许的许可读法，直接保留必要先后条件。

其他读法与限度：英语也可作非规范性的可能审批行为叙述，此时可译为“地方当局は、交通と公共サービスへの予想される影響を評価した後に限って、新たな住宅開発を許可することがあります”。这不等于目前“許可できるのは…に限られる場合があります”所报告的限制适用范围。若明确有 in some cases / may be restricted to / 不同制度背景，现译的限制时有成立读法才更有直接依据。不能据本例推断任何特定地区实际施行的法规。

裁决：改判两份初稿：may 的词义可有许可与可能性，但不能因此把 only-after 的先后限制移成限制有时适用。选择英文允许且行政批准场景支持的许可义保留条件；这是译句判断，不是任何地方实际法规的断言。

`may`的另一选义候选（不改变必改结论）：

> 地方当局は、交通と公共サービスへの予想される影響を評価した後に限って、新たな住宅開発を許可することがあります。

依据：

- [Cambridge English Grammar Today: May](https://dictionary.cambridge.org/grammar/british-grammar/may.)：官方语法确认许可、弱可能性及正式一般可能性等用法；这些释义不能自动决定作者意图，也不能单凭 may 多义证明当前日语把模态放到限制成立上仍等价。
- [British Council: Inversion after negative adverbials](https://learnenglish.britishcouncil.org/free-resources/grammar/c1/inversion-after-negative-adverbials)：官方语法将 only after 与 only if/when、only later 列为限制性的时间表达。该资料用于核对 only 与时间短语构成单位；具体与 may 的范围差异由本字段句法对照推断，不冒称词典已裁定本例作者意思。

来源绑定：`U-01`，词条上下文 SHA-256 `4faa34188df5b93b0c034420ee0138ef91aeea9fc918b86722455b1a1671afad`；原票据 `f209725b7b87a52aefec6b4fbd77fafcc3ea5ea2f9edf878127043495a58c5a0`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-02"></a>
### U-02 · adopt · `ex.1`

**可选优化**。

原文（英文）：

> Governments should adopt long-term strategies that improve public transport rather than simply building more roads.

当前日文（完整字段值）：

> 政府は、道路を増やすだけでなく、公共交通機関を改善する長期戦略を採用すべきです。

可选日文（完整字段值）：

> 政府は、単に道路を増やすのではなく、公共交通機関を改善する長期戦略を採用すべきです。

判断：rather than在此比较公共交通长期战略与「只是一味增建道路」。simply将被批评的方案限定为仅增建道路，并未禁止战略中也修路。日文「道路を増やすだけでなく」在该劝告语境中表达应超出仅修路、同时重视公共交通，保留了实质政策要求，不能据此断言它把英文变成必须修路。若希望更清楚显示比较与优先关系，可改为「単に道路を増やすのではなく」，属于可选澄清。

其他读法与限度：英文可允许同时修路，只是否定仅修路的做法；也可以强调以改善公共交通取代道路扩张。上下文未要求二选一的绝对排斥，因此不把前一种可接受解读判错。

裁决：simply 限定了被批评的是仅修路的办法；不把だけでなく机械判成支持必须增路。建议突出原文对比，属于消歧。

依据：

- [Cambridge English Grammar Today: Rather](https://dictionary.cambridge.org/grammar/british-grammar/rather)：官方语法说明rather than比较两个方案或偏好时赋予其中一个更高重要性；并不独自证明本句禁止兼有道路建设。

来源绑定：`U-02`，词条上下文 SHA-256 `f6d76b05398c688bd229e9afec853d5928e3324a4a596e99dba067609fd3b657`；原票据 `e9b078b6bd574ebf29f3b165c9ea7f4e33d14e46b94ee0a27e391dd2f7e19a35`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-03"></a>
### U-03 · assembly · `ex.0`

**可选优化**。

原文（英文）：

> The whole school gathered in the hall for assembly.

当前日文（完整字段值）：

> 全校生徒が、集会のためにホールに集まりました。

可选日文（完整字段值）：

> 学校のみんなが、集会のためにホールに集まりました。

判断：school在全校集会中可用学生群体代表学校，现译没有排斥教师在场，不能把未提教师直接解释为只有学生。英文字典的集体义及辅助中文更容易让读者想到师生整体，因而用学校のみんな可减少范围疑问，但现译属于自然概括，不确认为对象误译。

其他读法与限度：集体的school可泛指师生；日常叙述也常以学生作为学校集会的主体。

裁决：school 的学生集合读法成立；现译也未明说教师没有参加。选更宽的自然表达为可选项。

依据：

- [Cambridge Dictionary: school](https://dictionary.cambridge.org/us/dictionary/english/school)：核对school可作学校成员的集合称呼；不把该释义当成排除一切学生借代的规则。

来源绑定：`U-03`，词条上下文 SHA-256 `d22558837f2d0c193c0775c478b097f450b28c65da0f36278a4ad236c3baaf21`；原票据 `dce934819ab2806a6c77e7b088d04b8bafdd2ab89d74b32144dd25340b48a1c5`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-04"></a>
### U-04 · bounce · `ex.0`

**必须修正**（轻微）。

原文（英文）：

> The ball bounced over the fence into our neighbour's garden.

当前日文（完整字段值）：

> ボールは柵を跳び越えて、隣人の庭に入りました。

建议日文（完整字段值）：

> ボールは弾んで柵を越え、隣人の庭に入りました。

判断：球在本句 bounce 的接触表面后弹起/反弹这一运动方式没有保留；当前只明确了越过围栏的路径。完整词条第一义和同句中文均指向弹跳，不存在需要在飞行与反弹之间另选词义的证据。补出“弾んで”即可，不应自行指定地面、次数或碰撞材料。

其他读法与限度：无生命球“跳び越える”可以描写弹跳产生的越障，因而原译并非相反动作；但也可描写投掷或击打后飞过。允许反弹情景不等于译文仍传达了源文明示的反弹方式。

裁决：改判 root 初稿：跳／飛两种表记不能证明表面反弹。反弹方式是本字段已明示的教学信息，必须补回。

依据：

- [Cambridge English–Japanese Dictionary: bounce](https://dictionary.cambridge.org/zht/%E8%A9%9E%E5%85%B8/%E8%8B%B1%E8%AA%9E-%E6%97%A5%E8%AA%9E/bounce)：出版社双语释义把球的 bounce 解释为接触表面后迅速离开，并对应はねる、はね返る；没有仅越障即完整表达 bounce 的说明。
- [小学館デジタル大辞泉：飛（び）越える／跳（び）越える](https://kotobank.jp/word/%E9%A3%9B%E8%B6%8A%E3%81%88%E3%82%8B-584557)：同一词条列飛与跳两写，释义为从物体上方飞/跳过去，且用渡海候鸟举例；因此不能用“写了跳而非飛”证明有表面反弹。

来源绑定：`U-04`，词条上下文 SHA-256 `92fe557cfbd1951ce095d71b21e6cb97e6ad3ab9a417395b521ef490e1be1e20`；原票据 `707b66a509332f3c4ba05146fb34d1e4e68c2448845878708b60e7c5283ff300`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-05"></a>
### U-05 · comedy · `ex.0`

**可选优化**。

原文（英文）：

> We watched a comedy and laughed all evening.

当前日文（完整字段值）：

> 私たちは喜劇を見て、一晩中笑った。

可选日文（完整字段值）：

> 私たちは喜劇を見て、その晩はずっと笑っていた。

判断：一晩中有通宵义，all evening也不能一概当作直到天亮；但在无钟点的日常持续叙述中，出版社自身确有将 all evening 译为一晩中的直接用例。这里看喜剧笑了一晚，与这种自然持续叙述相合，不能把严格词典边界当作唯一实际读法。建议选“その晩はずっと”以减少通宵联想，属于可选消歧。

其他读法与限度：若语境精确区分睡前晚间与整夜（例如排班、服药、截至次日清晨），一晩中的通宵读法会产生实质时间变化。本句没有这样的锚点，不应断言实际笑到清晨，也不应断言当前读者必然获得该信息。

裁决：采用出版社直接 all evening→一晩中用例，排除把通宵词典义当作唯一实际读法的误报。候选仍可减少时间误读。

依据：

- [小学館プログレッシブ英和中辞典：repeat](https://kotobank.jp/ejword/repeat)：出版社词条直接把含 all evening 的食后味觉持续例句译为“一晩中残った”，证明该对应在普通持续叙述中有实际词典用例。
- [小学館プログレッシブ英和中辞典：evening](https://kotobank.jp/ejword/evening)：词条说明 evening 通常是日落到就寝，并与 night 不作严格分界；同时用一晩愉快に過ごす对应晚间娱乐。此项只支持弹性，单独不能推出每个一晩中都等同 all evening。
- [小学館デジタル大辞泉：一晩中](https://kotobank.jp/word/%E4%B8%80%E6%99%A9%E4%B8%AD-682390)：该词条确有日暮到天亮一直的释义，因此保留可选改写及通宵歧义提示，不宣称两词在所有语域完全等价。

来源绑定：`U-05`，词条上下文 SHA-256 `81a424e7b88db637095c0ef58d483e40a935008db6c1785dc34a3a063ab97e84`；原票据 `91976a642df5181cdc5c054b5804e4cb9374452b4234f80b53407be17535998f`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-06"></a>
### U-06 · county · `tip`

**必须修正**（轻微）。

原文（中文）：

> 英国的county通常译为“郡”，美国的译为“县”。

当前日文（完整字段值）：

> イギリスのcountyは通常「郡」、アメリカのcountyも日本語では一般に「郡」と訳します。

建议日文（完整字段值）：

> 中国語では、イギリスのcountyは通常「郡」、アメリカのcountyは「县」と訳します。

判断：本 tip 只有中文来源，按既定“仅中文 tip 按中文翻译”规则，须保留原文所述的中文译名对比。源文的引号对象是英国 county 对应“郡”、美国 county 对应“县”；现译删除美国“县”这一来源信息，改写成两国在日语中都称“郡”的另一条知识。现译知识本身可以正确，但不等于忠实翻译该中文元语言陈述。补明中国語では并保留原引号字形，足以消除跨语言误读。

其他读法与限度：日语界面中补充美国 county 也常称郡，确有官方用例支持且可能有帮助；这可以是另行标明的补充。本次规则没有授权用功能本地化知识替换中文 tip 的原有对比，不能以“理论上可以换编辑方针”制造必须等待作者的新决策。

裁决：改判两份初稿：已给出的中文-only 按中文翻译规则足以决定，现译日语术语事实正确仍不能替换中文译名对比。补明元语言即可，不需要新造编辑授权缺口。

依据：

- [在ニューヨーク日本国総領事館：管轄地域](https://www.ny.us.emb-japan.go.jp/itpr_ja/jurisdiction.html)：官方日文把美国 Fairfield、Idaho 等 county 称为郡，证明现译的日语知识有事实依据；该证据只说明日语命名正确，不能恢复被删掉的中文“县”译名对比。

来源绑定：`U-06`，词条上下文 SHA-256 `18b23f27607771c1ad7a00e69261e672ad886b97d40904c253e4e2159642f369`；原票据 `6ffdf121fd43fe6db279e65a3867fffcbc24b166cacfffc4a33ace951063a35a`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-07"></a>
### U-07 · craft · `ex.1`

**可选优化**。

原文（英文）：

> Traditional craft workshops can preserve cultural knowledge while creating employment opportunities in rural communities.

当前日文（完整字段值）：

> 伝統工芸の教室は、農村の地域社会で雇用機会を生みながら、文化的な知識を保存できます。

可选日文（完整字段值）：

> 伝統工芸のワークショップは、農村の地域社会で雇用機会を生みながら、文化的な知識を守り伝えることができます。

判断：workshop既可以是制作场所，也可以是实际操作、共同学习的课程或活动。「教室」选择了教学活动义，能够传承文化知识，也可为授课者等创造就业，后半句并未使这种读法不可能。中文「作坊」支持制作工坊读法，但英文没有排除课程义，不能仅凭中文认定误译。可用日语「ワークショップ」减少强行限定。

其他读法与限度：制作工房义同样合理，但资料无法确定作者特指工房。完整词条首例也有teaches the craft，并无足以排除教学活动的限定。

裁决：英文 workshop 的制作场所及实作课程义都成立；选ワークショップ避免强制替作者选择工房或教室。

依据：

- [Collins English Dictionary Resources: workshop](https://www.collinsdictionary.com/de/englisch-lernen/workshop)：出版社同时列出共同分享知识或经验的实践活动义，以及包含工具机器的制作场所义，确证本句真实多义。

来源绑定：`U-07`，词条上下文 SHA-256 `42cdf9a8777cbc4ab7fb05a24e60731f1aeb454692919015dd3a60aa28d767f3`；原票据 `6b667b6e1293fbe2e2504a86fe0d855469cb43d49a21aaff9bfc686b26e8b76e`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-08"></a>
### U-08 · difficult · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Many graduates find it difficult to secure stable employment without previous experience in their chosen field.

当前日文（完整字段值）：

> 多くの新卒者は、希望する分野での経験がないと安定した職を得るのが難しいと感じている。

建议日文（完整字段值）：

> 多くの卒業生は、希望する分野での経験がないと安定した職を得るのが難しいと感じている。

判断：graduate 指已完成学业/取得学位的人，源文没有毕业年份、recent/new 或初次求职的限定；新卒却明确加入当年毕业的时间类别。缺乏所选领域经验可以发生于刚毕业者，也可以发生于毕业已久未就业或转行者。改为卒業生可保留实际概括范围，不需要推定作者的典型招聘场景。

其他读法与限度：本句确实很容易让人联想到刚毕业找工作，但“容易联想”并非 graduate 的另一个已确立的近期毕业词义。英语也没有明确说第一份工作，不能以这一新增推断作为新卒的语境证据。

裁决：采纳源文范围分析：缺经验并不等于当年毕业，亦未明说第一份工作。不能用典型招聘情景补出新卒限制。

依据：

- [Cambridge English–Japanese Dictionary: graduate](https://dictionary.cambridge.org/dictionary/english-japanese/graduate)：双语词条以取得学位/成功完成教育界定 graduate，对应学士或卒業生，未加入近期毕业限制。
- [小学館デジタル大辞泉・精選版日本国語大辞典：新卒](https://kotobank.jp/word/%E6%96%B0%E5%8D%92-538260)：两部出版辞典都把新卒界定为当年毕业者，并与既卒对举，确立现译新增的时间限制。

来源绑定：`U-08`，词条上下文 SHA-256 `27631e07bedebabe538bbcb99157e55145d2c521ec64c71b59c7c5b0d2dcdf13`；原票据 `d75c52ffe3f365b497367cf0a0accc224fcd7aecb58bd5dded4f86f38c229e8a`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-09"></a>
### U-09 · disappointed · `ex.1`

**可选优化**。

原文（英文）：

> Graduates may feel disappointed if their first jobs offer few opportunities to apply the skills they have learned.

当前日文（完整字段值）：

> 最初の仕事で学んだ技能を生かす機会がほとんどないと、卒業生は失望するかもしれません。

可选日文（完整字段值）：

> 卒業生は、学んだ技能を最初の仕事で生かす機会がほとんどないと、失望するかもしれません。

判断：日文允许把「最初の仕事で」较远地修饰「生かす機会がない」，可正确理解为第一份工作缺少运用已学技能的机会。然而它紧邻「学んだ技能」，容易先被读成「在第一份工作中学到的技能」，产生源句未作的学习地点限制。由于正确高位附着读法真实存在，不把歧义本身认作确定误译；可选调整语序消除误读。

其他读法与限度：低位附着为「最初の仕事で学んだ技能」时会限制技能的学习地点；高位附着为「最初の仕事で〔学んだ技能を生かす機会〕がない」时与英文对应。英文的they have learned也未明说只在学校学得。

裁决：现句存在正确的高位附着读法，因此不是确定错误；调整语序可直接消除错误的就近附着。

来源绑定：`U-09`，词条上下文 SHA-256 `713abd30a5645a346dab8f25d25220f2fb79f2d94a70115587c97c342518d253`；原票据 `4cfe5a25bc0b9a38569226dc0224655b5e04f22fa101b947213e0110b9700747`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-10"></a>
### U-10 · diving · `ex.0`

**可选优化**。

原文（英文）：

> We went diving and saw colourful fish near the reef.

当前日文（完整字段值）：

> 私たちは潜水に出かけ、サンゴ礁の近くで色鮮やかな魚を見た。

可选日文（完整字段值）：

> 私たちは潜水に出かけ、礁の近くで色鮮やかな魚を見た。

判断：reef可由岩石、沙或珊瑚构成；サンゴ礁不是该词所有指称的总称，但属于真实可接受的reef读法。本句的潜水、彩色鱼与后例海洋生态旅游均允许珊瑚礁场景，未给出岩礁或非珊瑚的限定。因此不能把选择珊瑚礁直接认定为错误。若希望不预设礁的构成，可选用「礁」。

其他读法与限度：岩礁、沙礁也可能；中文「礁石」支持岩礁，却不能覆盖英文未限定的reef。资料只能说明可指哪些礁，不能复原作者见到的具体环境。

裁决：reef 的珊瑚礁读法与本句海洋潜水画面相容，是通常词义选择；候选用礁降低具体化。

依据：

- [Collins English Dictionary: reef](https://www.collinsdictionary.com/us/dictionary/english/reef)：出版社词典把reef列为靠近水面的岩石、珊瑚或沙形成的隆起，证实サンゴ礁是合法所指之一，但并非唯一。
- [Cambridge Dictionary: reef](https://dictionary.cambridge.org/us/dictionary/english/reef)：出版社词典列reef的一般义及a coral reef实例，说明用更宽的礁可避免构成推断。

来源绑定：`U-10`，词条上下文 SHA-256 `c81c217a3070be984a2a8e75646b5e0db5c876a497dbd8552c511108df02530d`；原票据 `58a8fd85ef451fcd4768f1d6e4cb4a6232dc7f61e9c3410adf34f6f63a5a2918`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-11"></a>
### U-11 · embroidery · `ex.0`

**可选优化**。

原文（英文）：

> I practise embroidery by stitching flowers onto plain cushions.

当前日文（完整字段值）：

> 私は無地のクッションに花を縫い付けて、刺繍を練習しています。

可选日文（完整字段值）：

> 私は無地のクッションに花の模様を刺して、刺繍を練習しています。

判断：flowers在刺绣例句中是花形装饰，日文的花を縫い付ける可能被读成缝上花形部件，但并不排除用针线制作并缝上花样。英文stitch onto也容许装饰缝附，不能据此断定实际技法相反。为清楚展示embroidery的图案义，用花の模様を刺す更直接，属于可选表达优化。

其他读法与限度：线绣花样及缝附花形装饰都有语言上的可能，完整例句已明确是刺绣练习。

裁决：英文 stitch onto 以及刺绣的添附技法允许现译；花样表达更直接，按可选清楚度改善处理。

来源绑定：`U-11`，词条上下文 SHA-256 `fc264eb285ef92983de7d830606d150b5ffb8b97fbc64e9e9285ac36ccd3ee31`；原票据 `34d32e3894567aa4f0ee28fefab1fbae5ba4e8284fad60c8da49e174f2e0e88e`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-12"></a>
### U-12 · expect · `col.2`

**原样保留**。

原文（英文）：

> fully expect

当前日文（完整字段值）：

> fully expect｜十分に予想する

处理：保留现有字段值。

判断：fully expect表示强烈预计会发生；在预期语境中十分に予想する是对预见程度的自然表达，不必读成预测工作完成得充分。同条起こるだろうと予想する与expect/hope对比已说明是对发生可能的判断。没有必要仅凭十分的另一读法保留错误疑点。

其他读法与限度：如需更直白可说強く見込む，但现译与强预期义相容，无须强制替换。

裁决：现译可表达充分预见、强烈预计；词条也已区分 expect 与 hope。不为另一个更顺口译法制造必改项。

依据：

- [Cambridge Dictionary: fully expect someone/something to do something](https://dictionary.cambridge.org/dictionary/english/fully-expect-to)：核对该搭配表示强烈相信某事会发生，不引入额外义务或希望义。

来源绑定：`U-12`，词条上下文 SHA-256 `3771d4489f161a148bd138bbb2d3378f240397260b71accbdcb0eddbac6870c7`；原票据 `001eb57eb6a5e8ab504036f1c58c8158a5702a5fc2bbdd7e58892c26e40cff10`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-13"></a>
### U-13 · expert · `ex.0`

**必须修正**（轻微）。

原文（英文）：

> We asked an expert to examine the old painting.

当前日文（完整字段值）：

> 私たちは、古い絵を専門家に調べてもらいました。

建议日文（完整字段值）：

> 私たちは、古い絵を調べるよう専門家に依頼しました。

判断：asked an expert to examine 报告向专家提出检查请求；普通过去陈述“調べてもらいました”报告接受了专家进行的检查服务。源文并不保证该请求已执行。完整 entry 没有接受、完成、结果报告等可支持事件推进的事实，故应写依頼しました，保留请求阶段。examine 可译調べる，不需受中文鉴定影响进一步加入真伪鉴定。

其他读法与限度：提出请求通常可能获得执行，但也允许对方尚未处理或拒绝。てもらう在未来、愿望或疑问句中也能进入请求/安排表达；这里的单独过去陈述没有相应形式，不能用这些用法抹去已接受行为的解读。

裁决：改判 root 初稿：请求履行是可取消的后续推断，不能写成已经接受检查服务。依頼しました保留事件阶段。

依据：

- [Cambridge Dictionary: ask, REQUEST](https://dictionary.cambridge.org/dictionary/english/ask?dictionary_id=5)：出版社把 ask 的请求义界定为说或写出希望对方做某事，未包含对方必已执行该行为。
- [国際交流基金：やりもらい（1）NはNにVてもらう](https://www.jpf.go.jp/j/project/japanese/teach/tsushin/grammar/pdf/tushin44_p22-23.pdf)：官方语法资料把てもらう描述为从他人的行为得到服务/恩惠，并在过去例句中区分行为事实与受益情感；支持此处过去陈述已经报告接受检查行为。

来源绑定：`U-13`，词条上下文 SHA-256 `d1cc58f809eefe09f7b8812dcfe32c79a749292e4d42b5eb4b4bd0a502367bc8`；原票据 `3a58426c8a3e17042e23baccf7122c2798de433cdcfa7603c1ffae12ab440ab1`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-14"></a>
### U-14 · familiar · `ex.1`

**可选优化**。

原文（英文）：

> Students who are familiar with digital tools may adapt more easily to online learning environments.

当前日文（完整字段值）：

> デジタル機器によく慣れた学生は、オンライン学習環境へより容易に適応できるかもしれない。

可选日文（完整字段值）：

> デジタルツールによく慣れた学生は、オンライン学習環境へより容易に適応できるかもしれない。

判断：教育语境中的digital tools可包括硬件、软件与平台；「デジタル機器」容易让读者首先想到硬件，但也可在一般叙述中通过设备使用概括其数字操作经验。源句没有列出必须包含的软件或平台，熟悉设备也确可有助于适应在线学习，因此不能仅凭该术语总体范围更广，就认定本句的设备读法被排除。可选改为デジタルツール，保留更宽的原表达并避免硬件偏向。

其他读法与限度：若作者特指应用程序、平台等软件工具，機器会显得过窄；若泛指计算机等数字工具的使用经验，现译可成立。当前entry无额外材料确定具体工具范围。

裁决：与 integrate 采用同一尺度：数字设备的使用可包含软件操作，ツール更宽但当前不是排他性的硬件限定。

依据：

- [OECD: PISA 2022 ICT Framework](https://www.oecd.org/en/publications/pisa-2022-assessment-and-analytical-framework_dfe0bf9c-en/full-report/component-7.html)：官方教育框架同时列硬件、软件及网站程序为digital tools；说明广义术语范围，并不单独决定该例句特指何类工具。

来源绑定：`U-14`，词条上下文 SHA-256 `8ae86dce8f6006f407ad6605f55682abf5b71f2f09fd0398de1af4e387bb8753`；原票据 `95f7356f6f6610b24bf9ab1c4812dd1efc80edc0f9fc68a0401a85417ca3ee56`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-15"></a>
### U-15 · farmer · `ex.1`

**可选优化**。

原文（英文）：

> Small farmers need reliable access to water and affordable technology to maintain production during dry periods.

当前日文（完整字段值）：

> 小規模農家が干ばつの時期にも生産を維持するには、安定した水源と手頃な費用の技術が必要です。

可选日文（完整字段值）：

> 小規模農家が雨の少ない時期にも生産を維持するには、水を安定して利用できることと、手頃な費用の技術が必要です。

判断：dry periods一般可指雨少、干燥的时期，未必达到长期干旱，但在需要可靠水源维持农业生产这一具体语境中，以干ばつ描述缺雨时期是可接受的农业读法。英文未说是正常旱季或仅短暂无雨，不能把这些其他可能读法当作足以排除干旱的事实。可选用「雨の少ない時期」避免给持续程度增加暗示；水源是reliable access to water的自然压缩表达。

其他读法与限度：普通季节性干燥或较短雨少期同样可能，若需刻意保留这些情况可用更宽的措辞。气象专业上drought通常强调持续缺雨，现译比原词组更具体，但当前农业语境支持这一读法。

裁决：农业供水语境及辅助中文支持干旱读法；采用雨の少ない時期作为更中性的可选表达。

依据：

- [Cambridge Dictionary: drought](https://dictionary.cambridge.org/us/dictionary/english/drought)：出版社将drought定义为少雨或无雨持续较长时期，说明干旱读法与一般dry periods的重叠及更强程度。
- [気象庁: 農業対策に活用いただける気象情報](https://www.jma.go.jp/jma/kishou/nougyou/document/kyushu_south/kyushu_south.pdf)：官方农业资料以少雨（干ばつ）和农业用水管理相联系，支持该农业语境中干ばつ的正常用法；不能据此判定例句所指的实际持续时间。

来源绑定：`U-15`，词条上下文 SHA-256 `f1a90179d040f076162fe80c61e63c70a1e542a253fca8e61606d6c2a261538e`；原票据 `932c3f898eb8cceb2e1ca13fbfa40c5ccc3887e4cfb532ae6a876bb73c7a07bf`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-16"></a>
### U-16 · fresh · `senses.0`

**必须修正**（轻微）。

原文（英文）：

> Recently produced or picked, and not preserved or stale.

当前日文（完整字段值）：

> 新鮮な；保存・加工されておらず古くなっていない

建议日文（完整字段值）：

> 作られたばかり、または収穫したばかりで、保存処理されておらず古くなっていない；新鮮な

判断：preserved在此是为长期保存而作的处理，不是所有加工。现译用「保存・加工されておらず」排除一般加工，会使刚制作的新鲜面包、奶油、咖啡等正常fresh用法不成立，也弱化了源句明确写出的刚生产或采摘这一时间条件。应限定为保存処理并补明近期制作或采收。

其他读法与限度：如果把現译中的加工默读为保存のための加工，可接近原义，但日文并未给出该修饰，通常会按保存与加工并列的广范围理解。源句有produced且词典列fresh bread/cream/coffee，不支持一概排除加工。

裁决：本项是总定义，不能用两条果蔬例句排除刚制作食品。preserved 不能扩大为一切加工。

依据：

- [Cambridge Dictionary: fresh](https://dictionary.cambridge.org/us/dictionary/english/fresh)：出版社将食物fresh与人工保存过程对照，并列fresh bread、fresh coffee、fresh cream，证实一般加工或制作不与fresh相斥。
- [Collins English Dictionary: fresh](https://www.collinsdictionary.com/dictionary/english/fresh)：出版社定义近期采摘或生产且未经冷冻、罐装等保存处理，支持以保存処理替代泛称加工。

来源绑定：`U-16`，词条上下文 SHA-256 `7dfb5e00f7fab259e336128966255c6370c875e9d6ab5d113758eb5acd37f6ce`；原票据 `e1414d9ea1a621c5b50a878b8ebb6a24b9e211776bec0e4b2b6d44f19eb6ce95`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-17"></a>
### U-17 · from · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Students from rural communities may face additional barriers when applying to universities in major cities.

当前日文（完整字段值）：

> 農村の地域社会出身の学生は、大都市の大学に出願する際に、さらに大きな障壁に直面することがあります。

建议日文（完整字段值）：

> 農村の地域社会出身の学生は、大都市の大学に出願する際に、さらなる障壁に直面することがあります。

判断：additional在此是已有或通常障碍之外的附加障碍，现译则把障碍本身表述为进一步更大。障碍多一项可以增加总体负担，但不必使任一障碍的大小或难度更大；完整entry没有提供后一种比较。应保留附加关系，删去未经给出的大小限定。

其他读法与限度：可以把所有障碍概念化为一个总体负担，附加障碍确会使总体负担增加；这属于正常可推得的后果，却不是additional作为前置修饰语变成greater的独立词义。也不能声称additional只涉及可数项目，额外的量同样成立。

裁决：改判 root 初稿：additional 的 put-with 关系不可只保留为困难程度更大；恢复附加的障碍。

依据：

- [Cambridge Dictionary: additional](https://dictionary.cambridge.org/us/dictionary/english/additional)：Advanced与Business义均为extra；Intermediate义先说明加到别物上，再列数量、量、重要性之增加效果，不能截掉前半部当作greater的同义证明。
- [Oxford Advanced Learner's Dictionary: additional](https://www.oxfordlearnersdictionaries.com/us/definition/english/additional)：释义为超过已提或通常的量，extra为同义词；支持附加基准而非障碍个体的尺度比较。

来源绑定：`U-17`，词条上下文 SHA-256 `c90738e2a6cd4a33310e68b96206db0e75b1c5fc6f602f62f5a6c3b1a502dc6c`；原票据 `d564a3ba2d086bcca79b29d1fe34fe65cf8e0048eeeaf449e4b89c06a1fa6ede`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-18"></a>
### U-18 · happen · `ex.0`

**原样保留**。

原文（英文）：

> What happened to the plant beside your window?

当前日文（完整字段值）：

> あなたの窓辺の鉢植えは、どうなったのですか。

处理：保留现有字段值。

判断：plant可以指盆栽这一具体植物，窗边场景自然，而且辅助中文明确说那盆植物；这不是用中文覆盖相反英文事实，而是给英文未限定的植物形态作合理消歧。happened to对应どうなった准确，现译可保留，不必为抽象覆盖所有种植形式而改为生硬的植物。

其他读法与限度：英文单独也可能指其他窗旁植物，但当前盆栽读法由同例中文支持，没有冲突。

裁决：辅助中文明确盆栽，帮助英文未限定处消歧，未覆盖相反的英文事实。现译保留。

来源绑定：`U-18`，词条上下文 SHA-256 `5418a1fe1b874159423885c61de2f49f2435b11846af773616d85773791cd8fa`；原票据 `84459a3e52bebed6d7d258b7df630043c86c149930c8e8a393fed6ebcfb77871`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-19"></a>
### U-19 · high · `ex.1`

**可选优化**。

原文（英文）：

> High housing costs can prevent young adults from living independently, particularly in major urban centres.

当前日文（完整字段值）：

> 特に大都市の中心部では、高い住宅費によって、若い成人が自立して暮らせなくなる場合があります。

可选日文（完整字段值）：

> 特に大都市では、高い住宅費によって、若い成人が自立して暮らせなくなる場合があります。

判断：urban centre可以指城市聚集区，也有城市中心的常见字面读法；住房成本场景容许后者，同例中文明确用了大城市中心。现译关于居住自立与可能性的主旨准确，不能确认其选择必然缩窄了作者所指。若本库希望按整个大城市理解urban centres，可使用大都市，但属于选义上的统一。

其他读法与限度：这里既可能泛指大城市，也可能强调其核心区域，完整例句未作区分，辅助中文支持现译。

裁决：辅助中文明示城市中心，支持当前读法；若要按城市聚集区整体理解，使用大都市更不限定内部区域。

来源绑定：`U-19`，词条上下文 SHA-256 `2e3e3b86ccd2c9e8b68068941035231a0da2cb1569f24a7fa46408968897b644`；原票据 `b9e3aef9e66803b6dd381c90b8f7d69869d10e5a43eeaa312c06a0275c1940d6`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-20"></a>
### U-20 · impost · `col.2`

**必须修正**（重大）。

原文（英文）：

> impost block

当前日文（完整字段值）：

> impost block｜アーチの起拱石

建议日文（完整字段值）：

> impost block｜アーチを支える台石（インポスト・ブロック）

判断：英文完整entry把impost定义为拱从其上起立的突出支承，而一手英文专业索引和大学标色图都把impost block置于柱头与上方拱构件之间；springer则是直接落在impost上的最低拱石。日文官方石桥部件资料第6页将起拱石定义为最下端的轮石，第7页图示其处于拱圈末端；日文建筑史研究亦分别论述柱头上的インポスト・ブロック与再往上承接的アーチ起拱石。综合这些部件位置与支承关系，现译把承托拱石的台块与拱石本体混为一个术语，已超出可选日语消歧；建议用インポスト・ブロック并附简短功能说明。此判断依据实际构件关系，未把中文拱座石或同形汉字当成唯一权威。

其他读法与限度：起拱部附近的台石与最低拱石紧邻，且有些通俗术语会把起拱、迫元等部位名称宽泛混用；仅凭英文springing或汉字起拱本身，确实不足以判错。本次进一步核对了国土交通省网站发布的日文部件定义、大学区分两部件的标色图，以及日文原始建筑史研究中的分层用法，能支持标准术语层面的区分。国土资料范围是石桥，不能据它单独宣称所有日语建筑传统的命名绝无差异；但已查一手证据未支持把本条不加说明的起拱石作为impost block的准确对应。

裁决：新增同属西方拱建筑的日本学术资料，明确インポスト上才放拱起点，补足此前仅石桥术语证据的局限。起拱石与支承台石是不同构件，定为 major。

依据：

- [Getty Research Institute AAT: impost blocks (300001163)](https://www.getty.edu/vow/AATFullDisplay?find=&logic=AND&note=&subjectid=300001163)：定义为置于柱头和从其上起拱的拱之间的石块，确立impost block为承托台块，而非拱圈最下石。
- [Getty Research Institute AAT: springers (voussoirs) (300265528)](https://www.getty.edu/vow/AATFullDisplay?find=&logic=&note=&subjectid=300265528)：明确定义最低拱石从这里开始弯曲，并且直接落在impost上；确认两者为上下相接的不同构件。该页中文起拱石标记未被当作日语翻译证据。
- [University of Pittsburgh: Glossary of Medieval Architecture, impost block or abacus](https://sites.pitt.edu/~medart/menuglossary/impost.htm)：文字定义为柱头顶部与上方构件之间的板块；已查看其abacus.jpg标色图，红色突出平台在柱头上，未标作弧形拱圈中的楔石。
- [University of Pittsburgh: Glossary of Medieval Art and Architecture, springer](https://sites.pitt.edu/~medart/menuglossary/springer.htm)：定义为两侧最下voussoir；已查看springer.jpg标色图，红色最低楔形拱石位于下方水平支承板之上，与impost图形成位置对照。
- [道路橋石橋の構造特性と現状（国土交通省九州地方整備局掲載、2023年9月6日講習会資料）](https://www.qsr.mlit.go.jp/rd_mainte/site_files/file/kousyuukai/01kouzoutokusei.pdf)：已读并渲染检查第6页部件表、第7页部件图。表中輪石是拱的构成石，輪石基礎／起拱石是接触基础地盘的最下端轮石；图中指出其位于拱圈末端。它是日本官方专业用法的证据，限于该资料石桥范围。
- [伊藤喜彦「再利用・再解釈・再構成されるローマ──コルドバ大モスクにおける円柱」西洋中世研究7（2015）, pp.73–96](https://www.jstage.jst.go.jp/article/jsmes/7/0/7_73/_pdf/-char/ja)：出版者全文检索输出的p.90–91描述柱头上的インポスト・ブロック、其上的拱迫元，以及列端部繰形上所载アーチ起拱石；p.93再次说明柱头上的インポスト・ブロック。支持日文建筑史实际叙述将台块与所承托的拱起拱石分层处理。原PDF在本地渲染时部分日文字体不显，因此不将该渲染图充作已读日文段落的依据；日文段落依据出版者全文检索输出。
- [伊藤喜彦（2015）再利用・再解釈・再構成されるローマ（西洋中世研究7、73–96頁）](https://www.jstage.jst.go.jp/article/jsmes/7/0/7_73/_pdf/-char/ja)：出版社索引的论文原文90–91页区分インポスト、其上アーチ迫元与アーチ起拱石。是与西方建筑同领域的直接日语术语证据；不声称已从有字体缺失的渲染图读完该日语段落。

来源绑定：`U-20`，词条上下文 SHA-256 `a9d44a592aa024f5f05da2200b3b9ad55cd2e134f22c2067acb7a08ff379c9fb`；原票据 `7ee45702fa3b103bb5932fe4be4ecc26651cc89ed688a02f887c244f70c67df5`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-21"></a>
### U-21 · integrate · `ex.1`

**可选优化**。

原文（英文）：

> Schools should integrate digital tools into classroom activities while ensuring that all students have equal access.

当前日文（完整字段值）：

> 学校は、すべての生徒が平等に利用できるようにしながら、デジタル機器を授業の活動に取り入れるべきです。

可选日文（完整字段值）：

> 学校は、すべての生徒が平等に利用できるようにしながら、デジタルツールを授業の活動に取り入れるべきです。

判断：在课堂中引入数字设备可以自然包含设备及其软件用途，而不是声称软件不在范围内。digital tools允许设备这一具体读法，整条没有指定工具必须是软件，平等使用条件也完整保留。可将機器改为ツール以便跨软硬件保持统一，与familiar同型处理，不把常见教学用语硬判为术语错误。

其他读法与限度：tools可广指设备和软件，现译偏设备但可在情境中代表整体数字教学工具。

裁决：与 familiar 一致，可选改用ツール以统一软硬件范围，不把常见设备使用表达强判为错。

来源绑定：`U-21`，词条上下文 SHA-256 `59b3cb3fff69838ee2c943d7aac3aae816cfea096b39687763297954ec9ea1aa`；原票据 `9e30dcf92842ad213d0e9c1197a295883a58c3570f28e642a03077e5d182c7e1`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-22"></a>
### U-22 · keyboard · `ex.1`

**可选优化**。

原文（英文）：

> Students with limited mobility may benefit from an adapted keyboard that makes digital learning more accessible.

当前日文（完整字段值）：

> 移動に制約のある生徒には、デジタル学習をより利用しやすくする改良型のキーボードが役立つ場合がある。

可选日文（完整字段值）：

> 身体の動きに制約のある生徒には、操作しやすいように調整され、デジタル学習をより利用しやすくするキーボードが役立つ場合があります。

判断：改良型的具体用途已由前后行动受限与学习更易使用说明，因而可指为其需求改良的键盘，不必理解为任意新品。W3C资料表明此处mobility也涉及手部动作，日文移動容易联想到步行，建议用身体の動き、需求调整来把使用场景说清；当前尚非排斥肢体动作的唯一读法，按可选消歧处理。

其他读法与限度：现译能恢复适应需求的功能，但改良型与移動两词都比专门的操作适配说法更容易泛化。

裁决：适应行动限制的键盘用途可从整句恢复；候选明确身体动作及适配目的，减少移動只指步行的误读。

依据：

- [W3C WAI: Physical in Diverse Abilities and Barriers](https://www.w3.org/WAI/people-use-web/abilities-barriers/physical/)：以手部控制和专门设计键盘说明适配范围，不将mobility仅等同于步行能力；此处只核查翻译。

来源绑定：`U-22`，词条上下文 SHA-256 `b653dec96e13a7df31ec17aa9d6cbeeb6d80c6375c855fb25143586ca23daa14`；原票据 `6ba220e3b79803f9ba8f96b82abb4c70c658e20be8992a835c3332fb13de1c65`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-23"></a>
### U-23 · kill · `tip`

**必须修正**（轻微）。

原文（中文）：

> kill强调造成死亡；die表示自身死亡，不接宾语。

当前日文（完整字段值）：

> kill は死を引き起こすことを強調する。die は自ら死ぬことを表し、目的語を取らない。

建议日文（完整字段值）：

> kill は死を引き起こすことを強調する。die は「死ぬ」という意味の自動詞で、目的語を取らない。

判断：中文在使死亡／自身死亡的语法对照中，只说主语发生死亡，并未赋予主语致死原因或责任。现文的「自ら死ぬ」中，自ら位于动词前，通常按副词解读为自己实施、自己导致或自然由自身产生。即使不把它读作自杀，也不应把这种额外的自因性概括成die的一般意义；die同样用于被外力致死。应直接说死ぬ这一自动态。

其他读法与限度：在自他动词教学中，用自ら说明主体变化是可见的简化，不能把自ら一概当成有意自杀；名词或名词附加用法也可强调自身。可是此句没有「主語自身が」的结构，动词前副词的正常用法即便非意志，仍常含主体为该事态原因／责任者。

裁决：改判 root 初稿：副词自ら不同于主语自身这一名词性说明；非意志用法仍可带自身致因，不等同中性的死亡。并不宣称现译必然等于自杀。

依据：

- [小学館デジタル大辞泉: 自ら](https://kotobank.jp/word/%E8%87%AA%E3%82%89-637852)：区分自分自身的名词义与自己力量实施的副词义；不能不分词类挪用名词释义来豁免动词前副词。
- [小薬哲哉「『自ら』の2つの強意用法とその形式的・意味的特徴について」（2020）](https://ir.library.osaka-u.ac.jp/repo/ouka/all/76977/gbkp_2019_r5_021.pdf)：pp.23–24区分动词句副词用法；pp.28–29明确列非意志例，并解释为主体负有事态责任、自动地／自身为原因。支持修正双方过强的意志与纯中性论证。
- [Cambridge Dictionary: die](https://dictionary.cambridge.org/dictionary/english/die)：基本义为生命结束，列不及物用法，并不限于自己实施死亡；这里只用于通用词义对照。

来源绑定：`U-23`，词条上下文 SHA-256 `f13e6bbd1204b7c6c45d888cb7c3e0f3a1c6423be7167ef567df0adb0aa2a808`；原票据 `ba5c7eca9ed098a3a42085a0b8119cf739b7ef18819928fa699edc5cdf65227d`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-24"></a>
### U-24 · kitchen · `ex.1`

**可选优化**。

原文（英文）：

> Shared kitchen facilities can encourage social interaction among students living in university accommodation away from home.

当前日文（完整字段值）：

> 共用の台所設備は、親元を離れて大学の宿舎で暮らす学生同士の交流を促進できます。

可选日文（完整字段值）：

> 共用の台所設備は、家を離れて大学の宿舎で暮らす学生同士の交流を促進できます。

判断：大学宿舍及离家读书的常见情境容许把home理解为原先与父母生活的家，親元を離れる是自然的本地表达，没有同条证据反驳它。英文也能包括离开自己家庭的成年学生，因而更中性的家を離れて更便于覆盖多年龄读者；这是减少默认背景的表达选择，不直接确认原译增加了错误亲属事实。

其他读法与限度：home可为父母家，也可为学生自己其他形式的家，现译采用典型大学生活读法。

裁决：大学住宿离家场景允许親元这一常规读法；家を離れて可覆盖更多家庭背景，属于可选宽化。

来源绑定：`U-24`，词条上下文 SHA-256 `49172f2e4f0201589ce8cf710a53c60df7ea6ba9286bb714a031dfb0b61bf9f2`；原票据 `86b8b90246a3766023360ffe972576c557582a0bc23c2e60e960c40c7c63b38f`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-25"></a>
### U-25 · librarian · `ex.0`

**可选优化**。

原文（英文）：

> The librarian helped me find a book about birds.

当前日文（完整字段值）：

> 図書館員は、私が鳥についての本を探すのを手伝ってくれました。

可选日文（完整字段值）：

> 図書館員に手伝ってもらい、私は鳥についての本を見つけました。

判断：英文肯定过去时的helped me find以发现所需书籍为助成目标，通常叙述的是找到书，不能说它只编码尝试寻找。日文探す的词汇义确实只保证寻找活动，但研究指出完成的探す叙述存在找到的结果含意。在此普通的图书馆员服务完成叙述中，手伝ってくれました与明确的所需书籍使读者自然把它理解为帮忙找成，而非专门报告未果的协助；全词条也没有失败、持续搜索或尚未找到的取消线索。因而按允许自然日语表达、不能仅以形式动词区别判错的标准，保留为通过，并可选把结果显式写出。此结论不以「没说找不到」作为充分理由。

其他读法与限度：若加上「しかし本は見つかりませんでした」，日文原则上仍可成立，证明找到不是探す的严格蕴涵；英文当前句的通常完成读法则不能这样自然取消。该差别是真实的，若编辑要求每个明示结果都以日语词汇直接保证，则应统一采用见つける结果句，而不能只修本项而放过同构的officer/steward。当前孤立服务叙述没有迫使采用未果读法的事实。

裁决：与 officer、steward 同类统一：英语通常包含找到结果，日语完成服务叙述可通过正常结果含意恢复；候选显式写出结果。研究不等于对本三句做过读者实验。

依据：

- [Cambridge / GLOBAL English-Japanese Dictionary: find](https://dictionary.cambridge.org/ja/dictionary/english-japanese/find)：出版社词典将所寻物的find定义为发现正在寻找的对象，并用见つかる／见つける表达；支持find端点含义，不能当作单纯search的同义词。
- [Naoko Komoto (2003): Restructuring and Implicative/Non-implicative Verb Sentences, OUPEL 7:33–64](https://ir.library.osaka-u.ac.jp/repo/ouka/all/72927/oupel07_033.pdf)：大学原始论文印刷第35页将help列入implicative谓语。支持肯定、已发生的助成事件通常带补语实现的解读；不能把清单外推到所有时态、疑问、请求或未完成help情形。论文并未直接测试这里三个find句子或其日译。
- [国立国語研究所 IPAL 基本動詞: さがす](https://www2.ninjal.ac.jp/dictionaries/IPALBV/pdf_dir/%E3%81%95%E3%81%8C%E3%81%99.pdf)：官方词汇说明把探す定义为查找并试图发现所求对象，且把本列为适用宾语。说明该词的词汇语义不独自保证找到，也不表示必定失败。
- [中本武志: 動能交替の語彙操作, 言語文化論集49（1999）, pp.159–209](https://tsukuba.repo.nii.ac.jp/record/1746/files/1.pdf)：大学公开原始论文第201页脚注13直接区分探す动作的完了与发现结果：完了并不保证找到，但作者承认相应结果含意存在。这支持在普通完成叙述中可恢复找到，也明确它不是严格的词汇同义或不可取消的结果保证。没有对本次三个服务例句做母语者可接受度实验。

来源绑定：`U-25`，词条上下文 SHA-256 `1826905023b6a60d2b1bbed6d798e713fa2e9c73caababed1ab6f12616cc73a8`；原票据 `4b5f66c399382021fd5b97760cb9b8300c9deb30e80940d814b6c604f075e5eb`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-26"></a>
### U-26 · mathematical · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Mathematical models help researchers predict how rising temperatures may affect coastal communities over time.

当前日文（完整字段值）：

> 数学モデルは、気温上昇が将来、沿岸地域にどう影響し得るかを研究者が予測する助けになります。

建议日文（完整字段值）：

> 数学モデルは、気温上昇が時間の経過とともに沿岸地域にどのような影響を及ぼし得るかを、研究者が予測する助けになります。

判断：over time指出随着时间经过或在延展时间段中的作用，现译将其换成了相对于现在的未来定位。将来不必是单一时点，但它也不要求关注随时间的发展过程；数学模型预测未来影响这一本就可由predict读出的信息，不能完全取代原文另加的时间过程关系。建议明确时间经过，同时保留may的可能性。

其他读法与限度：将来可以覆盖未来一个阶段，root反对“将来一定是单点”是正确的。本句的升温、预测使未来过程成为自然背景，但这种可相容性不足以让任意未来影响叙述自动表达over time。over time本身也不保证影响单调增大或速度缓慢，不能强加这些细节。

裁决：改判 root 初稿：将来可以是一段时期，但没有表达源文明示的随时间推移关系。兼容未来过程不等于翻出了过程。

依据：

- [Cambridge Dictionary: over, DURING](https://dictionary.cambridge.org/us/dictionary/english/over)：over time例句明确释为as time passes，确立经过时间这一关系。
- [Cambridge English Grammar Today: over](https://dictionary.cambridge.org/grammar/british-grammar/over_2)：时间用法指延展的时间段，而非该时间段内任意一点；该资料说明源文关系，不用来声称日语将来必然只指一点。
- [小学館デジタル大辞泉: 将来](https://kotobank.jp/word/%E5%B0%86%E6%9D%A5-533605)：释为これから先、未来、前途；允许未来阶段，但未内含随着时间经过的过程修饰。

来源绑定：`U-26`，词条上下文 SHA-256 `fe2ebe59bb74f40e03f25cc05e2eb2281d6fd15af2abf1f3fd072c0793bcbe0d`；原票据 `f36be3925e747ad776f426001bc6f25841e8f01ea8bcd87e4c06b86b1b1e3a8d`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-27"></a>
### U-27 · medium-sized · `ex.1`

**可选优化**。

原文（英文）：

> Medium-sized cities can offer diverse employment opportunities while maintaining shorter commuting times than major urban centres.

当前日文（完整字段值）：

> 中規模の都市は、大都市中心部より短い通勤時間を保ちながら、多様な雇用機会を提供できる。

可选日文（完整字段值）：

> 中規模の都市は、大都市より短い通勤時間を保ちながら、多様な雇用機会を提供できます。

判断：本句把中等城市与大型城市聚集中心比较，较自然的概括译法是大都市。现译也可能将通勤目的地的城市核心区作为比较对象，仍保留中等规模城市通勤较短的意思；中心范围没有被原文进一步说明，尚不足以确认错误。建议与high同型表达统一为较不限定内部区域的大都市，作为范围消歧。

其他读法与限度：urban centre可描述城市这一聚集中心，也能在普通语境中让人联想到中心区域；本句更偏前者，但不是独立地理定义。

裁决：可选统一为大都市，避免把城市聚集中心只读成内部核心区；不凭另一种宽译法就把当前词义选择确认为错。

来源绑定：`U-27`，词条上下文 SHA-256 `e552a282184db11957bfeda00d76a8ac6f82b3933c5fcdb5bf9fc3ef4fd5d404`；原票据 `6b89b4f86fb73d835865f2d5df6be30d377e94c9d833a929e078384354ba2001`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-28"></a>
### U-28 · nowhere · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Without affordable housing, some low-income families have nowhere to live despite having regular paid employment.

当前日文（完整字段值）：

> 手頃な価格の住宅がないため、低所得の家庭の中には、定期的に賃金の出る仕事をしていても住む所がない家庭がある。

建议日文（完整字段值）：

> 手頃な価格の住宅がないため、低所得の家庭の中には、継続的に有償の仕事をしていても住む所がない家庭がある。

判断：英文regular修饰paid employment，强调规律或持续的有偿工作；现译中定期的に直接修饰賃金の出る，把规律关系改放在工资发放。持续工作与按期领薪常重合，却不是同一事实，尤其间歇或临时工作也可按月结薪。保留工作持续性即可，无需推成法律意义上的永久、正社员或终身雇佣。

其他读法与限度：工资定期发放可以让人推想就业稳定，住房负担语境也让这一步推理很容易；但源文没有明说工资支付周期，译文也没有明说工作本身规律。without在本句可作当前缺乏住房的原因，未发现必须另外变成条件句的证据。

裁决：改判 root 初稿：持续有偿就业与按期发薪不是同一个依存关系。候选修饰就业持续性，不擅加正社員或永久合同。

依据：

- [Cambridge Dictionary: regular](https://dictionary.cambridge.org/us/dictionary/english/regular)：收录固定规律发生义，并分别举regular income、regular hours；HR义另外举regular employment，强调工作持续性。不能据此把regular employment归为发薪周期。

来源绑定：`U-28`，词条上下文 SHA-256 `26e2b89043a48d73e5236f5f378618f6f049348b261785b87e673c221dfa3f6b`；原票据 `b72ac10f371635022cc25192f8dc4ac11177b86eaaa266a1339a959b76c51e02`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-29"></a>
### U-29 · occurrence · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Improved drainage systems can reduce the occurrence of flooding in densely populated urban areas.

当前日文（完整字段值）：

> 排水設備を改善すると、人口密集地域での洪水の発生を減らせます。

建议日文（完整字段值）：

> 排水設備を改善すると、人口が密集した都市部での洪水の発生を減らせます。

判断：英文明确同时限定人口密集和城市属性；日文只保留人口密集，整条也未以都市等词补回。人口密集地域不等于城市，不能仅凭排水设施就排除村镇密集地区。这里有独立、明确的urban修饰词被省略，宜补都市部，以保留原文的适用范围；不涉及对防洪知识本身作判断。

其他读法与限度：读者常联想到城市，但这种常见联想不能代替原文已明确给出的地理限定。

裁决：urban 是独立明示的限定，人口密集不能自动补回城市属性。需补都市部。

来源绑定：`U-29`，词条上下文 SHA-256 `e05519afa4c13f8619bbbe63f8c2498feaa45636e44e9a864fedbffdafd2a9c6`；原票据 `39d692477489b76e07b79a43bfea2783a36961d430734dbdb14501dafec0edfb`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-30"></a>
### U-30 · officer · `ex.0`

**可选优化**。

原文（英文）：

> A police officer helped us find the station.

当前日文（完整字段值）：

> 警察官が、駅を探すのを手伝ってくれた。

可选日文（完整字段值）：

> 警察官に手伝ってもらい、私たちは駅を見つけた。

判断：英文helped us find通常叙述警察的协助促成定位车站，结果比helped us look for更明确；肯定help的助成读法不能被轻率说成无结果。日文探す本身不保证终点，但已完成的协助叙述可以通过常见的查找结果含意表达找成。此句没有仍在寻找、失败或结果另有悬念的线索，警察提供服务的场景也使成功定位这一读法自然。因此作为正常日译可通过，同时建议可选显式写出见つけた以保留英文端点的清晰度。中文车站只用于支持駅，不作为推翻英文的权威。

其他读法与限度：「駅を探すのを手伝ったが、結局見つからなかった」是语法上可成立的日文续句；这说明当前日文不是严格结果保证，不说明当前完整场景已经改变成失败。若要求翻译逐一保留不可取消的事件结果，应在三项同构例句统一采用显式结果表达。station在警察语境也可能是警察署，但英文没有station前的police，中文支持车站，现译駅有可接受来源读法。

裁决：与 librarian、steward 同类统一。接受过程叙述中的通常结果含意，但保留显式找到结果的可选候选。

依据：

- [Cambridge / GLOBAL English-Japanese Dictionary: find](https://dictionary.cambridge.org/ja/dictionary/english-japanese/find)：出版社词典将所寻物的find定义为发现正在寻找的对象，并用见つかる／见つける表达；支持find端点含义，不能当作单纯search的同义词。
- [Naoko Komoto (2003): Restructuring and Implicative/Non-implicative Verb Sentences, OUPEL 7:33–64](https://ir.library.osaka-u.ac.jp/repo/ouka/all/72927/oupel07_033.pdf)：大学原始论文印刷第35页将help列入implicative谓语。支持肯定、已发生的助成事件通常带补语实现的解读；不能把清单外推到所有时态、疑问、请求或未完成help情形。论文并未直接测试这里三个find句子或其日译。
- [国立国語研究所 IPAL 基本動詞: さがす](https://www2.ninjal.ac.jp/dictionaries/IPALBV/pdf_dir/%E3%81%95%E3%81%8C%E3%81%99.pdf)：官方词汇说明把探す定义为查找并试图发现所求对象，且把本列为适用宾语。说明该词的词汇语义不独自保证找到，也不表示必定失败。
- [中本武志: 動能交替の語彙操作, 言語文化論集49（1999）, pp.159–209](https://tsukuba.repo.nii.ac.jp/record/1746/files/1.pdf)：大学公开原始论文第201页脚注13直接区分探す动作的完了与发现结果：完了并不保证找到，但作者承认相应结果含意存在。这支持在普通完成叙述中可恢复找到，也明确它不是严格的词汇同义或不可取消的结果保证。没有对本次三个服务例句做母语者可接受度实验。

来源绑定：`U-30`，词条上下文 SHA-256 `0a3ea8a4eaadb19f154e9b8feee59d86ecac5ab376dd4056c1b337b4b922ebee`；原票据 `24877d8cbbaec373fa60b0f9beb3e71887f4dbe2e78abba50b9dca1f249e2122`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-31"></a>
### U-31 · persistence · `ex.1`

**必须修正**（重大）。

原文（英文）：

> The persistence of poverty suggests that economic growth alone cannot guarantee better living conditions for every household.

当前日文（完整字段值）：

> 貧困が続いていることは、経済成長だけでは、どの家庭にもよりよい生活条件を保証できないことを示唆しています。

建议日文（完整字段值）：

> 貧困が続いていることは、経済成長だけでは、すべての家庭の生活条件が改善することを保証できないことを示唆しています。

判断：英文否定的是仅靠增长就能为所有家庭保证更好生活条件这一全覆盖保证；它没有排除对某些家庭能够作出保证，也没有说没有家庭实际改善。日文「どの家庭にも〜保証できない」的正常量化读法，是对每个家庭分别否定保证的可能性，即任何家庭都无法确保。wh-mo与普通すべて并非在否定中可任意互换：一手研究不仅给出主语例，也给出目的语wh-mo不能取否定以下范围的对比，另有可能形否定例仍无部分否定读法。完整前句虽让读者容易猜到作者意在批评未能普及，但语用猜测不能自动证明当前句法有正常的「无法保证全覆盖」读法。建议把全称家庭放入显式的保证内容从句，令否定清楚作用于全覆盖保证。这是保证量化范围的修正，不应扩写成没有任何家庭受益。

其他读法与限度：可尝试在篇章层面把「どの家庭にもよりよい生活条件を保証する」整体理解为普遍保障的方案，再否定其可行性；本句的贫困持续语境确实促成这种修复性理解。但现有一手资料将do-no N-mo与否定搭配为每一项均否定，且将它与可有否定宽范围的subete区别处理；未找到直接支持当前受益对象结构可稳定表达部分否定的证据。研究材料不等于对本句每位母语者的实测，故不能声称所有读者都绝不可能猜出原意；这也不同于已有可接受语法读法而仅需可选消歧。

裁决：采用 major：不是任何家庭都能保证与任何一家都不能保证的范围差异影响核心命题。语法研究支持どの…も配否定的全否定风险；并未据此宣称增长毫无益处。

依据：

- [Cambridge English Grammar Today: Every](https://dictionary.cambridge.org/grammar/british-grammar/every)：出版社官方语法说明every指完整群体的每个成员，通常否定为not every。此处结合cannot guarantee后的补足内容，区分不保证全体与不保证任何个体；不是断言实际改善人数。
- [Hadas Kotek: Diagnosing covert syntax: Lessons from wh-in-situ (Yale, April 2019)](https://hkotek.com/diagnosing-covert-syntax-handout.pdf)：研究者本人提供的讲义第3页例14直接比较目的语dono mondai-o-mo与subete-no mondai-o，前者只有every大于not，后者可有两种范围。这比仅凭主语「どの学生も来なかった」推广到本句更相关；它仍不是当前保证句的母语者实验。
- [Masaaki Kamiya and Zhaosen Guo: Acquisition of L2 English Negative Quantifiers without Equivalent Lexical Items in an L1 (2024)](https://journals.us.edu.pl/index.php/TAPSLA/article/download/13029/13649/83437)：研究论文第3页例7使用dono-uma-mo和可能形否定tobikoer-are-nakat-ta，明确标记every大于not而拒绝not大于every；说明出现可能形本身不自动解锁部分否定。
- [Shuichi Yatabe: Negation and Focusing in the Grammar of Japanese](https://phiz.c.u-tokyo.ac.jp/~yatabe/negation.pdf)：东京大学研究者原文例27将dono gakusei mo konakatta说明为无学生来，并与后续可歧义的表达区分；支持不同全称表达的否定范围不能笼统等同。

来源绑定：`U-31`，词条上下文 SHA-256 `db598af0a5a89ad839107702d757f67eead3f919200a743ce388e164067c69e8`；原票据 `a0cc575573650fd79ecf6b694bd318d1adca72ab8a0074b5c1a9a1fec1ccb24e`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-32"></a>
### U-32 · portrait · `ex.0`

**原样保留**。

原文（英文）：

> My grandmother's portrait hangs above the living room fireplace.

当前日文（完整字段值）：

> 祖母の肖像画は、居間の暖炉の上に掛かっている。

处理：保留现有字段值。

判断：portrait允许绘画这一常见所指，壁炉上挂祖母肖像的情境自然，同条总释义也正确覆盖绘画、素描和照片。例句不需要同时列出该词所有可能媒介；没有照片或其他排除绘画的说明，因此肖像画不是已证实的媒介误译，可以保留。

其他读法与限度：也可能是照片，但这是英文的未指定性，而不是足以否定当前合法绘画读法的证据。

裁决：portrait 的绘画义明确成立，且总释义已涵盖照片等媒介。无需让每条独立例句列出所有可能媒介。

来源绑定：`U-32`，词条上下文 SHA-256 `11ff9a38b9a5cd2fcdf6b9eeb0c162f91afffbc92e4d06c2069ffbb391d7d658`；原票据 `dfe240b16429b8ef6981b9fb7d415b3b3894f54ba244edf521ffb5ac13cea1ce`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-33"></a>
### U-33 · pot · `col.2`

**可选优化**。

原文（英文）：

> a pot of tea

当前日文（完整字段值）：

> a pot of tea｜お茶1壺

可选日文（完整字段值）：

> a pot of tea｜ティーポット1杯のお茶

判断：壺在日语可以作容器称呼，お茶一壺也并非绝无可接受的文化或书面用法，不能直接确定它必然指干茶叶而非饮用茶。作为A2常用搭配，现代读者更容易从ティーポット1杯理解壶装的一份茶；建议换成这一常见说法，属于用词清楚度优化，而非确认容积或数量事实错误。

其他读法与限度：传统容器称呼与现代茶壶习惯用语的差异，不能只凭不常见就断定知识错误。

裁决：一壺并非无效日语，但现代日常学习词条用ティーポット1杯更直观。只作表达优化。

来源绑定：`U-33`，词条上下文 SHA-256 `10391e9e105cd1f6cbcf43ab7a29bdf82d5d45f0833f29696238fa8b370b3b9b`；原票据 `147beb9a2f319468ee4465f50b334b6ce62de6ff50cbd394e58d73f587c959ee`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-34"></a>
### U-34 · prominent · `ex.0`

**可选优化**。

原文（英文）：

> A prominent local artist opened the exhibition yesterday.

当前日文（完整字段值）：

> 昨日、地元の著名な芸術家が展覧会を開きました。

可选日文（完整字段值）：

> 昨日、地元の著名な芸術家が展覧会を開幕させました。

判断：open可泛指使活动开始，也可指正式揭幕；日语「展覧会を開く」保留了使展览开始举办的正常读法。英文没有officially、ceremony等限定，不能仅依据中文「揭幕」就断定艺术家只担任剪彩嘉宾、绝非举办者。现译可以保留；如果编辑希望突出开幕时点，可选用「開幕させました」。

其他读法与限度：著名人士为展览揭幕是很自然的读法，但艺术家使展览开始举行同样不违背英文及完整entry。词典能证明两种关系，不能决定作者未说明的活动角色。

裁决：open 与開く都可使活动开始；没有明确剪彩、典礼限定。开幕表达是可选选义澄清。

依据：

- [Oxford Advanced Learner's Dictionary: open verb](https://www.oxfordlearnersdictionaries.com/definition/english/open_2)：start something义为使活动或事件开始，另有正式启用仪式义；支持不把opened强制限定为剪彩。

来源绑定：`U-34`，词条上下文 SHA-256 `21be51f2c7d93976f1fd4b647084ea5d844ddfcd464f5741e13dfad3bf228fc9`；原票据 `21229f9fb33de84f40b0c723481ca290240a516bd3355051ad4bd73eb056463c`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-35"></a>
### U-35 · propose · `ex.1`

**必须修正**（轻微）。

原文（英文）：

> Researchers propose expanding urban green spaces to improve air quality and encourage residents to exercise more regularly.

当前日文（完整字段值）：

> 研究者たちは、大気の質を改善し、住民の定期的な運動を促すため、都市の緑地拡大を提案しています。

建议日文（完整字段值）：

> 研究者たちは、大気の質を改善し、住民がより定期的に運動するよう促すため、都市の緑地拡大を提案しています。

判断：原文more明确比较运动规律性或频率的提高，现译只剩定期运动这一种行为，没有比较增量。研究目的、提议和绿地扩大的关系其余均保留；应补出「より」，避免学习者漏掉more的实际贡献。

其他读法与限度：regularly可表示经常，也可表示有规律地；两者在运动语境都合理。现译采用规律义本身不是错误，问题是任何一个读法中的比较级都未呈现。

裁决：more regularly 的比较增量必须保留，不以目的可推知改善代替明示比较级。

依据：

- [Cambridge Dictionary: regularly](https://dictionary.cambridge.org/us/dictionary/english/regularly?topic=frequency-and-regularity-general-words)：区分OFTEN与EVENLY两个义项；不能把其中任一正常义项本身当成误译。

来源绑定：`U-35`，词条上下文 SHA-256 `b3fbdc59aba5e749ae6350106fe0201b81239e36de9bd10997867bcb37307d9e`；原票据 `b97a0fa48b19627dd025c0a954ea613049cc8f2a514d1bb001de7dabdd74776a`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-36"></a>
### U-36 · replace · `ex.1`

**可选优化**。

原文（英文）：

> Renewable energy could gradually replace fossil fuels if governments invest sufficiently in infrastructure and storage technology.

当前日文（完整字段值）：

> 政府がインフラや蓄電技術に十分投資すれば、再生可能エネルギーは徐々に化石燃料に取って代われる可能性がある。

可选日文（完整字段值）：

> 政府がインフラやエネルギー貯蔵技術に十分投資すれば、再生可能エネルギーは徐々に化石燃料に取って代われる可能性がある。

判断：再生可能エネルギー在此可以正常指再生能源发电，storage technology也常指帮助其并网的电力储存；所以「蓄電技術」是一种有实据的正常语境读法，不能仅因energy storage还包含直接供热用途而强判错误。不过英文没有限定electricity，改成「エネルギー貯蔵技術」能保留更广的适用范围，适合作可选澄清。条件、逐渐替代以及可能性均未发生反转。

其他读法与限度：官方资料同时支持电力储存配合再生能源和储热直接用于供热、制冷。源句未指明电力系统，不能声称作者排除了后者，也不能声称作者必然在说后者。现译采取电力读法可成立。

裁决：蓄電是再生能源储能的正常具体场景；使用エネルギー貯蔵可覆盖热与化学等形式，属于可选宽化。

依据：

- [US EPA: Electricity Storage](https://www.epa.gov/energy/electricity-storage)：说明电力储存用于把更多再生能源整合进电网，确立现译电力读法的正常专业语境。
- [US Department of Energy: Solar Integration: Solar Energy and Storage Basics](https://www.energy.gov/cmei/systems/solar-integration-solar-energy-and-storage-basics)：储热可直接用于供热制冷，也可发电；支持更广译语作为可选范围保留，不证明作者意图。

来源绑定：`U-36`，词条上下文 SHA-256 `f3f9ac434f2c6fe8a51180b31923400195573b955fa33d7c7bd7bbe93861b748`；原票据 `cbc9e3199057e9a5a5ca7ffd900428ef27224bddb2aa263d6b5f1b77f6a389bc`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-37"></a>
### U-37 · sausage · `col.1`

**可选优化**。

原文（英文）：

> vegetarian sausage

当前日文（完整字段值）：

> vegetarian sausage｜植物性ソーセージ

可选日文（完整字段值）：

> vegetarian sausage｜ベジタリアン向けソーセージ

判断：现译作为肉类替代品的常用类别名可以成立，并未写成「100%植物性」或「ヴィーガン」。vegetarian并不排除蛋奶，而日本官方对植物来源替代食品的说明也明确可含部分动物来源原料，因此不能把「植物性ソーセージ」一律当成严格纯素承诺再判错。若要精确保留适用饮食类别，建议可选改成「ベジタリアン向け」。

其他读法与限度：如果把植物性强读为所有成分都只来自植物，译文会比vegetarian窄；但食品类别的普通用法未必做这一承诺，完整entry只说替代传统肉制品，未给出配方或纯素声明。

裁决：与同词例句统一。植物性作为类别称呼未自动承诺100%植物或纯素；向け直接表达 vegetarian 适用类别。

依据：

- [Collins English Dictionary: vegetarian](https://www.collinsdictionary.com/dictionary/english/vegetarian)：食物义是不含肉或鱼，并未要求排除蛋奶。
- [東京都多摩府中保健所: プラントベース食品／食物アレルギー表示](https://www.hokeniryo.metro.tokyo.lg.jp/shisetsu/jigyosyo/hokenjyo/tamafuchu/kouhou/tabemono/b041704020230925162414710)：说明植物来源替代食品有全植物来源、也有部分动物来源成分的种类，避免直接等同纯素。

来源绑定：`U-37`，词条上下文 SHA-256 `3fd00b0e71d307694afc53c36b17c43c51b4ab1fb823d6059e4b524609959887`；原票据 `593a6b8dd0a85ce795831467704874746633661bc765a84bbf011f4e3bf5c486`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-38"></a>
### U-38 · sausage · `ex.1`

**可选优化**。

原文（英文）：

> Consumers are increasingly choosing vegetarian sausages as they seek alternatives to traditional meat products.

当前日文（完整字段值）：

> 従来の肉製品の代わりを求めて、植物性のソーセージを選ぶ消費者が増えている。

可选日文（完整字段值）：

> 従来の肉製品の代わりを求めて、ベジタリアン向けのソーセージを選ぶ消費者が増えている。

判断：寻找传统肉品替代品、选择这类香肠的消费者增加，三者关系均正确。这里的植物性是食品类别用语，并未限定百分之百或排除全部蛋奶；官方日本说明也允许植物来源替代食品含部分动物来源原料，故不应将现译自动解释成纯素再判定范围错误。可选改成「ベジタリアン向け」以直接表达英文饮食类别。

其他读法与限度：vegetarian不一定vegan，现译若被读成所有成分纯植物会较窄；但现文无100%或纯素声明，完整entry也没有具体配方，普通肉类替代食品的读法可成立。

裁决：与同词搭配统一，不把植物性自动强读成不含任何蛋奶。候选直接对应 vegetarian，未作产品成分判断。

依据：

- [Collins English Dictionary: vegetarian](https://www.collinsdictionary.com/dictionary/english/vegetarian)：vegetarian food的定义是不含肉鱼，不等于排除所有动物来源成分。
- [東京都多摩府中保健所: プラントベース食品／食物アレルギー表示](https://www.hokeniryo.metro.tokyo.lg.jp/shisetsu/jigyosyo/hokenjyo/tamafuchu/kouhou/tabemono/b041704020230925162414710)：植物来源替代食品类别在日本用法中可包括部分动物来源原料，支持不要把现译强读为纯素。

来源绑定：`U-38`，词条上下文 SHA-256 `3fd00b0e71d307694afc53c36b17c43c51b4ab1fb823d6059e4b524609959887`；原票据 `34532fde2c9013d7c40b73a32874814d76aefd4bbdebfb79e8c90be265a2c120`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-39"></a>
### U-39 · shiny · `col.0`

**必须修正**（轻微）。

原文（英文）：

> shiny shoes

当前日文（完整字段值）：

> shiny shoes｜光るほど磨いた靴

建议日文（完整字段值）：

> shiny shoes｜つやのある靴

判断：shiny描述鞋表面的光泽、反光状态，现译却断言已经磨到发亮，增加了造成该状态的打磨行为。完整entry第一例确实另有polished，但独立搭配shiny shoes没有polished，不能把另一条例句的事件移进搭配的词义。应直接描述鞋的光泽。

其他读法与限度：打磨是鞋发亮的常见原因，且与第一例相符；这能说明现译画面合理，却不能让shiny本身蕴含打磨，亮面材质或新鞋也可shiny。

裁决：独立搭配没有 polished；不得把另一条例句的打磨事件移入通用搭配的状态义。

依据：

- [Oxford Advanced Learner's Dictionary: shiny](https://www.oxfordlearnersdictionaries.com/definition/english/shiny)：定义为光滑明亮、反射光，并直接列shiny black shoes；不把已打磨列为必要条件。

来源绑定：`U-39`，词条上下文 SHA-256 `50936f4fc53dacef0a44aa3da3c3275cabd9997e7fa846c4453ed17a4872edab`；原票据 `14ddbf89c00c9f4f05f6ea8947804577c90b976763b5ffc78ee0f80d686325a8`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-40"></a>
### U-40 · stake · `ex.0`

**可选优化**。

原文（英文）：

> She bought a small stake in her sister's bakery.

当前日文（完整字段值）：

> 彼女は姉（または妹）のパン屋に少額出資しました。

可选日文（完整字段值）：

> 彼女は姉（または妹）のパン屋の持ち分を少し購入しました。

判断：stake可指持分，也有投在企业里的资金金额这一商业用法。小企业中少额出资取得权益是本例的合理读法，不能只凭持分比例与金额并非恒等就确认现译错误；姉または妹也保留了sister未说明的年龄。为让bought与financial share更显明，可改为持ち分を少し購入しました，但当前译文可保留。

其他读法与限度：小比例持份或小额投资都有词典依据；参考资料不能证明作者唯一强调哪个维度，现译选择后一读法成立。

裁决：商业词典允许把 stake 解释为所投资金额，少额出资并非已证实错误。可选持ち分购买表达更直接对应 bought；原撤回记录保持不变。

依据：

- [Cambridge Business English Dictionary: stake](https://dictionary.cambridge.org/us/dictionary/english/stake?topic=increasing-and-intensifying)：商业定义包含投入公司的金额且常以股本比例表示；因此不能把金额读法宣布为不存在。

来源绑定：`U-40`，词条上下文 SHA-256 `000aeec9c641fd6ee0b66caa16b86dc4fb3dad45606fd065efe1d9066b63ed54`；原票据 `bc6d55d03732bc8dd6b581d0f1945ae0a5c4da673cd88bb9ef8c0deb3da8a9eb`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-41"></a>
### U-41 · stay · `ex.1`

**可选优化**。

原文（英文）：

> Tourists who stay longer in rural areas may contribute more to local businesses than short-term visitors.

当前日文（完整字段值）：

> 農村部に長く滞在する観光客は、短期の旅行者よりも地元の商店に多くの収益をもたらすかもしれません。

可选日文（完整字段值）：

> 農村部に長く滞在する観光客は、短期の旅行者よりも地元の事業者に多くの収益をもたらすかもしれません。

判断：countable business 的出版双语词条直接列公司、商店、店、店舗等对应，local businesses 在旅游消费叙述中用地元の商店是有常规词汇依据的读法。这里没有所有企业类型或排除零售的明示范围；中文商家和收益也支持经济消费关系。事業者可更稳妥覆盖住宿、交通等，建议可选宽化，不把当前词汇对应定为必改。

其他读法与限度：旅游收入当然可能惠及住宿、交通和体验经营者，事業者因此更全面。但这只能证明更宽译法有用，不能证明源句已对每个行业作全称或类别穷尽陈述。也不能从出版社列出商店反推出本例实际只谈零售。

裁决：补入出版社对可数 business 的商店直接对应，不能只靠子类关系辩护。旅游句未明示类别穷尽，事業者是可选宽化。

依据：

- [小学館プログレッシブ英和中辞典：business](https://kotobank.jp/ejword/business)：可数商贸组织义直接列出商店、店、店舗及公司等日译，并有店铺开闭、店权转让例子，证实商店是常规对应，并非仅凭集合包含关系临时选出的实体。

来源绑定：`U-41`，词条上下文 SHA-256 `fc40cbdfdbebf7aa531824fe0cbc06588670e414e31a1f03c30632ab49bdb825`；原票据 `ab17a9c1effef9d4fc219337e516b01ac46e9f10a8076cd26f9eee037933b334`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-42"></a>
### U-42 · steward · `ex.0`

**可选优化**。

原文（英文）：

> A steward helped us find our seats before the concert.

当前日文（完整字段值）：

> 演奏会の前に、係員が席を探すのを手伝ってくれました。

可选日文（完整字段值）：

> 演奏会の前に、係員に手伝ってもらい、私たちは自分たちの席を見つけました。

判断：helped us find our seats在该过去肯定事件中通常包含找到座位的助成结果；不能因为有help就把find降为纯尝试。日文探す不独自蕴涵找到，但演奏会前係員完成协助的叙述可正常让读者恢复成功定位自己座位的结果，且全entry没有取消这一结果的内容。这与图书馆找书、警察帮找车站同构，应使用同一尺度通过，并可选补写见つけました。係員符合活动服务人员义，席的所有者也可由受益参与者自然恢复，不需额外增加亲自带路或已经坐下。

其他读法与限度：当前日文的结果含意可取消，故不能称它与英文在严格语义上完全等价；若作者要对是否找到作对比、排除只是帮忙找过或要求结果完全显式，则宜改成完整结果句。正常服务场景中过程词可用来概述整个目标活动，这属于语用恢复而非探す词典中另有「已找到」义。

裁决：与 librarian、officer 同类统一，不把找座位和找书、车站采用不同标准。候选可明确找到结果。

依据：

- [Cambridge / GLOBAL English-Japanese Dictionary: find](https://dictionary.cambridge.org/ja/dictionary/english-japanese/find)：出版社词典将所寻物的find定义为发现正在寻找的对象，并用见つかる／见つける表达；支持find端点含义，不能当作单纯search的同义词。
- [Naoko Komoto (2003): Restructuring and Implicative/Non-implicative Verb Sentences, OUPEL 7:33–64](https://ir.library.osaka-u.ac.jp/repo/ouka/all/72927/oupel07_033.pdf)：大学原始论文印刷第35页将help列入implicative谓语。支持肯定、已发生的助成事件通常带补语实现的解读；不能把清单外推到所有时态、疑问、请求或未完成help情形。论文并未直接测试这里三个find句子或其日译。
- [国立国語研究所 IPAL 基本動詞: さがす](https://www2.ninjal.ac.jp/dictionaries/IPALBV/pdf_dir/%E3%81%95%E3%81%8C%E3%81%99.pdf)：官方词汇说明把探す定义为查找并试图发现所求对象，且把本列为适用宾语。说明该词的词汇语义不独自保证找到，也不表示必定失败。
- [中本武志: 動能交替の語彙操作, 言語文化論集49（1999）, pp.159–209](https://tsukuba.repo.nii.ac.jp/record/1746/files/1.pdf)：大学公开原始论文第201页脚注13直接区分探す动作的完了与发现结果：完了并不保证找到，但作者承认相应结果含意存在。这支持在普通完成叙述中可恢复找到，也明确它不是严格的词汇同义或不可取消的结果保证。没有对本次三个服务例句做母语者可接受度实验。

来源绑定：`U-42`，词条上下文 SHA-256 `63f22b2be303ae5f51183ecb908ad5c0c37558a7c9450200acf9a1df5f23bf5c`；原票据 `2c2c83fc77e1cb913a2f069269600e0c77af119e0d20a45dbcec0e1eb7d3c92a`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-43"></a>
### U-43 · terminable · `ex.1`

**可选优化**。

原文（英文）：

> Employment contracts should be terminable by either party, provided that reasonable notice is given.

当前日文（完整字段值）：

> 雇用契約は、妥当な期間を置いて通知することを条件に、どちらの当事者からも終了できるべきです。

可选日文（完整字段值）：

> 雇用契約は、終了までに妥当な予告期間を設けて通知することを条件に、どちらの当事者からも終了できるべきです。

判断：notice在这里明确是终止前的预告，同条前例一か月前に通知也确认时间方向。当前妥当な期間を置いて通知可读成留出终止前猶予后予告，也容易被读成先等待再通知；并非只有错误读法，故不确认为倒置事实。无需猜作者意图，建议直接把期间的终点写成終了まで，让条件更清楚。

其他读法与限度：问题主要在日文附着不清，不是英文有几种法律要求；完整entry能支持正确理解，候选用于消歧。

裁决：整条第一例已说明终止前预告；现译存在正确读法。候选把期间参照点明确为終了まで，不把单句歧义等同已倒置顺序。

依据：

- [Employment New Zealand: Notice periods](https://www.employment.govt.nz/ending-employment/giving-notice)：官方解释预告期从给出通知到雇佣结束，核实英文术语的时间方向；不把该国规则推广为本例具体法律义务。

来源绑定：`U-43`，词条上下文 SHA-256 `919ef5538f05f67871939fea1b5a1e922e1de4445f91566a67be80a8842c72e1`；原票据 `a7b0db7dc1199fcd6e257926279e07d980009bccb68d1982639dbe0e5b7a2c40`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-44"></a>
### U-44 · territory · `tip`

**可选优化**。

原文（中文）：

> 领土义可不可数；一块辖区可用a territory。

当前日文（完整字段值）：

> 領土の意味では可算にも不可算にもなります。1つの管轄地域にはa territoryを使えます。

可选日文（完整字段值）：

> 領土の意味では可算・不可算のどちらでも使えます。1つの管轄地域を指す場合は a territory と言えます。

判断：可不可数在提示列表中可合理理解为可数/不可数的压缩写法；Cambridge的territory领土/区域义明确标为C or U，同时列不可数territory及可数territories。当前日译选择的是语法事实正确、与整条释义相容的读法，没有依据将它确定为错。原中文建议补写成可数或不可数，避免被误读成未回答的问句，日译本身可保留。

其他读法与限度：中文也有可能漏写可作不可数中的作，但原文不存在支持必须采用该排他解释的线索；不把这种可能性当成现译知识错误。

裁决：出版社的 C/U 标记支持现译。另建议原中文可不可数写明可数或不可数；本次不修改源文，也不将源文压缩表述误判成日译错误。

源文另行编辑建议（未修改）：领土义可数或不可数；一块辖区可用 a territory。

依据：

- [Cambridge Dictionary: territory](https://dictionary.cambridge.org/us/dictionary/english/territory)：AREA义明确C or U，并用territory/territories例子区分两种数法；支持当前解释的正确性，不改动中文源文。

来源绑定：`U-44`，词条上下文 SHA-256 `b8e428dcc8d1cf02670ca23f88a8fc3f6a07ca0552dfdc70d4f084aca53538b7`；原票据 `c963a26b79322466ee590b46d7888c2099932fa3508c0cdec970f6688c6e5012`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-45"></a>
### U-45 · thermometer · `ex.1`

**可选优化**。

原文（英文）：

> Accurate thermometers help researchers monitor temperature changes in natural habitats affected by global warming.

当前日文（完整字段值）：

> 正確な温度計は、地球温暖化の影響を受ける自然の生息地で、研究者が気温変化を監視する助けになります。

可选日文（完整字段值）：

> 正確な温度計は、地球温暖化の影響を受ける自然の生息地で、研究者が温度変化を監視する助けになります。

判断：temperature有明确的气温义，温暖化影响的自然生息地研究可正常监测当地空气温度，所以「気温変化」不是把英语不可能的义项带入译文。英文也未限定只测空气，若希望例句同时涵盖水温或地温，用「温度変化」更能保留范围；这属于可选的较宽表达，现有上下文不足以证明当前气温读法错误。

其他读法与限度：自然生息地可以为水域，温度计也能测水温、地温；这些读法真实存在。另一方面，英文temperature本身也可指大气冷热度，当前句无明确水域限定，不能把另一种可行研究对象当成唯一作者意图。

裁决：temperature 有气温这一正常义项，全球变暖场景支持；温度是覆盖水、土壤等介质的可选中性表达。

依据：

- [Collins English Dictionary: temperature](https://www.collinsdictionary.com/dictionary/english/temperature)：既列通用温度义，Webster’s New World义项也明确列大气冷热度，证明気温是正常词义而非错误专业事实。
- [Oxford Advanced Learner's Dictionary: temperature](https://www.oxfordlearnersdictionaries.com/definition/english/temperature)：列water/air/surface temperature等，证明宽泛温度表达可保留更多可能对象，但不能决定本句唯一测量对象。

来源绑定：`U-45`，词条上下文 SHA-256 `cd4300b61504d0e952e6cc747eb0d5c4d38256d65df304f6603abbb2356f2761`；原票据 `ccd0e420d650763e07d780f3ee397c1f1e909b06f4b1239923285a54ef4a751d`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-46"></a>
### U-46 · tiger · `ex.0`

**可选优化**。

原文（英文）：

> The tiger rested in the shade beside a pool.

当前日文（完整字段值）：

> そのトラは、水場のそばの木陰で休んでいました。

可选日文（完整字段值）：

> そのトラは、水場のそばの日陰で休んでいました。

判断：shade 不固有地限定树木，但英日出版资料确实把木陰列为正常日译，旺文社官方双语专栏也直接以未另写 tree 的 in the shade 对应木陰。因而在本动物水边休息的自然描写中，现译有常规语用对应的依据，不是只能从“有树也可能”凭空辩护。日陰保留遮阴来源开放性更好，可选采用。

其他读法与限度：实际阴影仍可能来自岩石、墙体或棚子；第二例森林不证明第一例有树。所查双语资料证明木陰可以是正常译法，不证明这只虎现场确有树，也不建立“所有 shade 都等于木陰”的规则。

裁决：出版社直接 in the shade→木陰 的用例支持正常日译；并非据此确认本例现场确有树。日陰作为来源中性候选。

依据：

- [アルク 英辞郎 on the WEB：shade](https://eow.alc.co.jp/search?q=shade)：出版词典服务将日陰、木陰、物陰并列为日光被遮挡义的正常对应，支持当前词汇选择的自然性。
- [旺文社 英語の友：英語で伝える「日本の行事」10月 運動会](https://eigonotomo.com/column/column_04/d6)：官方双语文章把独立的 in the shade 短语译作木陰，英文附近未另明说 tree；此实际出版社用例支持自然对应，不能据它确认本虎例的遮挡物。
- [Collins English–Japanese Dictionary: shade](https://www.collinsdictionary.com/dictionary/english-japanese/shade)：该词条的日陰释义以树等物体为例，说明树只是常见来源而非必需条件，支持保留来源中性的可选改写。

来源绑定：`U-46`，词条上下文 SHA-256 `db8eb42e27a0b962bb3c84aa7dfb92e28541ed65f2d0cc7a8fd27811efb58709`；原票据 `aa5b1f74326be82d8afaccd3d235ee3b5d94317803e8b6d8bb8110f94208710a`。初审、根审初稿和追加审查均保存在本次审查目录。

<a id="u-47"></a>
### U-47 · tune · `ex.1`

**原样保留**。

原文（英文）：

> A memorable tune can help young learners retain new vocabulary and develop greater confidence in speaking.

当前日文（完整字段值）：

> 覚えやすい旋律は、幼い学習者が新しい単語を記憶し、話す自信を高める助けになります。

处理：保留现有字段值。

判断：young既可译年轻也可译幼小；旋律帮助学词的教育场景及同例中文低龄学习者支持儿童读法，原文没有明确的青春期年龄组与之冲突。不能拿某一机构young learner考试的固定年龄反推本句必指更大儿童。现译can及greater confidence也以一般助益和高める自然表达，可保留。

其他读法与限度：young learners有更宽的年龄可能，但幼い不是一个固定法定年龄段，语境中的低龄读法成立。

裁决：young 的幼小义与教育语境、辅助中文低龄一致；不能套某考试年龄带强判幼い为错。现译保留。

依据：

- [小学館 プログレッシブ英和中辞典: young（コトバンク収録）](https://kotobank.jp/ejword/young)：年龄义列若い、年少、幼い；不把幼い限定为来源没有规定的具体岁数。

来源绑定：`U-47`，词条上下文 SHA-256 `a9733ea43388f8c6869410c23356071e5deca92dd6f4d4bf254f4eab3d03e6be`；原票据 `324d14f2722fba7fd4c4b47ed8d26b49bd062034a038c81efc08680ede8e333a`。初审、根审初稿和追加审查均保存在本次审查目录。

## 保存与验证

235个绑定的词库、组装脚本及既有说明文件逐字节未变；47个字段的完整源文与当前日文语境均未变。此前全库审查的2511个文件和树哈希保持不变。原有初审、撤回、二审及本轮初稿保留，不回写历史记录。

历史审查树 SHA-256：`7d7179ec26d17dac68ccff742843532afc0fc5d9a835b2687a9c1439f253b535`。

本轮没有运行翻译模型、重新组装语料、构建站点或发布。验证针对覆盖、来源绑定、完整候选、搭配英文前缀、分类及文件保护；这些检查不替代语义审阅，也不构成全库无错保证。

机器可读目录：`/Users/paulasmith/Documents/ChatGPT/IELTS-word-atlas/.local/ja-uncertain-focused-review-2026-10-28`。

- `summary.json`：完成状态与统计。
- `confirmed-errors.json`：15处必须修正及完整替换值。
- `optional-clarifications.json`：28处可选优化。
- `retained.json`：4处保留。
- `unresolved.json`：本轮未解决项，当前为空。
- `final/U-*.json`：逐项裁决、证据、旧票据与审阅文件哈希。
- `validation.json`、`evidence-manifest.json`：验证结果和文件字节绑定。
