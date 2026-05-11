# True Gpr2/Gpa2 核查记录

> 日期: 2026-04-27
> 问题: Kuo2024 / 数据库中是否存在 GPA2 <-> GPA3 标签互换, 导致本项目 chimeric Gpa1 pipeline 误用非天然偶联 G alpha 序列?

## 结论

当前证据支持: 本项目使用的 `TGJ64397.1` 是 Kuo2024 补充表中 `GPA2` 构建对应的 G alpha 序列, 未发现把 `GPA3` 错当 `GPA2` 的证据。

因此:

- `Gpr2/Gpr3 -> AoGpa2` 作为 cognate 配对暂不撤回。
- `Gpa1-AoGpa2-C*` 系列 AF3 / MD 起始结构暂不需要因该问题重跑。
- `Gpr2 x AoGpa2 ipTM 低可能是 AF3 假阴性` 这一解释仍可保留, 但应补充本核查指针。
- 若湿实验团队另有 GPA2/GPA3 标签互换证据, 需要提供具体 gene ID / accession / CDS 序列, 不能只依据名称层面的传闻推翻当前序列链。

## 核查对象

本项目当前 AoGpa2 源文件:

- `experiments/chimeric-gpa1/sequences/Ao_Gpa2_TGJ64397.fasta`
- Header: `TGJ64397.1 Guanine nucleotide-binding protein alpha-2 subunit [Orbilia oligospora]`
- N 端: `MGGCMS...`
- C 端: `...QATDTSNIRLVFAAVKETILQNALKDSGIL`

下游依赖:

- `experiments/chimeric-gpa1/alignment/generate_chimeras.py` 读取 `Ao_Gpa2_TGJ64397.fasta`
- `experiments/chimeric-gpa1/chimeras/Gpa1-AoGpa2-C*.fasta`
- `experiments/chimeric-gpa1/analysis/ranking_summary.md`
- Chimeric MD: Ch-1 / Ch-2 / Ch-4

## 官方来源

1. Kuo2024 主文
   - Nature Microbiology: `https://www.nature.com/articles/s41564-024-01679-w`
   - DOI: `10.1038/s41564-024-01679-w`
   - PubMed: `38649409`

2. Kuo2024 官方补充表
   - 文件: `41564_2024_1679_MOESM4_ESM.xlsx`
   - URL: `https://static-content.springer.com/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM4_ESM.xlsx`
   - 本次临时下载位置: `/tmp/kuo2024_supp.xlsx`

3. NCBI protein record
   - Accession: `TGJ64397.1`
   - EFetch URL: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=TGJ64397.1&rettype=fasta&retmode=text`
   - 本次临时下载位置: `/tmp/TGJ64397.fasta`

## 关键证据

### 1. Kuo2024 补充表 GPA2 forward primer 匹配 TGJ64397.1 N 端

Kuo2024 Supplementary Table 3:

| Row | Primer | Sequence | Description |
|---:|---|---|---|
| 137 | 4207 | `ATATAAAACAGCTAGCATGGGTGGCTGCATGTCG` | Amplification of GPA2 tagged with Myc (forward) |
| 139 | 4209 | `ATATAAAACAGCTAGCATGTGCATGGGTGGAGATG` | Amplification of GPA3 tagged with Myc (forward) |

去掉前置接头/限制位点后:

- GPA2 gene-specific start: `ATGGGTGGCTGCATGTCG` -> translates to `MGGCMS`
- GPA3 gene-specific start: `ATGTGCATGGGTGGAGATG` -> translates to `MCMGGD`

本项目 `TGJ64397.1` N 端:

```text
MGGCMSREASEEMEQRKKS...
```

判定: `TGJ64397.1` 与 Kuo2024 `GPA2` primer 匹配, 与 `GPA3` primer 不匹配。

### 2. Kuo2024 GPA2 reverse primer 匹配 TGJ64397.1 C 端

Kuo2024 Supplementary Table 3:

| Row | Primer | Sequence | Description |
|---:|---|---|---|
| 138 | 4208 | `AATTCAATTCAATGGCGCGCCGAGGTCTTCTTCGGAAATCAACTTCTGTTCTGACCCACCGCCACCTAATATACCGGAGTCCTTGAGGGC` | Amplification of GPA2 tagged with Myc (reverse) |
| 140 | 4210 | `ATTCAATTCAATGGCGCGCCGAGGTCTTCTTCGGAAATCAACTTCTGTTCTGACCCACCGCCACCTAGTATCAATTGGTGGAGATTCTTT` | Amplification of GPA3 tagged with Myc (reverse) |

GPA2 reverse primer 的基因特异尾段 `AATATACCGGAGTCCTTGAGGGC` 反向互补后为:

```text
GCCCTCAAGGACTCCGGTATATT
```

按正确 reading frame 可翻译出:

```text
ALKDSGI
```

本项目 `TGJ64397.1` C 端:

```text
...KETILQNALKDSGIL
```

判定: Kuo2024 `GPA2` reverse primer 覆盖 `TGJ64397.1` C 端核心片段 `ALKDSGI`; 这与当前 chimeric 设计使用的 C 端供体一致。

### 3. Kuo2024 strain/plasmid 表确认 Fig. 4a 使用的是 GPA2-Myc 构建

Kuo2024 Supplementary Table 4:

| Row | Construct / strain | Relevant genotype |
|---:|---|---|
| 33 | CYK131 | `pPGK::GPA2-MYC-NAT` |
| 36 | CYK111 | `pPGK::GPR2-3xHA-URA3, pPGK::GPA2-MYC-NAT` |
| 39 | CYK99 | `pPGK::GPR3-3xHA-URA3, pPGK::GPA2-MYC-NAT` |
| 65 | pPH1188 | `pPGK::GPA2-MYC cDNA NAT AmpR` |

结合 Supplementary Table 3 的 GPA2 primers, Fig. 4a 中的 `GPA2-MYC` 构建指向 `MGGCMS...ALKDSGI...` 这条序列, 即本项目当前的 `TGJ64397.1`。

### 4. NCBI `TGJ64397.1` 与本地 FASTA 序列一致

NCBI EFetch 返回:

```text
>TGJ64397.1 Guanine nucleotide-binding protein alpha-2 subunit [Orbilia oligospora]
MGGCMSREASEEMEQRKKSQAIDREIMDDSRRLRRECKILLLGSGESGKSTIVKQMKIIHQNGYTVDELQ
...
KDSGIL
```

本地文件 diff 结果: 仅 header 多了项目注释, 蛋白序列无差异。

## 命令摘录

下载官方补充表:

```bash
curl -L -o /tmp/kuo2024_supp.xlsx \
  'https://static-content.springer.com/esm/art%3A10.1038%2Fs41564-024-01679-w/MediaObjects/41564_2024_1679_MOESM4_ESM.xlsx'
```

搜索补充表中的 GPA 构建:

```bash
python - <<'PY'
from openpyxl import load_workbook
wb = load_workbook('/tmp/kuo2024_supp.xlsx', data_only=True)
for ws in wb.worksheets:
    for row in ws.iter_rows():
        text = '\t'.join('' if c.value is None else str(c.value) for c in row)
        if any(k in text.lower() for k in ['gpa2', 'gpa3', 'gpa1', 'myc', 'q208l']):
            print(ws.title, row[0].row, text)
PY
```

拉取 NCBI `TGJ64397.1`:

```bash
curl -L \
  'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id=TGJ64397.1&rettype=fasta&retmode=text' \
  -o /tmp/TGJ64397.fasta
```

比对 NCBI 与本地 FASTA:

```bash
diff -u /tmp/TGJ64397.fasta experiments/chimeric-gpa1/sequences/Ao_Gpa2_TGJ64397.fasta
```

## 对项目的具体影响评估

| 模块 | 是否受影响 | 说明 |
|---|---|---|
| docking-repro | 否 | 受体-配体对接不依赖 G alpha 序列 |
| GprC x AfGasA | 否 | 使用 `A0A436ZRX2`, 与 Ao GPA2/GPA3 问题无关 |
| Ste2 x Gpa1-WT control | 否 | 酵母内源阳性对照 |
| Gpr2/Gpr3 x AoGpa2 AF3 | 暂不受影响 | 当前 `TGJ64397.1` 与 Kuo2024 `GPA2` 构建匹配 |
| Ch-1 / Ch-2 / Ch-4 MD | 暂不受影响 | 不因本问题重跑, 但应在后续文档加本核查指针 |
| `Gpr2-AoGpa2 ipTM 低 = AF3 假阴性` 解读 | 保留但加注 | 序列身份已核对; 低 ipTM 仍需按 AF3 局限解释, 不可升级为功能失败 |

## 保留的不确定性

Kuo2024 补充表没有直接写 `GPA2 = TGJ64397.1` accession。当前结论依赖:

1. Kuo2024 `GPA2` primers 的 N 端和 C 端均匹配 `TGJ64397.1`;
2. NCBI 当前注释 `TGJ64397.1` 为 alpha-2 subunit;
3. 本地文件与 NCBI `TGJ64397.1` 序列一致。

如果后续有人提出 GPA2/GPA3 标签互换, 需要提供至少一项:

- Kuo2024 原始 plasmid / CDS 序列;
- GPA2/GPA3 的 AOL gene ID 与 NCBI protein accession 映射表;
- 可复现的 primer-to-genome mapping;
- 湿实验团队发现的具体数据库版本和记录截图/URL。

在没有这些新增证据前, 不应暂停或推翻当前 `TGJ64397.1` 作为 AoGpa2 C 端供体的设计。
