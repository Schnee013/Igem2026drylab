# Lee et al. 2022 — GPCR AF2 Docking Benchmark 总结

**全名**：Evaluating GPCR modeling and docking strategies in the era of deep learning-based protein structure prediction  
**期刊**：Comput Struct Biotechnol J 21:158-167  
**PMID**：36544468  
**PDF**：`pdf/Lee2022-GPCR-AF2-docking-benchmark.pdf`

---

## 核心结论

AF2 预测结构用于 GPCR 对接显著优于传统同源建模（+30% 成功率），但**必须用受体灵活对接**，否则性能严重下降。

---

## 关键数据

### AF2 vs 同源建模

| 方法 | 小分子对接成功率 |
|------|---:|
| 传统模板建模（TBM） | ~5-8% |
| AF2（as-is，默认） | ~35-47% |
| 实验晶体结构（cross-docking） | ~47% |
| 实验晶体结构（self-docking） | ~82% |

### 刚性 vs 灵活对接（关键！）

| 对接方式 | 成功率 |
|---------|---:|
| 刚性对接（AutoDock Vina 默认） | **24-32%** |
| 灵活对接（Rosetta GALigandDock） | **47%** |

### p-lDDT 置信度阈值

| 结合口袋 p-lDDT | 对接成功率 |
|----------------|---:|
| > 0.95 | ~70% |
| 0.85-0.95 | ~35% |
| < 0.85 | ~0%（不可靠） |

---

## 主要注意事项

1. **功能状态（激活 vs 非激活）影响 ~20%**：AF2 需要用 state-specific biasing（AF,bias 或 AF,Gα 策略）才能获得最好的结合口袋预测
2. **课外环和 ECD 可能预测不准**：尤其 Class B1 GPCR 的大胞外域需要 AlphaFold-multimer + G protein
3. **虚拟筛选表现略低于对接**：AF2 AUC ~0.68-0.75（实验结构 ~0.75+），仍远优于 TBM

---

## 对本项目的直接影响（⚠️ 重要）

### 好消息
- AF2 可靠性已被验证，优于同源建模，用于 Gpr2/Gpr3/GprC 对接是合理的
- 不存在实验结构的情况下，AF2 是最优选择

### 风险点
1. **我们目前使用的是刚性 Vina**（默认参数），对应 24-32% 成功率。灵活对接（Rosetta GALigandDock）可达 47%。差异约 15 个百分点。
2. **必须检查 p-lDDT**：需要查 Gpr2/Gpr3/GprC 预测结构中结合口袋残基（Kuo2024 报告的 Y168、N161；Hu2024 报告的 R6.45 等）的 p-lDDT 值：
   - > 0.95 → 结果可信
   - 0.85-0.95 → 结果需谨慎
   - < 0.85 → 不应引用

### 行动项
- [ ] 检查 Gpr2/Gpr3/GprC AF2 结构的结合口袋 p-lDDT（可从 AlphaFold Database 下载 pLDDT per-residue 数据）
- [ ] 在 wiki 报告中明确说明使用刚性 Vina 的局限性，引用 Lee2022
- [ ] 如 p-lDDT 低于 0.85，结论需加 caveat

---

## 推荐引用场景

- 方法学 §：解释为何用 AF2 结构做对接（"AF2 substantially outperforms homology models..."）
- 局限性 §：说明刚性对接的成功率上限（~30%）
