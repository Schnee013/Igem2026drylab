# 项目全貌

> 来源: PRD v3 §1 | 最后更新: 2026-04-03

## 一句话描述

构建一个**基于 GPCR 生物传感器**的植物寄生线虫田间早期检测系统：线虫分泌特征性蛔苷素（ascarosides）→ 捕食性真菌来源的 Gpr 受体感知 → 底盘生物（**酿酒酵母或丝状真菌，待定**）信号转导与级联放大 → 肉眼可见的显色输出 → 防治建议闭环。

> **底盘决策状态**: 尚未确定。详见 [底盘决策分析](chassis-decision.md)。

## 核心信号链路

```
土壤中有害线虫 (PPNs)
    │ 分泌
    ▼
ascr#18 / ascr#3（特征比例）
    │ 配体结合
    ▼
Gpr2 / Gpr3 / GprC（来自 A. oligospora / A. flagrans）
    │
    ├─── 方案 A: 异源表达于酵母膜 ──┐
    │    嵌合 Gpa1 → MAPK 级联      │
    │    GAL4 正反馈放大              │
    │                                 │
    ├─── 方案 B: 丝状真菌原生表达 ──┤
    │    内源 MAPK/PKA 通路           │
    │    寻找响应启动子               │
    │                                 │
    ▼                                 │
显色蛋白 (Lycopene / Betalain / amilCP)◄┘
    │
    ▼
田间可视化判读 → 防治建议闭环
```

## 双靶标判别逻辑

- **ascr#18**: 在植物寄生线虫（PPNs）中占绝对优势
- **ascr#3**: 在自由生活线虫中占主导
- 通过改造 Gpr 受体获得对 ascr#3 / ascr#18 的差异化特异性，双信号比例判别有害线虫

## 团队组织

| 组别 | 核心目标 | 关键任务 |
|------|---------|---------|
| 核心感应组 | 靶标表征与受体决策 | ascr#3/#18 定量、Gpr 受体筛选与评估、受体特异性改造方案 |
| 通路工程组 | 偶联适配与信号增益 | 酵母底盘偶联、级联放大回路、可视化输出与产品化 |
| 背景调研组 | 叙事与社会影响 | 危害与经济学分析、技术痛点对比、防治联动、安全性 |

## 关键受体信息

| 受体 | UniProt | 来源物种 | 结构状态 | AlphaFold DB |
|------|---------|---------|---------|-------------|
| Gpr3 | G1XJN1 | *A. oligospora* | AlphaFold 预测，已验证 | [AF-G1XJN1-F1](https://alphafold.ebi.ac.uk/entry/AF-G1XJN1-F1) |
| Gpr2 | G1X9E2 | *A. oligospora* | AlphaFold 预测，已验证 | [AF-G1X9E2-F1](https://alphafold.ebi.ac.uk/entry/AF-G1X9E2-F1) |
| GprC | A0A437AGY2 | *A. flagrans* | AlphaFold 预测，已验证 | [AF-A0A437AGY2-F1](https://alphafold.ebi.ac.uk/entry/AF-A0A437AGY2-F1) |

## 核心参考文献

| 文献 | 内容 |
|------|------|
| Kuo et al. (2024) *Nature Microbiology* | Gpr2/Gpr3 感知线虫信息素 |
| Hu et al. (2024) *Nature Microbiology* | GprC 激活线粒体并重编程真菌细胞 |
| Lengger & Jensen (2020) *FEMS Yeast Research* | 酵母 GPCR 信号工程综述 |
| Shaw et al. (2019) *Cell* | 酵母 GPCR 信号通路模块化调控模型 |
| Fan & Yuan (2024) *Biosensors and Bioelectronics* | GPCR+GAL4 级联放大酵母传感器 |

## iGEM 评审策略

详见 [干实验总策略](dry-lab-strategy.md) §5 部分。核心要求：**Model 与湿实验之间有实际互动**（model-experiment feedback loop），需完成至少一个 Design-Build-Test-Learn cycle。
