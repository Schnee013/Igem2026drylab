# 五个受体如何区分 ASCR3 与 ASCR18

## 最主要的结论

五个受体中，能够跨受体重复的配体区分信号主要出现在 ASCR18 一侧：gpr2、gpr3、gprc 和 srbc64 都有芳香残基形成的 `Hydrophobic` 作用稳定偏向 ASCR18，只有 daf37 没有出现这一模式。现阶段最合理的解释是，不同受体可能通过额外的芳香疏水包围来适应 ASCR18；这是**功能趋同候选**，还不是已经证实的序列保守机制。

ASCR3 没有相应的跨受体共同模式。唯一达到区分标准的是 gprc 的 `ASN56.A–HBAcceptor`。因此，目前的结果更像是：ASCR18 的区分具有可跨受体复现的疏水化学特征，而 ASCR3 的区分可能更多依赖各受体自己的方向性作用，或当前对接构象尚未充分捕捉其共同规律。

这些残基并非只与某一种配体接触。这里的“偏向”指同一受体的五个 model 配对后，该 residue–interaction 对某一配体反复呈现更高的 ProLIF Frequency。因此，本分析只把它用于描述构象接触频率的重复差异；物理效应与因果解释需要后续计算、动力学分析或突变实验检验。

## ASCR18：跨受体重复的芳香疏水识别

| 受体构建体 | ASCR18 偏向残基 | 跨 model 表现 | 解释 |
| --- | --- | --- | --- |
| gpr2 deltaN | `TRP338.A–Hydrophobic` | 5/5 model 出现；5/5 偏向 ASCR18；中位差值 +0.222 | 芳香疏水模式的一部分 |
| gpr3 deltaN | `TYR172.A–Hydrophobic` | 5/5 model 出现；5/5 偏向 ASCR18；中位差值 +0.333 | 本组最稳定的芳香疏水候选之一 |
| gpr3 deltaN | `TRP306.A–Hydrophobic` | 4/5 model 出现；3/5 偏向 ASCR18；中位差值 +0.222 | 同时指向暂定共同口袋位置 |
| gprc WT | `TRP388.A–Hydrophobic` | 5/5 model 出现；3/5 偏向 ASCR18；中位差值 +0.333 | 同时指向暂定共同口袋位置 |
| gprc WT | `TRP155.A–Hydrophobic` | 5/5 model 出现；3/5 偏向 ASCR18；中位差值 +0.333 | gprc 内部的第二个芳香疏水候选 |
| gprc WT | `TRP157.A–Hydrophobic` | 5/5 model 出现；3/5 偏向 ASCR18；中位差值 +0.222 | 与 TRP155 共同提示局部芳香环境 |
| srbc64 WT | `PHE161.A–Hydrophobic` | 5/5 model 出现；4/5 偏向 ASCR18；中位差值 +0.222 | 跨受体芳香疏水模式的独立支持 |
| daf37 WT | 未发现 | — | 不能把该模式扩展为 5/5 受体共有 |

这组结果支持的是一种**残基化学类别和作用类型的重复**：不同受体使用 Trp、Tyr 或 Phe，以疏水方式更频繁地容纳 ASCR18。由于这些残基尚未被证明位于彼此同源的位置，更准确的称呼是“芳香疏水功能趋同”，而不是“芳香残基序列保守”。

## ASCR3：目前只有受体特异的方向性信号

ASCR3 只有 gprc 的 `ASN56.A–HBAcceptor` 达到区分标准。该作用在 5/5 model 中出现，3/5 model 的 Frequency 高于 ASCR18，中位差值为 +0.222。它提示 ASN56 可能参与 gprc 对 ASCR3 的相对偏好，但在 daf37、gpr2 deltaN、gpr3 deltaN 和 srbc64 中没有找到可与之组成跨受体模式的候选。

因此，当前不能提出 ASCR3 的跨受体保守区分残基。更合适的实验定位是先把 gprc ASN56 当作受体特异候选，而不是把它推广为 ASCR3 的普遍识别位点。

## 一个值得优先检验的共同口袋位置

现有模板对齐把以下三个 ASCR18 芳香疏水候选暂时投射到同一个模板位置 `c7xmsA:226`：

- gpr2 `TRP338`
- gpr3 `TRP306`
- gprc `TRP388`

这是目前最接近“同一口袋位置被不同受体重复使用”的线索。如果新的五受体 MSA 能证明三者属于同一个可靠同源列，并且 WT 与 deltaN 的编号关系得到明确处理，那么这三个位点可以从“功能趋同候选”升级为“同源保守区分候选”。

不过，现有材料只是各受体到共同模板的低一致性配对对齐，identity 约为 9–19%；相同模板列本身不足以证明三者真正同源。它们目前的证据等级是“优先验证的共同口袋位置假说”，正式保守性判断取决于五受体 MSA 或结构级逐残基映射。

## contact-only 线索放在第二优先级

ASCR18 还出现了跨受体重复的脂肪族 `VdWContact`：gpr2 `VAL368`、gpr3 `MET92` 和 gprc `VAL91`，覆盖 3/5 个受体。另有若干芳香或受体特异的 `VdWContact` 候选。

这些结果可以帮助描绘 ASCR18 在口袋中的空间占位，但 `VdWContact` 只是非特异接触。它们不应与氢键或疏水作用合并排名，也不能据此推断结合更强。就验证顺序而言，应先看 4/5 受体重复的芳香 `Hydrophobic` 残基，再把这些 contact-only 位点作为局部口袋形状的辅助线索。

## MSA 能增加什么证据

补充 MSA 会显著增加证据，但它解决的是“这些功能相似的残基是否真的同源”，不会替代配体区分本身的五-model 证据。最有价值的 MSA 应包括五个完整受体序列，并明确给出 gpr2、gpr3 的 WT 与 deltaN 编号换算。

MSA 的首要检验对象是 `TRP338 / TRP306 / TRP388`：

- 如果三者落在同一个高可信同源列，且邻近保守区和结构环境也一致，就会形成真正的跨受体保守位点证据。
- 如果它们不能可靠对齐，但各自仍处在结合口袋并稳定产生相同的 ASCR18–Hydrophobic 偏向，则更支持功能趋同。
- 如果序列 identity 过低导致局部对齐不稳定，应以结构级逐残基映射作为更强证据，MSA 单独不足以下结论。

## 建议的验证顺序

第一优先级是 ASCR18 芳香疏水组，尤其是暂定共同位置上的 gpr2 `TRP338`、gpr3 `TRP306`、gprc `TRP388`，并加入 gpr3 `TYR172` 和 srbc64 `PHE161` 作为独立的功能趋同对照。第二优先级是 gprc `ASN56`，用于检验 ASCR3 是否存在受体特异的氢键区分。contact-only 位点适合辅助解释口袋形状，不宜作为首轮机制验证的核心。

## 结果指针

- 完整的 22 个区分候选及逐 model Frequency、差值和 source CSV 行号：`prolif_ligand_discrimination_candidates.csv`
- 跨受体功能趋同与暂定模板位置：`prolif_ligand_discrimination_cross_receptor.csv`
- 未经候选阈值截断的同受体配对矩阵：`prolif_ligand_discrimination_matrix_all.csv`

本文件只提炼跨受体的生物学解释；候选筛选采用同一受体内的五-model 配对比较，未重新引入被排除的 gpr2/gpr3 WT 结果。
