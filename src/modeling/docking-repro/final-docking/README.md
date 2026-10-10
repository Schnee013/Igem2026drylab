# Docking 工具

结构格式转换、受体与配体准备、搜索盒、Vina 批处理、ProLIF 指纹和 GUI 共用本目录代码。
[环境安装](../../../../environments/final-docking/INSTALL_AF2_RELAX.md)固定工具版本；
[研究与数据入口](../../../../docs/modeling/final-docking/README.md)说明体系和结果。

在 drylab 根目录运行：

```bash
conda activate docking
python src/modeling/docking-repro/final-docking/docking_gui.py
DRY_RUN=1 bash src/modeling/docking-repro/final-docking/run_all_vina.sh
python src/modeling/docking-repro/final-docking/batch_prolif.py --dry-run
python src/modeling/docking-repro/final-docking/merge_prolif_csv.py \
  --output-dir /tmp/final-docking-csv-review --layout both --kinds frequency presence counts
```

两个 dry-run 只检查输入、搜索盒和任务发现，不执行对接或 ProLIF。
这批保存的结果对应 35 个受体模型 × 两种配体，共 70 组。
Vina 使用五个 WT 家族的七种构建体：DAF-37、Gpr2、Gpr3、GprC、SRBC-64，
Gpr2/Gpr3 各有全长与截短构建体；每种构建体使用五个模型。

[configs/paths.json](configs/paths.json)定义仓库相对路径。Vina 的
`ROOT`、`BOX_FILE`、`RECEPTOR_ROOT`、`LIGAND_ROOT`、`OUTPUT_ROOT` 和 `VINA`
允许显式覆盖；ProLIF 的同类路径由 `--root`、`--docking-root`、
`--receptor-pdb-root`、`--receptor-pdbqt-root`、`--output-root` 指定。
实际重算时请指定新的输出位置，以保留已有结果。

Meeko 的 35 个 `receptor.json` 属于可重建缓存，默认位于仓库旁的
`drylab-payloads/final-docking/prolif/af3/`。可用 `DRYLAB_PAYLOAD_ROOT` 更改
payload 根目录，或用 `--receptor-json-root` 显式指定缓存目录。缺少缓存时，
程序依据对应 PDB 重建，并要求重新生成的 PDBQT 与保存的对接输入逐字节相同。
[外部文件清单](../../../../experiments/docking-repro/analysis/final-docking/payload_manifest.tsv)
记录缓存及 AF2 relax runtime wheel 的校验值和位置。

CSV 合并只插入分组和来源标签，保留每个结果块的原始行顺序与内容，不重算指标。
GUI 通过同目录工具注册表定位 CLI；它使用启动 GUI 的 Python 环境。
