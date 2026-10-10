# Phase1分析：批次01–03

- [初始位点筛选](residue-priorities.md)：03的单点线索及02组合解释。
- [评分与接触统计](statistics.md)：最低分pose主统计，01侧链路线单列。
- top1-contacts/：01–03的11条评分、22条接触增减和324行四格条目。
- candidate-allposes/：03批36条pose和135行接触频次，作为参考。

CSV内原batch字段保留历史名称：gpr2-combination-run01=01，gpr2-af3-combination-run01=02，gpr2-single-af3-run01=03。多pose文件子目录现为03-af3-single-alanine。历史audit内输入路径保持原样，可结合[file-organization迁移清单](../file-organization/analysis-reorganization.json)和批次目录解析。04证据已归[phase2](../phase2-analysis/README.md)。
