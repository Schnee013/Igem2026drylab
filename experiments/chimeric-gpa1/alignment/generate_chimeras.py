"""
生成嵌合 Gpa1 候选序列。

设计逻辑:
- 骨架: 酵母 Gpa1 (P08539, 472 aa)
- 供体 C 端: A. oligospora Gpa2 (Gpr2/3) 或 A. flagrans GasA (GprC)
- 替换量: 5 / 10 / 15 / 25 / 37 残基

切割位点安全性验证 (Hara 2012 + Ueda 2003):
- gust37 (last 37 aa) = 功能正常 (酵母 + 哺乳动物)
- gust44 (last 44 aa) = 酵母中失败 (侵入 α4 helix, T433 被替换)
- 最大替换 = 37 aa, Gpa1 T433 保留在骨架中 (pos 433 < 436=cut)

结构域边界 (基于比对保守性分析):
- pos -5 ~ -1: eCT (extreme C-terminus), 受体偶联特异性决定区
- pos -7: L (fully conserved), α5 helix 终止标志
- pos -12: I (fully conserved), α5 helix 中段
- pos -20: V (fully conserved), α5 helix 核心
- pos -26 ~ -27: DT (fully conserved), α5 helix 起始/β6 连接
- pos -37: β6 sheet 区域, Ueda2003 功能化下限

C25/C37 设计理由 (v2, 2026-04-13):
- C5/C10/C15 AF3 结果: cognate ≈ cross, 嫁接特异性未体现
- Ueda2003: 5/11/23 aa 均失败, 37+ aa 才功能化 (β6 sheet 不可缺)
- C25: 覆盖完整 α5 helix + eCT, 测试 α5 是否足够
- C37: 覆盖 β6 + α5 + eCT, 匹配 Ueda2003/Hara2012 功能阈值
"""

from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO
from pathlib import Path
import textwrap

BASE = Path(__file__).parent.parent

# --- 读取源序列 ---
def read_fasta(fpath):
    rec = next(SeqIO.parse(fpath, "fasta"))
    return str(rec.seq).replace("\n", "")

gpa1 = read_fasta(BASE / "sequences/yeast_Gpa1_P08539.fasta")
gpa2 = read_fasta(BASE / "sequences/Ao_Gpa2_TGJ64397.fasta")
gasA = read_fasta(BASE / "sequences/Af_GasA_A0A436ZRX2.fasta")

assert len(gpa1) == 472, f"Gpa1 length {len(gpa1)} != 472"

# --- 生成嵌合体 ---
chimeras = []

donors = [
    ("Ao", "Gpa2", gpa2, "A. oligospora Gpa2", "Gpr2/Gpr3 (cAMP-PKA)"),
    ("Af", "GasA", gasA, "A. flagrans GasA", "GprC (MAPK)"),
]

for species_code, protein_name, donor_seq, full_name, receptor_info in donors:
    for n_replace in [5, 10, 15, 25, 37]:
        backbone = gpa1[:472 - n_replace]
        graft = donor_seq[-n_replace:]
        chimera_seq = backbone + graft

        chimera_id = f"Gpa1-{species_code}{protein_name}-C{n_replace}"
        description = (
            f"Chimeric Gpa1: Sc_Gpa1(1-{472-n_replace}) + {full_name}(last {n_replace} aa) "
            f"| target receptor: {receptor_info} "
            f"| junction: ...{gpa1[472-n_replace-3:472-n_replace]}|{graft[:3]}..."
        )

        chimeras.append(SeqRecord(
            Seq(chimera_seq),
            id=chimera_id,
            description=description,
        ))

# --- 写入单独文件和合并文件 ---
chimera_dir = BASE / "chimeras"
chimera_dir.mkdir(exist_ok=True)

for rec in chimeras:
    fpath = chimera_dir / f"{rec.id}.fasta"
    SeqIO.write(rec, fpath, "fasta")
    print(f"Written: {fpath.name}")

# 合并文件 (for AF3 batch)
all_path = chimera_dir / "all_chimeras.fasta"
SeqIO.write(chimeras, all_path, "fasta")
print(f"\nWritten combined: {all_path.name}")

# --- 输出汇总表 ---
print("\n" + "=" * 100)
print("CHIMERA SUMMARY")
print("=" * 100)
print(f"{'ID':30s} {'Length':6s} {'Backbone':12s} {'Graft':20s} {'Junction':20s}")
print("-" * 100)

for rec in chimeras:
    seq = str(rec.seq)
    n = len(seq) - (472 - int(rec.id.split("-C")[-1]))
    backbone_end = 472 - n
    graft = seq[backbone_end:]
    junction = f"...{gpa1[backbone_end-3:backbone_end]}|{graft[:5]}..."
    print(f"{rec.id:30s} {len(seq):6d} {'Gpa1(1-'+str(backbone_end)+')':12s} {graft:20s} {junction:20s}")

# --- 同时生成 WT 对照 FASTA ---
wt_rec = SeqRecord(
    Seq(gpa1),
    id="Gpa1-WT",
    description="Wild-type Sc Gpa1 (P08539, 472 aa) | positive control for AF3",
)
wt_path = chimera_dir / "Gpa1-WT.fasta"
SeqIO.write(wt_rec, wt_path, "fasta")
print(f"\nWritten WT control: {wt_path.name}")
