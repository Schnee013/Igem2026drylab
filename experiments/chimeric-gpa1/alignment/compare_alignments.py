"""比较 MUSCLE 和 ClustalΩ 比对结果的 C 端一致性。"""

from Bio import AlignIO
from pathlib import Path

BASE = Path(__file__).parent

def extract_cterminal(aln_file, n_cols=30):
    """提取比对的最后 n_cols 列。"""
    aln = AlignIO.read(aln_file, "fasta")
    aln_len = aln.get_alignment_length()
    start = max(0, aln_len - n_cols)
    result = {}
    for rec in aln:
        short_id = rec.id.split("|")[0]
        result[short_id] = str(rec.seq)[start:]
    return result

muscle = extract_cterminal(BASE / "muscle_alignment.afa", 40)
clustalo = extract_cterminal(BASE / "clustalo_alignment.afa", 40)

print("C-TERMINAL ALIGNMENT COMPARISON (last 40 columns)")
print("=" * 80)

all_match = True
for seq_id in muscle:
    m = muscle[seq_id]
    c = clustalo.get(seq_id, "N/A")
    match = "✓" if m == c else "✗"
    if m != c:
        all_match = False
    print(f"{seq_id:12s}")
    print(f"  MUSCLE:   {m}")
    print(f"  ClustalΩ: {c}")
    print(f"  Match: {match}")
    print()

if all_match:
    print("RESULT: C-terminal alignment CONSISTENT between MUSCLE and ClustalΩ")
else:
    print("RESULT: DISCREPANCY detected — manual inspection needed")
    # Show where differences are
    for seq_id in muscle:
        m = muscle[seq_id]
        c = clustalo.get(seq_id, "")
        if m != c:
            diff = ""
            for i, (a, b) in enumerate(zip(m, c)):
                diff += "^" if a != b else " "
            print(f"\n  {seq_id} diffs:")
            print(f"    MUSCLE:   {m}")
            print(f"    ClustalΩ: {c}")
            print(f"    Diff:     {diff}")
