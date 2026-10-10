# Gpr2 model_0 deltaN 组合 Ala 突变：用户执行命令

运行目录：`/Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab`。

本地输入与对接归档实际位于 `projects-done/inputs&outputs-deltaNlid/`，接触归档位于 `projects-done/prolif/prolif-batch-full/`。
选择 `gpr2_twf154_wt/deltaN_aligned/gpr2_twf154_wt_model_0_deltaN1-21_deltaN164-178_aligned`。
FASTA 全长 406 aa；受体 A 链保留 22–163、179–406，共 370 残基；PDB/PDBQT 原编号和保留序列一致。
归档 ProLIF 的 `receptor_regenerated.pdbqt` 与实际对接受体逐字节一致。

三组为同一 deltaN 基线、N84A/L90A/R345A、V110A/R181A/W338A/V368A。每组分别对接去质子化 ascr#3、ascr#18。

## 源码选择

使用 `vina/src/`。另一份目录实际名为 `vina/src 2/`；28 个同名 Python 文件逐字节相同，`src/` 另有 `align_pdb_to_reference.py`、`run_vina.py`。
这两份目录均没有组合突变或 ProLIF runner。此目录新增 `helpers.py` 补足这两步，`commands.sh` 调用已有源码完成 Meeko 制备、box 配置、Vina 运行、结果汇总和 pose 导出。已有源码未修改。

## 执行

在同一终端逐步执行。下面第 2 条才运行对接。

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
bash outputs/batches/01-sidechain-combination/cli/commands.sh prepare
bash outputs/batches/01-sidechain-combination/cli/commands.sh dock
bash outputs/batches/01-sidechain-combination/cli/commands.sh contacts
```

默认结果目录是 `outputs/batches/01-sidechain-combination/run-01/`。更换批次时，在执行三个阶段前设置：

```bash
export GPR2_OUT=/absolute/path/to/a/new/run-directory
```

`DOCKING_PYTHON` 和 `VINA_EXE` 可覆盖命令文件内的本机环境路径。`prepare` 遇到已有 input.pdb 会停止；失败后先查看日志，修正问题后使用新的结果目录重新准备。

## 本轮协议

固定重原子骨架：目标位点改为 ALA，保留 N/CA/C/O/CB，删除其他侧链重原子；三组统一去氢后用 Meeko 0.7.1、Gasteiger 重新制备，不做能量最小化或骨架重排。保留 370 个残基及原编号。校验器要求重原子清单和保留坐标一致；允许 Meeko 对 406 位末端两个氧的 O/OXT 名称互换，要求两个坐标的集合完全不变。

| 参数 | 值 | 依据 |
|---|---|---|
| center | 20, −20, 5 Å | 两份历史日志 |
| size | 26 × 26 × 26 Å | 两份历史日志 |
| spacing | 0.375 Å | 两份历史日志 |
| exhaustiveness | 8 | 两份历史日志 |
| seed | 1919 | 两份历史日志 |
| cpu | 16 | 两份历史日志 |
| num_modes | 9 | 本轮最多输出 9 个；历史实际输出 9 个 |
| energy_range | 3 kcal/mol | 本轮统一设定；历史日志未记录 |
| min_rmsd | 1 Å | 本轮统一设定；历史日志未记录 |
| max_evals | 0 | 本轮统一设定；历史日志未记录 |

历史 Vina 标识为 `7ac2999-mod`，本机为 `1.2.5`。六组使用同一个本机可执行文件、同一处理及参数，分数差以本轮重新对接的 deltaN 基线计算。历史分数仅留作来源记录：ascr#3 −6.610，ascr#18 −6.557 kcal/mol。

## 查看结果

`score_comparison.csv` 中差值 = 组合突变最佳 Vina 分数 − 同配体本轮基线最佳分数；正值表示评分变差。各构象的完整分数保存在每个组合的 `summary.json` 与日志。

每个受体组生成 `review.pml`，用 PyMOL 打开后逐个 state 检查两种配体的 poses。核对是否仍在相同口袋、是否发生翻转或移位、是否有明显穿插，以及极性头部和侧链位置。不同组的相同 mode 编号不表示同一种结合姿势。

`contacts` 使用每组自身 Meeko receptor.json 和对应新 poses；沿用归档的 ProLIF 2.1.0、9 类接触、6 Å vicinity cutoff。
每个 residue/pose 对全部接触类型做 OR，得到 `residue_presence.csv`、`residue_counts.csv`。
总表 `contact_comparison.csv` 按原残基编号比较，因此 ASN84→ALA84 仍归于 84 位。表中同时保留配体间次数差和每种配体相对基线的接触频率变化。

`num_modes=9` 是上限。实际 pose 数在输出中保留；若各组数量不同，使用频率比较，不能直接比较原始次数。所有新 poses 的计算结果还需人工复查；当前人工通过的状态只适用于两份历史 pose 集合。

## 已核对的选位依据

| 残基 | #3 接触 pose 数 | #18 接触 pose 数 | #18−#3 |
|---|---:|---:|---:|
| ASN84 | 4 | 2 | −2 |
| LEU90 | 6 | 2 | −4 |
| ARG345 | 3 | 1 | −2 |
| VAL110 | 3 | 6 | +3 |
| ARG181 | 4 | 7 | +3 |
| TRP338 | 1 | 4 | +3 |
| VAL368 | 4 | 6 | +2 |

该实验探索固定 model_0 骨架上两组接触残基共同改变后的配体响应。Ala 替换未必消除该位点的所有接触，需检查重排及补偿接触。位点尚无跨模型稳健验证，组合实验不能拆分单个位点贡献，Vina 分数差不能等同于实验结合自由能变化。

## 本次验证范围

Python/Bash 语法检查通过。三组构建和 Meeko 制备在临时目录中通过 370 残基、原子清单、残基名称及保留几何校验。接触辅助脚本在历史 SDF 和 receptor.json 上重现 #3 的 270 个、#18 的 297 个 pose×残基×接触类型布尔值，与归档矩阵全部一致。本次未调用 Vina，六组新对接分数和新姿势尚待用户执行后产生。
