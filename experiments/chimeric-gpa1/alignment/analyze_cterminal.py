"""分析 MUSCLE 比对结果的 C 端区域，用于确定嵌合切割位点。"""

from Bio import AlignIO
from pathlib import Path

ALN_FILE = Path(__file__).parent / "muscle_alignment.afa"

aln = AlignIO.read(ALN_FILE, "fasta")

# 提取每条序列的 ID 和 ungapped 序列
seqs = {}
for rec in aln:
    short_id = rec.id.split("|")[0]
    seqs[short_id] = str(rec.seq)

# --- 1. 打印全长比对的 C 端最后 80 列 ---
aln_len = aln.get_alignment_length()
start_col = max(0, aln_len - 80)

print("=" * 90)
print(f"C-TERMINAL ALIGNMENT (columns {start_col+1}–{aln_len} of {aln_len})")
print("=" * 90)

for rec in aln:
    short_id = rec.id.split("|")[0]
    segment = str(rec.seq)[start_col:]
    print(f"{short_id:12s} {segment}")

# --- 2. 提取 ungapped C 端并逐位置对齐展示 ---
print("\n" + "=" * 90)
print("UNGAPPED C-TERMINAL SEQUENCES (last 30 residues)")
print("=" * 90)

for rec in aln:
    short_id = rec.id.split("|")[0]
    ungapped = str(rec.seq).replace("-", "")
    last30 = ungapped[-30:]
    print(f"{short_id:12s} ...{last30}  (total {len(ungapped)} aa)")

# --- 3. C 端 5/10/15 切割方案 ---
print("\n" + "=" * 90)
print("CHIMERIC REPLACEMENT SCHEMES (Gpa1 backbone + fungal Gα C-terminal)")
print("=" * 90)

gpa1_ungapped = seqs["Sc_Gpa1"].replace("-", "")
gpa1_len = len(gpa1_ungapped)

donors = {
    "Ao_Gpa2": ("A. oligospora Gpa2", "Gpr2/Gpr3"),
    "Af_GasA": ("A. flagrans GasA", "GprC"),
}

for donor_key, (donor_name, receptor) in donors.items():
    donor_ungapped = seqs[donor_key].replace("-", "")
    print(f"\n--- Donor: {donor_name} (for {receptor}) ---")
    for n in [5, 10, 15]:
        backbone = gpa1_ungapped[:gpa1_len - n]
        graft = donor_ungapped[-n:]
        chimera = backbone + graft
        print(f"\n  Chimera-{n} ({donor_key}):")
        print(f"    Gpa1 backbone: residues 1–{gpa1_len - n} ({gpa1_len - n} aa)")
        print(f"    Graft from {donor_key}: last {n} aa = {graft}")
        print(f"    Junction: ...{gpa1_ungapped[gpa1_len-n-5:gpa1_len-n]}|{graft}")
        print(f"    Total length: {len(chimera)} aa")

# --- 4. 与 Hara2012 gustducin 模板的 C 端对比 ---
print("\n" + "=" * 90)
print("COMPARISON WITH HARA2012 GUSTDUCIN TEMPLATE")
print("=" * 90)

gnat3_ungapped = seqs["Rn_GNAT3"].replace("-", "")

print(f"\n  Rn_GNAT3 last 5:  {gnat3_ungapped[-5:]}")
print(f"  Ao_Gpa2  last 5:  {seqs['Ao_Gpa2'].replace('-','')[-5:]}")
print(f"  Af_GasA  last 5:  {seqs['Af_GasA'].replace('-','')[-5:]}")
print(f"  Sc_Gpa1  last 5:  {gpa1_ungapped[-5:]}")

print(f"\n  Rn_GNAT3 last 10: {gnat3_ungapped[-10:]}")
print(f"  Ao_Gpa2  last 10: {seqs['Ao_Gpa2'].replace('-','')[-10:]}")
print(f"  Af_GasA  last 10: {seqs['Af_GasA'].replace('-','')[-10:]}")
print(f"  Sc_Gpa1  last 10: {gpa1_ungapped[-10:]}")

print(f"\n  Rn_GNAT3 last 15: {gnat3_ungapped[-15:]}")
print(f"  Ao_Gpa2  last 15: {seqs['Ao_Gpa2'].replace('-','')[-15:]}")
print(f"  Af_GasA  last 15: {seqs['Af_GasA'].replace('-','')[-15:]}")
print(f"  Sc_Gpa1  last 15: {gpa1_ungapped[-15:]}")

# --- 5. 保守性分析 (C 端 30 列) ---
print("\n" + "=" * 90)
print("CONSERVATION ANALYSIS (last 30 alignment columns)")
print("=" * 90)

for col_offset in range(30, 0, -1):
    col_idx = aln_len - col_offset
    residues = [str(rec.seq)[col_idx] for rec in aln]
    non_gap = [r for r in residues if r != "-"]
    if len(non_gap) == 0:
        cons = "gap"
    elif len(set(non_gap)) == 1:
        cons = "***"
    elif len(set(non_gap)) <= 2:
        cons = " : "
    else:
        cons = " . "
    col_str = " ".join(f"{r}" for r in residues)
    print(f"  col {col_idx+1:3d} (pos -{col_offset:2d}): {col_str}  {cons}")
