# Receptor input identity for Gpr2/Gpr3 pocket alignment

## Findings

### Bottom Line

本研究已冻结六个唯一受体输入，后续分析只使用 `input_manifest.tsv` 指定的文件。TWF154 Gpr2/Gpr3 采用与 NCBI 蛋白序列一致的本地 ColabFold AF2-ptm rank 1 模型；ATCC Gpr2/Gpr3、GprC 和 N2 SRBC-64 采用对应 AlphaFold DB v6 模型。

所用结构全部是预测模型，没有一个是实验解析的 PDB 结构。因此，“数据库登记可靠”在这里主要保证受体身份、序列与来源可追溯，并不等于原子坐标已经由实验确认。

### Input status

| Receptor | Frozen identity | Structure | Identity assessment | Structural evidence limit |
|---|---|---|---|---|
| TWF154 Gpr2 | TGJ68930.1, 406 aa | ColabFold AF2-ptm rank 1 | NCBI 序列、本地 FASTA 与 PDB 序列完全一致 | 本地预测模型；不是数据库实验结构 |
| TWF154 Gpr3 | TGJ67963.1, 401 aa | ColabFold AF2-ptm rank 1 | NCBI 序列、本地 FASTA 与 PDB 序列完全一致 | 本地预测模型；不是数据库实验结构 |
| ATCC Gpr2 | G1X9E2, 406 aa | AF-G1X9E2-F1 v6 | UniProt reviewed，PDB 与 AFDB 下载逐字节一致 | AF2 预测坐标 |
| ATCC Gpr3 | G1XJN1, 401 aa | AF-G1XJN1-F1 v6 | UniProt reviewed，PDB 与 AFDB 下载逐字节一致 | AF2 预测坐标 |
| GprC | A0A437AGY2 / RVD90404.1 / DFL_001370, 538 aa | AF-A0A437AGY2-F1 v6 | UniProt reviewed，PDB 与 AFDB 下载逐字节一致 | AF2 预测坐标；菌株标签有数据库差异 |
| SRBC-64 | G5ECV4 / NP_740807.1 / Y39G10AR.22, 289 aa | AF-G5ECV4-F1 v6 | N2 RefSeq、UniProt、FASTA 与 PDB 序列完全一致 | AF2 预测坐标；不能认定为 Hu 2024 的历史模型文件 |

### Practical Implications

- TWF154 是目标菌株；ATCC 只用于检测菌株差异是否改变候选口袋。两组序列等长：Gpr2 有 7 个替换位点，Gpr3 有 6 个替换位点。
- SRBC-64 使用 N2 标准序列，因为 Hu 的克隆材料来自 N2 cDNA。Hu 论文的 Ballesteros–Weinstein 位置与功能突变信息可映射到该序列。
- Hu 没有报告 SRBC-64 的 AFDB accession 或模型版本，所以我们的 SRBC-64 输入是“身份匹配的 N2 参照”，不是“Hu 原始坐标的复制品”。
- 下一门槛是给六个受体定义 TM1–TM7，并把 Hu 报告的相对口袋位置映射到绝对残基号；在此之前不执行结构拟合。

## Gaps and Conflicts

- Hu 2024 的 Methods 只写明 GprC、SRBC64 和 DAF37 模型来自 AlphaFold DB，没有列出 accession、文件名、下载日期或数据库版本。论文提供的信息不足以逐坐标复原其 SRBC-64 输入。
- `G5ECV4` 与 N2 RefSeq 完全匹配，但 AFDB API 对现有 v6 模型给出的 `modelCreatedDate` 是 2025-08-01。这个日期晚于 Hu 论文，因而现有文件不能被标成 Hu 使用的历史模型；该元数据也不能单独证明更早版本是否曾存在。
- 2024 年前已有的三个 290 aa 同名条目分别映射到 KR314 (`B1NYG7`)、JU1088 (`G5ECA4`) 和 CB4853 (`G5EEB2`)；它们不是 N2 标准序列，论文也未说明选用了其中哪一个。
- Hu Methods 把实验菌株写为 CBS 349.94，而 NCBI `RVD90404.1`/PRJNA494930 将基因组菌株标作 CBS H-5679。Hu 的 Data availability 明确指向 PRJNA494930，且 UniProt 将 `A0A437AGY2` 的 `gprC` 注释链接到该论文；两种 CBS 标签之间的收藏学关系仍未由所查来源解释。

## Research Objective

- Decision/use: 冻结六个可复用、可校验的受体序列与主结构输入，供 TM-core 和口袋比对使用。
- Target question: 每个受体名称具体对应哪个 accession、菌株、序列和结构模型；Hu 2024 的 SRBC-64 能否被唯一复原。
- Source scope: Hu 2024 原文、NCBI/RefSeq、UniProt、AlphaFold DB 和仓库内原始 ColabFold结果。
- Exclusions: 本记录只判定输入身份与来源；TM 边界、结构拟合和口袋结论由后续步骤产生。
- Access date: 2026-08-14.

## Verified Source Ledger

| ID | Source | URL | Authority | Access | Relevance | Status |
|----|--------|-----|-----------|--------|-----------|--------|
| S1 | [Hu et al. 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/) | <https://pmc.ncbi.nlm.nih.gov/articles/PMC11222155/> | primary | 2026-08-14 | 结构来源说明、实验菌株、N2 cDNA 与功能位置 | used |
| S2 | [NCBI TGJ68930.1](https://www.ncbi.nlm.nih.gov/protein/TGJ68930.1) | <https://www.ncbi.nlm.nih.gov/protein/TGJ68930.1> | official | 2026-08-14 | TWF154 Gpr2 蛋白与菌株记录 | used |
| S3 | [NCBI TGJ67963.1](https://www.ncbi.nlm.nih.gov/protein/TGJ67963.1) | <https://www.ncbi.nlm.nih.gov/protein/TGJ67963.1> | official | 2026-08-14 | TWF154 Gpr3 蛋白与菌株记录 | used |
| S4 | [UniProt G1X9E2](https://www.uniprot.org/uniprotkb/G1X9E2/entry) | <https://www.uniprot.org/uniprotkb/G1X9E2/entry> | official | 2026-08-14 | ATCC Gpr2 identity and annotation | used |
| S5 | [UniProt G1XJN1](https://www.uniprot.org/uniprotkb/G1XJN1/entry) | <https://www.uniprot.org/uniprotkb/G1XJN1/entry> | official | 2026-08-14 | ATCC Gpr3 identity and annotation | used |
| S6 | [UniProt A0A437AGY2](https://www.uniprot.org/uniprotkb/A0A437AGY2/entry) | <https://www.uniprot.org/uniprotkb/A0A437AGY2/entry> | official | 2026-08-14 | GprC identity, reviewed status and cross-references | used |
| S7 | [NCBI NM_170823.3](https://www.ncbi.nlm.nih.gov/nuccore/NM_170823.3) | <https://www.ncbi.nlm.nih.gov/nuccore/NM_170823.3> | official | 2026-08-14 | N2 srbc-64 transcript, NP_740807.1 and sequence | used |
| S8 | [UniProt G5ECV4](https://www.uniprot.org/uniprotkb/G5ECV4/entry) | <https://www.uniprot.org/uniprotkb/G5ECV4/entry> | official | 2026-08-14 | SRBC-64 UniProt/WormBase/RefSeq mapping | used |
| S9 | [AlphaFold DB G5ECV4 API](https://alphafold.ebi.ac.uk/api/prediction/G5ECV4) | <https://alphafold.ebi.ac.uk/api/prediction/G5ECV4> | official | 2026-08-14 | SRBC-64 model ID, v6 URL, sequence and model date | used |
| S10 | [AlphaFold DB G1X9E2 API](https://alphafold.ebi.ac.uk/api/prediction/G1X9E2) | <https://alphafold.ebi.ac.uk/api/prediction/G1X9E2> | official | 2026-08-14 | ATCC Gpr2 model v6 metadata | used |
| S11 | [AlphaFold DB G1XJN1 API](https://alphafold.ebi.ac.uk/api/prediction/G1XJN1) | <https://alphafold.ebi.ac.uk/api/prediction/G1XJN1> | official | 2026-08-14 | ATCC Gpr3 model v6 metadata | used |
| S12 | [AlphaFold DB A0A437AGY2 API](https://alphafold.ebi.ac.uk/api/prediction/A0A437AGY2) | <https://alphafold.ebi.ac.uk/api/prediction/A0A437AGY2> | official | 2026-08-14 | GprC model v6 metadata | used |
| S13 | [NCBI ABX83020.1](https://www.ncbi.nlm.nih.gov/protein/ABX83020.1) | <https://www.ncbi.nlm.nih.gov/protein/ABX83020.1> | official | 2026-08-14 | B1NYG7 source strain KR314 | used |
| S14 | [NCBI ABX83005.1](https://www.ncbi.nlm.nih.gov/protein/ABX83005.1) | <https://www.ncbi.nlm.nih.gov/protein/ABX83005.1> | official | 2026-08-14 | G5ECA4 source strain JU1088 | used |
| S15 | [NCBI ABX82991.1](https://www.ncbi.nlm.nih.gov/protein/ABX82991.1) | <https://www.ncbi.nlm.nih.gov/protein/ABX82991.1> | official | 2026-08-14 | G5EEB2 source strain CB4853 | used |
| S16 | [NCBI RVD90404.1](https://www.ncbi.nlm.nih.gov/protein/RVD90404.1) | <https://www.ncbi.nlm.nih.gov/protein/RVD90404.1> | official | 2026-08-14 | GprC genomic protein and CBS H-5679 label | used |

## Evidence Table

| Claim/Requirement | Source ID | Pointer | Evidence Summary | Confidence | Caveats |
|-------------------|-----------|---------|------------------|------------|---------|
| Hu used AFDB models but did not name receptor accessions or versions | S1 | Methods, “Modelling and docking” | The paper names GprC, SRBC64 and DAF37 and the database only | high | Absence claim limited to the article text and extended data inspected here |
| Hu's C. elegans cloning material was N2 cDNA | S1 | Methods, “Strains and culture conditions” and “Plasmid construction” | N2 was the WT; receptor fragments and full-length genes were amplified from C. elegans cDNA | high | Sequenced clone files were not deposited |
| TWF154 Gpr2 is TGJ68930.1, 406 aa | S2 | source and ORIGIN fields | NCBI record gives strain TWF154, locus EYR41_005010 and 406 aa sequence | high | Protein is computationally annotated as hypothetical |
| TWF154 Gpr3 is TGJ67963.1, 401 aa | S3 | source and ORIGIN fields | NCBI record gives strain TWF154, locus EYR41_007055 and 401 aa sequence | high | Protein is computationally annotated as hypothetical |
| ATCC Gpr2 is a reviewed G1X9E2 sequence | S4 | Entry status, organism and sequence | UniProt maps GPR2 to ATCC 24927/CBS 115.81/DSM 1491, 406 aa | high | Structure remains predicted |
| ATCC Gpr3 is a reviewed G1XJN1 sequence | S5 | Entry status, organism and sequence | UniProt maps GPR3 to ATCC 24927/CBS 115.81/DSM 1491, 401 aa | high | Structure remains predicted |
| GprC is reviewed A0A437AGY2/DFL_001370, 538 aa | S6 | Entry status, gene and sequence | UniProt identifies gprC and links the 538 aa sequence to Hu 2024 | high | UniProt organism field does not display a strain |
| N2 srbc-64 is NP_740807.1/Y39G10AR.22, 289 aa | S7 | source and CDS fields | RefSeq gives Bristol N2, gene srbc-64, locus Y39G10AR.22 and the 289 aa translation | high | Transcript is labeled partial and partially confirmed by transcript evidence |
| G5ECV4 is the UniProt entry matching the N2 RefSeq/WormBase identity | S8 | Cross-references and sequence | UniProt links G5ECV4 to NP_740807.1 and Y39G10AR.22 with the same 289 aa sequence | high | UniProt entry is unreviewed and protein existence is predicted |
| The selected SRBC-64 structure is AF-G5ECV4-F1 v6 | S9 | API fields entryId, latestVersion, sequence, pdbUrl and modelCreatedDate | API returns the 289 aa N2-matching sequence and v6 PDB URL | high | Current API metadata does not identify Hu's historical model |
| The selected ATCC Gpr2 structure is AF-G1X9E2-F1 v6 | S10 | API fields entryId, latestVersion, sequence and pdbUrl | API sequence is 406 aa and matches the frozen FASTA | high | Predicted structure |
| The selected ATCC Gpr3 structure is AF-G1XJN1-F1 v6 | S11 | API fields entryId, latestVersion, sequence and pdbUrl | API sequence is 401 aa and matches the frozen FASTA | high | Predicted structure |
| The selected GprC structure is AF-A0A437AGY2-F1 v6 | S12 | API fields entryId, latestVersion, sequence and pdbUrl | API sequence is 538 aa and matches the frozen FASTA | high | Predicted structure; Hu did not state version |
| B1NYG7's source protein represents strain KR314 | S13 | source field | NCBI ABX83020.1 records a 290 aa SRBC-64 from KR314 | high | Not the N2 standard sequence |
| G5ECA4's source protein represents strain JU1088 | S14 | source field | NCBI ABX83005.1 records a 290 aa SRBC-64 from JU1088 | high | Not the N2 standard sequence |
| G5EEB2's source protein represents strain CB4853 | S15 | source field | NCBI ABX82991.1 records a 290 aa SRBC-64 from CB4853 | high | Not the N2 standard sequence |
| GprC's genome protein record uses the label CBS H-5679 | S16 | source field and DBLINK | RVD90404.1 maps DFL_001370 to PRJNA494930 and labels the source CBS H-5679 | high | Relationship to paper label CBS 349.94 remains unexplained |

## Audit Notes

- Checked SHA256 for all 12 frozen files; values are stored in `input_manifest.tsv`.
- Compared every FASTA with its PDB sequence. All six pairs match exactly and cover the full sequence.
- Compared the three pre-existing AFDB PDB files with fresh v6 downloads. All three are byte-identical.
- Compared the two TWF154 FASTAs with NCBI protein records. Both are exact sequence matches.
- Pairwise strain check: TWF154 versus ATCC differs at 7/406 Gpr2 positions and 6/401 Gpr3 positions; no insertions or deletions were found.
- Repository contains duplicate byte-identical copies under older names. Only manifest-listed paths have authority for this task.
