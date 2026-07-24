# CHARMM-GUI Membrane Builder 操作指南

> 首次记录：2026-04-16（Gpr2_WT / Gpr3_WT 实测）
> 2026-04-18 更新：扩展至 Chimeric 多链体系（GPCR + Gα）

官网：[https://www.charmm-gui.org/?doc=input/membrane](https://www.charmm-gui.org/?doc=input/membrane)

---

## 踩坑 & 经验

- **关闭网络代理再提交**：实测开代理时任务提交成功率下降、延迟明显偏高；直连更稳定。

---

## 单链 GPCR 体系（突变体 MD 线）

**适用**：Gpr2/Gpr3 WT + 点突变体，单链蛋白 + 配体
**实测 Job 参考**：Gpr2_WT = 7628027774；Gpr3_WT = 7628627163

### 输入文件

- **来源**：PPM 2.0 对齐后的 clean PDB，已手动移除 DUM HETATM
- **位置**：`experiments/md-simulation/structures/` 下各体系目录（突变体不走 chimeric submit 流程）
- **前置步骤**：无 HSD 修复需求（单链体系 HSD 处理方式 → `docs/logs/2026-04-17.md` §Phase A）

### 输出文件与存档

- **存档路径**：`experiments/md-simulation/systems/{体系名}/gromacs/`
- **必须包含**：`topol.top` + `step5_input.gro` + `index.ndx` + `step6*.mdp` + `toppar/`
- **实测体系**：`systems/Gpr2_WT/gromacs/` + `systems/Gpr3_WT/gromacs/`（已完成）
- **后续衔接**：当前 mutant GPR input gate 与配体插入路线见 `codex/docs/plans/mutant-gpr-md-input-gate-plan-20260705.md`

### STEP 1 — PDB Reader

1. 进入 Membrane Builder → Bilayer Builder
2. 上传 PPM 对齐后的 clean PDB（已移除 DUM atoms）
3. "Membrane Only System" — **不勾**
4. "Check pKa" — **不勾**（用默认质子化态）
5. Chain Selection — 默认全选 → Next Step

### STEP 2 — Orientation

1. **"Use PDB Orientation"** — 选上（PPM 已对齐，不重新定向）
2. 其他保持默认 → Next Step

### STEP 3 — System Size

1. Heterogeneous Lipid → **Rectangular** box（默认）
2. Water thickness: **22.5 Å**（默认）
3. Length of X and Y: **90 Å**（Gpr2/Gpr3；GprC 需 ≥ 130 Å）
4. Lipid：PC → **POPC**，Upper + Lower 各填 **1**（手动）
5. 点 "Show the system info"：确认 ~100 POPC/叶，无 "system is smaller than protein extent" 警告
6. → Next Step

### STEP 4 — Build Components

1. Building method: **Replacement method**（默认）
2. "Check lipid ring penetration" — **勾上**（默认）
3. Include Ions — **勾上**；Ion Type: **KCl**；Concentration: **0.15**；Neutralizing: **勾上**
4. Ion Placing Method: **Distance**（默认）
5. → Next Step，等 packing 完成，确认 "No penetration found"

### STEP 5 — Assembly

1. 等 5–15 分钟，刷新至显示体系信息
2. 检查总原子数（~130k 量级合理）
3. → Next Step

### STEP 6 — Generate Inputs

1. Force Field: **CHARMM36m**（默认）；WYF / HMR / Multi-site Ca²⁺ — **全不勾**
2. Input Generation: **只勾 GROMACS**（手动勾，其他取消）
3. More CHARMM minimization — **不勾**
4. Equilibration：NPT ensemble 勾上；NVT / NPAT / NPgT 等全不勾；Temperature: **303.15 K**
5. Generate grid info for PME FFT automatically — **勾上**（默认）
6. → Generate → 下载 `download.tgz`

**存档**：`experiments/md-simulation/systems/{体系名}/gromacs/`

---

## 多链 GPCR-Gα 体系（Chimeric MD 线）

**适用**：Ch-1/Ch-2/Ch-4/Ch-ctrl（GPCR + Chimeric/WT Gα 双链）
**PPM 版本**：PPM 3.0（2026-04-18 起；突变体线用 PPM 2.0，混用理由 → `docs/logs/2026-04-18.md` §Session 3）

### 已完成体系（CHARMM-GUI Job ID + 规格）

| 体系 | Job ID | 原子数 | Box (Å) | POPC | 本地存档路径 | SLURM 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| Ch-ctrl（Ste2+Gpa1-WT） | 7649276832 | 263,906 | 120×120×192 | 389 | `systems/chimeric-ste2-gpa1-wt/gromacs/` | C-M4 ✅，Phase C4 Job 6688/6689/**6745**（rep3 2026-04-20 重提，见 [logs/2026-04-20.md](../logs/2026-04-20.md)） |
| Ch-1（Gpr3+AoGpa2-C37） | 7650133176 | 328,928 | 140×140×179 | 538 | `systems/chimeric-gpr3-aogpa2-c37/gromacs/` | C-M4 ✅，Phase C4 Job **6746/6747/6748**（2026-04-20 从 6691-6693 重提，见 [logs/2026-04-20.md](../logs/2026-04-20.md)） |
| Ch-2（Gpr3+AoGpa2-C15） | 7652252454 | 366,017 | 140×140×197 | 537 | `systems/chimeric-gpr3-aogpa2-c15/gromacs/` | Phase C3 Job 6694 PD |
| Ch-4（Gpr2+AoGpa2-C10） | 7652598711 | 370,926 | 140×140×200 | 537 | `systems/chimeric-gpr2-aogpa2-c10/gromacs/` | Phase C3 Job 6695 PD |

### 输入文件

- **上传文件**：`*_submit.pdb`（纯 ATOM，无 DUM HETATM，文件名无连字符）
- **位置**：`experiments/md-simulation/structures/chimeric/`
- **生成流程**：PPM 3.0 输出 `*_cleanout.pdb` → HSD HETATM 修复 → 提取 ATOM+TER+END → `*_submit.pdb`
  - 修复记录 → `docs/logs/2026-04-18.md` §Session 4（PPM 3.0 仍有 HSD HETATM 问题，修复代码同 PPM 2.0）
  - PPM 3.0 结果数据（ΔG / 倾角 / TM 数）→ 同上 §Session 4 表格

### 输出文件与存档

- **存档路径**：`experiments/md-simulation/systems/chimeric-{体系名}/gromacs/`
- **必须包含**：`topol.top` + `step5_input.gro` + `index.ndx` + `step6*.mdp` + `toppar/`
- **关键验证**：`index.ndx` 中须有 `SOLU_MEMB` 合并组；若缺失需 `gmx make_ndx` 手动合并
- **后续衔接**：历史 E2 C3 脚本与 gate 见 `codex/docs/plans/e2-chimeric-md-restart.md`；当前启动状态从 `docs/INDEX.md` 判断

### 链顺序与 PROA/PROB 对应

| 体系 | PROA（Chain A） | PROB（Chain B） | PPM N-ter 选项 |
| --- | --- | --- | --- |
| Ch-1/Ch-2/Ch-4 | GPCR（Gpr3/Gpr2） | 嵌合 Gα | OUT |
| Ch-ctrl | **Gpa1-WT** | **Ste2** | **IN**（链顺序反） |

### STEP 1 — PDB Reader

1. 进入 Membrane Builder → Bilayer Builder
2. 上传 `*_submit.pdb`
3. "Membrane Only System" — **不勾**
4. "Check pKa" — **不勾**
5. Terminal patching（PROA/PROB）— **默认 NTER/CTER，不改**
6. Disulfide bonds — 若 CHARMM-GUI 自动检出则确认（GPCR 常有 TM3-ECL2 二硫键），未弹出不主动填
7. 其余全部保持默认 → **Generate PDB and Orient Molecule**

### STEP 2 — Orientation

1. **"Use PDB Orientation"** — 选上（PPM 3.0 已对齐）
2. 其他保持默认 → Next Step

### STEP 3 — System Size

1. Heterogeneous Lipid → **Rectangular** box（默认）
2. Water thickness: **22.5 Å**（比 plan 写的 17.5 Å 保守值更安全，Gα 胞质侧延伸大）
3. Length of X and Y：**先填 120 Å**，点 Show the system info，若出现警告则递增至 130 → 140 Å；若 Step 4 报 "Protein size is larger than the bilayer size" hard error 也需增大
   - Chctrl（蛋白 X 跨度 60.02 Å）：120 Å 无警告 ✓
   - Ch-1（蛋白 X 跨度 69.23 Å）：120/130 Å 均有警告且 130 Å Step 4 hard error → **140 Å**
   - Ch-3 stretch（GprC，X 跨度 97.9 Å）：直接填 **140 Å**（保守估计）
4. Lipid：PC → **POPC**，Upper + Lower 各填 **1**（手动）
5. 点 "Show the system info"：确认无 protein extent 警告
   - Chctrl 实测：A=B=120.25 Å，C=192.84 Å，POPC 192/197，总原子数 263,906，水分子 65,687
6. → Next Step

### STEP 4 — Build Components

与单链相同：Replacement method + KCl 0.15 M + Neutralizing

### STEP 5 — Assembly

检查总原子数（~200–250k 量级合理）

### STEP 6 — Generate Inputs

与单链相同：CHARMM36m + 只勾 GROMACS + NPT + 303.15 K

**存档**：`experiments/md-simulation/systems/chimeric-{体系名}/gromacs/`

---

## 常见问题

| 问题 | 原因 | 解决 |
| --- | --- | --- |
| 上传报错 "character not allowed in filename: '-'" | 文件名含连字符 | 重命名去掉 `-`，使用 `*_submit.pdb` |
| "system is smaller than protein extent" | XY box 不够大 | 加大 XY 值重试 |
| HSD 残基缺失 | PPM 将 HSD 放入 HETATM | 提交前用脚本修复（`HETATM HSD → ATOM`）再生成 submit |
| Step 4 穿透检查失败 | 脂质插入碰撞 | 重新提交 Step 4，或加大 XY |
