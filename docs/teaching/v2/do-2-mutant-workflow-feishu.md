# DO-2：突变体全流程 — 从突变设想到 ΔΔG_sel
> **前置条件**：DO-1 完成 + KNOW-1 已读（理解 ΔΔG_sel 概念）
> **预计耗时**：1-2 小时（含 AF3 等待时间；AF3 约 5-30 分钟 + 本地对接 ~6 分钟）
> **运行环境**：Mac / WSL2 本地全程（不需要服务器）
> **学完能做**：从一个突变设想走到 ΔΔG_sel 数字，判断是否过 3σ 阈值

> ⚠️ **Caveat（2026-04-23）**：本课示例 **Gpr3 V138R** 及 `ratio_channel_report.md` 中的全部 Gpr 突变排名，均基于 2026-04-16 修复 grid box 胞内/胞外偏移前的 **污染数据**。Gpr2 重跑已于 2026-04-23 在 Win 节点启动；Gpr3 重跑策略尚在 Phase 2a 审查（pose 仍落在 TM 束边缘，需另议修复方案）。候选突变的 ΔΔG_sel 绝对值与相对排名在修复后会变动。**学员请以掌握 pipeline 操作流程为目标**，不以复现具体候选为目标；若要对照真实阳性突变，请等待重跑完成后刷新的报告。
---
本课用一个**已有结果的突变**（Gpr3 V138R）做验证性复走。这样你跑完之后可以对照已知结果，确认操作正确。独立做新突变的入口在 DO-4。
## 1. 选一个突变来做
打开双通道全谱排名看看已有的突变列表：
```bash
head -30 experiments/docking-repro/analysis/ratio_channel_report.md
```
这个表按 sel_mut 排序了 122 条突变。我们用 **Gpr3 V138R** 做练习——它是 Channel A #5，sel_mut = −0.875，强 ascr#18 偏好信号。选它的理由：信号强、已有 IFP 数据可以交叉验证。
---
## 2. 生成突变体 FASTA
```bash
conda activate docking
cd ~/Igem2026drylab                   # 回到项目根目录（WSL 用户路径相同）
python src/modeling/docking-repro/generate_mutant_fastas.py \
  --receptors Gpr3
```
这个脚本从 `config.yaml` 里读取 Gpr3 的 WT 序列和 `scan_residues`，对每个位点 × 每个替换残基生成一份 FASTA。
输出目录：
```
experiments/docking-repro/mutagenesis/fastas/Gpr3/
├── V138A.fasta           ← alanine scan（默认模式）
├── F170A.fasta
├── ...
└── saturation/           ← saturation scan（--scan-type saturation）
    ├── V138R.fasta       ← 我们要用的
    ├── V138D.fasta
    ├── ...（每个位点 × 18 种替换）
```
> **注意**：默认 `--scan-type alanine` 只生成 V138**A**（在 `Gpr3/` 下）。V138**R** 来自 saturation scan，在 `Gpr3/saturation/` 子目录下。教学练习直接用已有的 saturation 结果即可，不需要重新跑生成脚本。

打开 V138R.fasta 看一眼：
```bash
cat experiments/docking-repro/mutagenesis/fastas/Gpr3/saturation/V138R.fasta
```
你应该看到一条完整的蛋白质序列，和 WT 相比只有 **第 138 位从 V（Val）变成了 R（Arg）**。
---
## 3. 提交 AF3 Server
1. 浏览器打开 **alphafoldserver.com**（需要 Google 账号）
2. 点 **"New job"** → 选 **"Protein"**
3. 把 V138R.fasta 的序列**粘贴**到输入框（只粘贴序列，不粘贴 header 行）
4. Job name 填 `Gpr3_V138R`
5. 点 **"Submit"**
6. 等待 5-30 分钟（取决于服务器排队）
7. 下载结果 zip，解压后放到对应目录：
```bash
mkdir -p experiments/docking-repro/mutagenesis/af3_downloads/Gpr3_V138R
```
把解压后的文件放到：
```
experiments/docking-repro/mutagenesis/af3_downloads/Gpr3_V138R/
```
zip 里有 5 个 model（ranked_0 到 ranked_4），每个带 pLDDT 和 PAE 数据。
---
## 4. 处理 AF3 结果
**第 1 步**：选最优 model。
```bash
python src/modeling/docking-repro/process_af3_structures.py
```
这个脚本读取每个 job 的 5 个 model 的 `ranking_score`，选分数最高的那个，复制到 `af3_structures/` 目录。
> 输入：`af3_downloads/Gpr3_V138R/` 下的 5 个 model CIF 文件
> 处理：比较 5 个 model 的 ranking_score，选最高分
> 输出：`experiments/docking-repro/mutagenesis/af3_structures/Gpr3/V138R.cif`
**第 2 步**：CIF → PDB 格式转换。
```bash
python src/modeling/docking-repro/cif_to_pdb.py
```
> 输入：`af3_structures/Gpr3/V138R.cif`
> 处理：mmCIF 格式转换为 PDB 格式（Vina 和 ADFR 需要 PDB/PDBQT 格式）
> 输出：`experiments/docking-repro/mutagenesis/af3_structures/Gpr3/V138R.pdb`
**第 3 步**：TM 域截断。
```bash
python src/modeling/docking-repro/extract_mutant_tm.py
```
> 输入：`af3_structures/Gpr3/V138R.pdb`（完整结构）
> 处理：按 `config.yaml` 中的 `tm_topology` 截断 ICL3 等非 TM 区域，只保留 TM 螺旋和结合腔附近区域（和 WT 用同样的截断规则）
> 输出：`experiments/docking-repro/mutagenesis/af3_structures/Gpr3/V138R_tm.pdb`

---

## 5. 准备 PDBQT（下载预制文件）

AF3 给出的 PDB 要转成 Vina 能读的 PDBQT 格式——加 Gasteiger 电荷、清理非标准残基。标准工具是 ADFR Suite 的 `prepare_receptor`，但它在 Mac 上装起来比较痛苦，通常只在 Linux/Windows 上跑。

本课直接下载已用 ADFR 处理好的 `V138R_tm.pdbqt`，你只需要了解 ADFR 做了什么，不需要自己跑。

### 5a. ADFR 在做什么（阅读即可，不用跑）

脚本：[src/modeling/docking-repro/run_adfr_mutants.py](../../../src/modeling/docking-repro/run_adfr_mutants.py)

关键调用（`prepare_one()` 函数，精简版）：

```python
cmd = [
    adfr_bin / "prepare_receptor",
    "-r", str(pdb_path),                  # 输入：AF3 输出的 PDB
    "-o", str(out_pdbqt),                 # 输出：Vina 可读的 PDBQT
    "-A", "hydrogens",                    # 按 pH 7.4 预测质子化状态 + 加氢
    "-U", "nphs_lps_waters_nonstdres",    # 清除非极性氢 / 孤对电子 / 水 / 非标准残基
]
```

两个关键选项的含义：

- `-A hydrogens`：决定带电侧链（Asp/Glu/His/Lys/Arg）的质子化状态。pH 7.4 下 Arg 带 +1，Asp 带 −1——这直接影响 Vina 打分里的静电项和盐桥识别
- `-U nphs_lps_waters_nonstdres`：Vina 打分函数只支持有限的原子类型，不支持的原子（比如水分子、糖链里的非标准残基）必须删掉，否则 Vina 会报错或打分偏差

Gasteiger 电荷由 ADFR 用经验公式自动分配，写入 PDBQT 每行第 10 列（不涉及量子化学计算，这是对接规模下的标准做法）。

### 5b. 下载预制 PDBQT

下载链接：`<老师在飞书文档里贴>`

下载后解压到项目目录：

```bash
# 先确保你在项目根目录
cd ~/Igem2026drylab                 # 或你的实际路径

# 创建目标目录并解压
mkdir -p experiments/docking-repro/mutagenesis/af3_prepared
unzip ~/Downloads/do2_prepared_pdbqt.zip \
    -d experiments/docking-repro/mutagenesis/af3_prepared/

# 验证文件到位
ls experiments/docking-repro/mutagenesis/af3_prepared/Gpr3/
```

预期输出：看到 `V138R_tm.pdbqt` 文件（~190 KB）。

---

## 6. 跑对接（Mac / WSL2 本地）

在项目根目录执行：

```bash
conda activate docking
cd ~/Igem2026drylab                 # 回到项目根目录

# 先确认 af3_prepared/Gpr3/ 里只有 V138R.pdbqt（否则会多跑其他突变）
ls experiments/docking-repro/mutagenesis/af3_prepared/Gpr3/
# 预期输出：V138R_tm.pdbqt（仅此一个；如有其他 .pdbqt，请先挪走或删除）

python src/modeling/docking-repro/run_mutagenesis_saturation.py \
    --vina-bin $(which vina) \
    --receptors Gpr3
```

几个参数的含义：

- `--vina-bin $(which vina)`：用 conda `docking` 环境里的 vina 可执行文件。`which vina` 会输出类似 `/opt/homebrew/Caskroom/miniforge/base/envs/docking/bin/vina`（Mac）或 `/home/<user>/miniconda3/envs/docking/bin/vina`（WSL2），`$(...)` 是 shell 的命令替换，把路径填回去
- `--receptors Gpr3`：只扫 Gpr3，不扫 Gpr2（否则 preflight 会报 `Gpr2/` 目录缺失）

> **耗时预估**：脚本会扫描 `af3_prepared/Gpr3/` 下所有 PDBQT × 2 配体（ascr18 + ascr3）。你只放了 V138R，所以是 2 次对接 × 3 分钟 ≈ **6 分钟**。

### 查看结果

作业跑完后，结果落在：

```text
experiments/docking-repro/mutagenesis/mutagenesis_results.json
experiments/docking-repro/mutagenesis/mutagenesis_report.md
```

快速看一眼：

```bash
cat experiments/docking-repro/mutagenesis/mutagenesis_report.md
```

你应该看到 `Gpr3 V138R` 一行，带 `ΔΔG(ascr18)` / `ΔΔG(ascr3)` / `ΔΔG_sel` 三列数字。

> **脚本在做什么**：自动读 `results/wt_singlestage/docking_results.json`（DO-1 §4 产出的 WT 基线），拿 V138R 的新 ΔG 减 WT 对应值得到 ΔΔG，最后 `ΔΔG(ascr18) − ΔΔG(ascr3) = ΔΔG_sel`。如果 DO-1 §4 没跑完整 3 × 3 矩阵，这一步会因缺 Gpr3 基线报错。
---
## 7. 手动计算 ΔΔG_sel（验证理解）
即使 pipeline 自动算了 ΔΔG_sel，你也要手动算一次来确认你理解了公式。
从结果 JSON 里找到 V138R 的三个 ΔG：
| 对接对 | ΔG |
|--------|-----|
| Gpr3_V138R × ascr18 | −6.14 |
| Gpr3_V138R × ascr3 | −5.31 |
从 DO-1 的 WT 结果里找到基线：
| 对接对 | ΔG |
|--------|-----|
| Gpr3_WT × ascr18 | −5.755 |
| Gpr3_WT × ascr3 | −6.006 |
手动计算：
```
ΔΔG(ascr18) = ΔG(V138R, ascr18) − ΔG(WT, ascr18) = −6.14 − (−5.755) = −0.385
ΔΔG(ascr3)  = ΔG(V138R, ascr3)  − ΔG(WT, ascr3)  = −5.31 − (−6.006) = +0.696
ΔΔG_sel = ΔΔG(ascr18) − ΔΔG(ascr3) = −0.385 − 0.696 = −1.081
```
> 注意：上面的 WT 基线用的是单次对接值（DO-1 的结果），pipeline 实际使用的可能是 5-seed 均值，所以你的手动计算结果和 pipeline 输出会有微小差异（在 seed 噪声范围内）。已知 pipeline 输出 ΔΔG_sel = −1.070。
**判断**：|ΔΔG_sel| = 1.070 >> 0.477（3σ 阈值）→ **Channel A 候选，强 ascr#18 偏好信号**。
---
## 8. 这个流程的要点
你刚走完了"从一个突变设想到 ΔΔG_sel 数字"的完整链路。几个关键控制：
1. **参数一致性**：box / spacing / exh / seed 全部和 WT 一致（config.yaml 管控），这是 ΔΔG_sel 有意义的前提
2. **AF3 给的是静态结构**：它不能预测动态构象变化。V138R 的 Arg 侧链在 ns 级时间尺度上怎么摆动、盐桥是否真的形成——这些问题属于 MD（Molecular Dynamics, 分子动力学建模）
3. **ΔΔG_sel 过了 3σ 不等于"这个突变一定好"**：它只说明信号超出了搜索噪声。至于机制是否可靠、湿实验是否验证得了——需要更多证据层。为什么，读 **KNOW-2**

> **下一步**：对接完成后可以跑 IFP 分析来看突变改变了哪些残基-配体接触。操作流程见 **DO-3 §3b**。
