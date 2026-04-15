# DO-1：环境配置 + 首次 WT 对接
> **前置条件**：DO-0 完成（VS Code + 终端 / WSL 已就绪）+ 网络 + 向我索取项目仓库访问权限
> **预计耗时**：1.5-2 小时（配置 30 min + 操作 1h）
> **学完能做**：在 Mac 上跑出 GprC × ascr18 的 ΔG 数字，看到 JSON 结果
---
## 1. 获取项目代码和数据
**第 0 步**：登陆 GitHub
**第 0.5 步**：首次认证（只需做一次）。
仓库是私有的，clone 之前必须让 Git 知道你是谁。最简单的方式是用 GitHub CLI。
**Mac**：
```bash
# 如果还没装 Homebrew，先装它（Mac 的包管理器）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 再安装 GitHub CLI
brew install gh
```
**WSL2（Windows）**：
```bash
sudo apt update && sudo apt install gh -y
```
安装完后，两个系统都一样登录：
```bash
gh auth login
```
遇到选项一路回车选默认值（HTTPS → GitHub.com → Login with a web browser）。
浏览器弹出页面点 **Authorize GitHub CLI**，终端显示 `Logged in as 你的用户名` 即成功。
> **只需做一次**：认证信息会保存在本地，以后 clone / pull 不再需要重复操作。
> **WSL2 注意**：如果浏览器没有自动弹出，把终端里显示的链接手动复制到 Windows 浏览器里打开即可。
**第 1 步**：克隆仓库（或向我索取）。
```bash
git clone https://github.com/Schnee013/Igem2026drylab.git
cd Igem2026drylab
```
**第 1.5 步**：拉取最新代码。
仓库代码会持续更新（修 bug、加功能）。**每次开始操作前**养成习惯先拉一次：
```bash
cd ~/Igem2026drylab
git pull
```
如果终端输出 `Already up to date.` 说明你已经是最新的。如果有更新，会显示变更的文件列表。
> **硬规矩**：每次打开终端准备跑 pipeline 之前，先 `git pull`。不拉最新代码就运行，遇到的 bug 可能早就修好了。

**第 2 步**：获取数据文件。
pipeline 运行需要的 PDBQT 文件（受体和配体的预处理结果）不在 Git 仓库里（二进制文件太大）。文件压缩包：`prepared_pdbqt.zip`
放到正确位置：
```
experiments/docking-repro/prepared/
├── receptors/
│   ├── GprC_A0A437AGY2_tm.pdbqt
│   ├── Gpr2_G1X9E2_tm.pdbqt
│   ├── Gpr3_G1XJN1_tm.pdbqt
│   ├── GprC_A0A437AGY2_tm.pdb      ← 质心计算用
│   ├── Gpr2_G1X9E2_tm.pdb
│   └── Gpr3_G1XJN1_tm.pdb
└── ligands/
    ├── ascr1_optimized.pdbqt
    ├── ascr18_optimized.pdbqt
    ├── ascr3_optimized.pdbqt
    └── ascr7_optimized.pdbqt
```
**第 3 步**：验证文件到位。
```bash
ls experiments/docking-repro/prepared/receptors/*.pdbqt | wc -l
ls experiments/docking-repro/prepared/ligands/*.pdbqt | wc -l
```
预期输出：
```
3
4
```
如果数量不对，检查文件是否放对了目录。

> **PDB 命名注意**：`receptors/` 下的 3 个 `.pdb` 文件（质心计算用）必须带 `_tm` 后缀。如果你解压出来的文件名是 `GprC_A0A437AGY2.pdb`（没有 `_tm`），需要手动重命名：
> ```bash
> cd experiments/docking-repro/prepared/receptors
> mv GprC_A0A437AGY2.pdb  GprC_A0A437AGY2_tm.pdb
> mv Gpr2_G1X9E2.pdb      Gpr2_G1X9E2_tm.pdb
> mv Gpr3_G1XJN1.pdb      Gpr3_G1XJN1_tm.pdb
> cd ~/Igem2026drylab
> ```
> PDBQT 文件不需要改名。
目录结构速览——你只需要知道三条路径：
| 路径 | 放什么 |
|------|--------|
| `src/modeling/docking-repro/` | 代码（`.py` 脚本 + `config.yaml`） |
| `experiments/docking-repro/prepared/` | PDBQT 输入文件（受体 + 配体） |
| `experiments/docking-repro/results/` | 对接输出（JSON + pose） |
---
## 2. 安装 Miniconda + 创建 docking 环境
如果你的 Mac 已经装过 Miniconda / Anaconda，跳到第 3 步。
**第 1 步**：下载并安装 Miniconda（Apple Silicon 版本）。
```bash
# 下载（在终端里执行）
curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
# 安装
bash Miniconda3-latest-MacOSX-arm64.sh
```
安装过程中一路回车 + yes。装完后**关闭终端再重新打开**，确保 conda 生效。
**第 2 步**：验证 conda 安装。
```bash
conda --version
```
预期输出（版本号可能不同）：
```
conda 24.x.x
```
**第 3 步**：用项目的环境定义文件创建 docking 环境。
```bash
cd ~/Igem2026drylab                           # 替换成你的实际项目路径
conda env create -f environments/mac-docking.yml
```
这会创建一个叫 `docking` 的环境，包含 Python 3.11 + 所有需要的库（Vina、RDKit、ProLIF、MDAnalysis 等）。首次创建需要 5-10 分钟。
**第 4 步**：激活环境并验证。
```bash
conda activate docking
python -c "import vina; print('vina OK')"
python -c "import prolif; print('prolif', prolif.__version__)"
```
预期输出：
```
vina OK
prolif 2.x.x
```
> **硬规矩**：以后每次打开终端跑 pipeline 脚本，第一件事是 `conda activate docking`。不要往 base 环境装包——环境一旦混了很难排查问题。
---
## 3. 跑一次 WT 对接：GprC × ascr18
```bash
# 确保在项目根目录 + docking 环境
conda activate docking
cd ~/Igem2026drylab                           # 回到项目根目录，如果是Windows系统，根目录路径可能会不同
# 跑 GprC × ascr18 单阶段对接
python src/modeling/docking-repro/run_wt_singlestage.py \
  --receptors GprC \
  --ligands ascr18
```
每个参数的含义：
- `--receptors GprC`：只对接 GprC 受体（不加则默认全部 3 个）
- `--ligands ascr18`：只对接 ascr18 配体（不加则默认全部 4 个）
运行过程中终端会打印日志，大约 **2-3 分钟**完成。
**查看结果**：
```bash
cat experiments/docking-repro/results/wt_singlestage/docking_results.json
```
你应该看到类似这样的输出（关注 `best_affinity`）：
```json
[
  {
    "pair_name": "GprC_ascr18",
    "receptor": "GprC_A0A437AGY2_tm",
    "ligand": "ascr18_optimized",
    "best_affinity": -8.235,
    "all_affinities": [-8.235, -7.817, -7.684, ...],
    "box_type": "singlestage",
    "exhaustiveness": 200,
    "spacing": 0.1,
    "elapsed_sec": 167.8
  }
]
```
**对照检查**：`best_affinity` 应该在 **-8.2 到 -8.3** 之间。
Hu2024 文献报告 GprC × ascr18 的 ΔG = −8.29 kcal/mol，我们的复现值 = −8.235。差值 0.055 kcal/mol，远小于 Vina 的 seed 噪声（SD ≈ 0.01，详见 KNOW-1）。
> **如果数值偏差超过 0.5 kcal/mol，排查**：
> 1. PDBQT 来源：是否用的 `experiments/docking-repro/prepared/` 下的文件？
> 2. Vina 版本：`python -c "import vina; print(vina.__version__)"` 应该是 1.2.x
> 3. 环境：是否在 `docking` 环境下运行？`which python` 应指向 conda 路径
---
## 4. 跑完整 WT 矩阵：3 受体 × 3 配体
```bash
python src/modeling/docking-repro/run_wt_singlestage.py \
  --receptors GprC Gpr2 Gpr3 \
  --ligands ascr18 ascr3 ascr7
```
这条命令跑 3 × 3 = 9 个对接对，每个 ~3 分钟，共约 **25-30 分钟**。
> ⚠️ **覆写警告**：每次运行会**完全覆写** `docking_results.json`，不会和之前的结果合并。所以要一次跑完所有想要的对接对，不要分批跑。
> 除非你已经会看代码了，那就自己改或者叫 AI 改好后检查。
跑完后检查结果：
```bash
python3 -c "
import json
with open('experiments/docking-repro/results/wt_singlestage/docking_results.json') as f:
    data = json.load(f)
for d in data:
    print(f\"{d['pair_name']:20s} ΔG = {d['best_affinity']:.3f} kcal/mol\")
"
```
预期输出（5-seed 均值参考，你的单次结果会略有波动）：
| 对接对 | 预期范围 | 5-seed 均值 |
|--------|---------|------------|
| GprC_ascr18 | −8.2 ~ −8.3 | −8.271 |
| GprC_ascr3 | −7.4 ~ −7.6 | −7.485 |
| GprC_ascr7 | −7.2 ~ −7.3 | −7.243 |
| Gpr2_ascr18 | −6.6 ~ −7.1 | −6.784 |
| Gpr2_ascr3 | −6.2 ~ −6.5 | −6.359 |
| Gpr2_ascr7 | −6.3 ~ −6.4 | −6.319 |
| Gpr3_ascr18 | −5.7 ~ −5.8 | −5.708 |
| Gpr3_ascr3 | −5.9 ~ −6.1 | −6.006 |
| Gpr3_ascr7 | −5.7 ~ −5.8 | −5.719 |
你刚跑出的 9 组数字，就是 Hu2024 / Kuo2024 文献里 WT 亲和力排名的计算复现。
---
## 5. 你刚才做了什么
你把一个蛋白质结构（PDBQT 格式）和一个小分子（也是 PDBQT 格式）丢给了一个叫 **Vina** 的对接打分程序。它在受体表面的一个 40 Å 的盒子里搜索配体可能的结合姿态，然后对每个姿态打分。输出的 `best_affinity = -8.235` 是打分最好的那个姿态的**近似结合自由能（ΔG）**，单位是 kcal/mol。
这个数字本身**不够用**——因为我们的工程目标不是"结合得紧不紧"，而是"突变后对 ascr18 的选择性变了多少"。为什么不够用、还需要什么额外指标（ΔΔG_sel），读 **KNOW-1**。
