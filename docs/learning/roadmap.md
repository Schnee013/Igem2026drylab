# 学习路线图与工具环境

> 来源: PRD v3 §4 + §6 | 最后更新: 2026-04-03

## 阶段一: ODE 建模基础（第 1 周）

**目标**: 掌握 ODE 建模思路（已有 Python 基础，跳过 Python 入门）

| 资源 | 类型 | 说明 |
|------|------|------|
| [Caltech BE150: Biological Circuit Design](http://be150.caltech.edu/2020/) | 课程 | Justin Bois 的课程，从 Python 到生物回路 ODE 建模，有完整 Jupyter Notebook。**强烈推荐第一站** |
| [iGEM Webinar: ODEs and Hill Functions (Valencia UPV)](https://2020.igem.org/wiki/images/a/a5/Webinar_2a_Presentation.pdf) | 讲座 PDF | iGEM 官方建模 Webinar，45 min，涵盖质量作用定律、Hill 函数、QSSA |
| [iGEM Oxford 2015 Modeling Tutorial](https://2015.igem.org/Team:Oxford/Modeling/Tutorial) | 教程 | 从化学反应到 ODE 的入门讲解，面向非数学背景 |
| SciPy `solve_ivp` 文档 | 官方文档 | Python 求解 ODE 的标准工具 |
| Nature npj: *The art of modeling gene regulatory circuits* (2024) | 综述 | 基因调控回路建模方法论 |

**里程碑**: 能用 Python 独立实现一个 Hill 函数驱动的基因表达 ODE 模型并绘制剂量-响应曲线

---

## 阶段二: 分子对接（第 1-2 周，可与阶段一并行）

**目标**: 完成 Gpr 受体与 ascaroside 的对接

| 资源 | 类型 | 说明 |
|------|------|------|
| [EMBL-EBI AlphaFold 实践指南](https://www.ebi.ac.uk/training/online/courses/alphafold/) | 在线课程 | 免费，3 小时，涵盖结构预测、置信度评估、ColabFold |
| [AlphaFold DB](https://alphafold.ebi.ac.uk/) | 数据库 | 直接下载 Gpr2/3/GprC 预测结构 PDB 文件 |
| [AutoDock Vina 官方教程](https://autodock-vina.readthedocs.io/en/latest/docking_basic.html) | 官方教程 | 命令行分子对接 step-by-step |
| PMC4868550: *Computational protein-ligand docking with AutoDock suite* | Protocol | 完整 5 小时 protocol |
| PMC4669947: *AutoDock made easy for non-bioinformaticians* | 教程论文 | 面向无生信背景的 click-by-click |
| [PyMOL](https://pymol.org/) | 工具 | 分子可视化，教育版免费 |

**里程碑**: 完成 ascr#18 与 Gpr3 的对接，获得结合能和关键残基

---

## 阶段三: 信号通路建模（第 2-3 周）

**目标**: 建立完整的 GPCR → 显色输出的 ODE 模型

| 资源 | 类型 | 说明 |
|------|------|------|
| Shaw et al. 2019 *Cell* | 核心论文 | 酵母 GPCR 通路模块化调控，**含定量参数和模型** |
| Fan & Yuan 2024 *Biosensors and Bioelectronics* | 核心论文 | GPCR+GAL4 正反馈级联放大，LOD 0.25 pM |
| [COPASI](http://copasi.org/) | 工具 | GUI 生化反应网络模拟器 |
| [PySB](https://pysb.org/) | Python 库 | 用代码构建生化反应模型 |
| BioCRNpyler + AutoReduce (bioRxiv 2022.10.05.511053) | 工具链 | 从详细反应网络到简化 ODE 的自动化 |
| [iGEM XJTLU 2022 Dry Lab (GitHub)](https://github.com/JiayiLi21/iGEM-XJTLU2022_Dry-Lab) | 开源项目 | iGEM 金牌项目干实验代码 |

**里程碑**: 建立通路 ODE 模型，预测系统最低可检测 ascr 浓度

---

## 阶段四: 高级主题与防治建模（第 3+ 周，按需）

| 主题 | 资源 |
|------|------|
| 反应-扩散方程 | [IPython Cookbook: Reaction-Diffusion PDE](https://ipython-books.github.io/124-simulating-a-partial-differential-equation-reaction-diffusion-systems-and-turing-patterns/); [Mathematics LibreTexts Ch13.6](https://math.libretexts.org/) |
| 贝叶斯推断 | PyMC 官方教程; *Bayesian Analysis with Python* (Osvaldo Martin) |
| 蛋白质工程计算筛选 | Rosetta 或 FoldX 突变扫描 |
| STEPS (随机反应扩散模拟) | [STEPS Python simulator](https://pmc.ncbi.nlm.nih.gov/articles/PMC2706651/) |
| 剂量-响应建模 | R `drc` 包; SciPy `curve_fit` + Hill 方程 |
| 经济效益建模 | Sasser & Freckman 1987 综述; 成本-收益分析方法 |

---

## 硬件需求

| 任务 | 最低配置 | 推荐配置 | 备注 |
|------|---------|---------|------|
| ODE 建模 / 数据拟合 | 任意笔记本 | 无特殊要求 | 纯 CPU，秒级 |
| 分子对接 (AutoDock Vina) | 4 核 CPU, 8GB RAM | 8 核, 16GB | CPU 密集，分钟级 |
| AlphaFold2 预测 | Google Colab 免费 GPU | 本地 NVIDIA ≥16GB VRAM | **建议用 ColabFold** |
| AlphaFold-Multimer | Colab Pro ($10/月) | NVIDIA A100 40GB | 大复合体 |
| 分子动力学 (GROMACS) | NVIDIA ≥8GB VRAM | A100/H100 | 仅 P3 需要 |
| 反应-扩散 PDE | 4 核, 16GB RAM | 8 核, 32GB | 3D 网格需更多内存 |

**结论**: P0 任务（对接 + ODE）不需要额外硬件，笔记本 + Colab 即可。GPU 服务器仅 MD 模拟或大复合体预测时需要（推荐 AutoDL，A100 约 ¥3-5/h）。

## 软件环境

| 工具 | 用途 | 安装 |
|------|------|------|
| Python 3.10+ | 所有建模 | Anaconda/Miniconda |
| Jupyter Lab | 交互式开发 | `conda install jupyterlab` |
| NumPy, SciPy, Matplotlib | 科学计算 + ODE | `conda install numpy scipy matplotlib` |
| ColabFold | 蛋白结构预测 | Google Colab |
| AutoDock Vina | 分子对接 | `pip install vina` |
| Meeko | PDBQT 准备 | `pip install meeko` |
| PyMOL | 分子可视化 | 教育版免费 |
| COPASI | 反应网络 GUI | copasi.org |
| PySB | Python 生化模型 | `pip install pysb` |
| R + drc 包 | 剂量-响应曲线 | `install.packages("drc")` |
| Claude Code | AI 辅助编码 | 已有 |
