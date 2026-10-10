# 受体FASTA输入

批次目录与outputs/batches同名。每个目录保留该批原有FASTA文件名及序列头；WT是共用参考序列。

| 当前目录 | 原目录 |
|---|---|
| 03-af3-single-alanine/ | gpr2_single_mutants_full_length/ |
| 04-af3-more-single-alanine/ | gpr2_design_round2_full_length/ |
| 05-af3-n84-v110-v368-saturations/ | gpr2_phase2_saturation_05_full_length/ |
| 06-af3-supplement-singles/ | gpr2_batch06_supplement_full_length/ |
| 07-af3-w338-saturation/ | gpr2_batch07_w338_saturation_full_length/ |
| 08-af3-double-mutants/ | gpr2_batch08_double_mutants_full_length/ |

旧manifest中的fasta_output保留历史值以维持校验哈希；当前FASTA生成/校验和归档脚本按所属批次定位此处同名目录。旧结果中的路径记录通过outputs/file-organization/fasta-directory-renaming.json映射追溯。

08批提交文件位于08-af3-double-mutants/individual/，每个FASTA对应一个独立单体任务。
