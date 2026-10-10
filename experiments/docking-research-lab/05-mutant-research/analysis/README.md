# 突变结果的比较与阅读口径

依次阅读[01–03初筛](01-03-initial-screen/README.md)、[04–07单突变](04-07-single-mutants/README.md)和[08双突变](08-double-mutants/README.md)。

ΔS_i=S_i(突变体)−S_i(WT)，D=ΔS18−ΔS3。负ΔS表示评分降低，正D为相对WT向#3偏移。检查D时同时保留ΔS3与ΔS18，分清目标改善、另一配体变差与两者共同变化。

01与02分别使用自己的路线WT；04–07单突变主统计保留各自来源WT。08使用05-WT为主、07-WT作敏感性参照，亲本按05或07来源标记。组合相对亲本直接比较S(AB)−S(A)和S(AB)−S(B)；非加和残差在同一WT下计算S(AB)−S(A)−S(B)+S(WT)。

[组合数据](data/combination-mutants.json)共同保存04批1条三突变及08批18条双突变。其来源字段和source_sha256保持原值，通过[迁移表](../../provenance/file-map.csv)定位交付文件。

其他pose是同次搜索候选，不能当独立重复。AF模型例外、CPU差异和结构来源分别记录；更换WT的算术敏感性检查不能消除模型来源差异。
