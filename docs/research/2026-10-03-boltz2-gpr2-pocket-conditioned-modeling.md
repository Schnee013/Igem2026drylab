# Boltz-2 调研与使用说明：Gpr2、ascr18/ascr3 和 ECL2 口袋遮挡问题

> source：本 side chat 的用户问题；指定 Gpr2 输入审查；Boltz 官方论文、仓库、输入文档、实现代码及软件发布页；相关方法的一手资料。来源与逐项证据见文末。
> as_of：2026-10-03，Asia/Shanghai。在线文档和仓库 main 分支可能继续变化。
> allowed_use：方法选型、解释功能边界、准备后续小试；不能作为 Gpr2 已预测成功、选择性已证实、生产 MD 已获准换输入或已启动的依据。
> update_trigger：软件版本、输入格式、配体化学状态、口袋定义或用户授权改变；出现实际 Gpr2 试跑结果；引用的输入审查更新。
> 执行状态：本次只查询和编写本文件，没有安装 Boltz、下载模型权重、上传序列、提交云任务、运行 e2 预测或修改主线程的 MD 输入。

## Findings

**Boltz-2 在功能上满足“全长蛋白序列＋自定义小分子＋指定口袋，共同预测复合物”的需求，值得作为独立建模路线评估；它不能保证 ECL2 一定正确让开，也不能直接代替“固定现有 top1，只修复 lid”的局部建模。** 其输入可以包含 SMILES、口袋残基和接触距离；`force: true` 通过采样时的势能引导加强约束，输出仍须检查约束是否满足及结构是否合理。[S01][S02][S05][S07]

这次 side chat 的几个问题可归纳如下：

| 问题 | 核实后的回答 |
|---|---|
| 能同时输入受体和小分子吗？ | 能。蛋白提供氨基酸序列，小分子提供 SMILES 或 CCD 化学组分；不是给小分子提供“蛋白序列”。 |
| 会共同预测蛋白和配体吗？ | 会。模型生成复合物结构，受体构象与配体位置都可能变化。 |
| 能指定配体到结合口袋吗？ | 能用 `pocket` 指定口袋残基，用 `contact` 指定更具体的接触；它不是 Vina 的三维网格框。 |
| 能保证配体全部原子必须留在口袋中心吗？ | 标准接口不提供这种空间区域的绝对保证；约束的具体含义是距离条件，须逐个验证输出。 |
| 能保留全长 ECL2，同时避免现有 AF3 lid 构象挡路吗？ | 可以尝试共同预测新的相容构象；没有针对本 Gpr2 的成功证据，大构象变化也是论文明确列出的困难。 |
| 能保持目前 top1 pose 和其余蛋白逐原子不动，只改变 164–178 吗？ | 本次核实的标准 Boltz-2 接口不能视为这种局部、严格坐标保持的操作。 |
| 能直接证明 N84V 偏好 ascr18、V368R 偏好 ascr3 的机制吗？ | 不能。它提供候选结构及辅助亲和力预测，需要对照、物理检查与实验验证。 |
| AlphaFold Server 能替代吗？ | 当前官方服务器的配体输入受允许列表限制，不能直接提交任意 ascr SMILES；本地 AF3 可接受 SMILES，但公开标准接口没有同等的非共价口袋约束。 |

建议把 Boltz-2 定位为**受口袋先验引导的独立结构假说生成器**。若今后试用，先评估完整 ECL2 与目标口袋能否共同形成合理结构，再讨论是否值得进入独立的 MD 验证分支。此建议不改变主线程已确认的来源、排程或共同起始结构设计。

## Research Objective

- Decision/use: 判断 Boltz-2 是否适合 Gpr2 的口袋定向复合物建模，并提供可审查、可复现的后续使用说明。
- Target question: 自定义 ascr18/ascr3 与全长 Gpr2 能否共同预测，并把配体引导到核心口袋，使 ECL2 参与构象调整；这种结果能够支持什么科学结论？
- Source scope: 优先核对开发者文档和实现、原始研究论文；用本地输入审查核对本项目背景。额外检索原始评估论文，避免只依据产品宣传。
- Exclusions: 不执行预测，不评估 e2 当前资源，不替换主线程输入，不为现有 MD 生成新 pose，不把网页教程当作本体系的实测结果。
- Access date: 2026-10-03，Asia/Shanghai。

## 1. 本 side chat 的问题背景与结论演变

### 1.1 实际要解决的问题

现有思路是先预测 Gpr2 受体结构，再用 AutoDock Vina 生成配体 pose。用户提出：AF3 结构的 ECL2/lid 挡住核心口袋，因此 docking 使用了删除 N 端 1–21 和 ECL2 164–178 的受体；湿实验表达的却是保留这些区域的全长突变体。问题因此是**如何获得化学和几何合理的全长结合态候选**，而不只是“换一个 docking 打分器”。[L01][L02]

本项目的背景身份如下；此处记录既有决定，不重新授权执行：

| 项目 | 已有背景与边界 |
|---|---|
| 受体 | Gpr2 TWF154，406 aa；WT、N84V、V368R。 |
| 序列来源 | `/Users/roy/Documents/docking/inputs/receptors/fasta/Gpr2_TWF154_TGJ68930.1.fasta`；不用 drylab 旧菌株 FASTA。 |
| ECL2/lid | 全长编号 164–178，`LGYGYIGGWCWLTSD`。 |
| 配体 | ascr18、ascr3；每套体系放一种配体。 |
| 用户报告的 docking 趋势 | N84V 偏好 ascr18，V368R 偏好 ascr3；视为后续检验的假说。 |
| 完整比较矩阵 | 三种受体 × 两种配体，共六组；同配体内比较 mutant 与 WT，再判断改变是否具有配体差异。 |
| 主线程当前来源限制 | 结构及 pose 限指定 `md-handoff-n84v-v368r` 交接包；Boltz 重新预测得到的 pose 不在该来源授权内。 |
| 既有 MD 排程 | 优先 N84V–ascr18、V368R–ascr3 的 rep1，各先 100 ns，用户再决定续到 200 ns、补对照或补重复。 |

背景入口：[输入审查报告][L01]、[2026-10-03 决定记录][L02]。这里只引用已有审查，没有重新计算或覆盖其结果。

### 1.2 需要纠正的前提

用户最初将遮挡归因于“AF3 中 lid 置信度低”。但对这两份指定模型的已有审查显示，lid CA pLDDT 均值分别约 **88.45、85.24**，不能把它们笼统称为低置信度区域。与此同时，恢复 lid 后四个 top1 都存在严重重原子重叠，且涉及 lid 主链。[L01]

这两点可以同时成立：模型对局部形状较有信心，仍可能没有预测到本配体对应的结合状态。pLDDT 不是柔性测量，也不能证明 lid 在生理环境里必然打开。当前最可靠的表述是：**已有全长模型与指定 docking pose 不相容；是否存在可容纳该 pose 的完整 lid 构象，仍待验证。** 不应从“低置信度”或“预热后自然移开”直接推出解决方案。[L01]

审查还发现 Cys99–Cys173 的 SG 距离约 2 Å，符合二硫键几何，但这不是实验成键证明。任何候选都应核查该连接的化学依据，不能靠无说明地断键制造空间。[L01]

### 1.3 师兄所说的“Rosetta”可能指什么

目前没有软件全名，不能确定师兄具体指哪一个工具。至少应区分以下类别：

| 方法 | 典型输入与主要操作 | 与本问题的关系 |
|---|---|---|
| RosettaLigand / ROSIE ligand docking | 受体 PDB、配体化学结构及起始位置/搜索范围；结构采样与能量优化。 | 可以做指定区域 docking，但不是只输入序列的共同折叠神经网络。[S13] |
| RoseTTAFold All-Atom | 蛋白序列、小分子文件等；预测包含多种分子的全原子结构。 | 名称很可能与“Rosetta”混用，但是否支持所需的口袋约束须另查具体接口。[S14] |
| RoseTTAFold3（RF3） | Foundry 中的复合物预测模型，支持序列与 SMILES 等输入。 | 是另一类共同预测工具；本次看到的公开说明将进一步的 pairwise-contact API 列作扩展方向，不能直接承诺等同 Boltz 的约束接口。[S15] |
| DynamicBind | 已有蛋白结构与配体；用神经网络联合调整复合物构象。 | 原论文展示过环段调整以容纳配体；本次没有确认其标准接口能按本项目要求指定口袋。[S16] |
| Boltz-2 | 蛋白序列/MSA＋配体化学图，可加口袋、接触及模板条件。 | 已核实拥有最贴近本次问题的显式输入项，本文重点详述。[S02] |

因此，“共同预测”不等于“任意 Rosetta docking 软件都可从序列开始”；“可指定结合区域”也不等于“必然能解开 ECL2 遮挡”。

### 1.4 AlphaFold 3 与 AlphaFold Server 的边界

| 版本 | 自定义小分子 | 受体/配体共同预测 | 标准公开口袋约束 | 对本需求的判断 |
|---|---|---|---|---|
| 官方 AlphaFold Server | 只接受其允许的配体类型/CCD 列表；不能任意填 SMILES。 | 支持允许输入范围内的复合物。 | 未提供这里所需的非共价 pocket/contact 输入。 | 不能直接满足自定义 ascr18/ascr3＋指定口袋。[S10] |
| 本地 AF3 | 可输入 SMILES、CCD 或自定义 CCD。 | 支持。 | 本次核实的标准输入文档没有该功能；`bondedAtomPairs` 是共价连接，不是非共价 docking 约束。 | 满足自定义配体共同预测，不能据此承诺口袋定向。[S11] |
| AF3 论文中的口袋条件模型 | 论文研究过另外训练的 pocket-conditioned 版本。 | 支持相应研究设置。 | 不能把论文实验直接当成公开版本开关。 | 不应据此指导用户在官网填写不存在的字段。[S12] |

AlphaFold Server 上传 JSON 的入口不会绕过服务器允许的配体范围。之前若将“本地 AF3 接受 SMILES”表述为“官网可随便填 SMILES”，应以本节纠正。[S10][S11]

## 2. Boltz-2 是什么，以及本次核实的版本

Boltz-2 是蛋白、小分子等生物分子复合物的共同结构预测模型，也提供小分子–蛋白亲和力预测。模型将蛋白序列、进化信息、配体化学图及可选条件编码为相互作用表示，再用扩散去噪生成全原子坐标，并输出结构置信度；亲和力模块使用结构相关表示与预测坐标给出两个不同性质的读数。[S08][S09]

```text
蛋白序列 / MSA ─┐
配体 SMILES ────┼→ 复合物表示 → 扩散生成坐标 → 结构与置信度
口袋 / 模板 ────┘                    └────→ 可选亲和力预测
```

这是生成结构的算法流程，不是配体真实进入口袋的时间轨迹。即使使用与 MD 有关的训练信息或 method conditioning，也不能把样本顺序解释为打开 lid 的动力学过程。[S07][S08]

| 名称 | 本次核实结果 | 使用时的注意事项 |
|---|---|---|
| 开源模型名称 | `boltz2` | 下文的本地命令以此为准。 |
| PyPI 软件包 | `boltz==2.2.1`，发布日 2025-09-08 | 软件包版本 2.2.1 不等于存在名为“Boltz-2.2.1”的新模型。[S04] |
| Python | `>=3.10,<3.13` | 建议独立使用 3.11 或 3.12；不要直接复用其他任务的 Python 3.13 环境。[S03] |
| 授权 | 官方仓库声明代码和权重采用 MIT 许可 | 本地运行无需商业 API 账户；GPU、存储和 MSA 仍有实际成本。[S01] |
| 当前官方云服务 | 文档使用 `boltz-api` 与模型标识 `boltz-2.1` | 与开源 `boltz predict` 是不同接口，不能混用参数与版本名。[S17] |
| 本次代码阅读范围 | 查询日的 GitHub main 分支 | 未取得不可变 commit 快照，也未实装验证 wheel 与 main 逐项一致；正式执行应冻结安装版本、依赖与权重校验和。 |

**特别注意编号：开源 YAML 的口袋残基从 1 开始；当前云 API 的 `contact_residues` 文档从 0 开始。** 例如全长 residue 84，在本文开源 YAML 中填 84，而该云 API 中对应 83。这里只举编号换算，不建议把 84 当作应当强制接触的位点。[S06][S17]

云服务的费用、数据保留条款和可用配额未在本次核实；本文不推荐在尚未决定这些事项前上传项目序列。e2 方案应优先评估本地开源版，是否运行另行决定。

## 3. 口袋约束到底能做什么

### 3.1 `pocket`：指定结合区域的残基，而非三维方盒

开源输入中的 `binder: B` 选择配体链，`contacts` 列出受体链及残基编号。`max_distance` 的文档定义是：配体中某个原子与**每一个**被指定接触元素中某个原子的距离应在上限内；默认 6 Å，文档支持范围 4–20 Å。[S02]

对每个被指定残基 r，可以用下面的表达理解并核查距离条件：

```text
d(r) = min distance(atom in ligand B, atom in residue r)
要求逐个检查：d(r) <= max_distance
```

这不要求每个配体原子都靠近 r，也不要求整条配体都位于某个口袋体积内。长疏水尾部仍可能伸出口袋。所有指定残基均被施加条件，因此把整个大口袋的几十个残基全部填进去，可能形成相互冲突的要求。

**针对 Gpr2 的建议，尚未执行：** 根据已锁定坐标系的核心口袋，预先选少量具有空间辨识力、能同时围定结合区域的残基，再检查两个配体能否合理满足相同定义。数量、残基和距离阈值均需由几何与生物依据决定；不能因为研究 N84V/V368R 就自动把 84/368 设为必须接触的位点。

### 3.2 `force: false`、`force: true` 和 `--use_potentials`

| 设置 | 作用 | 不能据此推断 |
|---|---|---|
| 不写 pocket/contact | 未加入这类用户指定的距离条件。 | 不是不存在模型自身的结构先验。 |
| `force: false` | 把接触/口袋信息作为条件交给网络。 | 输出必定满足距离。 |
| `force: true` | 增加对应约束势能的采样引导。 | 数学上的绝对硬边界；每个输出都没有碰撞。 |
| `--use_potentials` | 开启改善物理合理性的额外引导与重采样。 | 可以代替 pocket 定义、完整力场制备或膜内平衡。 |

这两个“势能”开关不是同一个东西。已核实的 CLI 实现默认启用 contact guidance 路径，而 `--use_potentials` 另行控制 physical guidance 和重采样；不能写成“没有 `--use_potentials`，`force: true` 必定无效”。扩散实现通过有限步梯度更新施加引导，因此本文仍要求在输出上实测约束满足率。[S05][S07]

### 3.3 `contact` 与 `bond` 不可混用

`contact` 可规定两个 residue/token 的接近关系，也可使用经过核验的配体原子标识。它更适合有实验支持的具体接触。配体原子名不能照抄 PDBQT 后假设与 Boltz 从 SMILES 生成的名字一致，必须检查映射。[S02][S06]

`bond` 声明的是共价连接。它不能用于把 ascr 配体“拴在”本应非共价结合的口袋里。若核实受体有特定二硫键，可以研究相应的蛋白原子连接输入；但当前 C99–C173 的实验化学依据尚未确认，本文不把它写入可直接执行的默认输入。[S02][L01]

### 3.4 模板能提供参考，但不保证仅移动 lid

Boltz-2 支持蛋白 PDB/mmCIF 模板，可设置链映射；`force: true` 配合 `threshold` 可限制相对模板的主链偏离。[S02][S06]

本项目中要谨慎：如果把含“挡口袋 lid”的完整 AF3 模板强行约束得很紧，同时强迫配体进入核心，两个条件可能互相冲突。可研究的选项包括不提供模板、用软模板，以及经过验证后使用不覆盖冲突区域的模板信息；最后一种需要实际核查映射和支持范围，本文没有验证成品流程。

标准模板输入不等于“固定指定 top1 及 lid 外全部坐标”。即使结果看起来像原 AF3，也应对齐跨膜核心，量化核心、lid 和配体的实际变化。若要求逐原子保持现有种子，当前主线程的局部重建问题与 Boltz 的共同预测问题仍应分开处理。

## 4. 为 Gpr2 准备输入的方法

以下是后续操作说明，没有生成实际任务文件。

### 4.1 蛋白：全长序列和准确编号

从指定 docking 项目的 FASTA 获取 WT，确认长度 406、84=N、368=V、164–178 为指定 lid。分别只改变目标位点生成 N84V、V368R；所有输入保留 N 端和完整 ECL2，不把删段受体的 370 个残基当成全长序列。[L01]

拟运行前，应将原 FASTA、派生序列、突变位点检查结果和校验和一起归档。口袋编号按输入序列的 1-based 索引填写，不能沿用一个未知重编号 PDB 的数字。

### 4.2 配体：确认化学身份，不只复制名字

推荐从既有已审核 SDF 的化学图生成带立体信息的 SMILES，核对 ascr18/ascr3 的连接关系、双键构型、手性和形式电荷。现有审查记录 SDF 的总形式电荷为 -1，但后续 Boltz 和 MD 使用何种质子化状态仍须统一决定。[L01]

SDF/PDBQT 中的现有坐标与 SMILES 中的化学图是不同信息。**把 top1.sdf 转成 SMILES 输入 Boltz，只传递分子身份，不会把 top1 坐标固定下来。** 不应据此声称继续使用了相同起始 pose。[S02]

两个配体各作为一个 ligand chain 输入；本次所需的是单配体复合物，不是同时把 ascr18 和 ascr3 放在一个口袋里竞争。

### 4.3 MSA：三种受体可比，但 query 必须对应各自序列

可选以下路径：[S02][S05]

- 使用 `--use_msa_server` 自动获取 MSA。默认服务器是 `https://api.colabfold.com`，会向该服务提交待搜索的蛋白序列。
- 提供预先准备的 `.a3m`；适合冻结输入、离线复现及避免再次提交序列。
- `msa: empty` 进入单序列模式；官方不推荐把它作为默认高质量方案。

本项目若进行 WT/mutant 比较，建议尽量保持同源序列背景、比对列和采样策略一致；但每份 MSA 的 query 行必须匹配各自输入序列，不能给 N84V 原样使用 WT query。以上是一致性设计建议，不是本次已经生成或验证的 MSA。

### 4.4 YAML 模板：开源版本

下面是**待填内容的模板，不能原样提交**。`FULL_LENGTH_*`、SMILES 与 `K1/K2/K3` 都是占位符；K 值需替换为核实过的全长整数编号。示例只展示一个组合，其他组合分别建文件。

```yaml
version: 1
sequences:
  - protein:
      id: A
      sequence: FULL_LENGTH_GPR2_N84V_SEQUENCE
      # 若使用本地 MSA，取消下一行注释，并在命令中省略 --use_msa_server
      # msa: /absolute/path/to/N84V.a3m
  - ligand:
      id: B
      smiles: 'VERIFIED_ISOMERIC_SMILES_OF_ASCR18'

constraints:
  - pocket:
      binder: B
      contacts:
        - [A, K1]
        - [A, K2]
        - [A, K3]
      max_distance: 6.0
      force: true

# 仅在需要辅助亲和力预测时启用：
# properties:
#   - affinity:
#       binder: B
```

这里 6 Å 是官方默认示例，不是已经批准的 Gpr2 几何阈值。三条 contacts 只是格式展示，并不意味着本项目必须选三个残基。首轮不默认添加完整 AF3 强模板，以免把待解决的 lid 构象重新锁定。

## 5. 安装、资源与运行说明

### 5.1 环境与资源

建议后续在 e2 的独立环境中评估 Linux＋NVIDIA GPU 路线。官方支持 CPU 推理，但会很慢。本次未连接 e2 查询 GPU 型号、空闲显存、驱动、磁盘或网络，所以不能承诺某块卡足够或给出可靠运行时间。[S01][S05]

显存和耗时受蛋白/配体大小、MSA、模板、样本数、并行样本及物理引导影响。先用单输入、单样本记录显存峰值与耗时，再决定批量；多 GPU 不应直接理解为把一个结构任务均匀拆到所有卡上。官方 CLI 的多设备路径与输入记录数有关，需按实际安装版行为调度。[S05]

临时目录应与主线程隔离。本机如做将来的测试，可沿用用户偏好的 `/private/tmp/` 独立子目录；e2 应使用该机器已批准的临时/工作盘路径，不能假设 macOS 路径在 Linux 上存在。临时盘可能被清理，正式结果应有独立归档。

以下命令**仅供后续部署参考，本次没有执行**；须先将路径替换成目标机器上已批准的位置：

```bash
BOLTZ_WORK=/absolute/path/to/approved/scratch/boltz2-gpr2-RUN_ID
mkdir -p "$BOLTZ_WORK"/env "$BOLTZ_WORK"/cache "$BOLTZ_WORK"/tmp "$BOLTZ_WORK"/inputs "$BOLTZ_WORK"/outputs
export TMPDIR="$BOLTZ_WORK/tmp"
export PIP_CACHE_DIR="$BOLTZ_WORK/cache/pip"
export BOLTZ_CACHE="$BOLTZ_WORK/cache/boltz"
export HF_HOME="$BOLTZ_WORK/cache/huggingface"
export TORCH_HOME="$BOLTZ_WORK/cache/torch"

python3.11 -m venv "$BOLTZ_WORK/env"
"$BOLTZ_WORK/env/bin/python" -m pip install 'boltz[cuda]==2.2.1'
"$BOLTZ_WORK/env/bin/boltz" predict --help
"$BOLTZ_WORK/env/bin/python" -m pip freeze > "$BOLTZ_WORK/environment.txt"
```

安装版本取自本次核实的 PyPI 版本；CUDA、PyTorch 和优化内核能否与 e2 驱动兼容，仍需正式部署时检查。`--no_kernels` 是遇到相关内核兼容问题时可研究的退路，不保证解决所有环境问题。[S01][S03][S04][S05]

首次推理可能自动获取化学组分和模型文件。所读实现会检查并下载 `mols.tar`、结构权重 `boltz2_conf.ckpt` 和亲和力权重 `boltz2_aff.ckpt`；不能因为 YAML 未启用 affinity 就保证绝不下载亲和力权重。用独立 cache 保存，并核对下载完整性。[S05]

### 5.2 单样本可行性测试

先替换完模板并保存为 `N84V_ascr18.yaml`。如果选用在线 MSA，可参考：

```bash
"$BOLTZ_WORK/env/bin/boltz" predict "$BOLTZ_WORK/inputs/N84V_ascr18.yaml" \
  --model boltz2 \
  --out_dir "$BOLTZ_WORK/outputs/seed101" \
  --cache "$BOLTZ_CACHE" \
  --use_msa_server \
  --use_potentials \
  --seed 101 \
  --recycling_steps 3 \
  --sampling_steps 200 \
  --diffusion_samples 1 \
  --max_parallel_samples 1 \
  --devices 1 \
  --accelerator gpu \
  --write_full_pae
```

用本地 `.a3m` 时，填写 YAML 的 `msa` 并去掉 `--use_msa_server`。建议先不启用 affinity，便于判断结构输入、约束与环境是否可用；这只是省去该预测步骤，不是对权重下载的保证。

`--seed` 已在 CLI 源码中确认，虽然预测文档的参数表没有列出。具体 wheel 是否提供相同选项，以安装后的 `predict --help` 为准。随机种子有助复现，但 GPU、依赖版本及内核差异仍可能影响数值结果。[S05]

### 5.3 再增加样本，而不是把扩散步数当作 MD 时长

| 参数 | 含义 | 本项目后续建议，尚未执行 |
|---|---|---|
| `--recycling_steps` | 网络表示迭代次数。 | 先用默认 3，避免同时改很多变量。 |
| `--sampling_steps` | 生成一个结构时的去噪步数。 | 先用默认 200；不是 200 ps 或 ns。 |
| `--diffusion_samples` | 输出结构样本数。 | 单样本通路通过后，再考虑每 seed 5 个样本。 |
| `--max_parallel_samples` | 文档所述并行样本上限。 | 先设 1，并监测实际显存；不要把配置值当作资源保证。 |
| `--seed` | 随机数种子。 | 后续可用固定的 101、202、303 三组种子检查敏感性。 |
| `--use_potentials` | 改善物理合理性的采样引导。 | 成对比较时统一设置，记录额外耗时。 |
| `--write_full_pae` | 保存完整 PAE 矩阵。 | 建议保存，以便看 lid 与受体、配体的相对位置不确定性。 |

“三个 seed × 五个结构”只是建议的小规模敏感性检查，不是充分采样的保证，也不是 MD 的 rep1/2/3。改变输入、约束、版本或 seed 时用新输出目录，避免复用旧结果造成混淆；默认行为会跳过已有预测。[S02][S05]

## 6. 输出在哪里，如何读

源码实际会在 `--out_dir` 下再建立 `boltz_results_<输入文件名去后缀>`。以上示例的预测路径应按以下形式查找：[S05]

```text
outputs/seed101/
└── boltz_results_N84V_ascr18/
    └── predictions/
        └── N84V_ascr18/
            ├── N84V_ascr18_model_0.cif
            ├── confidence_N84V_ascr18_model_0.json
            ├── pae_N84V_ascr18_model_0.npz
            └── affinity_N84V_ascr18.json  # 仅启用 affinity 并成功完成后
```

该结构是依据源码和文档整理，未在本机实跑；还可能有预处理文件、日志和其他置信度文件。

### 6.1 结构置信度不等于结合强度

| 输出 | 可用于什么 | 本项目重点 |
|---|---|---|
| `confidence_score` | 按预测结构可信程度排序。 | 不等于结合能，也不是选择性分数。 |
| `complex_plddt`、局部 pLDDT | 评估局部结构置信度。 | 不能只看全链平均；单独看 lid 与口袋。 |
| `iptm`、`ligand_iptm`、链间指标 | 评估界面/链间布置可信程度。 | 高值仍不证明发生结合或激活受体。 |
| PAE | 查看不同部分相对位置的不确定性，距离量纲为 Å。 | 关注 lid–核心与配体–口袋区域。 |
| 多个结构样本 | 查看候选构象和位置的一致性。 | 对齐共同核心再比较；不能把出现次数直接当成热力学占比。 |

官方 confidence JSON 中多个汇总指标使用 0–1 的尺度；读取结构文件中具体字段时另核对其标度，避免和熟悉的 0–100 pLDDT 混用。[S02]

### 6.2 亲和力两个输出要分开读

启用 `properties: affinity` 后，主要有：[S01][S02][S08]

- `affinity_probability_binary`：模型区分 binder/decoy 的 0–1 分类输出。适合辅助筛选，不是实验浓度下的受体占有率，也不代表已经在 Gpr2 上校准的成功概率。
- `affinity_pred_value`：官方接口按以 µM 为单位的 `log10(IC50)` 风格解释，数值越小代表预测越强。但论文说明训练混合了 Ki、Kd、IC50 等读数，应当视为辅助排序的 IC50-like 输出，而不是特定实验的精确 IC50。

如果记输出为 y，形式换算为：

```text
IC50-like（µM）= 10^y
pIC50-like = 6 - y
```

例如 y=-1 对应 0.1 µM 和 pIC50-like=7。这只是输出尺度说明，不是本项目的预测结果。pIC50 无量纲，不能写成 kcal/mol。

**文档冲突：** 当前 `prediction.md` 的相关段落把 `(6-y)*1.364` 写作 pIC50/kcal/mol 转换，混淆了对数浓度和能量。本文不采用这一表述。不能把混合训练标签的 IC50-like 数值直接换算成可靠的结合自由能；实验 IC50 与 Kd 也不能在没有条件说明时等同。[S02][S08]

当前标准 affinity 只指定一个小分子 binder。文档上限为 RDKit `RemoveHs` 后计数不超过 128 个原子，并不推荐远大于训练上限 56 的配体；落在大小范围内也不表示对本受体/配体家族已验证。[S02]

论文还指出，口袋、界面或蛋白状态预测错误会影响下游亲和力；当前 affinity 模块不能充分显式处理离子、水或多聚伙伴等依赖。**对于本项目尤其关心的水介导网络、膜环境与受体激活，分数只能提供线索。**[S08]

## 7. 如何用它研究 ECL2，同时避免把答案预先写入条件

以下是可评审的建议方案，不是已决定的新任务。

### 7.1 先验证建模是否可行

先选择一个已明确化学身份的受体–配体组合，比较三个设置：

| 设置 | 目的 | 其余条件 |
|---|---|---|
| 不加 pocket | 看模型自身是否把配体放到目标口袋。 | 固定序列、配体、MSA、seed 方案和物理引导设置。 |
| 同一 pocket，`force: false` | 看口袋条件本身是否足以引导预测。 | 不额外指定预期突变相互作用。 |
| 同一 pocket，`force: true` | 看加强引导后能否形成合理的全长复合物。 | 核查距离满足率、局部形变和原子碰撞。 |

如果只有强引导下能够进入口袋，结论应是“在给定口袋先验下找到候选”，不能表述为模型独立发现了该结合位点。若为满足条件牺牲链连续性、手性或二硫键几何，则该输出不合格。

### 7.2 可行后再考虑六组对照

评价“突变是否改变配体偏好”需要 WT、N84V、V368R 分别配 ascr18/ascr3。只比 N84V–ascr18 与 V368R–ascr3，同时改变了受体和配体，不能归因于某个突变。[L01]

建议六组采用一致的口袋定义、化学规则、MSA 背景、模型版本和采样规模，不针对某个组合单独加强约束直到出现预期结果。口袋若必须按配体采用不同设置，应预先写清依据，并将约束差异作为解释限制。

不要强制 Arg368–羧酸接触后，再把该接触作为 V368R 新增盐桥的独立证据。也不要因 N84V 名称就要求 residue 84 直接抓住配体：现有种子审查没有支持这些应被预设的直接接触。[L01]

### 7.3 候选结构至少检查什么

1. **身份**：完整 406 aa，突变正确，lid 和 N 端保留；配体化学图、手性、电荷与输入一致。
2. **约束**：逐条实测 pocket/contact 距离，记录满足比例及违反幅度；不只看是否“视觉上在口袋里”。
3. **几何**：肽链连续性、局部键长键角、手性、二硫键假设、蛋白–配体及蛋白内部碰撞。不能只用全局 RMSD 通过验收。
4. **变化来源**：对齐共同跨膜核心，分别量化核心重排、lid 移动和配体 pose 变化；检查是否通过不合理扩大整个受体来满足约束。
5. **不确定性**：局部置信度、界面置信度、PAE、不同 seed 的结构簇；保留未入袋和不支持偏好的输出。
6. **后续解释**：在结构合格后提出可检验的接触/水合/构象假说，再决定是否值得建立膜体系验证。Boltz 结果本身不提供相互作用持续时间或真实开合速率。

没有一个通用置信度阈值可以单独证明本 Gpr2 结构正确；具体几何验收标准应在实际小试前固定，不能按是否符合 docking 预期事后放宽。

### 7.4 与主线程 MD 的关系

主线程选择的是“共同全长骨架＋同配体共享起始 pose”，且只允许指定交接包的结构来源。Boltz 可能同时改变骨架、lid 和配体姿势，因此其输出属于**新的候选来源和新的建模假说**。如果日后要纳入 MD，应先明确是独立验证分支、输入敏感性比较，还是重新设计共同起点；不能悄悄替换既有 top1。[L01][L02]

Boltz 不决定生产 MD 应为 100、200 或 300 ns。能否观察到 lid 重排、配体稳定性和选择性线索，仍依赖真实体系的采样与对照。当前 100 ns 的既有决定没有在此次调研中改变。

## 8. 性能宣传与实证的边界

开发论文报告 Boltz-2 在若干亲和力基准上接近 FEP 方法、推理显著更快；这应限定为论文的任务与评估条件，不能推导成“在 Gpr2 上与自由能计算同样准确”或“快一千倍就可替代 MD”。原论文自己明确承认较大结合诱导构象变化、错误界面及不同 assay 的泛化困难。[S08]

补充检索了两篇直接相关的原始研究，作为边界参考：

| 原始研究 | 本次阅读范围与结果 | 如何用于本项目 |
|---|---|---|
| Wan 等，2026，*On the Reliability of AI Methods in Drug Discovery* | 读取 arXiv 摘要；研究 3CLPro 和 TNKS2，报告与 ESMACS 结果相关性有限，部分高排名子集无显著相关。[S18] | 说明不能只相信宣传。ESMACS 本身也是计算结果，两个靶点的比较不能直接证明 Boltz 对所有体系失败。 |
| Thaler 等，2025，*Boltz-ABFE* | 读取 arXiv 摘要；把 Boltz 结构质量处理与另外的绝对自由能流程结合，在四个靶点展示可行性。[S19] | 支持“结构预测→质量处理→独立物理验证”的思路，不等于本项目已经具备可直接运行的 ABFE 流程。 |

这两条不是穷尽性文献评估，也未核实其最终同行评审状态；本文只按已读取摘要的范围引用，未从中提取未经核对的性能数字。

## Gaps and Conflicts

| 项目 | 已知 | 尚未确定 / 处理原则 |
|---|---|---|
| 师兄所指工具 | Rosetta、RoseTTAFold 与 Boltz 的算法和接口不同。 | 缺少软件全名或链接，不能指认具体工具。 |
| 口袋残基 | Boltz 支持 residue-defined pocket。 | 尚未为本项目冻结残基集合、编号映射、距离阈值；本文不编造。 |
| ECL2 状态 | 现有结构与 pose 冲突；这两份 lid 的 pLDDT 不低。 | Boltz 能否生成合格全长结合态，必须实测；动态柔性仍未知。 |
| 二硫键 | C99–C173 在既有预测中呈相容几何。 | 实验化学状态/拓扑依据待核验，不把几何近邻当作最终证明。 |
| 配体化学 | 已有 SDF 与 docking 坐标对应；审查记录 -1 形式电荷。 | 最终 SMILES、手性、质子化和原子映射须在实际输入制备中核对。 |
| e2 可运行性 | 有独立部署的技术路线。 | 本次没有查设备、网络与显存，不能给出可用算力或耗时承诺。 |
| PyPI 与 GitHub | 发布包 2.2.1；main 提供所述 CLI 和字段。 | 未逐文件验证同一性；未来冻结 wheel/commit、依赖和权重。 |
| 本地与云 API | 模型名、字段、编号约定不同。 | 本文命令不可直接复制给云 API，反之亦然。 |
| 文档与源码 | `--seed` 存在于源码；输出根多一层 `boltz_results_*`。 | 正式环境以实际 CLI 和生成文件为准；不能只看简化文档树。 |
| 亲和力单位 | 输出是 IC50-like 对数尺度。 | 文档的 pIC50/kcal/mol 表述有误；不据此计算本项目 ΔG。 |
| 选择性与机制 | 有 docking 偏好假说和对照设计。 | 没有 Boltz 实测、完整 MD 对照或相应湿实验结果，不能写“机制已验证”。 |

推荐的下一步是先审阅本报告并确定是否另开 Boltz 可行性分支；若选择运行，首先准备可核验的 SMILES 和 pocket 定义，再做单样本环境与几何测试。本文不把这个建议当作已批准的算力任务。

## Verified Source Ledger

所有在线访问日期为 2026-10-03。`main`/`production` 链接是可变来源；本报告记录访问日，未声称已封存不可变代码快照。

| ID | Source | URL | Authority | Access | Relevance | Status |
|---|---|---|---|---|---|---|
| S01 | Boltz 仓库 README | [官方仓库][S01] | 开发者 | 正文 | 模型定位、安装、授权 | 已使用 |
| S02 | Boltz prediction.md | [输入与预测文档][S02] | 开发者 | 正文 | YAML、距离、模板、输出 | 已使用；单位问题另列 |
| S03 | Boltz pyproject.toml | [包元数据][S03] | 开发者代码 | 源码 | Python 与依赖边界 | 已使用 |
| S04 | boltz on PyPI | [发布页][S04] | 官方包分发记录 | 页面 | 2.2.1 与发布日期 | 已使用 |
| S05 | Boltz main.py | [CLI 实现][S05] | 开发者代码 | 相关函数 | seed、缓存、目录、steering | 已使用；未执行 |
| S06 | Boltz schema.py | [输入解析][S06] | 开发者代码 | 相关函数 | 1-based、约束、模板映射 | 已使用；未执行 |
| S07 | Boltz diffusionv2.py | [扩散实现][S07] | 开发者代码 | sample 函数 | 梯度引导、非时间轨迹 | 已使用；未执行 |
| S08 | Passaro 等，Boltz-2 技术报告 | [PMC 正文][S08] | 原始研究作者 | 正文，重点 §3、§6 | 架构、训练标签、局限 | 已使用；原始预印本版本 |
| S09 | Boltz boltz2.py | [模型实现][S09] | 开发者代码 | 亲和力相关部分 | 结构与 affinity 模块关系 | 已使用；未执行 |
| S10 | AlphaFold Server JSON README | [服务器输入][S10] | Google DeepMind | 正文 | 允许的配体及服务器限制 | 已使用 |
| S11 | AlphaFold 3 input.md | [本地输入][S11] | Google DeepMind | 正文 | SMILES、自定义 CCD、公开字段 | 已使用 |
| S12 | Abramson 等，2024，AF3 论文 | [Nature 原文][S12] | 原始研究作者 | 相关段落 | 另训 pocket-conditioned 模型 | 已使用 |
| S13 | ROSIE ligand docking 文档 | [RosettaLigand 接口][S13] | Rosetta 官方服务 | 正文 | 结构输入与搜索位置 | 已使用；不代表所有 Rosetta protocol |
| S14 | RoseTTAFold All-Atom README | [RFAA 仓库][S14] | 开发者 | 输入说明 | 从序列等输入共同建模 | 已使用 |
| S15 | Foundry RF3 README | [RF3 文档][S15] | RosettaCommons | 输入与扩展说明 | 名称消歧、功能边界 | 已使用；接口可能更新 |
| S16 | Lu 等，DynamicBind | [Nature Communications 原文][S16] | 原始研究作者 | 方法与 Fig.4 相关说明 | 柔性受体/配体预测 | 已使用；指定口袋 API 未核实 |
| S17 | Boltz 云 API predictions guide | [官方 API 文档][S17] | 服务提供者 | 输入与约束正文 | 云/本地差异、0-based | 已使用；未调用服务 |
| S18 | Wan 等，2026，Boltz-2 可靠性评估 | [arXiv 摘要][S18] | 原始研究作者 | 摘要 | 跨靶点评估限制 | 部分阅读；仅支持摘要级表述 |
| S19 | Thaler 等，2025，Boltz-ABFE | [arXiv 摘要][S19] | 原始研究作者 | 摘要 | 结构预测结合物理验证 | 部分阅读；仅支持摘要级表述 |
| L01 | 指定 Gpr2 输入审查 | [本地报告][L01] | 本项目审查及指向的数据 | 本地读取 | 序列、碰撞、pLDDT、来源边界 | 已使用；未重算 |
| L02 | 2026-10-03 项目决定 | [本地日志][L02] | 用户决定的项目记录 | 本地读取 | 六组设计、100 ns、输入限制 | 已使用；不是本 side chat 的执行授权 |
| U01 | 本 side chat 用户问题 | 本对话，无公开 URL | 用户一手需求 | 对话原文 | Rosetta、共同预测、口袋、SMILES、报告请求 | 已使用 |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|---|---|---|---|---|---|
| 调研目标为自定义配体、全长受体、指定口袋 | U01 | side chat 连续提问及最终报告请求 | 用户将问题从 sequence-only 澄清为 ECL2 遮挡下的共同预测与口袋引导。 | high | 软件全名仍不明确。 |
| Boltz 是可本地运行的结构/亲和力模型，代码和权重 MIT | S01 | README：Installation、License | 有 pip 安装与两类输出说明。 | high | 授权不代表本机已安装。 |
| Python 范围 >=3.10,<3.13 | S03 | project.requires-python | 包元数据直接声明。 | high | CUDA/驱动兼容仍须实测。 |
| 查询到的发布包为 2.2.1，2025-09-08 | S04 | 版本页与 release history | PyPI 发布记录。 | high | 不能等同云模型版本。 |
| 配体可用自定义 SMILES，共同输入为 YAML | S02 | Sequences and molecules | ligand.smiles 与蛋白 sequence 同时输入。 | high | SMILES 不保留已有 pose 坐标。 |
| pocket 为逐接触元素距离，force 使用势能 | S02 | Constraints | 默认 6 Å，支持 4–20 Å，contacts 是链/残基或原子。 | high | 不是整个配体体积限制。 |
| 开源 pocket 残基编号为 1-based | S06 | token/constraint parsing；bond 的 r-1 转换 | 解析与文档的序列索引约定一致。 | high | 输入 PDB 编号仍须映射。 |
| 模板与共价 bond 是不同约束类型 | S06 | constraints、templates 解析 | 模板 force 需 threshold；bond 建立共价连接。 | high | 不能据此承诺固定 ligand pose。 |
| --seed 存在，输出根带 boltz_results_* | S05 | predict CLI；seed_everything；out_dir 构造 | 代码明确处理随机种子及输出根。 | high | 读取的是 main，不是本机安装版。 |
| contact guidance 与 use_potentials 不是同一开关 | S05 | BoltzSteeringParams；predict 的 steering_args | 默认 contact 开启，use_potentials 设置 physical 与 FK。 | high | 最终约束效果需运行后量测。 |
| force 通过有限步生成过程引导，需检查输出 | S07 | AtomDiffusion.sample | 使用条件势能梯度更新与采样。 | high | 这是实现解释，不是 Gpr2 成功率测量。 |
| 共同生成结构，不提供真实时间动力学 | S07 | 随机初始坐标与去噪 schedule | 样本从噪声生成；步骤是模型采样步骤。 | high | 不能把 sample 顺序当作 MD。 |
| affinity 与结构表示/坐标相关 | S09 | affinity_prediction 分支 | 亲和力使用结构输出相关输入，含模型集成。 | high | 集成不等于独立物理重复。 |
| affinity 训练标签混合 Ki、Kd、IC50 | S08 | §3 Affinity module | 作者将输出定位为可近似理解的 IC50-like 结合强度。 | high | 不可当作特定实验的精确数值。 |
| 大构象变化、错误口袋、cofactor 是限制 | S08 | §6 Limitations | 作者明确讨论结构与亲和力泛化困难。 | high | 未专门评估当前 Gpr2。 |
| pIC50/kcal/mol 表述不应直接采用 | S02 | Affinity 输出解释 | 文档给出的转换混合无量纲对数与能量单位。 | high | 本文作量纲核查，不产生替代 ΔG 估计。 |
| AlphaFold Server 不接受任意 SMILES | S10 | Entity types、Ligands | 配体为允许列表，JSON 与 UI 一致。 | high | 结论限定访问日服务器接口。 |
| 本地 AF3 支持 SMILES，但无标准 pocket 字段 | S11 | Ligands、完整输入格式 | 可自定义 ligand；共价 bondedAtomPairs 不等于非共价口袋。 | high | 不排除第三方修改版。 |
| AF3 论文另训口袋条件模型 | S12 | 蛋白–配体预测与 pocket-conditioned 讨论 | 论文实验不构成公开模型的同名功能开关。 | high | 不混入其他研究扩展版。 |
| RosettaLigand 常规输入是结构 | S13 | Input files、ligand placement | 需要 receptor PDB、ligand 与初始搜索位置。 | high | Rosetta 软件生态并不只有该服务。 |
| RFAA 支持多分子全原子共同预测 | S14 | Inference、protein/small molecule input | 受体序列与小分子输入可组合。 | high | 本文未验证其口袋约束实现。 |
| RF3 是另一共同预测工具，约束不能套用 | S15 | Input、future extensions | 文档有序列/SMILES，进一步 contact API 属扩展说明。 | medium | production 分支可变，后续需复查。 |
| DynamicBind 可调整蛋白构象 | S16 | Fig.4 与方法 | 原论文包含环段重排、配体复合物预测。 | high | 不证明本 Gpr2 可成功或有同等 pocket API。 |
| 云 API 与开源输入不同，pocket 0-based | S17 | Input format、Constraints | entities/contact_residues 与本地 sequences/contacts 不同。 | high | 未核实服务成本或执行结果。 |
| 独立评估提醒不能普遍等同 FEP 级准确性 | S18 | Abstract | 两靶点与 ESMACS 比较显示相关性限制。 | medium | 仅读摘要，比较对象也为计算方法。 |
| Boltz-ABFE 另接物理验证流程 | S19 | Abstract | 先处理预测结构质量，再做独立 ABFE。 | medium | 仅读摘要；未复现四靶点结果。 |
| 全长输入与 pose 冲突，但 lid pLDDT 不低 | L01 | 静态几何结果、输入身份 | 指定模型的距离和 pLDDT 已有审查记录。 | high | 本次引用既有数值，未重新计算。 |
| 固定 top1 的局部修复与 Boltz 共同预测不同 | L01 | 输入范围、lid 处理路线 | 当前来源与可动区域受到明确限制。 | high | 任何换输入需要另外的明确决定。 |
| 六组与先各 100 ns 是既有主线程决定 | L02 | 范围确认、排程与时长 | 用户确定当前优先组合和复审点。 | high | 不代表本次启动或续跑权限。 |

## Audit Notes

- 查询覆盖官方输入文档、发布元数据、实现代码和原始论文，未用聚合博客替代关键功能证据。
- Boltz-2 DOI 直达页首次访问返回 403，后通过 PMC 同一技术报告读取正文；因此不把首次失败误记为已读全文。两篇补充评估只按摘要引用。
- GitHub main、RF3 production 与云 API 都是动态页面；未声称获取不可变 commit、未安装验证。报告中的命令与 YAML 是准备模板，其中待填项明确保留。
- 没有实验或计算输出来自本次 side chat。本文没有给出虚构的 Gpr2 Boltz 分数、pose、耗时、显存或约束满足率。
- **References / 所引**：文末 S01–S19 为外部一手来源；L01 为本项目输入审查，L02 为既有决定记录；U01 为本 side chat 的用户问题。审查的原始数据权威仍是 L01 指向的 `audit.json` 与指定交接输入，本报告不复制成新的生产权威。
- **Referenced by / 被引**：本次未向其他项目文档增加引用；未来若选择 Boltz 分支，可由其独立试验计划引用本报告。其他线程或文件是否随后引用，未作穷尽搜索。
- 已对照 `docs/INDEX.md`：本报告没有改变主线程状态、优先级、阻塞项、既有输入范围或活动执行入口，故此次不修改 INDEX，也不改写正在进行的主线程日志。
- 本次仅新增本 Markdown，未修改其他已有工作文件。内容应作为选型资料阅读，不能单凭文件存在认定任何试跑完成。

[S01]: https://github.com/jwohlwend/boltz
[S02]: https://github.com/jwohlwend/boltz/blob/main/docs/prediction.md
[S03]: https://github.com/jwohlwend/boltz/blob/main/pyproject.toml
[S04]: https://pypi.org/project/boltz/2.2.1/
[S05]: https://github.com/jwohlwend/boltz/blob/main/src/boltz/main.py
[S06]: https://github.com/jwohlwend/boltz/blob/main/src/boltz/data/parse/schema.py
[S07]: https://github.com/jwohlwend/boltz/blob/main/src/boltz/model/modules/diffusionv2.py
[S08]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12262699/
[S09]: https://github.com/jwohlwend/boltz/blob/main/src/boltz/model/models/boltz2.py
[S10]: https://github.com/google-deepmind/alphafold/blob/main/server/README.md
[S11]: https://github.com/google-deepmind/alphafold3/blob/main/docs/input.md
[S12]: https://www.nature.com/articles/s41586-024-07487-w
[S13]: https://rosie.rosettacommons.org/ligand_docking/documentation
[S14]: https://github.com/baker-laboratory/RoseTTAFold-All-Atom
[S15]: https://github.com/RosettaCommons/foundry/blob/production/models/rf3/README.md
[S16]: https://www.nature.com/articles/s41467-024-45461-2
[S17]: https://api.boltz.bio/docs/api/guides/predictions/
[S18]: https://arxiv.org/abs/2603.05532
[S19]: https://arxiv.org/abs/2508.19385
[L01]: ../../experiments/md-simulation/results/gpr2-twf154-n84v-v368r/input-audit/20261003/README.md
[L02]: ../logs/2026-10-03.md
