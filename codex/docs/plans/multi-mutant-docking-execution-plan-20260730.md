# 双/多突变 docking 执行计划

> Status: `phase2_local_schema_test_ready_blocked_by_frame_repair`
>
> As of: `2026-07-30`
>
> Direction authority:
> [`docs/modeling/multi-mutant-docking/README.md`](../../../docs/modeling/multi-mutant-docking/README.md)
>
> Literature authority:
> [`literature-sources.md`](../../../docs/modeling/multi-mutant-docking/literature-sources.md)
>
> External-action gate: AF3 提交、远程 docking/MD、下载大体量结构或付费算力启动前，
> 必须重新展示当前事实、未知、成本、风险和推荐路线并取得确认。

## 0. 当前前置阻塞

本计划不能从旧 `ratio_spectrum.csv`、旧 IFP 或已撤回 shortlist 直接挑 AB。
当前 [P0 molecular docking](../../../docs/modeling/P0-molecular-docking.md) 已确认
mutant/WT coordinate-frame 缺陷；最新状态回该领域权威。2026-07-30 18-mode
审计确认旧 exact-20 validator 误判合法 Vina 输出，且 v4 遗漏显式 CPU8，不能
晋升为 production smoke。R1 已修正 maximum-20 和显式 CPU8 合同；seed 42 + 43
WT evidence 已冻结新 geometry gate，但 seed-44 独立 holdout 的 Gpr3/R167Y
两臂失败并 `fail_stop_before_full`。328-job 全量未启动。

进入双突变 Phase 1 前，单突变主线必须完成：

1. mutant→WT 七 TM Cα Kabsch 对齐；
2. 同一 PDBQT preparation 工具链和 provenance；
3. Gpr2/Gpr3 WT 与指定 smoke mutants 的双配体 smoke；
4. 膜方向、口袋位置、grid containment 和 pose geometry gate；
5. 162 mutants × 2 ligands + 4 WT baselines 的 328-job/6560-pose 全量重跑；
6. 从新 run-local ratio/IFP 重建并审计 active shortlist。

任一项未通过，本计划保持 `blocked`，只允许做本地 schema/test 准备，不生成或发布
双突变候选。

## 1. 目标与非目标

### 目标

- 从修复后的单突变 shortlist 冻结最多 4 个主双突变 cycle；
- 生成并验证 multi-mutation FASTA/genotype；
- 对 `WT / A / B / AB` 使用 matched-backbone 主比较；
- 用已对齐 WT frame 的独立 AF3 ensemble 做结构敏感性；
- 对 ASCR18/ASCR3 使用同 grid、matched seeds 和 Top 5 poses；
- 以 pose cluster、IFP、双突变周期和不确定性共同排名；
- 每个受体最多推进 1–2 个双突变到高成本验证讨论。

### 非目标

- 不做所有单突变的两两组合；
- 不进入三突变或更高阶组合；
- 不把单次最低 Vina score 当成最终 pose；
- 不把 Vina score 转写为 Kd、EC50、activation 或 sensor performance；
- 不把独立 AF3 models 当作 paired technical replicates；
- 不复用已撤回历史分析的 `±0.477 kcal/mol` threshold；
- 不在本计划落地时启动 AF3、远程 docking、MD 或湿实验。

## 2. 阶段总览

| Phase | 工作 | 主要输出 | 放行条件 |
|---|---|---|---|
| 0 | 等待/验证 frame repair 与新单突变 release | repaired single-mutant authority | active shortlist 重建完成 |
| 1 | 冻结候选 cycle | candidate cycles config | 每组有 WT/A/B/AB 和明确假说 |
| 2 | 升级多突变代码合同 | schema、生成器、tests | **本地完成**：focused tests 通过；不放行 Phase 1/3 |
| 3 | 生成两条结构路线 | matched-backbone + AF3 sensitivity | identity/frame/clash/confidence gate |
| 4 | 双配体多 conformer/multi-seed docking | Top 5 poses + long-form results | 运行完整、无 genotype 特例参数 |
| 5 | pose/IFP 与双突变周期 | clusters、IFP、`εsel_score`、CI | matched 样本完整且方向稳定 |
| 6 | 稳定性与 Pareto gate | ranked shortlist | 无单轴 cherry-pick |
| 7 | 有限 MD/湿实验验证设计 | 1–2 候选/受体 | 单独审批算力和实验资源 |
| 8 | versioned release 和状态更新 | manifest、报告、INDEX | 链接和证据边界校验通过 |

## 3. Phase 1 — 修复后候选 cycle 冻结

### 3.1 选择规则

从同一个 repaired release 中选择：

- 每个受体最多 2 个主 AB；
- 全项目最多 4 个主 AB；
- 另设最多 2 个 conditional exploratory AB；
- 优先组合不同机制：直接 pocket contact、第二壳层/构象位点、或有独立
  stability/expression 支持的补偿位点；
- 旧 R59C、R167Y 等身份不自动保留，必须重新通过 repaired release。

### 3.2 最小比较单元

每个 AB 定义一个完整 cycle：

```text
WT
A
B
AB
```

四臂必须共享 receptor、WT sequence authority、parent conformer、grid、ligand
preparation、Vina 参数和 seed list。

### 3.3 配置

执行时创建 `experiments/docking-repro/multi-mutant/configs/candidate_cycles.yaml`：

```yaml
cycle_id: GprX_AposB_CposD
receptor: GprX
source_release: <repaired_single_mutant_release_id>
channel_goal: A_or_B
mutations:
  A:
    - {position: <int>, wt: <AA>, mut: <AA>}
  B:
    - {position: <int>, wt: <AA>, mut: <AA>}
required_genotypes: [WT, A, B, AB]
ligands: [ascr18, ascr3]
status: preregistered
```

验收：

- 每个 A/B 都能回链到 repaired single-mutant row、pose cluster 和 IFP；
- 没有同位点冲突、通配 mutation、三突变或全组合生成器；
- 每组有机制假说和可证伪的失败解释。

## 4. Phase 2 — 多突变代码合同

> 2026-07-30 local checkpoint:
> [`multi_mutant.py`](../../../src/modeling/docking-repro/multi_mutant.py) 已实现
> canonical genotype、identity-checked FASTA、legacy single-mutation read
> adapter、完整 cycle validator 和 structured result join；
> [`test_docking_multi_mutant.py`](../../../tests/modeling/test_docking_multi_mutant.py)
> 的 14 项 synthetic focused tests 通过。目录合同和 placeholder template 见
> [`experiments/docking-repro/multi-mutant/README.md`](../../../experiments/docking-repro/multi-mutant/README.md)。
> 这只完成 Phase 2 本地准备，不解除 Phase 0、Phase 1 或工具链门禁。

### 4.1 Canonical genotype schema

```json
{
  "genotype_id": "GprX_A12V_C34D",
  "receptor": "GprX",
  "mutations": [
    {"position": 12, "wt": "A", "mut": "V"},
    {"position": 34, "wt": "C", "mut": "D"}
  ]
}
```

规则：

- mutations 按 residue number 排序；
- `genotype_id` 由排序后的 mutation list 确定；
- 验证 WT amino-acid identity；
- 拒绝重复 position、同位点冲突、越界和 noncanonical residue；
- 单突变旧 schema 继续可读，历史结果不重写；
- result 同时保存 `genotype_id` 和结构化 `mutations`。

### 4.2 需要改造/复核

- [`multi_mutant.py`](../../../src/modeling/docking-repro/multi_mutant.py)
- [`mutagenesis.py`](../../../src/modeling/docking-repro/mutagenesis.py)
- [`generate_mutant_fastas.py`](../../../src/modeling/docking-repro/generate_mutant_fastas.py)
- [`run_mutagenesis_saturation.py`](../../../src/modeling/docking-repro/run_mutagenesis_saturation.py)
- [`run_multiseed.py`](../../../src/modeling/docking-repro/run_multiseed.py)
- [`run_ifp_mutants.py`](../../../src/modeling/docking-repro/run_ifp_mutants.py)

双突变周期应新建独立分析模块，不把历史
[`ratio_channel_analysis.py`](../../../experiments/docking-repro/analysis/ratio_channel_analysis.py)
的阈值和分类逻辑直接扩写成混合口径。

### 4.3 Tests

新增 `tests/modeling/test_docking_multi_mutant.py`，覆盖：

- mutation 顺序规范化和稳定 genotype ID；
- WT identity 正确/错误；
- 重复位点、冲突位点、越界；
- FASTA 只修改指定 residue；
- 单突变 schema 向后兼容；
- WT/A/B/AB cycle 完整性；
- result join 不依赖脆弱的 label string 拆分；
- matched seed/conformer 缺失时拒绝计算周期。

Phase 2 本地验收已完成：14 项 multi-mutant focused tests 与 12 项 frame-repair
unittest 合并为 26/26 PASS；旧单突变 schema 的只读兼容由 focused test 覆盖。
真实 repaired docking smoke 已按完整性门失败并停止，因此不能据此放行 Phase 3。

## 5. Phase 3 — 输入冻结与结构生成

### 5.1 输入 manifest

冻结：

- repaired release ID、WT FASTA 和 residue numbering authority；
- WT receptor/chain/model 和七 TM alignment selection；
- ASCR18/ASCR3 identity、立体化学、质子化、charge 和 hash；
- receptor-specific、genotype-invariant grid；
- PDBQT/Vina/IFP 工具版本和参数；
- exhaustiveness、num_modes、energy_range、CPU 和 seeds；
- 所有输入 SHA-256。

若 FASTA、结构 residue identity、frame 或 grid 来源不一致，停止。

### 5.2 Route M：matched-backbone 主比较

1. 从同一 WT parent conformer 派生 WT、A、B、AB；
2. 使用相同 side-chain placement/local relaxation 合同；
3. 至少保留 3 个合格 parent conformers；
4. 保存 pre/post-relaxation 结构、日志、参数和 hash。

只有能保持四臂 parent mapping 的 conformer 才进入 paired cycle。

### 5.3 Route F：AF3 sensitivity

1. 为 WT、A、B、AB 生成并复核完整 FASTA；
2. 用户确认后分别提交 AF3；
3. 保存全部 models、confidence/ranking、输入 JSON/FASTA 和 checksum；
4. 每个 mutant 先用预冻结七 TM Cα 映射对齐 WT docking frame；
5. 对齐后再生成 PDBQT，并做膜方向、口袋、grid containment 和局部结构 gate。

不同 genotype 的 AF3 model rank 没有天然一一配对关系，不进入 Route M 的 paired
bootstrap。

## 6. Phase 4 — 双配体 docking

每个完整 cycle、每条合格结构路线至少包含：

```text
4 genotypes × 2 ligands × 3 receptor conformers × 5 Vina seeds
```

每次保存 Top 5 poses、stdout/stderr、config 和 receptor/ligand hash。若合格
conformer 少于 3 个，标记 coverage 不足，不重复同一 model 伪造样本数。

Long-form pose record 至少包含：

```text
cycle_id
genotype_id
mutations
ligand_id
structure_route
parent_conformer_id
receptor_conformer_id
alignment_transform_id
vina_seed
pose_rank
vina_score
pose_file
input_hashes
```

不得为某个 genotype 单独移动 grid 或调 exhaustiveness 后继续进入同一 paired
cycle。

## 7. Phase 5 — Pose/IFP 与双突变周期

### 7.1 Pose/IFP

1. 在同一 receptor/ligand/cycle 内聚类所有 Top 5 poses；
2. 标注预注册 pocket、膜侧和 grid containment；
3. 生成 IFP signature、关键残基接触和跨 seed recurrence；
4. 代表 pose 必须来自 recurring、pocket-consistent cluster；
5. 无共识 cluster 时标记 `inconclusive_pose`，不以最低 score 替代。

跨 5 seeds 的 recurrence 初始 operational rule 为至少 3 seeds 出现；先用 repaired
WT redocking/control 检查，并在查看 AB 结果前冻结或修订。

### 7.2 非加和 contrast

对 matched `(parent_conformer_id, vina_seed)`：

```text
S(g) = ΔG18(g) - ΔG3(g)
εsel_score = S(AB) - S(A) - S(B) + S(WT)
```

输出：

- 每个 genotype 的 `S(g)` 分布；
- `εsel_score` point estimate；
- paired bootstrap 95% CI；
- conformer-stratified 与 leave-one-conformer-out sensitivity；
- Channel A/B 方向一致性；
- pose cluster 和 IFP recurrence。

Route M 与 Route F 分开报告；只有 Route M 进入 paired bootstrap。

### 7.3 Noise floor

先用 repaired WT redocking、matched technical repeats 和置换/零对照建立 empirical
null，并在查看主候选 AB 排名前预注册。旧 `±0.477` 不进入本轮 go/no-go。

## 8. Phase 6 — 稳定性与 Pareto gate

每个 candidate 并列展示：

- target ligand score/cluster；
- off-target ligand score/cluster；
- `S(AB)` 和 `εsel_score`；
- pose/IFP recurrence；
- matched conformer/seed coverage；
- alignment/frame/geometry status；
- local clash、pocket geometry 和稳定性 triage；
- Route M/Route F 的 structure sensitivity。

若符号跨 conformer 翻转、CI 覆盖 null、pose 不收敛、target 绝对结合崩坏或
off-target 同步改善，结论为 `inconclusive`/不推进。

## 9. Phase 7 — 有限高成本验证

### MD

每个受体最多推进 1–2 个 AB。必须保留 WT/A/B/AB、同 ligand starting-pose
contract、同体系构建和独立重复。重点检查 pose/IFP persistence、pocket
hydration/contact network、mutation neighborhood stability 和 receptor global
motion。

远程构建、benchmark 和 production 需要新的 work order、资源 preflight 和用户
审批；本计划不授权启动。

### 湿实验

两个 ligand 同时测 expression、membrane localization、basal leak、dose-response、
EC50、Emax 和 Hill slope，并对 WT/A/B/AB 同批次比较。功能协同必须由四元实验
数据重新估计。

## 10. Phase 8 — 输出、验收与状态更新

执行时创建：

```text
experiments/docking-repro/multi-mutant/
├── README.md
├── configs/
├── inputs/
├── results/
├── analysis/
└── releases/<run_id>/
    ├── input_manifest.json
    ├── checksums.sha256
    ├── environment.tsv
    ├── config_snapshot/
    ├── docking_results_long.csv
    ├── pose_cluster_summary.csv
    ├── ifp_summary.csv
    ├── double_mutant_cycle_summary.csv
    ├── validation_report.md
    └── terminal_status.tsv
```

完成门：

- 所有相对链接、结果路径、DOI、genotype ID、hash 和 row count 可核对；
- 单/多突变 focused tests 通过；
- 每个 cycle 没有缺失臂；
- 报告区分 runtime facts、docking ranking、structure sensitivity 和 biological
  unknowns；
- 未出现 Kd/EC50/功能过度解释；
- 与 `docs/INDEX.md` 对照并按状态、优先级、阻塞项或入口变化更新。

## 11. Stop Conditions

满足任一项即停止扩展候选空间：

- frame repair 或 repaired single-mutant shortlist 未完成；
- 输入、PDBQT 或 alignment provenance 不可追溯；
- 单突变结果不能在冻结合同下复现；
- 主 cycles 的 pose/IFP 普遍不收敛；
- Route M 与 Route F 大面积方向相反；
- empirical null 无法区分候选差异；
- 用户未批准 AF3/远程计算/高成本验证；
- 需要进入三突变或全组合才能继续。
