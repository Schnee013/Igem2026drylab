# DO-3：PyMOL 可视化 + IFP 读图
> **前置条件**：DO-1 完成、PyMOL 教育版已安装
> **预计耗时**：2-3 小时
> **学完能做**：打开 Top 6 候选在 PyMOL 中看 WT vs mutant 叠合；读 IFP 热图找差异残基
---
## 0. PyMOL 安装与启动
### 下载安装
1. 访问 https://pymol.org/edu/ ，用 .edu 邮箱申请教育版许可证
2. 下载对应平台的安装包：
   - **macOS**：下载 `.dmg`，打开后拖入"应用程序"文件夹
   - **Windows**：下载 `.exe` 安装包，运行后一路下一步
3. 从 Launchpad（Mac）或开始菜单（Windows）打开 PyMOL
### 界面说明
首次打开后你会看到两个窗口：
- **命令行窗口（PyMOL>）**：在这里输入命令，和终端类似
- **3D 视窗**：分子结构的可视化区域，可以鼠标拖动旋转
### 验证安装
在 PyMOL 命令行里输入：
```pml
print(cmd.get_version())
```
如果正常输出版本号（如 `2.5.x`），安装成功。
---
## 1. PyMOL 基础：打开 V138R vs WT
在 PyMOL 命令行里逐行执行：
```pml
# 进入 PyMOL 素材目录（替换成你的实际项目路径）
cd ~/Igem2026drylab/experiments/docking-repro/analysis/pymol_top6
# 加载 WT receptor + ligand
load receptors/Gpr3_WT.pdb,       rec_wt
load ligands/Gpr3_WT_ascr18.pdb,  lig_wt_18
# 加载 mutant receptor + ligand
load receptors/Gpr3_V138R.pdb,    rec_mut
load ligands/Gpr3_V138R_ascr18.pdb, lig_mut_18
# 叠合：把 mutant receptor 对齐到 WT 坐标系
align rec_mut, rec_wt
# ⚠️ 关键步骤：把 align 的变换矩阵传给 ligand
matrix_copy rec_mut, lig_mut_18
# 应用样式
@style_detail.pml
```
> 📷 参考截图：见 `pymol_top6/README.md` 或找我要示例图
> **如果 ligand 飘在 receptor 外面** → 你忘了 `matrix_copy`。补上 `matrix_copy rec_mut, lig_mut_18` 后 ligand 会回到正确位置。这是最常见的新手错误，不是 pose 有问题。
验证：转到侧面视角，应该看到 ARG138 的长侧链伸向 ascr18 配体方向。
---
## 2. 第二个练习：M327A vs WT
同样的流程，换 Gpr2 M327A：
```pml
delete all
load receptors/Gpr2_WT.pdb,        rec_wt
load ligands/Gpr2_WT_ascr18.pdb,   lig_wt_18
load receptors/Gpr2_M327A.pdb,     rec_mut
load ligands/Gpr2_M327A_ascr18.pdb, lig_mut_18
align rec_mut, rec_wt
matrix_copy rec_mut, lig_mut_18
@style_detail.pml
```
这次你要看的是**丢失路径**：WT 的 Met327 有一条长疏水侧链，替换成 Ala 后侧链体积大幅缩小，口袋里多出一块空间。
练习目标：说出"WT 有什么接触、mutant 少了什么"——这就是 KNOW-1 §6 里"丢失路径"的可视化证据。
---
## 3. 渲染出图（选做）
如果需要高质量截图（PI 交付物或 wiki 用图）：
```pml
# 调整视角到合适角度后
ray 2400, 1800          # 渲染（需要等几秒）
png output/M327A_detail.png, dpi=300
```
出图规范：
- 分辨率 ≥ 2400 × 1800
- 每张图标注：受体名 / 突变名 / 配体名 / 关键残基 label
- WT 和 mutant 用不同颜色区分
- 截图同时包含：receptor surface（半透明）+ ligand stick + 关键残基 stick
完整资源目录和高级渲染技巧见 `pymol_top6/README.md`。
---
## 3b. 跑 IFP 分析（对接完 → 跑 IFP → 读热图）
对接完成后，IFP（Interaction Fingerprint）分析把 3D pose 翻译成"哪个残基和配体有什么类型的接触"。完整命令链分三步：

> **前置条件**：第 1 步只需要 DO-1 完成（WT 对接结果）。第 2 步需要 DO-2 **全部完成**（突变体对接结果 + pose 文件就位）。如果你还没跑完 DO-2，可以先跑第 1 步和第 3 步的 WT 部分。

### 第 1 步：WT IFP 分析
```bash
conda activate docking
cd ~/Igem2026drylab
python src/modeling/docking-repro/run_ifp_analysis.py
```
> 输入：`experiments/docking-repro/results/wt_singlestage/` 下的 pose PDBQT + 受体 PDB
> 输出：`experiments/docking-repro/results/ifp_analysis/ifp_all.csv`（每行 = 一个残基-配体接触）
> 参数：从 `config.yaml` 读取受体列表和配体列表
### 第 2 步：突变体 IFP 分析
```bash
python src/modeling/docking-repro/run_ifp_mutants.py
```
> 输入：`experiments/docking-repro/results/ifp_analysis_mutants/` 下的文件：
> - `receptors/{Rec}_{Label}_tm.pdb`（TM 截断后的突变体受体 PDB）
> - `poses/{Rec}_{Label}_{ligand}_poses.pdbqt`（突变体对接 pose）
>
> 输出（同目录）：
> - `mutant_contacts.csv`（全部突变体 × 配体 × 残基 × interaction 频率）
> - `mutant_vs_wt_diff.md`（相对 WT 的接触差异摘要）
>
> ⚠️ 如果 `ifp_analysis_mutants/` 下只有空的 `tmp/` 文件夹，说明输入数据还没就位。DO-2 的对接 pipeline 会将 pose 输出到 `mutagenesis/{Rec}/{Label}/docking/`，**不会**自动复制到这里。你需要手动准备：
> ```bash
> # 示例：准备 Gpr3 V138R 的输入（DO-2 全部完成后）
> mkdir -p experiments/docking-repro/results/ifp_analysis_mutants/{receptors,poses}
> # 1. 复制 TM 截断后的突变体 PDB
> cp experiments/docking-repro/mutagenesis/af3_structures/Gpr3/V138R_tm.pdb \
>    experiments/docking-repro/results/ifp_analysis_mutants/receptors/Gpr3_V138R_tm.pdb
> # 2. 复制对接 pose（每个配体一个）
> cp experiments/docking-repro/mutagenesis/Gpr3/V138R/docking/Gpr3_V138R_ascr18_poses.pdbqt \
>    experiments/docking-repro/results/ifp_analysis_mutants/poses/
> cp experiments/docking-repro/mutagenesis/Gpr3/V138R/docking/Gpr3_V138R_ascr3_poses.pdbqt \
>    experiments/docking-repro/results/ifp_analysis_mutants/poses/
> ```
> 命名规范：受体 PDB 为 `{Rec}_{Label}_tm.pdb`，pose 为 `{Rec}_{Label}_{ligand}_poses.pdbqt`。
### 第 3 步：绘制热图
```bash
python src/modeling/docking-repro/plot_ifp_heatmap.py
```
> 输入：第 1-2 步生成的 IFP CSV
> 输出：`experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png`（总览热图）
### 环境依赖
IFP 分析需要 **ProLIF** 库。如果你是用 `environments/mac-docking.yml` 创建的环境，ProLIF 已经包含在内。验证：
```bash
python -c "import prolif; print('prolif', prolif.__version__)"
```
### 验证结果
跑完后打开热图，交叉验证：在 Gpr3 V138R 的 mutant 热图上，ARG138 对 ascr18 应该有 **9 次**接触（全部为 VdWContact），对 ascr3 只有 **2 次**（与 KNOW-3 §1 数据一致）。
---
## 4. IFP 热图怎么读
打开热图总览：`experiments/docking-repro/analysis/ifp_heatmap_all_receptors.png`
热图结构：横轴 = 受体残基（按序列号），纵轴 = 配体（ascr18 / ascr3 / ascr7），色深 = 接触次数。
### 三步法
**第 1 步：找差异最大的残基**
对每个残基比较 ascr18 和 ascr3 的接触次数差值。差值大的残基是"选择性关键位点"的候选——它们解释了受体为什么能区分两个配体。
**第 2 步：定位 Hu2024 对照残基**
在热图上找 N60 / R395 / S44 / N56 的位置。三个真阳性（N60 / R395 / S44）应该在 ascr18 上有非零接触（说明它们确实是接触残基）。
**第 3 步：WT vs Mutant 前后对比**
每个 Top 6 候选都有 WT 和 mutant 两张热图。对比看"突变改变了哪些接触"。
**练习**：在 Gpr2 热图上找 M327，对比 ascr18 和 ascr3 的接触差值。然后看 M327A 的 mutant 热图——Ala 替换后 M327 位点的接触应该大幅减少或消失。
---
## 5. IFP 的关键警告
操作时记住两点：**接触频率 ≠ 结合贡献**（IFP 是提出假说的起点，不是 ΔΔG_sel 的等价替代），PDBQT 工作流下 ProLIF 的 **Anionic/Cationic 检测结构性失效**（输入无形式电荷，SMARTS 匹配永远为空——不是通道没开，是输入格式限制），因此盐桥几何不会被报告。这两点对理解 V138R 至关重要——完整展开见 **KNOW-3 §1-2**。
