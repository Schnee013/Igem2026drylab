# 共享工具 输入与环境

[通用脚本](scripts/)来自原`vina/src/`；[共享输入](inputs/)保存原`vina/inputs/`的序列、配体、AF2/AF3、拓扑和准备结构。AF3各批原始ZIP、全长CIF和FASTA按原集合保留，批次manifest中的原路径通过[迁移表](../provenance/file-map.csv)定位。

共享集合中含多个研究阶段的输入，使用时按manifest选择具体文件。突变流程还引用[基础资料输入](../04-vina-baseline/deltaNlid-source/inputs/)，已随交付保存。

[环境与使用说明](environment/README.md)区分只读交付核验与科学重运行；[原工具压缩包](original-archives/)用于追溯来源版本。
