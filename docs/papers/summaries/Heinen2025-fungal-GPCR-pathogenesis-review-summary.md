# Heinen et al. 2025 — 真菌 GPCR 综述总结

**全名**：The rise of fungal G-protein coupled receptors in pathogenesis and symbiosis  
**期刊**：PLoS Pathogens  
**PMID**：40504784  
**PDF**：`pdf/Heinen2025-fungal-GPCR-pathogenesis-review.pdf`

---

## 核心结论

迄今为止真菌 GPCR 领域唯一的实验结构是酵母 Ste2（PDB 7AD3）。Gpr2/Gpr3/GprC 所属的碳水化合物受体家族无任何实验结构，AF2 预测 + 计算对接是目前唯一可行的结构研究途径。

---

## GPCR 分类体系

论文采用卷积神经网络（CNN）分析 1357 种真菌物种，识别出 17 个真菌 GPCR 家族。哺乳动物 6 大类中真菌只有 4 类（Rhodopsin、Glutamate、Frizzled、Secretin）。

**NTF 受体的归属**：Gpr2、Gpr3（*A. oligospora*）和 GprC（*A. flagrans*）属于 **Gpr 碳水化合物受体家族**，从酵母葡萄糖感知受体（Gpr1）演化而来，配体特异性从糖转向了 ascaroside。

---

## 实验结构现状

| 受体 | 物种 | 实验结构 |
|------|------|---------|
| Ste2 + α-信息素 | *S. cerevisiae* | cryo-EM，PDB 7AD3（Velazhahan 2021-22） |
| Gpr2/Gpr3/GprC | *Arthrobotrys* spp. | ❌ 无 |
| 所有碳水化合物受体 | 所有真菌 | ❌ 无 |

→ **论文明确指出实验结构空白，AF2+对接是合理唯一选择**，为本项目方法论提供直接引用依据。

---

## NTF 专项内容

- **Gpr2/Gpr3 异源二聚**：配体结合后形成异二聚体（heterodimerize），对信号功能的影响尚未研究清楚
- **GprC 双定位**：除质膜外，GprC 还定位于线粒体膜，配体结合后直接激活线粒体呼吸/ROS，形成独特的双重信号机制
- **与线虫受体的进化关系**：Arthrobotrys Gpr 与猎物 *C. elegans* 的 SRBC-66 在配体结合口袋有**共同残基**，提示共同祖先起源（收敛进化或水平基因转移）
- GprC 的 ascaroside 感知与葡萄糖感知并存（双配体），类似 StNILR1 的双配体模式

---

## 配体结合机制

- Ste2 激活机制与哺乳动物 Rhodopsin 不同：配体结合诱导独特的构象转变
- Ste2 可形成同源二聚体，同时偶联两个 G 蛋白
- Gpr2/Gpr3 异二聚的信号影响未知
- GprC 近亲（*A. ochraceus*）可感知 9-羟基十八碳二烯酸（oxylipin）——与 ascaroside 均为脂质衍生分子，提示识别模式可能相通

---

## 对本项目的意义

1. **确认靶点正确**：Gpr2/Gpr3/GprC 是目前唯一已知的 NTF ascaroside 受体，综述未提及任何新受体
2. **方法论支撑**：无实验结构 → AF2+Vina 是标准做法，可直接引用此综述为方法论背书
3. **GprC 双定位**：如果要在 ODE 模型中纳入线粒体 ROS 信号，GprC 的双定位是一个关键节点
4. **Ste2 结构**：作为唯一已知的真菌 GPCR 实验结构，可作为 Gpr2/3 AF2 预测质量评估的参考系

---

## 推荐引用场景

- 方法论 §：说明无实验结构，AF2 预测合理
- 背景 §：NTF GPCR 在真菌 GPCR 演化中的地位
- 受体分类 §：carbon receptor family 归属
