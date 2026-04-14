# REF-C：Pipeline 代码目录 + 函数速查
> 想查"这个脚本在哪""这个函数做什么"时用这张表。不是教程，是查阅手册。
## 代码目录树
```
src/modeling/docking-repro/
│
├── config.yaml                  ← 全局配置（路径/参数/残基列表的单一权威源）
├── utils.py                     ← 配置加载、日志、路径拼接、结果持久化
│
│  ── 核心模块 ──
├── prepare_receptor.py          ← 受体准备：TM 域提取 → ADFR PDBQT
├── prepare_ligand.py            ← 配体准备：SMILES → Orca DFT → ADFR PDBQT
├── dock.py                      ← 对接引擎：单阶段对接 + 质心计算
├── mutagenesis.py               ← 突变扫描：alanine/saturation + ΔΔG_sel 评分
├── validate.py                  ← 验证：repro vs Hu2024 文献数值对标
│
│  ── Runner 脚本（执行入口）──
├── run_wt_singlestage.py        ← WT 单阶段对接（DO-1 用这个）
├── run_multiseed.py             ← 5-seed 方差评估
├── run_mutagenesis_alanine.py   ← Alanine scan runner
├── run_mutagenesis_saturation.py← 饱和扫描 runner
├── run_ifp_analysis.py          ← ProLIF IFP 分析
├── run_ifp_mutants.py           ← 突变体 IFP 对比分析
│
│  ── 突变体建模链（DO-2 流程）──
├── generate_mutant_fastas.py    ← 生成突变体 FASTA → 提交 AF3
├── process_af3_structures.py    ← 处理 AF3 下载：选最优 model
├── cif_to_pdb.py                ← mmCIF → PDB 批量转换
├── extract_mutant_tm.py         ← 批量提取突变体 TM 域
├── run_adfr_mutants.py          ← Windows 端批量 ADFR 准备
│
│  ── 辅助 ──
├── fix_ascr18.py                ← 修复 ascr18 PDBQT 截断 bug
├── plot_ifp_heatmap.py          ← IFP 热图
├── prep_pymol_top6.py           ← Top 6 PyMOL 素材导出
└── ...
```
记住三层就够了：**config.yaml** 管配置、**核心模块**（5 个）管逻辑、**runner 脚本**管执行。
## config.yaml 关键段
```yaml
paths:
  project_root: /Users/roy/Documents/drylab
  prepared_dir: experiments/docking-repro/prepared    # PDBQT 唯一来源
  results_dir: experiments/docking-repro/results
  mutagenesis_dir: experiments/docking-repro/mutagenesis
vina:
  seed: 42
  singlestage:
    box_size: 40.0        # Hu2024
    spacing: 0.1          # Hu2024
    exhaustiveness: 200   # Hu2024
```
所有路径和参数都从 config.yaml 读取，不硬编码。改路径只改一处。
## 关键函数速查
| 模块 | 函数 | 做什么 |
|------|------|--------|
| `prepare_receptor.py` | `extract_tm_domain_by_annotation()` | TM 域提取 + ICL3 截断 |
| `prepare_ligand.py` | `freeze_terminal_torsions()` | 冻结末端柔性键（ascr18 截断 bug 在这里）|
| `prepare_ligand.py` | `prepare_ligand_full()` | 配体 SMILES → PDBQT 全链路 |
| `dock.py` | `dock_pair_singlestage()` | 单阶段对接：读 PDBQT → 算质心 → 跑 Vina → 输出 JSON |
| `mutagenesis.py` | `run_mutagenesis()` | 突变扫描主循环 + ΔΔG_sel 评分 |
| `utils.py` | `save_results_json()` | 保存结果（latest + 时间戳副本）|
读代码的方法：先读 runner 看"它调用了核心模块的哪个函数"，再进核心模块看实现。
