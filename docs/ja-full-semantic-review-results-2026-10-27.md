# 全库日译语义复审汇总

完成时间：2026-10-27T18:17:06+09:00

全库 7,298 词条、60,387 日译字段已逐条审查或按未变语境复用结论；全部 120 个疑点字段已完成另一位审查者的源文二审。

确认错误：62 字段；仍存疑：47 字段；二审排除初审疑点：11 字段。

以下为审查结论和候选修改，尚未写回词库。存疑项需结合说明决定是否修改或先澄清源文。

审查由 Codex 执行，独立于之前被测的本地模型；并非专业人工认证。每项保留完整源文/日译语境与两轮依据。

其中 1,664 个字段复用源文、日文和整条语境均未变的历史结论，其余 58,723 个字段在本轮重新对照。另有 29,625 个原样保留或空字段通过完整性检查，不计入语义审查分母。

## 建议处理顺序

1. 优先修正 6 个重大错误字段，重点检查术语、对象范围和核心含义。
2. 再修正 56 个轻微错误字段，包括助词、搭配、时间边界和程度差异。
3. 将 47 个存疑字段单独保留，按原文歧义、可接受的自然译法和专业术语依次确认。候选译文供选择，不应批量视为已确认错误写回。

存疑项的级别表示问题若成立时的潜在影响，并不表示误译已经成立。报告给出完整字段的候选替换文本；搭配保留原有“英文｜日文”结构。正式修改后仍需同步打包产物并检查页面显示。

## 确认错误

### deduction / 第2个搭配（col.1）

级别：重大

源文：tax deduction

现译：tax deduction｜税額控除

建议（完整字段）：tax deduction｜所得控除（課税所得からの控除）

依据：本搭配tax deduction指从应税所得中扣减；现译「税額控除」指从计算后的税额中扣减，对应的是tax credit这一不同机制。二审根据英日官方说明及商业词典，确认计算基础从所得变成税额，属于实质专业术语混淆，不能依辅助中文表面形消除差别。

词库位置：`data/ja/entries/56.json`，`deduction`，`col.1`

修改注意：候选说明所得控除的词义；此结论不判断任何个人的具体税务适用。

参考：[IRS公式教材のdeductionとcreditの比較により、所得からの控除と計算済み税額からの控除を区別。](https://apps.irs.gov/app/understandingTaxes/hows/tax_tutorials/mod09/tt_mod09_02.jsp)

参考：[出版社のBusiness English原著定義の検索表示でも、納税前の所得から費用を差し引くtax用法を確認。本文再取得は403。](https://dictionary.cambridge.org/us/dictionary/english/deduction)

参考：[税額控除が算出所得税額からの控除であることを国税庁一次説明で確認。](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1200.htm)

### insect / 第1个词义（senses.0）

级别：重大

源文：A small animal with six legs and three main body sections.

现译：昆虫；6本の脚と主に3つの体節を持つ小動物

建议（完整字段）：昆虫；6本の脚を持ち、体が頭部・胸部・腹部の3つの主要な部分に分かれる小動物

依据：原文的three main body sections指头、胸、腹三个主要身体区段；「体節」则是各区段内更细的重复单位，不能把昆虫全身说成只有三个体节。此外main原本修饰区段的重要性，现译「主に3つ」却变成数量上的大致限定。二审确认术语和计数单位均改变了昆虫形态特征，属于实质错误。

词库位置：`data/ja/entries/8.json`，`insect`，`senses.0`

参考：[昆虫の腹部は第三の機能的な体の区分であり、さらに複数の体節からなるという大学の昆虫学教材。](https://genent.cals.ncsu.edu/bug-bytes/abdomen/)

参考：[昆虫の体の区分と体節を区別する大学の日本語教材。](https://www.brain.rcast.u-tokyo.ac.jp/ivbpf/%E6%98%86%E8%99%AB%E3%81%AE%E8%84%B3%E7%A5%9E%E7%B5%8C%E7%B3%BB/)

### relax / 第1个词义（senses.0）

级别：重大

源文：To become calm and comfortable, or make someone feel this way.

现译：くつろぐ；休む

建议（完整字段）：くつろぐ；気持ちを落ち着かせる；人をくつろがせる

依据：英文同一释义同时列出自己变得平静舒适，以及使别人进入这种状态两种用法。现译「くつろぐ；休む」只表达本人放松，漏掉使他人放松的及物用法。其他肌肉或规则释义及relaxing词形提示不能替代这部分定义，因此二审确认是实质性释义遗漏。

词库位置：`data/ja/entries/3.json`，`relax`，`senses.0`

### sidewalk / 第2个搭配（col.1）

级别：重大

源文：sidewalk café

现译：sidewalk café｜歩道沿いのカフェ

建议（完整字段）：sidewalk café｜歩道に屋外席を設けたカフェ

依据：Collins对sidewalk café的释义包含设在步道上的户外座位。现译「歩道沿いのカフェ」只说明沿步道的位置，连纯室内营业的沿街咖啡馆也符合，遗漏了区分这一固定搭配的核心特征。整条内容也未补足户外座位义，因此二审确认遗漏，建议在译文明确写出。

词库位置：`data/ja/entries/23.json`，`sidewalk`，`col.1`

参考：[複合語sidewalk caféの定義に、歩道に設けられた屋外席が含まれることを確認。](https://www.collinsdictionary.com/us/dictionary/english/sidewalk-cafe)

### terminal / 第2个词义（senses.1）

级别：重大

源文：Describing an illness that cannot be cured and causes death.

现译：病気が治療できず、死に至る；末期の

建议（完整字段）：治癒できず、死に至る病気についていう；末期の

依据：cannot be cured表示无法治愈，并不表示治疗或照护本身无法进行。现译「治療できず」扩大否定对象，改变了末期疾病的基本概念；同条搭配和提示原已正确使用治愈表述。二审据此确认实质术语错误，候选改为无法治愈且导致死亡，不否定持续治疗或照护的可能。

词库位置：`data/ja/entries/38.json`，`terminal`，`senses.1`

参考：[terminal illnessは治癒不能であって、継続中のケア・支援まで不可能という意味ではない。](https://www.nhs.uk/tests-and-treatments/end-of-life-care/your-wellbeing/coping-with-a-terminal-illness/)

### torture / 第2条例句（ex.1）

级别：重大

源文：International agreements prohibit torture and require governments to protect the basic rights of all prisoners.

现译：国際的な協定は拷問を禁じ、すべての受刑者の基本的な権利を守るよう政府に求めています。

建议（完整字段）：国際的な協定は拷問を禁じ、拘禁されているすべての人の基本的な権利を守るよう政府に求めています。

依据：prisoners可以包含未决羁押者，而日语「受刑者」限于正在服刑的人。原文要求保护所有被拘禁者的基本权利，现译会排除尚未定罪的人；相关官方资料也明确区分两类。二审确认这损害了人权保护对象的重要范围，属于实质性术语及对象范围错误，候选扩大回所有被拘禁的人。

词库位置：`data/ja/entries/33.json`，`torture`，`ex.1`

参考：[刑事施設の収容対象を受刑者と未決拘禁者に区別する法務省資料。](https://www.moj.go.jp/KYOUSEI/SHINJO/facilities.html)

参考：[国連の被拘禁者処遇規則は未決の人をuntried prisonersとして含める。](https://www.unodc.org/documents/justice-and-prison-reform/Nelson_Mandela_Rules-E-ebook.pdf)

### application / 第2条例句（ex.1）

级别：轻微

源文：Simplifying the application process could encourage more students from disadvantaged backgrounds to apply for university scholarships.

现译：応募の手続きを簡単にすれば、不利な立場にある学生が大学の奨学金に申し込みやすくなるかもしれません。

建议（完整字段）：応募の手続きを簡単にすれば、不利な立場にあるより多くの学生が大学の奨学金に応募するよう促せるかもしれません。

依据：英文说明简化程序可能鼓励更多处境不利的学生申请，明确比较参与人数。现译只说这些学生可能更容易申请，没有保留more所表达的人数增加。程序简化有助申请的大意仍在，但不能以便利性替代数量变化，因此二审确认轻微遗漏，候选补回更多学生参与。

词库位置：`data/ja/entries/30.json`，`application`，`ex.1`

### apprise / 第1条例句（ex.0）

级别：轻微

源文：Please apprise me of any changes before Friday.

现译：変更があれば、金曜日までに知らせてください。

建议（完整字段）：変更があれば、金曜日になる前に知らせてください。

依据：before Friday以周五开始前为界，「金曜日までに」却可能允许周五当天内通知。英文和辅助中文都没有包含当天的依据，现译因而延后了通知截止边界。其他变化即通知的请求内容保持准确，二审确认轻微时间范围错误，候选明确在周五到来之前。

词库位置：`data/ja/entries/71.json`，`apprise`，`ex.0`

### arrow / 第2个搭配（col.1）

级别：轻微

源文：an arrow points to

现译：an arrow points to｜矢印がを指す

建议（完整字段）：an arrow points to｜矢印が〜を指す

依据：现译「矢印がを指す」在主格「が」与目的格「を」之间没有所指对象或空位标记，日语内部构式不成立。英文to开放了后续对象位置，学习搭配可以保留这个位置，但日译需明确标示填入处。二审确认轻微语法缺口，候选用「〜」标明对象。

词库位置：`data/ja/entries/21.json`，`arrow`，`col.1`

### brief / 第3个搭配（col.2）

级别：轻微

源文：brief someone on

现译：brief someone on｜人にについて必要事項を説明する

建议（完整字段）：brief someone on｜人に〜について必要事項を説明する

依据：现译「人にについて必要事項を説明する」把说明对象的人与表示主题的「について」直接相连，内部缺少主题内容或空位标记。英文on后本可开放说明主题，但日语需显示内容应填入哪里。二审确认轻微构句缺口，候选明确空位，保留向某人说明必要事项的搭配功能。

词库位置：`data/ja/entries/23.json`，`brief`，`col.2`

### delivery / 第2条例句（ex.1）

级别：轻微

源文：The growing demand for home delivery has increased traffic congestion in many urban neighbourhoods.

现译：宅配需要の増加によって、多くの都市の地区で交通渋滞が悪化している。

建议（完整字段）：宅配需要の増加によって、都市部の多くの地区で交通渋滞が悪化している。

依据：many修饰的是城市地区的数量，原文可包括同一城市内多个地区；现译「多くの都市の地区」通常变成许多城市的地区，改变了数量限定的对象。原文未说明城市总数。宅配需求上升导致拥堵恶化的因果仍准确，二审确认轻微数量修饰错误，候选把多放回地区。

词库位置：`data/ja/entries/21.json`，`delivery`，`ex.1`

### destruction / 第3个搭配（col.2）

级别：轻微

源文：a trail of destruction

现译：a trail of destruction｜沿道に残る破壊の跡

建议（完整字段）：a trail of destruction｜通った所に残る破壊の跡

依据：a trail of destruction指行进后一路留下的破坏痕迹，并无道路沿线条件。现译「沿道」把位置限定到道路两旁，词条中的风暴与海岸语境也不支持这个限制。二审确认轻微地点增译，候选改为一般的经过之处，保留破坏连续留痕的意义。

词库位置：`data/ja/entries/46.json`，`destruction`，`col.2`

### dispute / 第2条例句（ex.1）

级别：轻微

源文：Independent experts dispute the claim that building more roads will permanently reduce traffic congestion.

现译：独立した専門家は、道路を増やせば交通渋滞が恒久的に解消するという主張に疑問を呈しています。

建议（完整字段）：独立した専門家は、道路を増やせば交通渋滞を恒久的に緩和できるという主張に疑問を呈しています。

依据：reduce允许拥堵仍然存在，只是程度或数量减少；「解消する」则容易读成问题消失。现译因此把专家质疑的命题由永久缓解拥堵加强为永久消除拥堵，改变了被质疑效果的强度。二审确认轻微意义变化，候选改用緩和，保留独立专家提出疑问的关系。

词库位置：`data/ja/entries/50.json`，`dispute`，`ex.1`

### drawing / 第2条例句（ex.1）

级别：轻微

源文：Drawing can help children express emotions that they may find difficult to communicate through spoken language.

现译：絵を描くことは、幼い子どもが話し言葉では伝えにくい感情を表す助けになれる。

建议（完整字段）：絵を描くことは、子どもが話し言葉では伝えにくい感情を表す助けになる。

依据：原文children面向儿童整体，并未只指幼童或低龄儿童；难以用口语表达情感也是能力条件，而非年龄限定。现译额外加入「幼い」，把受益对象缩窄，完整语境没有支持这一限制。二审确认轻微增译，候选删除年龄修饰并保留绘画辅助表达情感的关系。

词库位置：`data/ja/entries/17.json`，`drawing`，`ex.1`

### elbow / 第2个搭配（col.1）

级别：轻微

源文：rest your elbows on

现译：rest your elbows on｜両肘をに置く

建议（完整字段）：rest your elbows on｜両肘を〜に置く

依据：现译「両肘をに置く」把宾语后的「を」与地点助词「に」直接连在一起，缺少放置地点或空位标记。英文on可以在搭配中开放地点位置，但日语也须让读者看清内部哪里应填词。二审确认轻微构式缺失，候选在地点处加入「〜」，保留原来的搭配用途。

词库位置：`data/ja/entries/21.json`，`elbow`，`col.1`

### eventually / 第2个搭配（col.1）

级别：轻微

源文：eventually lead to

现译：eventually lead to｜最終的ににつながる

建议（完整字段）：eventually lead to｜最終的に〜につながる

依据：「最終的ににつながる」把副词「最終的に」与表示结果对象的「に」直接连接，中间没有结果内容或空位标记，按现形无法组成可用构式。英文to开放后续对象，日语学习搭配也需明确这个位置。二审确认轻微语法缺失，候选只补出填入标记。

词库位置：`data/ja/entries/23.json`，`eventually`，`col.1`

### eventually / 第3个搭配（col.2）

级别：轻微

源文：eventually become

现译：eventually become｜最終的にになる

建议（完整字段）：eventually become｜最終的に〜になる

依据：现译「最終的にになる」在表示最终的副词后直接接变化结果的「に」，没有告诉读者应在哪里填入变成什么。原文become所开放的结果位置可以保留，但必须在日语构式中明确。二审确认轻微内部缺项，候选标出变化结果的空位并保留最终成为的意义。

词库位置：`data/ja/entries/23.json`，`eventually`，`col.2`

### exchange / 第1条例句（ex.0）

级别：轻微

源文：Can I exchange this shirt for a smaller size?

现译：このシャツを一つ小さいサイズに交換できますか。

建议（完整字段）：このシャツをもっと小さいサイズに交換できますか。

依据：英文a smaller size只要求比当前尺码小，未指定小几档。现译「一つ小さいサイズ」把请求固定为只小一档，排除了希望小两档以上的情形。辅助中文的「小一号」不能确立英文没有的数量限制。二审确认轻微增译，候选去掉具体档数。

词库位置：`data/ja/entries/27.json`，`exchange`，`ex.0`

### graze / 第1条例句（ex.0）

级别：轻微

源文：Sheep graze quietly beside the river every summer morning.

现译：毎年夏の朝には、羊たちが川辺で静かに草を食べます。

建议（完整字段）：夏は毎朝、羊たちが川辺で静かに草を食べます。

依据：every summer morning表示夏季每个早晨，重复单位是每天的早晨；现译「毎年夏の朝には」转成每年夏天早晨，未明确夏季每日的频率。羊在河边安静吃草的内容准确，但every所修饰的时间单位已经改变。二审确认轻微频率错误，候选直接写夏季每天早晨。

词库位置：`data/ja/entries/33.json`，`graze`，`ex.0`

### grill / 第1个词义（senses.0）

级别：轻微

源文：To cook food using direct heat from above or below.

现译：上下からの直火で焼く

建议（完整字段）：上または下から直接熱を当てて焼く

依据：原文from above or below包括由上方或下方任一方向直接加热；「上下から」通常指上下两方同时作用，改变了选择关系。同条提示也区分英美用法中的热源方向，需保留这一差别。烤制核心义仍准确，二审确认轻微逻辑变化，候选明确上或下。

词库位置：`data/ja/entries/31.json`，`grill`，`senses.0`

### guess / 第1条例句（ex.0）

级别：轻微

源文：Can you guess what is inside this little box?

现译：この小さな箱の中に何が入っているか、当てられる。

建议（完整字段）：この小さな箱の中に何が入っているか、当てられますか。

依据：英文向对方提问能否猜出小盒子里的物品，现译主句却以「当てられる」结束，通常表示有这种能力。中间的「か」只构成关于箱内物品的间接疑问，不能使整句成为提问。二审确认独立学习例句失去问句功能，属于轻微语法及话语功能错误，候选恢复主句疑问。

词库位置：`data/ja/entries/12.json`，`guess`，`ex.0`

### interference / 学习提示（tip）

级别：轻微

源文：in多接事务指干涉；with多接活动指妨碍。

现译：inは事務や問題に続いて干渉を表すことが多く、withは活動に続いて妨害をよく表します。

建议（完整字段）：inの後には事柄を表す語を続けて干渉を表し、withの後には活動を表す語を続けて妨害を表すことが多いです。

依据：中文「接」说明in或with后接事务、活动等内容；日译却说in跟在事务或问题后、with跟在活动后，倒置了介词与名词的顺序。即使其他搭配展示了正确顺序，这条学习提示本身仍解释错误。二审确认轻微语法及意义问题，候选明确名词应置于介词之后。

词库位置：`data/ja/entries/53.json`，`interference`，`tip`

### internet / 第2个搭配（col.1）

级别：轻微

源文：an internet connection

现译：an internet connection｜ネットワーク接続

建议（完整字段）：an internet connection｜インターネット接続

依据：英文明确指互联网连接；「ネットワーク接続」还可指只连接局域网的网络连接，未必接入互联网。词条标题虽帮助推知对象，仍不能代替短语本身的限定；辅助中文也不能覆盖英文。二审因此确认是轻微的限定遗漏，建议明确写出互联网。

词库位置：`data/ja/entries/2.json`，`internet`，`col.1`

参考：[ローカルネットワークに接続していてもインターネットには接続されていない状態を区別する公式日本語用語例。](https://support.microsoft.com/ja-jp/windows/experience/connectivity-networking/fix-wi-fi-connection-issues-in-windows)

### investigation / 第1条例句（ex.0）

级别：轻微

源文：An investigation revealed why the kitchen ceiling was leaking.

现译：調査により、台所の天井から雨漏りする原因が分かりました。

建议（完整字段）：調査により、台所の天井から水が漏れていた原因が分かりました。

依据：英文只说明厨房天花板漏水及调查揭示原因，没有指定水来自雨水还是管道等。现译「雨漏り」提前限定了来源为雨水，增加调查对象的具体原因。二审确认轻微增译，候选用一般水漏，既保留天花板漏水与查明原因，也避免补写原文没有的水源。

词库位置：`data/ja/entries/48.json`，`investigation`，`ex.0`

### jealous / 第2条例句（ex.1）

级别：轻微

源文：Social media can make users jealous of others whose lives appear more successful or exciting.

现译：ソーシャルメディアによって、より成功し、刺激的に暮らしているように見える相手に、ユーザーが嫉妬することがあります。

建议（完整字段）：ソーシャルメディアによって、より成功していたり、より刺激的な生活を送っていたりするように見える相手に、ユーザーが嫉妬することがあります。

依据：英文successful or exciting是二选一关系，生活显得更成功或更精彩都可成为嫉妒对象。现译把成功与刺激并列到同一人身上，没有保留只符合其中一项的情况。可能嫉妒与表面观感仍准确，二审确认选择关系发生轻微变化，候选恢复两种情况的并列选择。

词库位置：`data/ja/entries/28.json`，`jealous`，`ex.1`

### jog / 第2个词义（senses.1）

级别：轻微

源文：A period of slow, steady running.

现译：短いジョギング

建议（完整字段）：ジョギング；ゆっくり一定のペースで走ること

依据：英文定义是一段以缓慢、稳定速度跑步的活动，没有说活动必须很短。现译「短いジョギング」额外把时间或距离限定为短，整条释义与例句也无此依据。「ジョギング」本身已传达慢速运动跑，因此二审确认「短い」是轻微的意义限制增译，候选删除该限制。

词库位置：`data/ja/entries/15.json`，`jog`，`senses.1`

### ladder / 第2条例句（ex.1）

级别：轻微

源文：Access to professional training can help young employees move up the career ladder more quickly.

现译：専門職の研修を受けられると、若い従業員は職業上の階段をより早く上る助けとなる。

建议（完整字段）：専門的な職業訓練を受ける機会は、若い従業員がより早く昇進する助けとなる。

依据：英文中培训机会是提供帮助的主体，年轻雇员是受益者。现译以「若い従業員は」作「助けとなる」的主题，无法自然衔接谁帮助谁以及谁晋升的格关系，前面的条件从句也不能解除问题。培训有助晋升的大意仍可理解，二审确认轻微构句错误，候选恢复培训机会作主体。

词库位置：`data/ja/entries/18.json`，`ladder`，`ex.1`

### large / 第2条例句（ex.1）

级别：轻微

源文：Large cities often offer better employment opportunities, although high housing costs can reduce residents' quality of life.

现译：大都市には良い就業機会が多い一方、高い住宅費は住民の生活の質を下げる可能性があります。

建议（完整字段）：大都市はより良い就業機会を提供することが多い一方、高い住宅費は住民の生活の質を下げる可能性があります。

依据：英文说大城市往往提供更好的就业机会，分别包含提供频率与质量比较。现译「良い就業機会が多い」改成好机会数量多，未保留better和often的原有关系。即使机会多少可能影响就业环境，也不能据此替换原文命题；城市与住房成本的对比仍在，二审确认轻微意义变化。

词库位置：`data/ja/entries/2.json`，`large`，`ex.1`

### latest / 第1条例句（ex.0）

级别：轻微

源文：Have you heard the latest news about our neighbour?

现译：近所の人についての最新の知らせを聞いた。

建议（完整字段）：近所の人についての最新の知らせを聞きましたか。

依据：英文是独立问句，询问对方是否听说邻居的最新消息。现译没有疑问助词、问号或支撑提问的对话语境，通常读作已经听说的过去陈述。口语靠升调能提问，仍不足以证明书面学习例句保留了功能。消息内容准确，二审确认轻微句式错误，候选恢复问句。

词库位置：`data/ja/entries/8.json`，`latest`，`ex.0`

### lean / 第2条例句（ex.1）

级别：轻微

源文：Lean production methods can help manufacturers reduce waste while maintaining the quality of their products.

现译：無駄を省いた生産方式は、製造業者が製品の品質を保ちながら廃棄物を減らすのに役立ちます。

建议（完整字段）：無駄を省いた生産方式は、製造業者が製品の品質を保ちながら、生産上の無駄を減らすのに役立ちます。

依据：精益生产中的waste除物理废弃物，也包括等待、过度生产、不必要搬运等不产生价值的浪费。同条效率释义与专业背景支持这一较广含义，不能只按垃圾理解。现译「廃棄物」收窄对象，因此二审确认轻微术语范围遗漏，候选改为生产上的无效耗费。

词库位置：`data/ja/entries/44.json`，`lean`，`ex.1`

参考：[Lean Enterprise Instituteはwasteを待ち・過剰生産・不要な運搬・動作等まで含む非付加価値の活動として説明する。](https://www.lean.org/lexicon-terms/seven-wastes/)

### link / 第1条例句（ex.0）

级别：轻微

源文：The new bridge provides a link between the villages.

现译：新しい橋が二つの村を結んでいる。

建议（完整字段）：新しい橋が村々を結んでいる。

依据：英文只说这些村庄，没有把数量确定为两个。桥有两端这一常见图像不等于只涉及两个村庄，between也能用于三者以上；整条没有补充村数。现译「二つの村」增加具体数量并收窄范围，因此二审确认轻微增译，候选用一般复数的村庄表达。

词库位置：`data/ja/entries/22.json`，`link`，`ex.0`

### low / 第2条例句（ex.1）

级别：轻微

源文：Low wages can prevent essential workers from finding affordable housing close to their places of employment.

现译：賃金が低いと、不可欠なサービスを担う労働者が、職場の近くに手頃な価格の住まいを見つけるのが難しくなることがあります。

建议（完整字段）：賃金が低いと、不可欠なサービスを担う労働者が、職場の近くに手頃な価格の住まいを見つけられなくなることがあります。

依据：原文can prevent保留可能性，但这种可能结果是找不到可负担住房。现译「見つけるのが難しくなることがあります」则只说可能更难找到，弱化为困难增加。二审确认差异在结果谓语的强度，不是机械地要求逐字翻译can；政策大意仍在，因此记为轻微错误。

词库位置：`data/ja/entries/1.json`，`low`，`ex.1`

参考：[preventの基幹義は発生や行動を止めること。難化だけとは異なる。](https://dictionary.cambridge.org/dictionary/english/prevent)

### mature / 第2条例句（ex.1）

级别：轻微

源文：Living independently can help young adults mature as they learn to manage money and resolve everyday problems.

现译：一人で暮らすことで、若者はお金の管理や日常の問題の解決を学びながら、成熟していくことができます。

建议（完整字段）：自立して暮らすことで、若者はお金の管理や日常の問題の解決を学びながら、成熟していくことができます。

依据：Living independently指不依赖他人而自主生活，并不要求没有同住者。全文的金钱管理与处理日常问题也强调自理能力，未规定居住人数。现译「一人で暮らす」收窄为独居，排除同住但自主的情形。二审确认轻微范围变化，候选改为自立生活。

词库位置：`data/ja/entries/52.json`，`mature`，`ex.1`

### mayor / 第1条例句（ex.0）

级别：轻微

源文：The mayor opened our new swimming pool yesterday.

现译：昨日、市長が私たちの新しいプールの開設を祝いました。

建议（完整字段）：昨日、市長が私たちの新しいプールの開設式を行いました。

依据：opened说明市长承担正式启用新泳池的角色，辅助中文也指主持启用仪式。现译只说「開設を祝いました」，单纯表达祝贺也可符合，漏掉官方开启设施的角色。昨日、市长和新泳池等内容准确，二审确认轻微角色意义遗漏，候选改为举行开设仪式。

词库位置：`data/ja/entries/31.json`，`mayor`，`ex.0`

### murderer / 第1个搭配（col.0）

级别：轻微

源文：convicted murderer

现译：convicted murderer｜有罪が確定した殺人犯

建议（完整字段）：convicted murderer｜有罪判決を受けた殺人犯

依据：搭配convicted murderer表示被判有罪的杀人犯，不直接表示上诉等程序结束、判决最终确定。现译「有罪が確定した」额外加入终局性；政府上诉资料也说明定罪后仍可争议并撤销。二审确认轻微术语限制增译，候选保留有罪判决而不追加确定义。

词库位置：`data/ja/entries/32.json`，`murderer`，`col.0`

参考：[convictionを受けた後でも有罪判決への上訴と取消しが可能であるという政府の手続案内。](https://www.gov.uk/appeal-against-crown-court-verdict/appeal-a-crown-court-decision)

### murderer / 第2条例句（ex.1）

级别：轻微

源文：Documentaries about convicted murderers should avoid sensationalism and consider the feelings of victims' families.

现译：有罪が確定した殺人犯についての記録映画は、扇情的な描写を避け、被害者の家族の気持ちに配慮すべきです。

建议（完整字段）：有罪判決を受けた殺人犯についての記録映画は、扇情的な描写を避け、被害者の家族の気持ちに配慮すべきです。

依据：convicted指已被判有罪，没有说明判决已终局确定；现译「有罪が確定した」多加了程序上的最终性，缩窄纪录片所述对象。二审参考有罪判决后仍可上诉的程序说明，确认这是轻微术语增译。避免煽情及顾及家属感受的要求保持准确，候选仅删除确定性限定。

词库位置：`data/ja/entries/32.json`，`murderer`，`ex.1`

参考：[有罪判決を受けた後の上訴と判決取消しを明示する英国政府資料。](https://www.gov.uk/appeal-against-crown-court-verdict/appeal-a-crown-court-decision)

### over / 第2条例句（ex.1）

级别：轻微

源文：Over half of the residents surveyed supported plans to create more green spaces in their neighbourhood.

现译：調査に答えた住民の半数以上が、自分たちの地区に緑地を増やす計画を支持した。

建议（完整字段）：調査に答えた住民の半数を超える人が、自分たちの地区に緑地を増やす計画を支持した。

依据：Over half严格表示超过一半；日语「半数以上」把恰好一半也算在内。该词条其他释义和搭配同样强调超过，因此这是目标词数量边界的变化，并非仅有文风差异。居民支持本地区增设绿地的其他关系均准确，二审确认轻微数量错误，候选明确超过半数。

词库位置：`data/ja/entries/7.json`，`over`，`ex.1`

### partly / 第1个搭配（col.0）

级别：轻微

源文：partly because

现译：partly because｜一部の理由はなので

建议（完整字段）：partly because｜一つには〜だから；部分的には〜という理由で

依据：现译「一部の理由はなので」把「理由は」与「なので」直接相连，没有理由内容或可填位置，无法对应because后承接原因从句的结构。二审确认这超出单纯文风偏好，须改为可用的接续表达。候选用「一つには〜だから」等构式，保留部分原因的含义。

词库位置：`data/ja/entries/22.json`，`partly`，`col.0`

### partly / 第2个搭配（col.1）

级别：轻微

源文：partly due to

现译：partly due to｜部分的にはが原因で

建议（完整字段）：partly due to｜部分的には〜が原因で

依据：整条例句能自然表达部分原因，但搭配栏「部分的にはが原因で」把「には」「が」直接相连，内部应放原因名词的位置消失。它不是只在句尾开放的简略模板，学习者无法照用。二审确认轻微内部构式缺失；候选保留原含义，仅明确标出应填原因的位置。

词库位置：`data/ja/entries/22.json`，`partly`，`col.1`

### persuading / 第3个搭配（col.2）

级别：轻微

源文：persuading someone that

现译：persuading someone that｜人にと信じさせること

建议（完整字段）：persuading someone that｜人に〜と信じさせること

依据：原搭配that后需要接使对方相信的内容，现译「人にと信じさせること」却在表示人的「に」后直接接引用助词「と」，漏掉内部内容从句及其空位标记。二审确认轻微语法缺口，候选明确显示that从句应填入的位置，继续表达使某人相信某事。

词库位置：`data/ja/entries/22.json`，`persuading`，`col.2`

### probable / 第1条例句（ex.0）

级别：轻微

源文：The mechanic explained the probable cause of the noise.

现译：修理工は、その騒音の原因として最も可能性の高いものを説明しました。

建议（完整字段）：修理工は、その騒音の原因と考えられるものを説明しました。

依据：英文probable只表示这个原因有可能成立，没有比较多个候选原因的概率高低。现译加入「最も」，额外断言它是最可能的原因；完整语境也没有提供这种排序。即使辅助中文有「最可能」，仍须以英文为准。二审确认是局部最高级增译，严重度为轻微。

词库位置：`data/ja/entries/50.json`，`probable`，`ex.0`

### proportion / 第2条例句（ex.1）

级别：轻微

源文：The proportion of residents using public transport increased after the city introduced cheaper monthly passes.

现译：市が安い定期券を導入した後、公共交通機関を使う住民の割合が増えました。

建议（完整字段）：市が、より安い1か月定期券を導入した後、公共交通機関を使う住民の割合が増えました。

依据：monthly passes明确为一个月期限的通票或定期券；「定期券」本身也可涵盖三个月等其他期限。虽然交通票券的一般名称对应，但该例句具体交代了时间单位，现译未保留。二审确认轻微期限遗漏，候选补出一个月，并保留推出较便宜票券后公交使用比例上升的关系。

词库位置：`data/ja/entries/38.json`，`proportion`，`ex.1`

### recognize / 第3个搭配（col.2）

级别：轻微

源文：recognize someone as

现译：recognize someone as｜人をとして認める

建议（完整字段）：recognize someone as｜人を〜として認める

依据：现译「人をとして認める」在宾语后的「を」与「として」之间，漏掉作为何种身份被认可的成分，也没有空位符号。英文as后本就应接角色、地位等内容，学习搭配可以开放此处，但日语须让填入位置明确。二审确认轻微构句缺失，候选加上空位标记。

词库位置：`data/ja/entries/21.json`，`recognize`，`col.2`

### register / 第2条例句（ex.1）

级别：轻微

源文：Residents should be able to register for local healthcare services online, reducing unnecessary travel and administrative delays.

现译：住民が地元の医療サービスへオンラインで登録できれば、不要な移動や事務手続きの遅れを減らせる。

建议（完整字段）：住民は地元の医療サービスにオンラインで登録できるようにすべきであり、それによって不要な移動や事務手続きの遅れを減らせる。

依据：should be able表示居民应当具备网上登记的能力、机会或这种预期状态；现译「登録できれば」仅说明如果能登记会有什么好处，没有保留应当如此的要求或期待。登记对象、线上方式及减少出行和延误均准确，二审确认情态轻微遗漏，候选恢复这一应有状态。

词库位置：`data/ja/entries/19.json`，`register`，`ex.1`

### reply / 第1条例句（ex.0）

级别：轻微

源文：Please reply before Friday so I can book dinner.

现译：夕食の予約ができるよう、金曜日までに返事をください。

建议（完整字段）：夕食の予約ができるよう、金曜日になる前に返事をください。

依据：before Friday要求在周五到来之前回复；日语「金曜日までに」通常把周五当天也纳入期限。整句没有补充当天几点等信息，因而译文实质上延长了为预订晚餐而回复的截止时间。请求的礼貌与目的均准确，二审确认是轻微的时间边界错误。

词库位置：`data/ja/entries/14.json`，`reply`，`ex.0`

### reproach / 第2条例句（ex.1）

级别：轻微

源文：Teachers should offer constructive guidance rather than reproach students for mistakes made during the learning process.

现译：教師は、学ぶ過程での間違いを生徒に責めるのではなく、建設的な指導をするべきです。

建议（完整字段）：教師は、学ぶ過程での間違いを理由に生徒を責めるのではなく、建設的な指導をするべきです。

依据：英文责备的对象是学生，原因是学习中犯的错误。日语应写责备学生，或责备学生的错误；现译「間違いを生徒に責める」未正确连接这两种角色。即使补读为朝向学生，也不适合作为标准学习例句。二审确认轻微格关系错误，候选把生徒改为责备的宾语。

词库位置：`data/ja/entries/62.json`，`reproach`，`ex.1`

### reverse / 学习提示（tip）

级别：轻微

源文：倒车用reverse；撤销决定可说reverse a decision。

现译：倒車にはreverseを使います。決定を覆すにはreverse a decisionと言えます。

建议（完整字段）：車を後退させることにはreverseを使います。決定を覆すにはreverse a decisionと言えます。

依据：中文「倒车」指使车辆后退，现代一般日语应使用後退或バック。现译「倒車」只作汉字替换，未转为能清楚说明动作的常用日语，也与同条例句的後退用语不一致。二审确认轻微未译及术语问题，候选把车辆后退明确写出，决定撤销的后半说明仍保留。

词库位置：`data/ja/entries/43.json`，`reverse`，`tip`

参考：[車両の操作を後退（バック）とするJAFの日本語用例。](https://jaf.or.jp/common/safety-drive/car-learning/user-test/highway)

### sack / 第2个词义（senses.1）

级别：轻微

源文：To dismiss someone from their job.

现译：仕事を解雇する

建议（完整字段）：人を解雇する

依据：英文dismiss someone from their job中，被解雇的对象是人，工作是其被解除的职位。现译「仕事を解雇する」却把工作当成解雇对象，混淆人的角色与职位的角色，也不符合同条解雇劳动者的例句。二审确认轻微的格及对象错误，候选明确用人作宾语。

词库位置：`data/ja/entries/33.json`，`sack`，`senses.1`

### saline / 第2条例句（ex.1）

级别：轻微

源文：Rising sea levels can make coastal groundwater more saline, reducing its suitability for drinking and irrigation.

现译：海面上昇によって沿岸の地下水の塩分が増え、飲用や灌漑に適さなくなることがあります。

建议（完整字段）：海面上昇によって沿岸の地下水の塩分が増し、飲用や灌漑への適性が低下することがあります。

依据：原文说地下水盐分增加会降低饮用和灌溉适用性，程度下降后仍可能可用。现译「適さなくなる」则推进到不再适用，强化结果。即使保留can的可能性，也不能消除程度下降与完全不合用途的差别。二审确认轻微意义加强，候选恢复适性降低。

词库位置：`data/ja/entries/66.json`，`saline`，`ex.1`

### simulate / 第1条例句（ex.0）

级别：轻微

源文：This driving game simulates icy roads surprisingly well.

现译：この運転ゲームは、驚くほどよく凍った道路を再現しています。

建议（完整字段）：この運転ゲームは、凍った道路を驚くほどうまく再現しています。

依据：英文surprisingly well修饰模拟得好，现译「驚くほどよく凍った道路」通常把程度接到结冰上，变成冻得惊人的道路。虽然理论上可将よく远接再现，普通语序首先传达的意思仍改变。二审确认轻微修饰错误，候选调整词序，明确惊人的是再现质量。

词库位置：`data/ja/entries/57.json`，`simulate`，`ex.0`

### skirmish / 第1条例句（ex.0）

级别：轻微

源文：Their skirmish over the remote ended with a compromise.

现译：リモコンをめぐる二人の小競り合いは、妥協で終わりました。

建议（完整字段）：リモコンをめぐる彼らの小競り合いは、妥協で終わりました。

依据：their表示复数参与者，没有限定两个人；围绕遥控器的争执也可能有三人以上，完整语境没有二人的依据。现译「二人」额外指定人数并缩窄对象。二审确认轻微数量增译，候选使用一般复数彼ら，保留小争执最终妥协的事件关系。

词库位置：`data/ja/entries/71.json`，`skirmish`，`ex.0`

### sky / 第2条例句（ex.1）

级别：轻微

源文：Light pollution prevents many urban residents from seeing stars clearly in the night sky.

现译：光害により、多くの都市の住民は夜空の星をはっきりと見ることができません。

建议（完整字段）：光害により、都市に住む多くの人々は夜空の星をはっきりと見ることができません。

依据：英文many修饰城市居民的人数；日译「多くの都市の住民」通常把数量转移到城市，变成许多城市的居民。原文没有说明涉及多少城市，整条语境也不能补出。光害与无法清楚看星星的关系仍保留，因此二审确认是轻微的数量修饰错误，候选把多明确放回居民。

词库位置：`data/ja/entries/2.json`，`sky`，`ex.1`

### slavery / 第2个搭配（col.1）

级别：轻微

源文：modern slavery

现译：modern slavery｜現代の奴隷労働

建议（完整字段）：modern slavery｜現代奴隷制；現代の奴隷状態

依据：modern slavery是现代奴役状态的总称，国际用法包含强迫劳动，也包括强迫婚姻等。现译「現代の奴隷労働」只涵盖劳动，缩窄了概念；其他例句提到forced labour也不能把这个独立搭配限定为劳动。二审确认轻微术语范围遗漏，候选恢复现代奴隶制或奴役状态。

词库位置：`data/ja/entries/51.json`，`slavery`，`col.1`

参考：[ILOはmodern slaveryを強制労働・強制結婚等の概念をまとめる語として説明する。](https://www.ilo.org/publications/global-estimates-modern-slavery-forced-labour-and-forced-marriage)

### stack / 第2条例句（ex.1）

级别：轻微

源文：Libraries increasingly store stacks of older journals off site to create more space for collaborative learning.

现译：図書館は、協働学習の空間を増やすため、積み重なった古い雑誌を別の場所に保管するようになっています。

建议（完整字段）：図書館は、協働学習の空間を増やすため、積み重なった古い雑誌を館外に保管するようになっています。

依据：off site明确在当前图书馆设施或场地之外储存，现译「別の場所」也可包括馆内另一个房间。腾出学习空间的目的不足以证明保管地一定在馆外。整体空间利用的意义虽保持，二审仍确认明示的内外位置限定轻微遗漏，候选用馆外恢复该信息。

词库位置：`data/ja/entries/48.json`，`stack`，`ex.1`

### stall / 第3个搭配（col.2）

级别：轻微

源文：stall an engine

现译：stall an engine｜エンジンを失速させる

建议（完整字段）：stall an engine｜エンストさせる

依据：本条stall an engine指使发动机意外停止，目标语应表达エンスト。现译「失速」在相关技术用语中与发动机运行停止不同，也不能在本搭配当作一般势头下降处理。二审结合词条释义和机械学会用语确认轻微术语错误，候选改用发动机熄火的日语表达。

词库位置：`data/ja/entries/42.json`，`stall`，`col.2`

参考：[日本機械学会はエンジンストールを運転中のエンジン停止、別名エンストと定義する。](https://www.jsme.or.jp/jsme-medwiki/doku.php?id=11%3A1001316)

参考：[失速の流体・翼の現象を別の技術語として説明する。](https://www.jsme.or.jp/jsme-medwiki/doku.php?id=09%3A1005238)

### student / 学习提示（tip）

级别：轻微

源文：student不限于大学生；pupil主要指中小学生。

现译：studentは大学生に限りません。pupilは主に小中学校の児童や生徒を指します。

建议（完整字段）：studentは大学生に限りません。pupilは主に小学校・中学校・高校の児童・生徒を指します。

依据：这条提示只有中文源文，其中「中小学生」包括小学、初中和高中，而日语「小中学校」只指小学与初中。即使保留「主に」这一限定，列举的主要学段仍少了高中；student本身范围较宽也不能补足pupil的说明。因此二审确认学段范围发生轻微变化，候选补出高中。

词库位置：`scripts/atlas/ja-reviewed-1.json`，`student`，`tip`

参考：[教育部の中小学生の対象は小学・初中・普通高中を含む。原語の学段範囲の補助確認。](https://www.moe.gov.cn/srcsite/A06/jcys_jyzb/202502/t20250207_1177647.html)

### submit / 第3个搭配（col.2）

级别：轻微

源文：submit something to

现译：submit something to｜物をに提出する

建议（完整字段）：submit something to｜物を〜に提出する

依据：「物をに提出する」把提出物后的「を」与表示提交对象的「に」直接接在一起，既无接收方也无空位标记。即使这是开放式搭配，内部的两个格也不能这样无说明相连。二审确认轻微构式缺口，候选用「〜」清楚标出to后对应的提交对象。

词库位置：`data/ja/entries/21.json`，`submit`，`col.2`

### surround / 第2个搭配（col.1）

级别：轻微

源文：surround yourself with

现译：surround yourself with｜自分の周囲をで満たす

建议（完整字段）：surround yourself with｜自分の周囲を〜で満たす

依据：这条搭配需要在with后的人或物对应位置填入日语成分。现译「自分の周囲をで満たす」把「を」「で」直接相连，既无补语也无空位标记，无法作为完整的日语构式使用。这不同于辞典保留开头助词的惯常略写。二审确认轻微构句缺口，候选明确标出可填入内容的位置。

词库位置：`data/ja/entries/21.json`，`surround`，`col.1`

### tactics / 第1条例句（ex.0）

级别：轻微

源文：Our coach changed tactics halfway through the football match.

现译：コーチは、サッカーの試合の途中で戦術を変えました。

建议（完整字段）：コーチは、サッカーの試合が半分ほど進んだところで戦術を変えました。

依据：halfway through指定比赛进行到约一半的时点；现译「途中で」只表示比赛过程中，也能涵盖刚开始或快结束。战术变化的具体时间限定因此遗漏，不能只靠一般的中途表达。二审确认轻微时间意义缺失，候选把变化发生在比赛约半程明确写出。

词库位置：`data/ja/entries/37.json`，`tactics`，`ex.0`

### though / 第1个搭配（col.0）

级别：轻微

源文：even though

现译：even though｜たとえでも；にもかかわらず

建议（完整字段）：even though｜〜にもかかわらず；〜だけれども

依据：现译后半「にもかかわらず」保留让步含义，但前半「たとえでも」没有从句或空位标记，不能独立成为可用的日语结构。原文主要对已知事实作让步，学习搭配需给出成立的让步构式。二审确认轻微语法问题，候选采用完整可填内容的让步表达。

词库位置：`data/ja/entries/21.json`，`though`，`col.0`

### though / 第2个搭配（col.1）

级别：轻微

源文：as though

现译：as though｜まるでのように

建议（完整字段）：as though｜まるで〜のように

依据：as though引出比较或仿佛如此的内容。现译「まるでのように」在「まるで」与「のように」之间缺少比较对象或空位标记，按显示形式无法形成日语构式。二审确认轻微内部成分缺失，候选明确标出填入比较内容的位置，而不改变原搭配的含义。

词库位置：`data/ja/entries/21.json`，`though`，`col.1`

### watermelon / 第2条例句（ex.1）

级别：轻微

源文：Growing watermelons in dry regions requires careful irrigation management to protect limited local water supplies.

现译：乾燥地域でスイカを育てるには、限られた地域の水資源を守るため、慎重な灌漑管理が必要だ。

建议（完整字段）：乾燥地域でスイカを育てるには、地域の限られた水資源を守るため、慎重な灌漑管理が必要だ。

依据：英文limited修饰当地水资源的数量，说明资源有限。现译「限られた地域の水資源」通常先组成有限的地区，转成只保护特定区域水资源的地理限定。虽能从干旱背景推知缺水，仍未正确表达修饰对象。二审确认是轻微的修饰范围错误，候选把有限明确放回水资源。

词库位置：`data/ja/entries/17.json`，`watermelon`，`ex.1`

## 仍存疑

### authorize / 第2条例句（ex.1）

级别：重大（若问题成立时的潜在影响）

源文：Local authorities may authorize new housing developments only after assessing their likely effects on traffic and public services.

现译：地方当局が新たな住宅開発を許可できるのは、交通と公共サービスに及ぼしそうな影響を評価してからに限られる場合があります。

建议（完整字段）：地方当局は、交通と公共サービスへの想定される影響を評価した後に限り、新たな住宅開発を許可できます。

依据：若may表示正式权限，only after使评估成为必备前提，现译「場合があります」可能把限制弱化为部分情况，差异可达重大程度。但may也能表示可能性，单句缺少法规或程序语境，不能只按权限义确认为错。二审保留重大级条件作用域存疑，未作错误确认。

词库位置：`data/ja/entries/56.json`，`authorize`，`ex.1`

修改注意：候选采用许可义；使用前须先确认may意图，不能自动批准改译。

参考：[mayにはformal permissionとpossibilityの両用法があり、文脈で区別する必要がある。](https://dictionary.cambridge.org/us/grammar/british-grammar/may)

### adopt / 第2条例句（ex.1）

级别：待定（若问题成立时的潜在影响）

源文：Governments should adopt long-term strategies that improve public transport rather than simply building more roads.

现译：政府は、道路を増やすだけでなく、公共交通機関を改善する長期戦略を採用すべきです。

建议（完整字段）：政府は、単に道路を増やすのではなく、公共交通を改善する長期的な戦略を採用すべきです。

依据：英文把改善公交的长期策略与单纯增建道路作对比；现译「だけでなく」偏向在增路之外再追加策略，可能弱化取舍关系。但simply只针对仅做增路，原文也未排除综合策略包含道路建设，现译亦可理解为不止步于单一办法。因此保留存疑，不能断言它必然额外赞同增路。

词库位置：`data/ja/entries/41.json`，`adopt`，`ex.1`

修改注意：候选译文用于明确原文对比，宜结合政策意图确认后采用。

### assembly / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：The whole school gathered in the hall for assembly.

现译：全校生徒が、集会のためにホールに集まりました。

建议（完整字段）：学校のみんなが、集会のためにホールに集まりました。

依据：whole school既可指包括教职员的全校人员，也能借代全体学生；辅助中文写师生，支持前者。现译全校生徒在集会场景中也是自然概括，并未断言教职员不在。二审无法确定是实质缩窄全体范围，还是可接受的借代，保留轻微存疑，候选用学校所有人避免限缩。

词库位置：`data/ja/entries/42.json`，`assembly`，`ex.0`

### bounce / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：The ball bounced over the fence into our neighbour's garden.

现译：ボールは柵を跳び越えて、隣人の庭に入りました。

建议（完整字段）：ボールは弾んで柵を越え、隣人の庭に入りました。

依据：bounce包含碰到物体后弹起的动作，现译「柵を跳び越えて」只明确越过围栏，未必表达反弹。但主语是球，读者也能从越过动作自然恢复弹跳，同条释义亦说明跳动。二审无法确认为动作误译，还是合理的一般化表达，保留轻微存疑；候选直接写出弾んで。

词库位置：`data/ja/entries/28.json`，`bounce`，`ex.0`

### comedy / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：We watched a comedy and laughed all evening.

现译：私たちは喜劇を見て、一晩中笑った。

建议（完整字段）：私たちは喜劇を見て、その晩はずっと笑っていた。

依据：all evening说明当晚娱乐时段一直在笑，没有指定直到黎明。现译「一晩中」可能让人理解为整夜持续，从而拉长时间，但日常叙述里也可宽松表示那晚一直如此。原文没有时刻或次日情境，二审未硬判时长变化，只保留轻微存疑，候选采用较中性的当晚表述。

词库位置：`data/ja/entries/10.json`，`comedy`，`ex.0`

### county / 学习提示（tip）

级别：轻微（若问题成立时的潜在影响）

源文：英国的county通常译为“郡”，美国的译为“县”。

现译：イギリスのcountyは通常「郡」、アメリカのcountyも日本語では一般に「郡」と訳します。

建议（完整字段）：中国語では、イギリスのcountyは通常「郡」、アメリカのcountyは「县」と訳します。日本語では、いずれも一般に「郡」と訳します。

依据：中文原文解释英国county通常译郡、美国译县；现译改为说明日语中两者都常用郡，替换了元语言信息。美国county日译郡本身有官方用例，不属错误知识。究竟应按日语读者作本地化，还是保留原文的中文译名区别，取决于编辑方针，二审因此保留轻微存疑。

词库位置：`data/ja/entries/40.json`，`county`，`tip`

修改注意：候选同时保留中文译名区别与日语常用译名，供编辑方针确认。

参考：[外務省の米国紹介はロサンゼルスCountyをロサンゼルス郡と表す。日本語の郡自体は妥当であることの確認。](https://www.mofa.go.jp/mofaj/kids/kuni/usa_la_2025.html)

### craft / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Traditional craft workshops can preserve cultural knowledge while creating employment opportunities in rural communities.

现译：伝統工芸の教室は、農村の地域社会で雇用機会を生みながら、文化的な知識を保存できます。

建议（完整字段）：伝統工芸の工房は、農村の地域社会で雇用機会を生みながら、文化的な知識を保存できます。

依据：workshop既可指制作工坊，也可指传授技能的讲习或教室。农村创造就业及辅助中文作坊支持工坊，但保存文化知识的教室也能产生就业，另一例句又涉及教授技能。二审无法唯一确定英文意图，故将教室与工坊的对象差别保留为轻微存疑，候选取工坊义供确认。

词库位置：`data/ja/entries/45.json`，`craft`，`ex.1`

### difficult / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Many graduates find it difficult to secure stable employment without previous experience in their chosen field.

现译：多くの新卒者は、希望する分野での経験がないと安定した職を得るのが難しいと感じている。

建议（完整字段）：多くの卒業者は、希望する分野での経験がないと安定した職を得るのが難しいと感じている。

依据：缺少经验而谋求稳定工作的毕业生，容易让人想到新近毕业者，因此「新卒者」在场景上自然。但graduates并不明确限定刚毕业，也可能包括毕业已久、尚无该领域经验的人。原文没有毕业时间，二审无法确认是合理语用补足还是群体缩窄，故保留轻微存疑。

词库位置：`data/ja/entries/6.json`，`difficult`，`ex.1`

### disappointed / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Graduates may feel disappointed if their first jobs offer few opportunities to apply the skills they have learned.

现译：最初の仕事で学んだ技能を生かす機会がほとんどないと、卒業生は失望するかもしれません。

建议（完整字段）：卒業生は、学んだ技能を生かす機会が最初の仕事にほとんどないと、失望するかもしれません。

依据：现译「最初の仕事で学んだ技能」容易把最初的工作读成学习技能的地点，而英文说的是第一份工作是否提供运用既有技能的机会，并未交代技能在哪学会。不过「で」也可宽泛修饰后面的运用机会，原意并非无法恢复。二审将这种修饰歧义保留为轻微存疑，候选调序以澄清。

词库位置：`data/ja/entries/24.json`，`disappointed`，`ex.1`

### diving / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：We went diving and saw colourful fish near the reef.

现译：私たちは潜水に出かけ、サンゴ礁の近くで色鮮やかな魚を見た。

建议（完整字段）：私たちは潜水に出かけ、礁の近くで色鮮やかな魚を見た。

依据：reef也可指岩礁等，并非只能是珊瑚礁，现译明确加上了珊瑚。潜水与色彩鲜艳的鱼使珊瑚礁成为自然场景，但完整语境没有指定礁的成因或材质。二审无法确定是合理场景具体化，还是不必要地缩窄对象，保留轻微术语存疑，候选采用较一般的礁。

词库位置：`data/ja/entries/21.json`，`diving`，`ex.0`

### embroidery / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：I practise embroidery by stitching flowers onto plain cushions.

现译：私は無地のクッションに花を縫い付けて、刺繍を練習しています。

建议（完整字段）：私は無地のクッションに花の模様を刺して、刺繍を練習しています。

依据：刺绣语境自然支持用线在靠垫上刺出花纹，现译「花を縫い付けて」也可能读作把现成花形零件缝上。但stitch onto本身也可表达缝附，整句练刺绣的目的又能帮助理解为缝花样。二审无法确定是技法误解还是自然表达，保留轻微存疑，候选明确花的图案。

词库位置：`data/ja/entries/62.json`，`embroidery`，`ex.0`

### expect / 第3个搭配（col.2）

级别：轻微（若问题成立时的潜在影响）

源文：fully expect

现译：fully expect｜十分に予想する

建议（完整字段）：fully expect｜〜すると強く見込む；〜すると確信している

依据：fully expect通常表示对事情会发生有很强的预期或信心；「十分に予想する」也可能读成预测工作做得充分，转换了程度的尺度。但日语这一组合亦可自然表达充分预料、强烈预计，单独搭配没有具体宾语可进一步判别。二审保留轻微术语存疑，未确认信心程度已经丢失。

词库位置：`data/ja/entries/18.json`，`expect`，`col.2`

### expert / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：We asked an expert to examine the old painting.

现译：私たちは、古い絵を専門家に調べてもらいました。

建议（完整字段）：私たちは、古い絵を調べるよう専門家に依頼しました。

依据：asked明确说请求专家检查，现译「調べてもらいました」通常还表示检查实际完成。依照请求已被履行的普通叙述补足，在语用上也自然，但只提出请求与已经检查仍属不同事件，全文没有确认材料。二审未认定重大结果捏造，而把请求与履行的边界保留为轻微存疑。

词库位置：`data/ja/entries/28.json`，`expert`，`ex.0`

### familiar / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Students who are familiar with digital tools may adapt more easily to online learning environments.

现译：デジタル機器によく慣れた学生は、オンライン学習環境へより容易に適応できるかもしれない。

建议（完整字段）：デジタルツールによく慣れた学生は、オンライン学習環境へより容易に適応できるかもしれない。

依据：digital tools可包括软件及在线学习工具；「デジタル機器」通常偏向设备和硬件，可能收窄范围。不过在在线学习语境中，设备的使用也能自然包含软件操作，原文未指定工具类别。二审无法确认范围缩小已造成实质误译，保留轻微存疑，候选改用较广的ツール。

词库位置：`data/ja/entries/19.json`，`familiar`，`ex.1`

### farmer / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Small farmers need reliable access to water and affordable technology to maintain production during dry periods.

现译：小規模農家が干ばつの時期にも生産を維持するには、安定した水源と手頃な費用の技術が必要です。

建议（完整字段）：小規模農家が乾燥する時期にも生産を維持するには、安定した水源と手頃な費用の技術が必要です。

依据：农业供水与维持生产的语境支持把dry periods理解为干旱时期，但它也可指正常干季或短暂少雨，并未明确异常、长期缺水。现译「干ばつ」可能把条件收窄为旱灾；其他内容也没有补足灾害或时长限定。二审因此保留轻微存疑，不确认必然误译。

词库位置：`data/ja/entries/2.json`，`farmer`，`ex.1`

### fresh / 第1个词义（senses.0）

级别：轻微（若问题成立时的潜在影响）

源文：Recently produced or picked, and not preserved or stale.

现译：新鮮な；保存・加工されておらず古くなっていない

建议（完整字段）：新鮮な；作られた、または収穫されたばかりで、保存処理されておらず古くなっていない

依据：preserved指对食品进行保存处理。若把现译「保存・加工」读成任何加工都不能有，就会排除刚制作、切分或烹调的食品，范围比原文窄；但该组合也能理解为保存加工这一整体处理。新鲜的核心译义和果蔬语境准确，二审因此保留术语范围的轻微存疑。

词库位置：`data/ja/entries/12.json`，`fresh`，`senses.0`

### from / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Students from rural communities may face additional barriers when applying to universities in major cities.

现译：農村の地域社会出身の学生は、大都市の大学に出願する際に、さらに大きな障壁に直面することがあります。

建议（完整字段）：農村の地域社会出身の学生は、大都市の大学に出願する際に、追加の障壁に直面することがあります。

依据：additional说明农村学生在申请时还会遇到额外障碍，并不直接说每项障碍更大；现译「さらに大きな」明确转向程度增加。不过若把障碍当作累积负担，额外负担也可自然概括为更大的障碍。出身、申请情境和可能性均保留，二审将数量与程度的边界保留为轻微存疑。

词库位置：`scripts/atlas/ja-reviewed-0.json`，`from`，`ex.1`

### happen / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：What happened to the plant beside your window?

现译：あなたの窓辺の鉢植えは、どうなったのですか。

建议（完整字段）：あなたの窓辺の植物は、どうなったのですか。

依据：现译保留了询问窗边植物情况以及happen to的用法。窗边放盆栽在普通场景中合理，辅助中文也写了「盆」，但优先英文只说plant，并不排除地栽。容器限定可能超出自然消歧，不过不足以确认实质错误；二审保留轻微存疑，候选用一般的植物称呼。

词库位置：`data/ja/entries/2.json`，`happen`，`ex.0`

### high / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：High housing costs can prevent young adults from living independently, particularly in major urban centres.

现译：特に大都市の中心部では、高い住宅費によって、若い成人が自立して暮らせなくなる場合があります。

建议（完整字段）：特に大都市では、高い住宅費によって、若い成人が自立して暮らせなくなる場合があります。

依据：urban centres在住房成本的一般论述中可指主要城市或整个城市聚集区，现译「大都市の中心部」可能缩小为都心。公用统计也有较广的用法，但本句没有定义术语，中心地区的读法亦不能彻底排除。可能妨碍独立居住的关系已保留，二审将地理范围保留为轻微存疑。

词库位置：`data/ja/entries/4.json`，`high`，`ex.1`

参考：[urban centreを高密度の都市集積に使う公的用例。一般英文の語義を一意に決める証拠にはしない。](https://www.ons.gov.uk/aboutus/whatwedo/programmesandprojects/europeancitystatistics)

### impost / 第3个搭配（col.2）

级别：轻微（若问题成立时的潜在影响）

源文：impost block

现译：impost block｜アーチの起拱石

建议（完整字段）：impost block｜アーチの起点を支えるブロック（インポスト・ブロック）

依据：建筑资料把impost block界定为柱头与拱之间的支承石，并与其上方最低拱石springer区分；日本石桥资料中的起拱石更偏后者，现译因此有具体混淆风险。但柱头建筑与石桥的对象有别，资料不足以排除日语译名兼容的范围，二审保留轻微专业术语存疑，未确认为错。

词库位置：`data/ja/entries/72.json`，`impost`，`col.2`

修改注意：候选采用中性支承构件说明，不代表已批准写回正式数据。

参考：[美術建築専門機関AATのimpost blocksの柱頭とアーチ間に置く石という定義を確認。](https://www.getty.edu/vow/AATFullDisplay?find=&logic=AND&note=&page=1&subjectid=300001163)

参考：[大学の中世建築教材で柱頭頂部と上部建築部材の間の板という意味を照合。](https://sites.pitt.edu/~medart/menuglossary/impost.htm)

参考：[springerがimpostの直上に載る別部材であることを専門機関の分類定義で確認。](https://www.getty.edu/vow/AATFullDisplay?find=genre&logic=null&note=&subjectid=300265528)

参考：[国交省講習資料PDF6頁の部材名称表で、起拱石が最下端の輪石と説明されることを確認。](https://www.qsr.mlit.go.jp/rd_mainte/site_files/file/kousyuukai/01kouzoutokusei.pdf)

### integrate / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Schools should integrate digital tools into classroom activities while ensuring that all students have equal access.

现译：学校は、すべての生徒が平等に利用できるようにしながら、デジタル機器を授業の活動に取り入れるべきです。

建议（完整字段）：学校は、すべての生徒が平等に利用できるようにしながら、デジタルツールを授業の活動に取り入れるべきです。

依据：课堂的digital tools可能包括终端及应用软件，「デジタル機器」通常以硬件为中心，可能缩窄范围。不过把设备引入课堂的日语说法也能自然包括软件使用，本句未指定工具类型，所有学生平等利用与should要求均保留。二审依照familiar例同样标准，保留轻微范围存疑。

词库位置：`data/ja/entries/37.json`，`integrate`，`ex.1`

### keyboard / 第2条例句（ex.1）

级别：待定（若问题成立时的潜在影响）

源文：Students with limited mobility may benefit from an adapted keyboard that makes digital learning more accessible.

现译：移動に制約のある生徒には、デジタル学習をより利用しやすくする改良型のキーボードが役立つ場合がある。

建议（完整字段）：身体の動きに制約のある生徒には、それぞれの必要に合わせて調整され、デジタル学習をより利用しやすくするキーボードが役立つ場合があります。

依据：adapted强调按使用者条件作适配，「改良型」则也包括一般性能升级；limited mobility又可能涵盖身体动作限制，而「移動に制約」偏向位置移动。不过整句的使用者和学习可及性说明能帮助恢复原意，两处范围差异均不足以确认误译，合并为同一字段保留存疑。

词库位置：`data/ja/entries/10.json`，`keyboard`，`ex.1`

修改注意：候选译文明确身体动作范围及按需要调整的用途，供进一步确认。

参考：[adaptは対象や条件に合うように変更することを示し、一般的改善だけには限定されない。](https://assets.cambridge.org/97805215/31054/sample/9780521531054ws.pdf)

### kill / 学习提示（tip）

级别：轻微（若问题成立时的潜在影响）

源文：kill强调造成死亡；die表示自身死亡，不接宾语。

现译：kill は死を引き起こすことを強調する。die は自ら死ぬことを表し、目的語を取らない。

建议（完整字段）：kill は死を引き起こすことを強調する。die は主語自身が死ぬことを表し、目的語を取らない。

依据：中文「自身死亡」是在语法上对比死亡的主体，不表示主动选择死亡。日语「自ら」既可指自己，也容易带出出于自己意愿的读法；不过kill与die的对照及不带宾语的说明都保留，整条也未必把die完全限定为自愿行为。二审因此保留学习上可能误解的轻微存疑。

词库位置：`data/ja/entries/16.json`，`kill`，`tip`

### kitchen / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Shared kitchen facilities can encourage social interaction among students living in university accommodation away from home.

现译：共用の台所設備は、親元を離れて大学の宿舎で暮らす学生同士の交流を促進できます。

建议（完整字段）：共用の台所設備は、家を離れて大学の宿舎で暮らす学生同士の交流を促進できます。

依据：大学住宿语境下，away from home常让人想到离开家庭或父母的家，译为「親元を離れて」有自然语用依据。但原文也可能包括已婚或离开自己家庭的学生，现译仍可能缩窄群体。二审未维持初审的重大错误判断，而将其保留为普通语用与严格范围之间的轻微存疑。

词库位置：`data/ja/entries/1.json`，`kitchen`，`ex.1`

参考：[homeが文脈により両親・幼少時の家を含意する用法を辞書出版社自身が説明している。](https://dictionaryblog.cambridge.org/2020/07/22/staying-at-home-going-home-or-working-from-home-using-the-word-home/)

### librarian / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：The librarian helped me find a book about birds.

现译：図書館員は、私が鳥についての本を探すのを手伝ってくれました。

建议（完整字段）：図書館員は、私が鳥についての本を見つける手助けをしてくれました。

依据：过去式helped me find通常让人理解为在帮助下找到了书；现译只明确帮助寻找，可能弱化结果。但help也可指面向发现的活动辅助，不能一概认为保证达成，日译也未说没有找到。二审依照同类officer例的标准，保留终点意义的轻微存疑，候选直接对应找到。

词库位置：`data/ja/entries/26.json`，`librarian`，`ex.0`

### mathematical / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Mathematical models help researchers predict how rising temperatures may affect coastal communities over time.

现译：数学モデルは、気温上昇が将来、沿岸地域にどう影響し得るかを研究者が予測する助けになります。

建议（完整字段）：数学モデルは、気温上昇が時間の経過とともに沿岸地域にどう影響し得るかを研究者が予測する助けになります。

依据：over time说明影响随时间推移的变化，现译「将来」可能只指未来某个时点，未明确过程。但模型预测气温上升影响的整句也自然带出时间推移，未来预测的大意一致。二审无法确定过程意义已实质遗漏，还是被上下文包含，因此保留轻微存疑，候选直接写随时间经过。

词库位置：`data/ja/entries/43.json`，`mathematical`，`ex.1`

### medium-sized / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Medium-sized cities can offer diverse employment opportunities while maintaining shorter commuting times than major urban centres.

现译：中規模の都市は、大都市中心部より短い通勤時間を保ちながら、多様な雇用機会を提供できる。

建议（完整字段）：中規模の都市は、大都市より短い通勤時間を保ちながら、多様な雇用機会を提供できる。

依据：与中等规模城市比较时，major urban centres自然可指整个大城市聚集区，原文没有理由只比较都心；现译「大都市中心部」可能缩窄地理范围。但一般英文也可能用urban centre指中心市街，且本句没有定义。通勤更短与就业多样均保留，二审因此只记轻微存疑。

词库位置：`data/ja/entries/23.json`，`medium-sized`，`ex.1`

### nowhere / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Without affordable housing, some low-income families have nowhere to live despite having regular paid employment.

现译：手頃な価格の住宅がないため、低所得の家庭の中には、定期的に賃金の出る仕事をしていても住む所がない家庭がある。

建议（完整字段）：手頃な価格の住宅がないため、低所得の家庭の中には、継続的に賃金を得る仕事に就いていても住む所がない家庭がある。

依据：regular通常限定就业本身的持续性或规律性，现译「定期的に賃金の出る仕事」则把重点放在工资按期支付，两者范围可能不同。不过在低收入家庭虽有正常工作仍无房可住的情境中，两种表达自然重合，原文也未给具体雇佣或支付形式。二审保留修饰范围的轻微存疑。

词库位置：`data/ja/entries/13.json`，`nowhere`，`ex.1`

### occurrence / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Improved drainage systems can reduce the occurrence of flooding in densely populated urban areas.

现译：排水設備を改善すると、人口密集地域での洪水の発生を減らせます。

建议（完整字段）：排水設備を改善すると、人口が密集した都市部での洪水の発生を減らせます。

依据：英文同时限定人口密集及城市地区；「人口密集地域」单独也可能包含农村密集聚落，未明示城市。但排水设施与人口密集的一般语境也能自然让人理解为都市，可能只是压缩表述。二审未确认都市限定实质丢失，保留轻微范围存疑，候选把都市部明确写出。

词库位置：`data/ja/entries/62.json`，`occurrence`，`ex.1`

### officer / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：A police officer helped us find the station.

现译：警察官が、駅を探すのを手伝ってくれた。

建议（完整字段）：警察官が、駅を見つける手助けをしてくれた。

依据：helped us find通常让人理解为警察帮助找到车站，现译「探すのを手伝って」只明确协助寻找，可能弱化到达结果。不过help也可只说明活动上的辅助，日译亦未断言最终没有找到。原文缺少后续结果说明，二审将终点意义可能变弱保留为轻微存疑。

词库位置：`data/ja/entries/17.json`，`officer`，`ex.0`

### persistence / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：The persistence of poverty suggests that economic growth alone cannot guarantee better living conditions for every household.

现译：貧困が続いていることは、経済成長だけでは、どの家庭にもよりよい生活条件を保証できないことを示唆しています。

建议（完整字段）：貧困が続いていることは、経済成長だけでは、すべての家庭によりよい生活条件を保証できるわけではないことを示唆しています。

依据：英文否定能保证每个家庭都改善，并不要求否定任何家庭获保证的可能。现译「どの家庭にも〜できない」也可能读成一个家庭都无法保证，不过贫困持续的语境又支持无法对所有家庭一律保证的理解。二审无法确定否定范围必然错误，因此保留轻微存疑，候选澄清并非所有家庭。

词库位置：`data/ja/entries/54.json`，`persistence`，`ex.1`

### portrait / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：My grandmother's portrait hangs above the living room fireplace.

现译：祖母の肖像画は、居間の暖炉の上に掛かっている。

建议（完整字段）：祖母の肖像は、居間の暖炉の上に掛かっている。

依据：portrait可指绘画、素描或照片，本例只说挂在壁炉上方，并未交代媒介。「肖像画」通常限定为画出来的肖像，但它也是portrait的常见标准译法，在室内场景中自然。二审无法确定这是合理选义还是多加了媒介限制，故保留轻微存疑，候选采用较宽的肖像。

词库位置：`data/ja/entries/20.json`，`portrait`，`ex.0`

### pot / 第3个搭配（col.2）

级别：轻微（若问题成立时的潜在影响）

源文：a pot of tea

现译：a pot of tea｜お茶1壺

建议（完整字段）：a pot of tea｜ティーポット1杯のお茶

依据：a pot of tea通常表示供饮用的一茶壶茶，现译「お茶1壺」较容易让现代日语读者想到存放茶叶的容器或特殊茶器，作为学习搭配可能偏离。不过「壺」在文化性或文语用法中也可广指装茶容器，二审未硬判不一致，只保留轻微存疑，候选明确ティーポット一杯。

词库位置：`data/ja/entries/16.json`，`pot`，`col.2`

### prominent / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：A prominent local artist opened the exhibition yesterday.

现译：昨日、地元の著名な芸術家が展覧会を開きました。

建议（完整字段）：昨日、地元の著名な芸術家が展覧会の開幕を告げました。

依据：opened既可表示著名艺术家为展览开幕，也可一般表示活动开始；辅助中文支持揭幕读法。日语「展覧会を開く」同样有开始或举办的范围，不能据此断定增加了主办者角色。二审将是否误导为亲自主办保留为轻微存疑，候选偏向明确宣布开幕的场景。

词库位置：`data/ja/entries/45.json`，`prominent`，`ex.0`

### propose / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Researchers propose expanding urban green spaces to improve air quality and encourage residents to exercise more regularly.

现译：研究者たちは、大気の質を改善し、住民の定期的な運動を促すため、都市の緑地拡大を提案しています。

建议（完整字段）：研究者たちは、大気の質を改善し、住民がより規則的に運動するよう促すため、都市の緑地拡大を提案しています。

依据：more regularly含有比现在更规律或更经常的比较，现译「定期的な運動」未直接表达增加。不过扩大绿地以促进运动，本身也自然带出改善运动习惯的方向。二审无法确定这是实质遗漏，还是日语对行为改善的自然压缩，因此保留轻微存疑，候选明确比较关系。

词库位置：`data/ja/entries/41.json`，`propose`，`ex.1`

### replace / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Renewable energy could gradually replace fossil fuels if governments invest sufficiently in infrastructure and storage technology.

现译：政府がインフラや蓄電技術に十分投資すれば、再生可能エネルギーは徐々に化石燃料に取って代われる可能性がある。

建议（完整字段）：政府がインフラやエネルギー貯蔵技術に十分投資すれば、再生可能エネルギーは徐々に化石燃料に取って代われる可能性がある。

依据：再生能源替代化石燃料的语境下，storage technology可包括电、热、化学能等储存技术，而「蓄電技術」只明示电力储存，全文未限定电力。但若原意是常见的再生电力并网问题，蓄电也自然成立。二审无法确定作者所指介质，因此保留术语范围的轻微存疑。

词库位置：`data/ja/entries/10.json`，`replace`，`ex.1`

参考：[エネルギー貯蔵の電気・熱・化学等の種類を区別する専門機関資料。](https://iea-es.org/energy-storage-technologies/)

### sausage / 第2个搭配（col.1）

级别：轻微（若问题成立时的潜在影响）

源文：vegetarian sausage

现译：vegetarian sausage｜植物性ソーセージ

建议（完整字段）：vegetarian sausage｜ベジタリアン向けソーセージ

依据：搭配中的vegetarian不能固定等同于全植物来源，否则可能排除含蛋奶的菜食产品；但「植物性ソーセージ」也可能只是植物主体肉替代品的通行名称，整条并未保证全部原料为植物。二审保留两种术语范围之间的轻微存疑，候选直接说明面向素食者。

词库位置：`data/ja/entries/8.json`，`sausage`，`col.1`

参考：[卵乳を許す菜食の類型があるためvegetarianは完全植物性と同一ではない。](https://vegsoc.org/blog/become-a-vegetarian/)

### sausage / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Consumers are increasingly choosing vegetarian sausages as they seek alternatives to traditional meat products.

现译：従来の肉製品の代わりを求めて、植物性のソーセージを選ぶ消費者が増えている。

建议（完整字段）：従来の肉製品の代わりを求めて、ベジタリアン向けソーセージを選ぶ消費者が増えている。

依据：vegetarian排除肉鱼，却未必排除蛋奶；如果「植物性」严格表示全部原料来自植物，现译就缩窄产品范围。不过它也可作为以植物为主要原料的肉类替代品通称，在本句中自然成立。原文未列成分或菜食类型，二审因此只保留术语范围的轻微存疑。

词库位置：`data/ja/entries/8.json`，`sausage`，`ex.1`

参考：[Vegetarianとveganの区別、前者は卵・乳を許すことがあるという団体自身の説明。](https://vegsoc.org/blog/become-a-vegetarian/)

### shiny / 第1个搭配（col.0）

级别：轻微（若问题成立时的潜在影响）

源文：shiny shoes

现译：shiny shoes｜光るほど磨いた靴

建议（完整字段）：shiny shoes｜つやのある靴；ぴかぴかの靴

依据：shiny只描述有光泽，不要求经过擦拭；现译「光るほど磨いた」可能排除因材质本身而发亮的鞋。不过同条例句涉及擦鞋，日常保养语境也使擦亮的鞋成为自然典型。二审把它留在一般释义范围与具体典型译法的边界，记为轻微存疑，候选仅描述光泽状态。

词库位置：`data/ja/entries/18.json`，`shiny`，`col.0`

### stake / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：She bought a small stake in her sister's bakery.

现译：彼女は姉（または妹）のパン屋に少額出資しました。

建议（完整字段）：彼女は姉（または妹）のパン屋の持ち分を少し購入しました。

依据：词条的financial share与small stake可按所有权比例理解，现译「少額出資」则转向投入金额。但复核后读到的Cambridge商业释义也允许stake表示投入公司的金额，不能排除本句的小额投资读法。因此二审已撤回原来的确认错误，现有效结论为轻微存疑，候选持份表述较能保留范围。

词库位置：`data/ja/entries/37.json`，`stake`，`ex.0`

修改注意：本说明依据撤回记录的有效assessment，并绑定该记录SHA；不是继续沿用旧错误结论，也不是新增通过票。

参考：[SHARE義に加えてBusiness Englishは会社に投じたamountという語義も掲げ、必ずしも比率だけに固定できない。](https://dictionary.cambridge.org/us/dictionary/english/stake?topic=the-stock-market)

### stay / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Tourists who stay longer in rural areas may contribute more to local businesses than short-term visitors.

现译：農村部に長く滞在する観光客は、短期の旅行者よりも地元の商店に多くの収益をもたらすかもしれません。

建议（完整字段）：農村部に長く滞在する観光客は、短期の旅行者よりも地元の事業者に多くの収益をもたらすかもしれません。

依据：businesses包括商品和服务企业，旅游语境也自然涵盖住宿、餐饮等经营者；「商店」可能让范围偏向店铺。不过原文未逐类限定受益对象，也可能用商店代表游客消费所及的本地经营活动。长短停留的比较和可能性均保留，二审仅将译语范围可能缩窄保留为轻微存疑。

词库位置：`data/ja/entries/1.json`，`stay`，`ex.1`

参考：[businessの組織義が商品又はサービスを売る企業・会社であることを確認。](https://dictionary.cambridge.org/dictionary/english-japanese/business)

### steward / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：A steward helped us find our seats before the concert.

现译：演奏会の前に、係員が席を探すのを手伝ってくれました。

建议（完整字段）：演奏会の前に、係員が私たちの席を見つける手助けをしてくれました。

依据：过去式helped us find自然表示帮助找到座位，现译只明确协助寻找，可能弱化到达结果。但help也可描述以发现为目标的辅助活动，双方均未补充最终结果。二审依照officer与librarian同型例的标准，保留轻微终点存疑，未确认为错，候选直接对应找到。

词库位置：`data/ja/entries/42.json`，`steward`，`ex.0`

### terminable / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Employment contracts should be terminable by either party, provided that reasonable notice is given.

现译：雇用契約は、妥当な期間を置いて通知することを条件に、どちらの当事者からも終了できるべきです。

建议（完整字段）：雇用契約は、終了までに妥当な予告期間を設けて通知することを条件に、どちらの当事者からも終了できるべきです。

依据：契约终止中的notice指终止前的通知，预告期从通知日持续到雇佣结束日。现译「妥当な期間を置いて通知する」既可能读成等待一段时间才通知，也可读为留有结束前猶予。同条前例说明提前通知，仍能帮助正确理解，因此二审保留轻微存疑，候选澄清通知后的预告期间。

词库位置：`data/ja/entries/70.json`，`terminable`，`ex.1`

参考：[notice periodが通知日から雇用終了日までの期間であることを確認。個別契約の法律判断には用いない](https://www.employment.govt.nz/ending-employment/giving-notice)

### territory / 学习提示（tip）

级别：待定（若问题成立时的潜在影响）

源文：领土义可不可数；一块辖区可用a territory。

现译：領土の意味では可算にも不可算にもなります。1つの管轄地域にはa territoryを使えます。

建议（完整字段）：領土の意味では可算・不可算のどちらでも使えます。1つの管轄地域を指す場合は a territory と言えます。

依据：中文源文「可不可数」既可能是可数与不可数均可的压缩写法，也可能省略或误写了「可作不可数」。日译选择了前者，后半a territory对应辖区的说明准确。英语资料支持territory有两种数法，但不能代替确认这条中文的作者意图，因此保留存疑，需先澄清中文意图。

词库位置：`data/ja/entries/39.json`，`territory`，`tip`

修改注意：须先确认中文意图；候选仅在确认两种用法均可时采用，不能自动视为改译批准。

参考：[territoryに同じ意味で可算と不可算の用法があるという英語語法の説明。ただし中国語の作者意図を確定するものではない。](https://learnenglish.britishcouncil.org/free-resources/grammar/english-grammar-reference/common-problems-count-uncount-nouns?page=14%3Fpage%3D14)

### thermometer / 第2条例句（ex.1）

级别：轻微（若问题成立时的潜在影响）

源文：Accurate thermometers help researchers monitor temperature changes in natural habitats affected by global warming.

现译：正確な温度計は、地球温暖化の影響を受ける自然の生息地で、研究者が気温変化を監視する助けになります。

建议（完整字段）：正確な温度計は、地球温暖化の影響を受ける自然の生息地で、研究者が温度変化を監視する助けになります。

依据：temperature可指空气、水或土壤等温度，「気温」则限于空气温度。全球变暖语境使气温观测成为自然理解，但自然栖息地也包括水域、地下等，全文未指定测量介质。二审因此保留测量对象可能缩窄的轻微存疑，候选使用较广的温度变化。

词库位置：`data/ja/entries/30.json`，`thermometer`，`ex.1`

### tiger / 第1条例句（ex.0）

级别：轻微（若问题成立时的潜在影响）

源文：The tiger rested in the shade beside a pool.

现译：そのトラは、水場のそばの木陰で休んでいました。

建议（完整字段）：そのトラは、水場のそばの日陰で休んでいました。

依据：原文只说老虎在水池旁的阴凉处休息，没有交代遮阴物。现译「木陰」增加树木这个具体来源；自然场景使其合理，却不足以确认为该句事实，其他例句的森林环境也不能移入本例。休息位置的大意一致，二审将额外的树木信息保留为轻微存疑。

词库位置：`data/ja/entries/2.json`，`tiger`，`ex.0`

### tune / 第2条例句（ex.1）

级别：待定（若问题成立时的潜在影响）

源文：A memorable tune can help young learners retain new vocabulary and develop greater confidence in speaking.

现译：覚えやすい旋律は、幼い学習者が新しい単語を記憶し、話す自信を高める助けになります。

建议（完整字段）：覚えやすい旋律は、若い学習者が新しい語彙を覚え、話す自信をさらに高める助けになります。

依据：young learners可覆盖较宽的小学生年龄范围，而「幼い学習者」容易让人联想到更年幼的儿童，存在缩窄对象的可能。不过原文与现译都没有固定年龄界线，特定考试资料也不能定义本句范围，因此只保留年龄表述存疑。一般效用语境的「助けになります」不另计为can误译。

词库位置：`data/ja/entries/26.json`，`tune`，`ex.1`

修改注意：候选保留较宽的年轻学习者范围，供确认用；并未认定现译年龄范围必然错误。

参考：[Young Learnersという用語が小学生年齢の幅を含めて使われる教育資料。個別試験の年齢を本例の厳密な定義にはしない。](https://assets.cambridgeenglish.org/network-services/yle-handbook-for-teachers.pdf)
