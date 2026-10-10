# Gpr2 TWF154 六组 rep1 × 100 ns 后分析方法

本文件说明本批次实际采用的输入核验、后处理与比较口径。完成状态由各组验证记录及 `comparison/comparison_status.json` 决定；方法说明本身不充当验收凭证。

## 输入与身份

六组仅使用 E2 `/ifs1/User/dengwei/igem/md/gpr2-autodl/runs/` 中各自正式生产 XTC 和 `production.tpr`，按 `operator_records/` 的 `closed_segment.json` 实际时间排序。第一段没有 part 后缀。资格、EM、NPT、预热与旧 E2 两条生产快照均不计入本轮 100 ns。

复用已独立逐文件 SHA 核验的 77 段回收证据，不重复计算旧大轨迹的源 SHA。当前重新核验每份归档 manifest 和闭合记录的 SHA、TPR SHA、XTC 字节数、每帧原子数、有限坐标和全部时间点；源 XTC 的预期 SHA 留在逐段清单中。低层 XDR 只读接口不向原 `runs/` 写缓存或 offsets。新派生文件重新计算 SHA256。

每组原始时间点的并集必须恰好是 `0,10,...,100000 ps`。只有 N84V–ascr18 的 1030 ps 和 WT–ascr3 新 lid 的 26970 ps 为已记录合法重复边界，还核对重复坐标的最大差异；原始重复保留。GROMACS `trjcat` 在派生副本中处理重复，随后重新读取全部帧，要求恰好 10001 个唯一时间点、无缺点或额外点。每组使用自身 TPR，验证全体系原子数、406 位受体、84/368 位身份和独立配体分子块。

受体母体与各自 top1 pose 的来源见 [母体/pose 溯源](configs/parent_pose_provenance.json) 和 [原输入选择证据](../../input-selection-20261005/provenance.json)。WT 使用独立 WT 母体；N84V、V368R 分别使用自己的 AF3 母体。WT–ascr18 沿已有 W174 侧链修复；V368R–ascr3 和 WT–ascr3 是各自母体与 pose 下的 lid 重构起点；其余三组保留 raw lid。各组另有自己的准备过程、膜/溶剂组成和生产初始状态，不能将差异归因于突变一项。

## PBC、拟合与 processed 门禁

先审查并适配仓库 [通用后处理脚本](../../../../scripts/postprocess_gpr_md_rep.sh)。本轮显式设置 100000 ps 和 10001 帧，以真实分段验收及派生合并验证 JSON 作为输入证据；没有创建旧布局的虚构生产终态文件。

原生产版本来自六组正式日志头，当前 E2 版本来自实际 `--version`；同系列构建的兼容性另以各组 TPR 实读、全量 XTC 网格及 processed 映射/坐标验收记录核对，详见 `e2_delivery/_shared/evidence/source_gromacs_versions.json` 和环境核验日志。GROMACS 2025.4 路线为：全体系合并 → `-pbc mol -center`（受体居中，输出受体和配体）→ `-pbc nojump` → 受体主链 `-fit rot+trans`。从同组完整 TPR 提取原子顺序一致的 solution TPR。该路线保留配体相对于受体的运动，不每帧强行把配体聚回受体。`prod_cluster.xtc` 是旧接口名，本轮文件实际是 nojump 输出。

生成共享接口 `processed/rep1/protein_ref.pdb` 和 `prod_protein.xtc`。TPR 到 reduced TPR 的名称、残基号、残基名逐原子严格一致；PDB 的受体名称严格一致，配体名按 GROMACS 四字符字段核验 `ASCR18/ASCR3 → ASCR`。原子名称、次序、残基号继续逐一核对，配体按已证实的原子索引范围选择，避免名称截断产生歧义。实际配体为 ascr18 54 原子/23 重原子、ascr3 46 原子/21 重原子，受体均 406 位。

所有 processed 帧检查有限坐标、完整 10 ps 时间网格、重原子共价键长度、相邻受体 CA 距离，以及每 10 ps 的配体相对受体 COM 位移。筛查上限分别为 3.0 Å、4.5 Å、10.0 Å，作为发现 PBC 断裂、原子映射或不连续跳跃的宽松数值检查；它们不是 pose 稳定、结合或亲和力阈值。原始与处理后计数、最大值和诊断图均留在每组 evidence 中。

## 七类共享指标和时间口径

[批次配置](configs/batch_config_v3.json) 固定 `CHIMERIC_MD_REPS=1`；它表示只选 rep1。每组 `system_config.json` 根据真实 processed 映射生成，七类共享 driver 不改成每组专用分析器。旧 driver 在 100 ns 轨迹上会将 after100 汇总退化为终点一帧，本轮给共享接口增加可配置窗口；未配置时保留历史行为。

主要窗口统一为 **50–100 ns，含两端**。选择后半程用于减少直接反映准备后初始变化的比重，同时保留 50 ns 描述区间；此选择不声称 50 ns 已达到平衡。全程曲线、0–50 ns 描述和不重叠 10 ns 时间块用于检查持续漂移。10 ns 块只描述同一条相关轨迹的时间变化，不用作独立重复或统计置信区间。

- **Convergence**：全部 10001 帧，受体主链相对本组第 0 帧的拟合 RMSD、受体 CA 回转半径 Rg；50–100 ns 共 5001 帧，汇总均值、范围和线性时间趋势。名称为 convergence 不等于已证明收敛。
- **Selection RMSD**：全部帧，配体重原子在受体主链等权 Kabsch 拟合后相对本组初始配体的 RMSD；这里的初始态是经历准备后的生产 t=0，不等同于原始 docking top1 坐标；ascr18 与 ascr3 各用自己的完整重原子集合，不使用 pose 稳定分类阈值。
- **H-bond**：每 50 帧即 0.5 ns，50–100 ns 共 101 个采样时点。共享手工几何筛查用 N/O/S、首帧近邻供体–H 配对、供体–受体 ≤3.0 Å、D–H–A ≥150°。这不是基于完整化学类型的独立氢键验证；报告为几何候选氢键占有率。没有检测到配对时保留空表和零占有率，不伪造配对。
- **COM distance**：全部帧，配体重原子质心至全受体质心，以及至本组第 0 帧 4 Å 接触残基簇的质心。全受体采用共同残基集合，但质量加权质心仍依赖本组侧链质量和构象；自己的初始簇因 pose 不同而不同，主要用于组内迁移描述，不能当作同一匹配口袋的组间距离。
- **RMSF**：受体拟合 processed 的 50–100 ns 共 5001 帧，406 个 CA 的均方根波动，相对该窗口平均位置。它受整体主链拟合和柔性区域运动影响，不直接等同于功能稳定性。
- **BSA**：0–100 ns 每 0.5 ns，共 201 帧；Shrake–Rupley 240 sphere points，`SASA(受体)+SASA(配体)−SASA(复合物)`，以 Å² 报告，不除以 2。保留绝对 BSA 和相对本组初始 BSA 的比例；配体尺寸和初始埋藏程度不同，不能将 BSA 排成亲和力顺序。
- **Contacts**：0–100 ns 每 0.5 ns，共 201 帧；接触为受体残基–配体残基最小重原子距离 ≤4.0 Å。初始接触保留比例定义于各自 frame0 接触集合，50–100 ns 的 101 个时点计算占有率。新增接触不属于该保留比例，另由已有 `compare_ligand_paths.py` 做动态接触描述。该共享结构复核以 WT–ascr18 初始受体为共同参考，逐组用相同受体主链等权拟合，每 0.5 ns 比较配体重原子几何质心路径与全部受体 4 Å 动态接触；0–50 ns 与 50–100 ns 分开统计。共同坐标系不消除不同母体、lid 和 pose 的起点差异。

六组图表保持固定体系顺序，不按指标给综合分或“优胜”排名。共享 [表格验证与比较入口](../../../../analysis/chctrl/summarize_metric_tables.py) 仅读取既有 driver 数值表，检查行数、时间点、有限值、选择、占有率分母和真实退出状态，再生成汇总和图表；它不新增轨迹指标。

## 资源与复现

分析环境位于 E2 项目个人目录 `/ifs1/User/dengwei/igem/envs/roy_md-analysis-py311`，与生产环境独立。版本和精确包清单留在 `e2_delivery/_shared/evidence/`。持久会话保留独立日志；后处理队列与通过严格验收后恢复的指标队列各限制 2 个计算线程、降低 CPU 优先级，最多两个此类队列同时工作。既有 MD 不停机、不重启，不使用 GPU 作本轮分析。

原始 `runs/`、`operator_records/` 只读，全部派生产物留在 E2 `analysis/<case_id>/`。本地回收配置、证据、CSV、图、参考 PDB 和中文报告；大轨迹留 E2，交付清单记录路径、字节数和 SHA256。RMSD 数值另在每组 0、25、50、75、100 ns 用独立 NumPy SVD 刚体拟合复算，分别对照受体主链 RMSD 和配体重原子 RMSD，操作容差为 1e-4 Å，不作为科学效应阈值。代码部署分版本保存：初次队列 v2 在严格残基名检查处停止；v3 只识别并重新验证确定的 PDB 格式截断，原失败日志保留。

所引：[E2 输入树与完成凭证](../E2_FILE_TREE.md)、[分段回收覆盖](configs/coverage_certificate.json)、[后处理规范第 3 节](../../../../../../docs/ops/md-gromacs-operational-pitfalls.md)、共享代码、各组 input_contract 与实际 TPR/processed 证据。被引：本目录中文报告、README 和六组比较交付；其他潜在下游引用未穷尽检索。
