# 批次05：三个位点饱和单突变

输入设计：N84X、V110X、V368X 各19种替换，共57个单突变，另加406 aa全长WT baseline。原序列和历史WT一致；原始编号84=N、110=V、368=V。

设计记录见 `manifests/saturation-singles.json`。每条记录保留突变、是否新增AF、历史FASTA/model_0/job_request路径与文件哈希。N84A映射到批次03，其余9种已有核心单突变映射到批次04；两个来源WT另列。历史CIF序列仍待结构归档阶段校验。

原提交计划：完整序列集58条；沿用[既定复用方案](../../phase2-design/parallel-screen.md)，新增提交47个突变体＋baseline＝48个任务。新baseline是本批主WT，历史WT保留来源映射。D＝ΔS18−ΔS3，主统计使用每次最低分pose。

## 用户分步执行

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
CLI=outputs/batches/05-af3-saturation-combinations/cli/saturation_fastas.py
"$DOCKING_PYTHON" "$CLI" check
```

预期 `SOURCE PASS`：检查原序列、设计覆盖、10个历史突变FASTA、两个历史WT及来源文件哈希。出现STOP先返回完整输出。

```bash
"$DOCKING_PYTHON" "$CLI" generate
"$DOCKING_PYTHON" "$CLI" validate
```

生成入口拒绝覆盖已有输出目录。预期 `FASTA PASS`：58条序列均406 aa；每个突变体仅指定位置变化；baseline与原序列完全相同；每个位点恰好19种替换；48条新增AF序列；文件哈希和manifest一致。重复检查用validate。若生成中断，保留目录并返回报错再处理。

输出目录：`vina/inputs/receptors/fasta/05-af3-n84-v110-v368-saturations/`。

| 文件 | 用途 |
|---|---|
| individual/baseline.fasta | 本轮全长WT |
| individual/突变名.fasta | 全部57种单突变的独立FASTA |
| all_58.fasta | 58条完整序列集，便于查看 |
| new_af_48.fasta | 按复用方案需要新增AF的48条序列汇总 |
| submission_ids.txt | 48个设计ID，baseline排首位 |
| submission_jobs.tsv | 设计ID、AF3 job名称、独立FASTA路径对照 |
| checksums.json | FASTA及manifest哈希 |

验证通过后，按submission_jobs.tsv逐个使用individual/中的对应FASTA提交，并将AF3的Job name填写为表中af_job_name，每个任务一条全长蛋白、单拷贝。汇总FASTA用于查阅，不将其作为一个多链复合物提交。AF预测输入保留完整406 aa。完成后返回下载包位置，再提供归档核验命令。

当前状态：已收到并归档全部58个新AF任务，290个模型的406 aa序列及编号核验通过。实际执行来源以 `manifests/received-af3.json` 为准，58个结构均使用本次新预测；原设计manifest保留历史复用计划与来源。

## AF3 job命名

实际下载包使用 `gpr2_b05_fl_*` 原名，原始文件保持不变。归档manifest用 `alias` 映射为 `05_baseline`、`05_n84c` 等简名，后续输出目录使用简名。已生成FASTA及原始请求保留提交时的名称。

## 已归档结果与下一步

输入包：`folds_2026_09_16_11_15.zip`（30任务）、`folds_2026_09_16_11_16.zip`（28任务）。
归档目录：`vina/inputs/receptors/af3/gpr2_batch05_20260916/`，含source_zips/、按来源ZIP分开的original_cif/、已核验的fasta_full_length/副本。

58个任务覆盖baseline和三个位置各19种替换；每任务单条蛋白、单拷贝；全部model_0–4的序列和原编号1–406核验通过。使用固定model_0进行下一步。

用户先执行baseline转换与删段：

```bash
cd /Users/yangruoxi/Documents/ChatGPT/Docking-Research-Lab
export DOCKING_PYTHON=/Users/yangruoxi/miniconda3/envs/docking/bin/python
CLI=outputs/batches/05-af3-saturation-combinations/cli/convert_received.py
"$DOCKING_PYTHON" "$CLI" baseline
```

预期406→370残基，删除原1–21和164–178，保留原编号及其余原子坐标。输出在run-01/05_baseline/，包含raw_model0.pdb、trimmed.pdb、trimming.json。先返回baseline输出；通过后再执行：

```bash
"$DOCKING_PYTHON" "$CLI" all-mutants
```

每步核对归档输入哈希，并拒绝已有输出目录。中断或报STOP时保留现场并返回输出。助手已执行解压归档与只读核验；结构转换、删段由用户运行。
