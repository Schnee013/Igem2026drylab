# DOCMAP: 项目文档管理规范

> 本文件是 drylab 项目的文档管理元规则，供项目成员和 AI 助手查阅。
> 改编自 [scientific-project-management-guide](archive/scientific-project-management-guide.md)（通用开源版），针对本项目定制。

---

## 1. 核心原则

### 单一权威源

每条信息只有一个权威位置，其他地方只放指针（`详见 xxx.md`），不复制内容。

**为什么**：6 个月的项目会产生数百个会话。如果同一信息出现在 3 处，到第 50 次会话时必然互相矛盾，AI 助手会按先读到的版本行动——可能是过期版本。

### 信息分层

不同信息的生命周期和加载频率不同：

| 生命周期 | 示例 | 存储位置 |
|---------|------|---------|
| 永久规则 | "代码改动后必须更新日志" | `AGENTS.md` / `CLAUDE.md` shim + `docs/DOCMAP.md` |
| 项目路由 | "哪些建模方向在进行，状态如何" | `INDEX.md` |
| 执行计划 | "下一 session 如何完成 docking 刷新" | `codex/docs/plans/` 项目内计划 |
| 跨会话状态 | "Pipeline X 正在 E2 tmux 会话中运行" | `codex/docs/memory/` 指针文件 |
| 当日叙事 | "今天发现 grid spacing 参数有误" | 当日日志 |
| 原始结果 | ΔG 数值、benchmark 分数 | 结果文件 (JSON/CSV) |

信息**向下流动**（规则 → 路由 → 状态 → 叙事 → 数据），不**向上流动**。日志可引用结果文件，结果文件不包含项目规则。

---

## 2. 五层持久化架构

```
┌──────────────────────────────────────────────────┐
│  Layer 1: Agent entry shims                        │
│  AGENTS.md / CLAUDE.md：仅放启动规则与指针            │
│  目标：各自 <50 行                                  │
└──────────────────────┬───────────────────────────┘
                       │ 指向
┌──────────────────────▼───────────────────────────┐
│  Layer 2: Agent skills / commands                  │
│  Codex global skills + Claude commands：工作流入口    │
│  只承载流程，不承载项目事实                           │
└──────────────────────┬───────────────────────────┘
                       │ 首先读取
┌──────────────────────▼───────────────────────────┐
│  Layer 3: INDEX.md（路由表）                       │
│  方向状态矩阵、阻塞项、最近 ≤5 条进展、活跃待办      │
└──────────────────────┬───────────────────────────┘
                       │ 路由到
┌──────────────────────▼───────────────────────────┐
│  Layer 4: 领域文档（按需加载）                      │
│  modeling/P*.md, decisions/, ops/, papers/         │
└──────────────────────┬───────────────────────────┘
                       │ 补充
┌──────────────────────▼───────────────────────────┐
│  Layer 5: Repo-scoped project memory                │
│  codex/docs/memory：索引、警示、handoff、流程纪律       │
│  目标：每个文件 10-20 行                            │
└──────────────────────────────────────────────────┘
```

### 各层该放与不该放

| 层 | 文件 | 该放 | 不该放 |
|----|------|------|--------|
| Agent 入口 | `AGENTS.md` / `CLAUDE.md` | 启动规则 + 指向权威文档的指针 | 可从其他文件推导的信息 |
| 工作流入口 | Codex skills / Claude commands | 可复用流程、命令别名、提交/审查纪律 | 项目事实、当前状态 |
| 路由表 | `INDEX.md` | 方向状态、阻塞项、最近 ≤5 条进展、活跃待办 | 已完成事项、详细结果数值 |
| 领域文档 | `modeling/`, `ops/` 等 | 各领域完整内容 | 跨领域的状态 |
| Project plans | `codex/docs/plans/` | 可跨工具使用的执行计划、next-session handoff、复杂工作分阶段方案 | 最终状态、原始结果、可由日志/领域文档承载的权威结论 |
| Project memory | `codex/docs/memory/` | docs/ 里没有的行为指导、警示、交接索引 | 已在 docs/ 有权威版本的信息 |
| 日志 | `docs/logs/YYYY-MM-DD.md` | 当日叙事（做了什么、为什么、踩坑） | 跨天状态（→ INDEX.md 或 memory） |

---

## 3. 目录结构

```
drylab/
├── AGENTS.md                    # Codex/通用 agent 入口 shim
├── CLAUDE.md                    # Claude Code 兼容入口 shim
├── .codex/                      # Codex 项目模板和 hooks
├── .claude/                     # Claude Code 本地配置（git ignored）
│
├── docs/
│   ├── INDEX.md                 # 路由表 —— "灵魂文件"
│   ├── DOCMAP.md                # 本文件：文档元规则 + 项目文档规范
│   ├── prd/                     # 需求与策略层
│   │   ├── overview-v4.md       #   项目全貌（当前权威，2026-04-11 锁定酵母-STE2）
│   │   ├── dry-lab-strategy.md  #   干实验总策略、痛点调研、防治决策
│   │   ├── chassis-decision.md  #   底盘选择分析（含 §最终决策）
│   │   └── archive/
│   │       └── overview-v3.md   #   已归档（底盘待定阶段，2026-04-03 ~ 04-10）
│   ├── modeling/                # 每个研究方向一个文件
│   │   ├── P0-molecular-docking.md       #   分子对接（completed）
│   │   ├── P0-md-simulation.md           #   MD 模拟（learning，技术栈调研中）
│   │   ├── P0-md-tech-stack-research.md  #   MD 技术栈调研报告（软件/力场/膜构建）
│   │   ├── P0-signal-pathway-ode.md      #   STE2 通路 ODE（in_progress）
│   │   ├── P0-*.md / P3-chimeric-gprotein.md  #   嵌合 Gpa1（priority P0，文件名保留 P3 前缀）
│   │   ├── P1-*.md              #   增强叙事完整性
│   │   ├── P2-*.md              #   完成检测→预防闭环（biocontrol-lv 已 archived）
│   │   └── wet-lab-handoff-*.md #   面向湿实验团队的交接文档
│   ├── learning/
│   │   └── roadmap.md           #   学习路线图、硬件需求、工具环境
│   ├── teaching/                # 组内教学材料（docking 方向答辩准备）
│   │   ├── v2/                  #   当前版本（DO/KNOW 双轨 + REF 参考手册，飞书导入格式）
│   │   │   ├── README-feishu.md        #     学习者入口：开场信 + 阅读顺序
│   │   │   ├── do-0-dev-setup-feishu.md #    Day 0 开发环境搭建（VS Code/Copilot/WSL2）
│   │   │   ├── do-{1-4}-*-feishu.md    #     操作轨（逐命令可复制，GROMACS tutorial 风格）
│   │   │   ├── know-{1-4}-*-feishu.md  #     理解+答辩轨（从湿实验知识搭桥到干实验）
│   │   │   ├── ref-{a-d}-*-feishu.md   #     按需查阅手册（工具/坑/代码/SSH）
│   │   │   └── ref-e-foundations-feishu.md #  终端命令详解 + 硬件 101
│   │   ├── v1/                  #   已归档 v1（lesson-01~07 + appendix-A~F）
│   │   └── _instructor/         #   讲师内部文档（题库/红队/验收/节奏，不发布）
│   ├── decisions/               # 技术决策记录
│   │   └── NNN-title.md
│   ├── ops/                     # 操作规范（SSH、环境、工具链）
│   │   ├── nkuliulab-e2-cloud-server.md # 当前服务器入口；使用服务器前必须先读
│   │   ├── md-gromacs-operational-pitfalls.md # GROMACS/MD 服务器中立踩坑索引
│   │   └── archives/            # 历史服务器操作指南，不作为新任务入口
│   │       ├── ssh-windows-compute.md  # [已弃用] Windows SSH（历史存档）
│   │       ├── slurm-md-server.md      # [已归档] Slurm GPU 集群
│   │       ├── hbu-sge-cluster.md      # [已归档] HBU SGE 集群
│   │       └── sources/                # 原始外部来源，仅供追溯
│   ├── logs/                    # 每日工作日志
│   │   └── YYYY-MM-DD.md
│   ├── papers/                  # 文献（矩阵 + 按需加载的总结）
│   │   ├── README.md                      #   组员使用说明（多维表格 + 云文档 + AI 读文献）
│   │   ├── literature-matrix.md           #   本地权威矩阵（按 Tier 分层，稳定 ID）
│   │   ├── literature-quick-ref.csv       #   扁平化 CSV，用于导入飞书多维表格
│   │   ├── literature-review-feishu.md    #   详细总结汇编（贴入飞书云文档）
│   │   ├── p2-economic-benefit/           #   P2 早期检测经济模型文献/参数/数据源矩阵与外部 benchmark
│   │   ├── pdf/                           #   本地 PDF
│   │   └── summaries/                     #   按 {Author}{Year}-{Topic} 命名的单篇总结
│   └── archive/                 # 归档文件（原始 PRD、通用指南等）
│
├── codex/                       # Codex 迁移、项目记忆和 agent/tooling 资料
│   ├── docs/
│   │   ├── plans/               #   repo-owned execution plans（跨工具、脱离私有 assistant 路径）
│   │   └── memory/              #   repo-scoped project memory（索引/警示/交接，不作事实权威）
│   └── migration/               #   Claude→Codex 迁移来源快照和 provenance，不作运行时配置
│
├── src/modeling/                # 源代码（按研究方向）
│   ├── docking/                 # v2 docking pipeline
│   ├── docking-repro/           # Hu2024 精确复现 pipeline
│   └── economic/                # P2 早期检测经济效益 deterministic MVP 框架
├── tests/                       # 自动化验证测试
│   └── modeling/                # 各建模方向的公式、配置和 guardrail 测试
│
├── experiments/                 # 实验产出（按研究方向）
│   ├── economic/                # P2 经济模型配置、公开示例结果和后续 HP 校准结果
│   ├── docking/                 # v2 pipeline 产出
│   │   ├── receptors/           # 原始 PDB（共享，被 docking-repro 引用）
│   │   └── ligands/             # 原始 SDF（共享）
│   ├── chimeric-gpa1/           # 嵌合 Gpa1 设计（序列→比对→AF3→评分）
│   │   ├── README.md            #   偶联关系 + 序列清单 + 目录说明
│   │   ├── sequences/           #   源 Gα 序列 FASTA + MUSCLE 比对输入
│   │   ├── alignment/           #   MUSCLE + ClustalΩ 比对结果
│   │   ├── chimeras/            #   6 个嵌合候选 FASTA
│   │   ├── af3_predictions/     #   AF3 Server 结果
│   │   └── scoring/             #   iPAE/pLDDT 评分矩阵
│   ├── md-simulation/           # MD 模拟体系（Pre-registered 8 holo + 4 chimeric）
│   │   ├── README.md            #   体系清单 + 采样协议 + 判据（锁定文档）
│   │   ├── systems/             #   每个体系一个目录（CHARMM-GUI 输出 + GROMACS 输入）
│   │   │   ├── Gpr2_WT/         #     Gpr2 WT 蛋白+POPC 膜体系（Job 7628027774, 132k atoms）
│   │   │   │   └── gromacs/     #       GROMACS 输入文件（.gro/.top/.mdp/.ndx + toppar/）
│   │   │   ├── Gpr3_WT/         #     Gpr3 WT 蛋白+POPC 膜体系（Job 7628627163, ~139k atoms）
│   │   │   │   └── gromacs/     #       GROMACS 输入文件（同上结构）
│   │   │   ├── chimeric-ste2-gpa1-wt/     #     Ch-ctrl: Ste2+Gpa1-WT（Job 7649276832, 263,906 atoms, 120×120×192 Å, POPC 389）
│   │   │   │   └── gromacs/     #       GROMACS 输入文件（C-M3 ✅，Phase C4 运行中）
│   │   │   ├── chimeric-gpr3-aogpa2-c37/  #     Ch-1: Gpr3+AoGpa2-C37（Job 7650133176, 328,928 atoms, 140×140×179 Å, POPC 538）
│   │   │   │   └── gromacs/     #       GROMACS 输入文件（C-M3 ✅，Phase C4 运行中）
│   │   │   ├── chimeric-gpr3-aogpa2-c15/  #     Ch-2: Gpr3+AoGpa2-C15（Job 7652252454, 366,017 atoms, 140×140×197 Å, POPC 537）
│   │   │   │   └── gromacs/     #       GROMACS 输入文件（C-M3 Phase C3 待运行，Job 6694 PD）
│   │   │   └── chimeric-gpr2-aogpa2-c10/  #     Ch-4: Gpr2+AoGpa2-C10（Job 7652598711, 370,926 atoms, 140×140×200 Å, POPC 537）
│   │   │       └── gromacs/     #       GROMACS 输入文件（C-M3 Phase C3 待运行，Job 6695 PD）
│   │   ├── parameters/          #   配体参数化（CGenFF + penalty audit + GROMACS .itp）
│   │   │   ├── ascr18/          #     penalty_summary.md + charmm-gui-7628908749/（完整输出含 gromacs/ASC18.itp）
│   │   │   └── ascr3/           #     penalty_summary.md + charmm-gui-7628970666/（完整输出含 gromacs/ASC3.itp）
│   │   ├── structures/          #   受体结构（PPM 对齐后）
│   │   │   ├── ppm2/            #     PPM 2.0 输出 PDB（突变体 MD 线，膜对齐）
│   │   │   ├── chimeric/        #     PPM 3.0 对齐后 clean PDB（chimeric MD 线）
│   │   │   │   ├── *_clean.pdb  #       HIS→HSD 修复后的多链 PDB（AF3 输出）
│   │   │   │   └── *_cleanout.pdb  #    PPM 3.0 对齐后（含 Gα 嵌入信息）
│   │   │   └── pdb/             #     参考 PDB（7AD3 等，仅分析验证用）
│   │   ├── mdp/                 #   MDP 模板（eq + production，chimeric 线共用）
│   │   ├── slurm/               #   SLURM 脚本（deploy_chimeric.sh + run_*.sh）
│   │   ├── analysis/            #   跨体系分析脚本
│   │   └── scripts/             #   Pipeline 通用脚本
│   └── docking-repro/           # Hu2024 复现产出
│       ├── prepared/            # ADFR 准备的 PDBQT（单一来源）
│       ├── results/             # 对接结果 JSON
│       │   ├── wt_singlestage/  # WT 单阶段对接结果（权威 WT 基线）
│       │   ├── multiseed/       # 多 seed 方差评估统计
│       │   └── ifp_analysis/    # ProLIF IFP 分析中间文件（contact_frequency.json 等）
│       ├── slurm/               # Slurm sbatch 脚本 + 部署脚本
│       ├── logs/                # 运行日志
│       ├── analysis/            # 分析产出
│       │   ├── deeptmhmm/       # DeepTMHMM TM 拓扑预测（UniProt 交叉验证）
│       │   ├── lignetwork/      # ProLIF LigNetwork 2D 交互示意图（HTML，交互式）
│       │   ├── plip_3d/         # PLIP 3D 交互 viewer（3Dmol.js HTML）+ 文本报告
│       │   ├── pymol_top6/      # Top 6 突变体 PyMOL 素材（complex PDB + compare_top6.pml）
│       │   ├── ifp_heatmap_*.png  # IFP 热图（按受体 + 全量）
│       │   └── ratio_channel_report.md  # 双通道全谱排名（权威源）
│       └── mutagenesis/         # 突变体相关
│           ├── fastas/          # AF3 输入 FASTA（按受体分子目录）
│           │   ├── {Rec}/{Label}.fasta       # alanine scan 单突变
│           │   └── {Rec}/saturation/         # 饱和扫描（Channel A 核心位点 × 18 AA）
│           │   # AF3 batch JSON 格式（提交后已清理，需要时按此格式重新生成）：
│           │   # [{"name":"gpr2_m327c","modelSeeds":["645910426"],
│           │   #   "sequences":[{"proteinChain":{"sequence":"...","count":1,
│           │   #   "useStructureTemplate":true}}],
│           │   #   "dialect":"alphafoldserver","version":2}]
│           ├── af3_downloads/   # AF3 原始下载（5 model × confidence JSON，冷存储）
│           ├── af3_structures/  # 最优 model PDB/CIF + TM 截断版（_tm.pdb）
│           ├── af3_prepared/    # ADFR 生成的突变体 PDBQT（Windows 端）
│           ├── archive/         # 已作废/替换的结果和结构（MMFF-voided、旧 fasta JSON）
│           ├── mutagenesis_results.json          # pipeline 实时写入（每次跑覆盖）
│           ├── mutagenesis_results_{run_id}.json # 时间戳备份（pipeline 自动创建）
│           └── mutagenesis_results_all_YYYYMMDD.json  # 手动合并全量（权威源）
│
├── environments/                # conda 环境定义和锁定
│   ├── md-production-sites.md   #   MD production site matrix（E2 primary + Slurm validated secondary）
│   ├── e2-md-gromacs.md         #   E2 MD/GROMACS 生产与分析环境版本矩阵
│   ├── mac-docking.yml
│   ├── mac-docking.lock.yml
│   └── win-docking-repro.lock
│
└── scripts/                     # 环境配置脚本
```

---

## 4. 命名规范

### 文件名

| 类型 | 命名模式 | 示例 |
|------|---------|------|
| 建模方向文档 | `P{0-3}-{英文短名}.md` | `P0-molecular-docking.md` |
| 技术决策记录 | `{NNN}-{短标题}.md` | `002-hu2024-repro-pipeline.md` |
| 工作日志 | `YYYY-MM-DD.md` | `2026-04-07.md` |
| 文献总结 | `{Author}{Year}-{Topic}-summary.md` | `Hu2024-GprC-summary.md` |
| 运行日志 | `run_{脚本名}_{YYYYMMDD}_{HHMMSS}.log` | `run_multiseed_20260406_072954.log` |

### 运行日志强制规则

所有 runner 脚本必须调用 `generate_run_id()` 生成时间戳后缀，禁止使用固定名称。查进度时用通配符找最新文件，不猜文件名：

```powershell
$log = Get-ChildItem path\run_script_*.log | Sort LastWriteTime -Desc | Select -First 1
Get-Content $log.FullName -Tail 20
```

### 远程脚本部署

- Mac/repo `src/` 是唯一权威源；服务器工作目录只是部署目标。
- 新服务器部署统一先读 `docs/ops/nkuliulab-e2-cloud-server.md`，再同步到个人目录（当前项目目录约定为 `/ifs1/User/dengwei/igem/`）。
- 服务器端不得反向成为脚本权威源；需要修改 `.py`、配置或工作流时，先改 repo，再同步到服务器。
- Windows 7500F 的旧部署细节仅保留在 `docs/ops/archives/ssh-windows-compute.md`，只用于追溯历史文件。

### 方法变体（同方向多 Pipeline）

当同一建模方向存在多条方法线时：

- **代码**: `src/modeling/{方向}-{变体名}/`，如 `docking-repro/`
- **实验产出**: `experiments/{方向}-{变体名}/`
- **共享数据**: 原始输入文件（PDB/SDF）通过引用主线目录，不复制
- **独立配置**: 每条方法线有自己的 `config.yaml`，不跨线共享
- **文档**: 在对应方向文档中新增"方法变体"小节，列明各变体的路径、工具链、状态
- **目的标注**: 每个变体需注明存在理由（如"精确复现 Hu2024"），不只写工具差异

---

## 5. 计算环境管理

### Mac 端（代码开发 + 分析）

| 环境名 | 阶段 | 激活方式 | 定义文件 |
|--------|------|---------|---------|
| `docking` | 分子对接（当前阶段） | `conda activate docking` | `environments/mac-docking.yml` |

后续建模阶段（ODE 信号通路、嵌合 G 蛋白设计等）各自创建独立环境，届时补充本表。

Mac 端所有 docking 阶段脚本（含 FASTA 生成等辅助脚本）默认在 `docking` 环境下运行。

### 当前远程服务器

新服务器/远程计算任务默认使用 **NKULiulab E2 共享云服务器**。任何人或 AI 助手在登录服务器、上传数据、运行远程命令、配置远程 IDE、创建软件环境或启动长任务前，必须先阅读 `docs/ops/nkuliulab-e2-cloud-server.md`，并按其中的个人目录、资源上限、tmux、备份和凭据规则执行。例外：2026-05-30 起，本轮 chimeric MD 统一 rerun 允许旧 Slurm RTX 5090 作为 validated secondary candidate；该例外只由 `environments/md-production-sites.md` 和新的 `experiments/md-simulation/scripts/slurm_*` gate scripts 承载。

MD / GROMACS 任务在确认 E2 入口后，再读取 `docs/ops/md-gromacs-operational-pitfalls.md` 作为服务器中立的操作踩坑索引；该文件只保存可迁移 guardrails，不承载旧 Slurm 节点、SBATCH 脚本或旧路径作为当前执行入口。

Slurm、HBU SGE 和 Windows 7500F 指南均为历史归档，只能用于追溯旧结果、理解旧日志或访问仍滞留在旧节点上的历史文件；不得作为新任务的默认服务器入口。当前 chimeric rerun 的 Slurm 路线不得复用 archived Slurm 指南中的旧 production 脚本、旧路径或旧 GROMACS provenance。

---

## 6. 关键文件角色说明

### INDEX.md — 路由表

AI 判断下一步加载什么的唯一入口。如果 AI 仅凭 INDEX.md 就能回答用户问题，说明 INDEX.md 太详细了。

**老化规则**（每日工作结束时执行）：
- **最近进展**：只保留最近 5 条，超出删除（历史在日志和 git 中）
- **待办**：已完成的 `[x]` 项下次更新时移除
- **当前阶段**：每次更新进展时同步审视

### Project memory — 跨会话行为规则

位于 `codex/docs/memory/`。每个文件 10-20 行，存储行为指导、交接索引和警示，不复制 docs/ 的内容。如果信息在 docs/ 有完整版本，memory 只放指针。Codex native global memory 和 Claude 私有 memory 只能指向本 repo 的 project memory 与权威 docs，不承载 drylab 科学结论。

### 文献管理 — 三文件架构 + 稳定 ID

文献采用 **Author-Year 稳定 ID**（如 `Hu2024`、`Huang2023a/b`、`FanC2023`、`iGEM-BITChina2017`），废弃全局序号——插入新文献不再触发下游重编号，跨文档引用永不失效。

| 文件 | 角色 | 读者 |
|------|------|------|
| `literature-matrix.md` | 本地权威矩阵，按 Tier 分层 | AI 助手、dry lab |
| `literature-quick-ref.csv` | 扁平 CSV，导入飞书多维表格 | 组员（通过多维表格） |
| `literature-review-feishu.md` | 详细总结汇编，贴入飞书云文档 | 组员（通过云文档） |
| `summaries/{ID}-{Topic}-summary.md` | 单篇按需加载总结 | AI 助手 |

组员使用流程（多维表格新增、AI 读文献 prompt 模板、ID 命名规则）详见 **[papers/README.md](papers/README.md)**。

### 当日日志 — 跨会话粘合剂

日志（`docs/logs/YYYY-MM-DD.md`）捕获其他文件无法记录的内容：决策的叙事上下文。

**踩坑记录是知识**："踩坑"章节是日志中对后续会话最有价值的部分。记录根因而非仅记修复方法。

**日志 → 操作规范的晋升路径**：
```
Day 1: 遇到问题，记录在日志
Day 2: 遇到类似问题，再次记录
Day 3: 识别模式 → 提升为 docs/ops/ 操作规范
       → 添加到 memory 作为行为规则
       → 可选：创建 hook 自动提醒
```

---

## 7. 上下文窗口经济学

### 文献按需加载

```
绝不：批量读取 summaries/ 目录或直接读 PDF
总是：先查 literature-matrix.md → 只读取具体某篇 summary
限制：同时最多加载 2-3 篇总结
```

文献矩阵的一句话摘要足以回答多数问题，无需打开全文。

### 按需加载策略

```
会话启动 → AGENTS.md 或 CLAUDE.md → docs/DOCMAP.md → docs/INDEX.md
用户问方向 A → 加载 modeling/P0-direction-a.md
用户要用服务器/远程计算 → 先加载 ops/nkuliulab-e2-cloud-server.md；当前 chimeric MD 的 Slurm secondary 例外只走 environments/md-production-sites.md + 新 slurm_* gate scripts（旧 Slurm、HBU SGE、Windows 节点指南均已归档）
用户问文献 → 查矩阵 → 加载单篇 summary
```

---

## 8. 文档生命周期

### 创建

1. 新建模方向 → 创建 `modeling/P{N}-{name}.md`，填充 frontmatter + 标准章节
2. 新增到 `INDEX.md` 的方向状态表
3. 涉及重大技术选择 → 同时创建 `decisions/NNN-title.md`

### 迭代

- **不删除历史**: 方法路线变更时，在文档内注明变更原因，而非直接覆盖
- **重大方向调整**: 如底盘决策导致策略切换（A→B），保留旧策略作为"历史记录/备选"

### 归档

- 已放弃的建模方向：status 改为 `archived`，文件保留不删除
- 已完成的方向：status 改为 `completed`，在文档中标注最终产出

### 版本追踪

版本追踪依赖三层机制协同，不使用文档内版本记录表（会与 git 历史漂移）：

1. **日志**（`docs/logs/YYYY-MM-DD.md`）：记录每次改动的语义（做了什么、为什么）——版本信息的主力
2. **git commit**（`/commit` / `safe-commit` 工作流）：提供时间点快照和精确 diff。Codex Stop reminder 只做未提交提醒；Claude 旧 reminder 已本地停用

AI 署名已通过 `attribution` 配置在源头关闭。

### INDEX.md 更新规则

- 任何建模方向的 status 变化 → 同步更新 INDEX.md 状态表
- 新增或删除方向 → 同步更新 INDEX.md
- 每日工作结束 → 更新 INDEX.md 的"最近进展"区域

---

## 9. 交叉引用规则

### 文档间引用

使用 markdown 相对路径：
```markdown
详见 [底盘决策分析](prd/chassis-decision.md)
```

### 方向间依赖标注

每个建模方向文档底部须有"与其他方向的依赖关系"章节：
- **输出到**: 本方向产出被谁消费
- **依赖于**: 本方向需要谁的产出

### 代码-文档联动

- 建模方向文档中标明对应代码路径 `src/modeling/{方向}/`
- 建模方向文档中标明实验产出路径 `experiments/{方向}/`
- 代码或实验产出变更时，更新对应文档

---

## 10. 反模式

### 信息重复（头号敌人）

**症状**：同一 SSH 连接信息出现在 agent 入口文件、memory 文件和 ops 文档三处。

**修复**：指定一个权威源（ops 文档），其他地方只放一行指针。

### INDEX.md 变成百科全书

**症状**：INDEX.md 超过 150 行，包含详细结果表和已完成任务历史。

**修复**：INDEX.md 是路由表不是 wiki。执行老化规则：最多 5 条进展，不保留已完成任务，不放结果数值。

### Memory 文件膨胀

**症状**：某个 memory 文件超过 60 行，包含 docs/ops/ 中已有的代码示例。

**修复**：memory 存行为提醒（10-20 行）。如果信息在 docs/ 有完整版，memory 只放指针和行为摘要。

### 代码中硬编码路径

**症状**：脚本用 `Path("experiments/docking-repro/mutagenesis/af3_structures")` 而非从 `config.yaml` 读取。`mutagenesis_dir` 变更时，主 pipeline 跟随更新但辅助脚本静默指向旧路径。

**修复**：所有 `.py` 脚本的目录路径必须从 `config.yaml` 的 `paths` 节读取（通过 `load_config()` + `get_project_root()`），不在代码中硬编码 `experiments/` 下的任何路径。`config.yaml` 是路径的唯一权威源。

### 猜测文件名

**症状**：AI 尝试 `cat run_results.log`，实际文件是 `run_multiseed_20260406_072954.log`。

**修复**：始终用通配符 + 排序找最新文件。

### 会话启动过度加载

**症状**：agent 入口文件 + skills/commands + INDEX.md + 最新日志 + memory 文件消耗 40% 上下文窗口。

**修复**：`AGENTS.md` / `CLAUDE.md` 各自 < 50 行，skills/commands 只放流程，INDEX.md 只路由不解释，领域文档按需加载。

---

## 11. 文档 Frontmatter（建模方向文档必须包含）

```yaml
---
direction: P0-molecular-docking
status: not_started | learning | in_progress | blocked | completed | archived
priority: P0 | P1 | P2 | P3
chassis_dependent: false | true
last_updated: YYYY-MM-DD
---
```

---

## 12. 模板索引

| 模板 | 用途 | 说明 |
|------|------|------|
| 建模方向文档 | 每个研究方向 | 含 frontmatter + 标准章节结构 |
| 技术决策记录 | 重大技术选择 | 背景 → 选项 → 决定 → 后果 |
| 工作日志 | 每日记录 | 摘要 → 完成工作 → 踩坑 → 待完成 |

### 技术决策模板

```markdown
# 决策 NNN：[标题]

- **日期**: YYYY-MM-DD
- **状态**: 讨论中 | 已决定 | 已废弃
- **关联方向**: [链接到相关建模方向文档]

## 背景
为什么需要做这个决策？

## 选项
1. **方案 A**: — 优点 / 缺点
2. **方案 B**: — 优点 / 缺点

## 决定
选择方案 X，因为...

## 后果
这个决定意味着...
```

### 工作日志模板

```markdown
# YYYY-MM-DD 工作日志

## 摘要
一句话概括今天的核心进展。

---

## §N [工作标题]
- 做了什么
- 关键发现/结果
- 相关文件: `path/to/file`

## §N 踩坑记录（如有）
### 问题：[简述]
- **现象**: 发生了什么
- **根因**: 为什么发生
- **修复**: 怎么解决的
- **预防**: 如何避免再犯

## §N 待完成
- [ ] 任务描述
```
