# SwissDock复现与输入检查

这一任务以Kuo2024的Gpr2/Gpr3–ascr#3对接为起点。已有受体序列和结构、配体化学身份检查、SwissDock返回结果、评分/pose整理，以及AF3模型和质子化比较资料。

## 阅读与结果入口

1. [文献阅读](tasks/001-gpr2-gpr3-ascr3-reproduction/literature/Kuo2024-reading-notes.md)：复现条件与论文信息。
2. [任务记录](tasks/001-gpr2-gpr3-ascr3-reproduction/README.md)：输入冻结、代表pose规则和当时状态。
3. [原始运行](tasks/001-gpr2-gpr3-ascr3-reproduction/runs/)与[分析结果](tasks/001-gpr2-gpr3-ascr3-reproduction/results/)：分别查看Gpr2/Gpr3及扩展比较。
4. [质子化比较](tasks/001-gpr2-gpr3-ascr3-reproduction/results/af3-model0-protonation-comparison.md)与[可视化矩阵](tasks/001-gpr2-gpr3-ascr3-reproduction/results/visualization-matrix/README.md)。

任务记录指出：Gpr2两个作业虽提交不同SMILES，返回拓扑均为中性羧酸；最低分pose位置不同，说明输入参数化与采样需要分别审查。新版Attracting Cavities流程与论文旧版EADock DSS存在算法差异，复现程度按原记录限定。

原总索引写“文献带读待开始”，已落后于现存运行结果。本次入口以实际文件为依据；图、接触表及最终复现判断的完整性需结合各子任务记录审阅。原索引见[来源快照](README.source.md)。
