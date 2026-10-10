# Gpr2 Vina操作协议：助手给命令，用户运行

## 1．必须延续的协作方式

**助手逐步解释、编写CLI/PyMOL命令；用户在终端/PyMOL执行并返回输出。** 默认不得由助手启动AF任务、Vina、ProLIF、批量结构制备或其他科研计算。用户已有的计算不重复运行。

助手可以读取文件、审阅结果、编写脚本/文档、整理目录和做静态语法/路径检查。序列生成、解压、结构转换等下一阶段准备步骤也先给用户命令；用户明确另行授权时才代执行。每步说明输入、输出、预期检查结果、失败时如何处理。新批次另建目录，不能覆盖旧poses或接触数据。

## 2．当前工具与输入

- 项目根：`/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab`。
- 科研脚本：`vina/src/`；另一份实际名为`vina/src 2/`。本次比对共同28个Python文件内容相同，src额外含align_pdb_to_reference.py、run_vina.py；本项目使用src。
- Python：`/Users/yangruoxi/miniconda3/envs/docking/bin/python`；Vina同环境`bin/vina`。历史运行Vina 1.2.5、ProLIF 2.1.0，新任务先由用户核对环境版本。
- 原序列：`projects-done/inputs&outputs-deltaNlid/inputs/receptors/fasta/Gpr2_TWF154_TGJ68930.1.fasta`（406 aa）。
- 配体：`projects-done/inputs&outputs-deltaNlid/inputs/ligands/deprotonated-minus1/pdbqt/ascr3_deprotonated.pdbqt`及`ascr18_deprotonated.pdbqt`。
- 对齐参考：同一归档下 `inputs/receptors/af3/pdb/gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_0_deltaN1-21_deltaN164-178_aligned.pdb`。

## 3．已用的完整流程

| 阶段 | 脚本/入口 | 做什么与验收 |
|---|---|---|
| FASTA/AF3 | 批次manifest、AF3输入 | 原序列只做指定点突变，全长送AF；单条蛋白独立任务 |
| 归档 | 批次helpers.py unpack | ZIP校验、保留原始CIF/job_request、核对突变序列和模型 |
| 转换/删除 | src/cif_to_pdb.py；批次02 cli/trim_after_full_length_af3.py | 全长model_0转PDB；先核验406 aa，再删除原1–21、164–178，370残基且保留编号 |
| 对齐 | src/align_pdb_to_reference.py | TM CA区间30–50、62–83、101–126、144–163、182–201、326–346、358–380；刚体对齐到共同参考，用户PyMOL检查 |
| 受体制备 | src/prepare_receptor_pdbqt.py | Meeko/Gasteiger，输出receptor.pdbqt、receptor.json、prepared.pdb；检查序列/编号 |
| 配置 | src/define_vina_box.py | 同一坐标系、两配体同一盒与参数；检查配置中的真实输入路径 |
| 对接 | src/run_vina.py | 用户启动Vina；保留stdout/stderr、run.json、poses.pdbqt；返回码与哈希核验 |
| 评分 | src/summarize_vina_results.py；批次compare | 按最低评分选pose，同分取最低MODEL编号；计算对应WT的ΔS与D |
| 接触 | 批次03 cli/top1_contacts.py | 核验来源哈希，选最低分MODEL，Meeko转SDF，读取receptor.json作ProLIF；用户检查view_contacts.pml |

## 4．冻结参数

历史配置：中心(20,−20,5) Å；尺寸26×26×26 Å；exhaustiveness=8；num_modes=9；energy_range=3；seed=1919。运行另传spacing=0.375、min_rmsd=1、max_evals=0；历史单任务cpu=16。新并行批次需显式限制CPU总占用。

ProLIF：2.1.0；vicinity_cutoff=6.0 Å；Anionic、CationPi、Cationic、HBAcceptor、HBDonor、Hydrophobic、PiCation、PiStacking、VdWContact。6 Å是邻域筛选，不是所有接触类型统一的距离阈值。

主统计：WT→突变体对#3的变化，与WT→突变体对#18的变化四格比较。残基次数按一个残基在最优pose出现任意接触计一次；残基–类型条目另列。多pose仅核查最优pose解释的代表性。

## 5．历史命令样式（说明用途，不应重跑已有结果）

以下入口目前只支持批次04已定义的突变。新增53种单突变和12个双突变需要新CLI，不能直接将新名称代入旧入口。

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
export VINA_EXE=/Users/yangruoxi/miniconda3/envs/docking/bin/vina
CLI=outputs/batches/04-af3-more-single-alanine/cli
# 用新输出目录重建配置，旧结果目录保持原样。
export ROUND2_AF3_OUT="$PWD/outputs/batches/04-af3-more-single-alanine/run-02"
group=N84Q
# 每次只执行已核对输入的一个阶段。
bash "$CLI/commands.sh" convert "$group"
bash "$CLI/commands.sh" align "$group"
# 用户PyMOL检查alignment_review.pml后再继续：
bash "$CLI/commands.sh" prepare "$group"
bash "$CLI/commands.sh" config "$group"
bash "$CLI/commands.sh" dock "$group"
# 两种配体分别提取最低分pose并计算接触：
"$DOCKING_PYTHON" outputs/batches/03-af3-single-alanine/cli/top1_contacts.py   --run-dir "$ROUND2_AF3_OUT/$group/ascr3"
"$DOCKING_PYTHON" outputs/batches/03-af3-single-alanine/cli/top1_contacts.py   --run-dir "$ROUND2_AF3_OUT/$group/ascr18"
```

批次commands.sh的contacts会处理全部poses；主统计用top1_contacts.py。历史配置、JSON和PML保留当时路径，部分仍含旧Projects根目录；不能直接重用旧vina.conf启动新计算。新CLI生成当前路径配置；可视化旧PML时先在新文件中修正路径。
