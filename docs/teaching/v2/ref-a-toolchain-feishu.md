# REF-A：工具版本速查
> 遇到"这个工具叫什么""版本号多少""从哪装"时查这张表。
## Pipeline 工具链（按执行顺序）
| # | 工具 | 版本 | 用在哪一步 | 安装渠道 |
|---|------|------|-----------|---------|
| 1 | AlphaFold DB | — | WT 受体 PDB 下载 | alphafold.ebi.ac.uk |
| 2 | AlphaFold 3 Server | — | 突变体结构预测 | alphafoldserver.com（学术免费）|
| 3 | DeepTMHMM | — | TM 域边界预测 | biolib.com/DTU/DeepTMHMM |
| 4 | Orca | 6.1.1 | 配体 DFT 几何优化 | orcaforum.koeln.de（学术免费）|
| 5 | ADFR Suite | 1.0 | 受体/配体 → PDBQT | ccsb.scripps.edu |
| 6 | AutoDock Vina | 1.2.7 | 分子对接 | github.com/ccsb-scripps/AutoDock-Vina |
| 7 | ProLIF | ≥2.0 | IFP 分析 | `pip install prolif` |
| 8 | PyMOL | 教育版 | 3D 可视化 | pymol.org 教育版免费 |
## 辅助工具
| 工具 | 用途 |
|------|------|
| GPCRdb | BW 编号 → 序列号映射验证 |
| UniProt | TM 螺旋注释 |
| PubChem | 配体 SDF 下载 |
| Python 3.11 | 脚本运行环境（`conda activate docking`）|
## 版本警告
**不要随意升级主版本**。Vina 2.0 的打分函数可能和 1.2.7 不同——所有 ΔG 数值就不可比了。版本锁定是协议一致性的一部分。
权威源：`docs/modeling/P0-molecular-docking.md` §工具栈
