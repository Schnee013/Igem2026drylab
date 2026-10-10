# 受体化学检查后，将特定的HIS组氨酸确定为HID/HIE/HIP，并在pH 7.4下重新生成氢。输出结构和微状态报告将被写入文件。

from pathlib import Path
import hashlib
import json

from openmm.app import PDBFile, Modeller, ForceField, element

INPUT = Path("receptor_ppm_noDUM.pdb")
OUTPUT = Path("receptor_pH7p4_confirmed.pdb")
REPORT = Path("receptor_pH7p4_microstates.json")

TARGET_PH = 7.4

# key = (chain ID, residue number, insertion code)
DECISIONS = {
    ("A", "123", ""): "HID",
    # ("A", "210", ""): "HIE",
    # ("B", "45",  ""): "HIP",
}

if OUTPUT.exists() or REPORT.exists():
    raise FileExistsError("输出已存在；不要无意覆盖正式结构")

pdb = PDBFile(str(INPUT))
modeller = Modeller(pdb.topology, pdb.positions)

# 若输入已有氢，先删除，确保所有氢都按本次决定重新生成和优化。
old_hydrogens = [
    atom for atom in modeller.topology.atoms()
    if atom.element == element.hydrogen
]
if old_hydrogens:
    modeller.delete(old_hydrogens)

residues = list(modeller.topology.residues())
variants = [None] * len(residues)
matched = {}

for i, residue in enumerate(residues):
    key = (
        residue.chain.id,
        residue.id,
        residue.insertionCode or "",
    )
    if key not in DECISIONS:
        continue

    if residue.name != "HIS":
        raise RuntimeError(
            f"{key} 预期为 HIS，实际为 {residue.name}"
        )

    variants[i] = DECISIONS[key]
    matched[key] = i

missing = set(DECISIONS) - set(matched)
if missing:
    raise RuntimeError(f"没有在输入结构中找到这些残基：{missing}")

forcefield = ForceField("amber99sb.xml")

# 明确指定的 variant 会删除不兼容的氢，再添加正确的氢。
actual_variants = modeller.addHydrogens(
    forcefield,
    pH=TARGET_PH,
    variants=variants,
)

expected_ring_h = {
    "HID": {"HD1"},
    "HIE": {"HE2"},
    "HIP": {"HD1", "HE2"},
}

realized = []

for key, residue_index in matched.items():
    residue = residues[residue_index]
    requested = DECISIONS[key]
    actual = actual_variants[residue_index]

    atom_names = {atom.name for atom in residue.atoms()}
    observed_ring_h = atom_names & {"HD1", "HE2"}

    if actual != requested:
        raise RuntimeError(
            f"{key}: 要求 {requested}，OpenMM 返回 {actual}"
        )

    if observed_ring_h != expected_ring_h[requested]:
        raise RuntimeError(
            f"{key}: {requested} 应有 {expected_ring_h[requested]}，"
            f"实际发现 {observed_ring_h}"
        )

    realized.append({
        "chain": key[0],
        "residue_id": key[1],
        "insertion_code": key[2],
        "requested_variant": requested,
        "actual_variant": actual,
        "ring_hydrogens": sorted(observed_ring_h),
    })

with OUTPUT.open("w") as handle:
    PDBFile.writeFile(
        modeller.topology,
        modeller.positions,
        handle,
        keepIds=True,
    )

report = {
    "target_pH": TARGET_PH,
    "input": str(INPUT),
    "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
    "output": str(OUTPUT),
    "output_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
    "microstates": realized,
}

REPORT.write_text(
    json.dumps(report, indent=2, ensure_ascii=False) + "\n"
)

print(f"wrote: {OUTPUT}")
print(f"wrote: {REPORT}")