# 两组各自母体与 pose 的 lid 候选生成

> Source: 用户授权、冻结输入、实际进程与候选坐标、独立检查结果。
> As of: 2026-10-06 凌晨；主采样于 10 月 5 日 23:56 +0800 前正常结束，后续有限精修和回收完成。
> Allowed use: 输入身份、局部建模结果与静态筛选；不代表结构最终验收、MD 就绪或机制成立。
> Update trigger: 候选验收、膜体系准备或输入选择改变。

**两组已各完成 24 次有限采样，现各保留一个经过有限精修、静态检查通过的待审候选。** 两组分别使用自己的全长母体及 ascr3 top1，没有使用旧混杂 rebuilt 坐标。两个主进程在本机并行、各限一个 CPU 线程，从启动到确认退出约 17 分钟。部分短程精修与主采样重叠，最多四个单线程本机进程；本轮未连接或启动 AutoDL/E2 计算。

完整六组表和“溯源”列见 [当前输入选择](../input-selection-20261005/README.md)，精确原始路径、MODE 1 来源与 SHA256 见 [provenance.json](../input-selection-20261005/provenance.json)。

本地保留两个交付候选、各自入选的首批候选、最终精修坐标、输入、源码和筛选表。其余候选坐标及原始采样/安装日志保存在 `nkuliulab-e2:/ifs1/User/dengwei/igem/backups/wiki-freeze-abc-20261010/`，目录沿用仓库相对路径；逐文件位置与校验值见该目录的 `MANIFEST.tsv`。下文运行记录及 `sha256_manifest.json` 是完整回收时的历史快照，复核全量历史文件时需连同 E2 归档读取。[归档入口](../../../../../docs/research/local-remote-sync-20261008/README.md)。

| 组合 | 首批尝试 | 几何及共价环检查通过 | 本轮待审候选 | 身份与坐标 | 当前状态 |
|---|---:|---:|---|---|---|
| V368R–ascr3 | 24 | 8 | candidate 12，精修第 3 轮 | 406 aa；lid 外重原子位移 0；自己的 SDF 字节不变 | 静态筛选通过，待结构与能量复核 |
| 独立 WT–ascr3 | 24 | 7 | candidate 24，精修第 3 轮 | 406 aa；lid 外重原子位移 0；自己的 SDF 字节不变 | 静态筛选通过，待结构与能量复核 |

候选文件名均包含各自组合和 `lid_rebuilt_own_pose_v1`：

- V368R：[受体 PDB](review_candidates/v368r_ascr3_lid_rebuilt_own_pose_v1/gpr2_twf154_v368r_ascr3_lid_rebuilt_own_pose_v1_receptor.pdb)、[本组 pose SDF](review_candidates/v368r_ascr3_lid_rebuilt_own_pose_v1/gpr2_twf154_v368r_ascr3_lid_rebuilt_own_pose_v1_ligand.sdf)、[身份与检查清单](review_candidates/v368r_ascr3_lid_rebuilt_own_pose_v1/candidate_manifest.json)。
- 独立 WT：[受体 PDB](review_candidates/native_wt_ascr3_lid_rebuilt_own_pose_v1/gpr2_twf154_native_wt_ascr3_lid_rebuilt_own_pose_v1_receptor.pdb)、[本组 pose SDF](review_candidates/native_wt_ascr3_lid_rebuilt_own_pose_v1/gpr2_twf154_native_wt_ascr3_lid_rebuilt_own_pose_v1_ligand.sdf)、[身份与检查清单](review_candidates/native_wt_ascr3_lid_rebuilt_own_pose_v1/candidate_manifest.json)。

文件放在 `review_candidates/`；输入合同的 `accepted_receptor_path` 与 `production_tpr_path` 仍为空。旧预热及原始版检查点不能接到新坐标上。

## 输入与方法

V368R 使用自己的 `af3_original/raw_model0.pdb`，按自己的 `alignment.json` 恢复 docking 坐标系；独立 WT 使用自己的 `full_length.pdb`，无需变换。父本、原样配体、配置和来源合同冻结在 `inputs/<case>/`。全部 48 个主批次候选均复核了全长序列、重原子身份和 lid 外坐标。

仅 164–178 可动，163/179 及其余受体重原子固定；保留假设的 Cys99–Cys173 二硫键。种子分别为 36831005、10053103；每组 24 次尝试，每次最多 2,000 次闭环尝试，均实际完成。沿用 GeneralizedKIC `peptide_first` 局部采样、侧链重排及带几何约束的 Cartesian 精修。

保留全部首批候选，先按成键、手性、接触与共价环检查筛选，再选择本批次 lid 最大 `rama_prepro` 项较低的候选精修。精修只动同一 lid，将本组原 pose 作为固定排斥障碍；主链构象项权重 3.0，三轮、每轮最多 1,000 次最小化迭代，交付第 3 轮。该排序不是亲和力排名，也没有证明找到全局最优或最小改动解。

| 静态量（最终导出坐标） | V368R–ascr3 | 独立 WT–ascr3 |
|---|---:|---:|
| lid 主链相对母体 RMSD，无额外拟合 | 10.157 Å | 10.907 Å |
| lid 外重原子最大位移 | 0.000 Å | 0.000 Å |
| lid 与配体最近重原子距离 | 3.843 Å | 6.158 Å |
| Cys99–Cys173 S–S 距离 | 2.030 Å | 2.029 Å |
| lid 最大 rama_prepro，初候选 → 精修 | 1.789 → 1.175 REU | 1.858 → 0.726 REU |
| 所检查共价环在 16 个投影下的 linking number | 均为 0 | 均为 0 |
| 开放 lid 两种人为补面的配体重原子键交点 | 0 / 0 | 0 / 0 |

这次明显改变了 lid 主链，是离散建模，不是配体物理穿出盖子的动力学路径。`rama_prepro` 是本环境的评分项，不是通用验收阈值。人为补面不是真实共价环；补面交点消失、有限环集 linking number 为 0，不能单独证明所有三维穿越问题均已解决。

尚未完成逐候选三维目视验收、同一 MD 力场能量检查或膜内最小化/平衡。下一步应先复核三维空间关系和局部能量，再以相同力场重新建立完整膜/水/离子体系、准备新 TPR。在六组比较中必须披露不同起点处理，不能把重构引起的差异全部解释为突变效应。

## 证据与失败尝试

- [逐候选简表](candidate_screening.tsv)：48 个候选的静态筛选、主链评分、序列与固定区检查。
- [待审候选汇总](review_candidates.json)：最终文件哈希、精修来源、完整检查及未完成事项。
- `runs/<case>/`：全部首批 PDB、候选 JSON、实际配置、环境、XML、程序快照和独立检查；`supplemental/` 保留精修与诊断尝试。
- [运行事件](run_state_events.tsv)、[主进程终态](live_status.json)、[启动及终态清单](launch_manifest.json)、`logs/`：两个主进程均退出码 0，24/24 为实际完成量。
- 新精修程序首次加载遇到 `BoundFunc` 命名空间差异，独立修正后重新运行；原历史采样程序未改，失败记录保留。
- 一次 WT `disulfide_first` 诊断在首个尝试遇到闭环 XML 指定二面角不在闭合链中的错误，已停止、未产生候选。此设置错误不能解释为该母体几何无解。
- WT candidate 2 的早期精修仍有主链评分较高的问题；完整首批的 candidate 24 更好，按同一流程精修后成为待审起点。早期结果保留在 `supplemental/refine_wt02/`。

本机隔离环境和中间文件在 `/private/tmp/gpr2-own-lid-20261005/`。Python 3.12.14、PyRosetta `2026.29+releasequarterly.80a0635615`（提交 `80a0635615099e1b918474a63acba7b1de6fd107`）、NumPy 2.5.3、RDKit 2026.3.6；锁定清单和官方下载校验在 `environment/`。这是本机建模环境，不是 AutoDL GROMACS 镜像；环境恢复耗时另计，不包含在约 17 分钟主采样中。轮子与缓存未写入仓库。

运行 JSON 保留当时临时绝对路径作为历史证据；对应实体已回收，见 [recovery_map.json](recovery_map.json)。回看结果不依赖临时目录；复跑需按回收输入位置重设路径。

方法参考：[GeneralizedKIC 二硫键教程](https://docs.rosettacommons.org/demos/latest/tutorials/GeneralizedKIC/generalized_kinematic_closure_4)、[PyRosetta 官方发行渠道](https://www.pyrosetta.org/downloads)。

所引：两个输入合同、原始 CIF/PDB/pose、溯源 JSON、实际采样与精修源码和检查结果。被引：当前输入选择、当前结果入口、INDEX、2026-10-05/06 日志。未启动完整生产、修改远端或提交/推送 Git。

回收完整性：[最终核验](validation.json)、[任务进程已结束](process_terminal_check.json)、[回收文件 SHA256 清单](sha256_manifest.json)。
