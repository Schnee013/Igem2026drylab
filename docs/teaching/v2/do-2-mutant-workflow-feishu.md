# DO-2：突变体全流程 — 从突变设想到 ΔΔG_sel
> **前置条件**：DO-1 完成 + KNOW-1 已读（理解 ΔΔG_sel 概念）
> **预计耗时**：3-4 小时（含 AF3 等待时间）
> **学完能做**：从一个突变设想走到 ΔΔG_sel 数字，判断是否过 3σ 阈值
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
cd ~/Igem2026drylab                   # 回到项目根目录，如果是Windows系统，根目录路径可能会不同
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
## 5. ADFR 准备 PDBQT
⚠️ **ADFR 在服务器端运行**（Mac 上不装 ADFR）。
有服务器访问权限后：
把 `V138R_tm.pdb` 同步到服务器，在服务器上运行：
```bash
python src/modeling/docking-repro/run_adfr_mutants.py \
  --project-root /path/to/drylab
```
输出：`experiments/docking-repro/mutagenesis/af3_prepared/Gpr3/V138R_tm.pdbqt`
---
## 6. 跑对接
突变体对接通过 mutagenesis runner 脚本执行，它会自动读取 WT 的 ΔG 基线来计算 ΔΔG_sel：
```bash
python src/modeling/docking-repro/run_mutagenesis_saturation.py \
  --receptors Gpr3
```
此命令会对 `af3_prepared/Gpr3/` 下**所有已有 PDBQT 的突变体**跑对接。如果目录下有多个 PDBQT，全部会被处理。想只跑 V138R，确保目录下只有它的 PDBQT。
每个突变体约 3 分钟 × 3 配体 = ~10 分钟。脚本会自动读取 WT 的 ΔG 基线来计算 ΔΔG_sel。
结果输出到：`experiments/docking-repro/mutagenesis/mutagenesis_results.json`
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
