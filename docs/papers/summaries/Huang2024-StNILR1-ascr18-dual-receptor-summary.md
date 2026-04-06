# Huang L et al. 2024 — StNILR1 ascr#18 双配体受体总结

**全名**：A receptor for dual ligands governs plant immunity and hormone response and is targeted by a nematode effector  
**期刊**：PNAS  
**PMID**：39388275  
**PDF**：`pdf/Huang2024-StNILR1-ascr18-dual-receptor.pdf`

---

## 核心结论

马铃薯 LRR-RLK 受体 StNILR1 可同时识别 ascaroside#18 和油菜素类固醇（brassinolide），两类配体结合位点不同但均依赖 Island Domain（ID）。线虫效应子 RHA1B（E3 泛素连接酶）通过泛素化降解 StNILR1 来抑制植物免疫。

---

## ascr#18 结合数据

| 参数 | 值 |
|------|-----|
| 结合亲和力（全长胞外域） | Kd ≈ 1.79 μM（ITC） |
| 结合亲和力（缺少 C 端 5 LRR） | Kd ≈ 23.1 μM（降低但保留） |
| 结合亲和力（缺少 Island Domain） | 完全丧失 |

**结论**：Island Domain 是 ascr#18 识别的必需结构元件；C 端 5 LRR 有贡献但非必需。

---

## 结合位点信息（局限性）

⚠️ **论文无原子分辨率晶体结构**：使用同源建模（SWISS-MODEL，GMQE 0.87）推断口袋，**未提供具体接触残基列表**。

已知信息：
- StNILR1 与 AtNILR1（拟南芥）胞外域 RMSD = 1.684，总体相似但结合口袋存在差异
- ascr#18 和 brassinolide 结构差异大（RMSD = 5.225），但均被同一受体识别
- 两者结合位点部分重叠，但 C 端 5 LRR 对 BL 必需、对 ascr#18 非必需 → **不完全共享结合口袋**

---

## 线虫效应子 RHA1B 机制

1. RHA1B = *Globodera pallida* 分泌的 E3 泛素连接酶
2. 直接结合 StNILR1 胞质域（CD）
3. 泛素化 StNILR1 → 蛋白酶体降解
4. **特异性**：只靶向 StNILR1，不影响共受体 StBAK1
5. 进化意义：仅囊线虫（cyst nematode）有 RHA1B 同源基因，根结线虫（root-knot nematode）没有 → 针对马铃薯专化的免疫逃避

---

## 对本项目（GprC-ascr#18 对接）的参考价值

| 信息 | 可用性 |
|------|--------|
| ascr#18 结合的亲和力量级（μM） | ✅ 有用：预期 GprC 亲和力也在此量级 |
| 具体接触残基 | ❌ 无（无晶体结构） |
| ascr#18 化学基团与受体的接触模式 | ❌ 无 |
| ascr#18 可被非 GPCR 受体识别 | ✅ 验证 ascr#18 作为信号分子的功能保守性 |
| Island Domain 关键性 | 参考：GprC ECD/TM 的特定区域可能对应 |

**实用结论**：Huang2024 提供的是功能性而非结构性信息。对 GprC-ascr#18 对接的直接结构参考价值有限，但亲和力量级（μM）可作为 Vina 评分的合理性参考。

---

## 推荐引用场景

- 背景 §：ascr#18 作为跨界信号分子（真菌、植物均能感知）
- 检测灵敏度 §：植物受体 Kd ~1.79 μM，推测生物传感器设计靶标浓度范围
- 方法局限性 §：对接结果为计算预测，缺乏实验结构验证（与 Huang2024 处境相同）
