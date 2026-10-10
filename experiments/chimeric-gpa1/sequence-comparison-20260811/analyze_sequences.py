#!/usr/bin/env python3
"""Reproducible sequence comparison for four fungal G-alpha proteins.

The four input FASTA files are immutable download artifacts.  This script
validates them, runs protein global alignments with a Needleman-Wunsch
equivalent implementation, runs Clustal Omega for the four-way MSA, and
writes all derived statistics and readable alignments below this directory.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import platform
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import Bio
from Bio import Align, AlignIO, SeqIO
from Bio.Align import substitution_matrices
from Bio.Seq import Seq


ROOT = Path(__file__).resolve().parent
SEQUENCE_DIR = ROOT / "sequences"
RECORD_DIR = ROOT / "records"
ALIGNMENT_DIR = ROOT / "alignments"
PAIRWISE_DIR = ALIGNMENT_DIR / "pairwise"
RESULTS_DIR = ROOT / "results"

CANONICAL_AA = set("ACDEFGHIKLMNPQRSTVWY")


@dataclass(frozen=True)
class ProteinSpec:
    key: str
    accession: str
    fasta_name: str
    species: str
    protein_name: str
    database: str
    url: str
    expected_length: int
    expected_sha256: str


PROTEINS = (
    ProteinSpec(
        key="ScGpa1",
        accession="P08539",
        fasta_name="ScGpa1_P08539.fasta",
        species="Saccharomyces cerevisiae (S288c)",
        protein_name="Gpa1 / guanine nucleotide-binding protein alpha-1 subunit",
        database="UniProtKB/Swiss-Prot (reviewed)",
        url="https://www.uniprot.org/uniprotkb/P08539/entry",
        expected_length=472,
        expected_sha256="1737d0116e06108c4613f504e92ed747bf46dcbc86b62d362fda9668458387bb",
    ),
    ProteinSpec(
        key="ScGpa2",
        accession="P10823",
        fasta_name="ScGpa2_P10823.fasta",
        species="Saccharomyces cerevisiae (S288c)",
        protein_name="Gpa2 / guanine nucleotide-binding protein alpha-2 subunit",
        database="UniProtKB/Swiss-Prot (reviewed)",
        url="https://www.uniprot.org/uniprotkb/P10823/entry",
        expected_length=449,
        expected_sha256="f6b1b72091c6dd0cb93109714556908a8e4d469f0c1f981c1a4ff2b93b7f47a0",
    ),
    ProteinSpec(
        key="AoGpa2",
        accession="TGJ64397.1",
        fasta_name="AoGpa2_TGJ64397.1.fasta",
        species="Arthrobotrys oligospora TWF154 (NCBI record: Orbilia oligospora)",
        protein_name="Gpa2 / guanine nucleotide-binding protein alpha-2 subunit",
        database="NCBI Protein/GenBank",
        url="https://www.ncbi.nlm.nih.gov/protein/TGJ64397.1",
        expected_length=356,
        expected_sha256="da014c9cde006fedac16398ec2cd149a9a3029a53c666b2a883e3fcf3dce2fc3",
    ),
    ProteinSpec(
        key="AfGasA",
        accession="A0A436ZRX2",
        fasta_name="AfGasA_A0A436ZRX2.fasta",
        species=(
            "Arthrobotrys flagrans (sequence-database strain label: CBS H-5679; "
            "Hu2024 experimental strain: CBS 349.94; equivalence unresolved)"
        ),
        protein_name="GasA / guanine nucleotide-binding protein alpha subunit A",
        database="UniProtKB/Swiss-Prot (reviewed); cross-checked with NCBI RVD81648.1",
        url="https://www.uniprot.org/uniprotkb/A0A436ZRX2/entry",
        expected_length=353,
        expected_sha256="872b7ea0fce717601ad315513b9b8b927704dae839631ca720527c6b7a252796",
    ),
)

PROTEIN_KEYS = tuple(spec.key for spec in PROTEINS)


# Direct database feature coordinates, all 1-based and inclusive.
# Sc features are from the downloaded UniProt flat files; Ao features are from
# the CDD feature table in the downloaded NCBI GenBank record.
DIRECT_FEATURES: dict[str, dict[str, tuple[int, int]]] = {
    "ScGpa1": {
        "G1_P_loop": (43, 56),
        "Switch_I_G2": (292, 300),
        "G3": (315, 324),
        "G4": (384, 391),
        "G5": (442, 447),
        "ScGpa1_insert": (127, 235),
    },
    "ScGpa2": {
        "G1_P_loop": (125, 138),
        "Switch_I_G2": (268, 276),
        "G3": (292, 301),
        "G4": (361, 368),
        "G5": (418, 423),
        "N_terminal_disordered": (1, 91),
    },
    "AoGpa2": {
        "G1_P_loop": (43, 50),
        "Switch_I_G2": (180, 188),
        "G3": (204, 207),
        "Switch_II": (205, 221),
        "G4": (273, 276),
        "G5": (327, 329),
        "CDD_receptor_binding": (319, 335),
    },
    "AfGasA": {
        "G1_P_loop": (40, 47),
        "Switch_I_G2": (176, 184),
        "G3": (200, 203),
        "Switch_II": (201, 217),
        "G4": (269, 272),
        "G5": (324, 326),
        # The NCBI CDD feature is discontinuous: 316..327,329..332.
        "CDD_receptor_binding_span": (316, 332),
    },
}


# Operational alpha5 boundary: the conserved Asp immediately after the aligned
# three-residue G5 core ([C/Q]AT) through the native C terminus.  This gives a
# 27-28 aa region rather than an arbitrary last-N-residue slice.
ALPHA5_REGIONS: dict[str, tuple[int, int]] = {
    "ScGpa1": (446, 472),
    "ScGpa2": (422, 449),
    "AoGpa2": (330, 356),
    "AfGasA": (327, 353),
}


# G-alpha domain starts are directly annotated (UniProt/NCBI CDD).  The core
# estimate starts there, retains the native C terminus, and removes only the
# documented 109-aa ScGpa1-specific insert.
G_ALPHA_STARTS = {"ScGpa1": 40, "ScGpa2": 122, "AoGpa2": 37, "AfGasA": 32}


PAIR_KEYS = (
    ("ScGpa1", "ScGpa2"),
    ("ScGpa1", "AoGpa2"),
    ("ScGpa2", "AoGpa2"),
    ("ScGpa1", "AfGasA"),
    ("ScGpa2", "AfGasA"),
    ("AoGpa2", "AfGasA"),
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def first_header(path: Path) -> str:
    with path.open(encoding="utf-8") as handle:
        line = handle.readline().rstrip("\n\r")
    if not line.startswith(">"):
        raise ValueError(f"Missing FASTA header in {path}")
    return line


def subseq(sequence: str, start: int, end: int) -> str:
    return sequence[start - 1 : end]


def make_aligner() -> tuple[Align.PairwiseAligner, object]:
    matrix = substitution_matrices.load("BLOSUM62")
    aligner = Align.PairwiseAligner()
    aligner.mode = "global"
    aligner.substitution_matrix = matrix
    # These assignments set left, internal, and right insertion/deletion gaps,
    # so terminal gaps are penalized using the same affine scheme.
    aligner.open_gap_score = -10.0
    aligner.extend_gap_score = -0.5
    return aligner, matrix


def marker(a: str, b: str, matrix: object) -> str:
    if "-" in (a, b):
        return " "
    if a == b:
        return "|"
    return ":" if matrix[a, b] > 0 else "."


def alignment_stats(alignment: Align.Alignment, matrix: object) -> dict[str, float | int]:
    a = str(alignment[0])
    b = str(alignment[1])
    if len(a) != len(b):
        raise AssertionError("Gapped alignment rows have unequal lengths")
    marks = [marker(x, y, matrix) for x, y in zip(a, b)]
    aligned_length = len(a)
    identities = marks.count("|")
    positives = identities + marks.count(":")
    gaps = sum("-" in (x, y) for x, y in zip(a, b))
    residue_columns = aligned_length - gaps
    return {
        "aligned_length": aligned_length,
        "identity_n": identities,
        "identity_pct": 100.0 * identities / aligned_length,
        "similarity_n": positives,
        "similarity_pct": 100.0 * positives / aligned_length,
        "gap_columns_n": gaps,
        "gap_columns_pct": 100.0 * gaps / aligned_length,
        "aligned_residue_columns": residue_columns,
        "aligned_residue_identity_pct": 100.0 * identities / residue_columns,
        "score": float(alignment.score),
    }


def independently_recalculate_score(row_a: str, row_b: str, matrix: object) -> float:
    """Recalculate BLOSUM62 + affine-gap score from the emitted gapped rows."""
    score = 0.0
    active_gap_row: str | None = None
    for a, b in zip(row_a, row_b):
        if a == "-" and b == "-":
            raise AssertionError("Pairwise alignment contains a double-gap column")
        if a == "-" or b == "-":
            gap_row = "a" if a == "-" else "b"
            score += -0.5 if gap_row == active_gap_row else -10.0
            active_gap_row = gap_row
        else:
            score += float(matrix[a, b])
            active_gap_row = None
    return score


def coordinate_span(fragment: str, position_before: int) -> tuple[str, int]:
    count = sum(char != "-" for char in fragment)
    if count == 0:
        return "-", position_before
    start = position_before + 1
    end = position_before + count
    return f"{start}-{end}", end


def readable_pairwise(
    key_a: str,
    key_b: str,
    alignment: Align.Alignment,
    matrix: object,
    stats: dict[str, float | int],
    width: int = 60,
) -> str:
    row_a = str(alignment[0])
    row_b = str(alignment[1])
    marks = "".join(marker(a, b, matrix) for a, b in zip(row_a, row_b))
    lines = [
        f"# {key_a} vs {key_b}",
        "# Algorithm: global Needleman-Wunsch equivalent (Biopython PairwiseAligner)",
        "# Matrix: BLOSUM62; gap open: -10.0; gap extend: -0.5; terminal gaps penalized",
        f"# Score: {stats['score']:.1f}",
        f"# Length: {stats['aligned_length']}",
        f"# Identity: {stats['identity_n']}/{stats['aligned_length']} ({stats['identity_pct']:.3f}%)",
        f"# Similarity (BLOSUM62 > 0): {stats['similarity_n']}/{stats['aligned_length']} ({stats['similarity_pct']:.3f}%)",
        f"# Gap columns: {stats['gap_columns_n']}/{stats['aligned_length']} ({stats['gap_columns_pct']:.3f}%)",
        "# Markers: | exact; : conservative/positive; . non-conservative; blank gap",
        "",
    ]
    pos_a = 0
    pos_b = 0
    label_width = max(len(key_a), len(key_b))
    for offset in range(0, len(row_a), width):
        chunk_a = row_a[offset : offset + width]
        chunk_b = row_b[offset : offset + width]
        chunk_m = marks[offset : offset + width]
        span_a, pos_a = coordinate_span(chunk_a, pos_a)
        span_b, pos_b = coordinate_span(chunk_b, pos_b)
        lines.extend(
            [
                f"{key_a:<{label_width}} {span_a:>9}  {chunk_a}",
                f"{'':<{label_width}} {'':>9}  {chunk_m}",
                f"{key_b:<{label_width}} {span_b:>9}  {chunk_b}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def run_pair(
    key_a: str,
    sequence_a: str,
    key_b: str,
    sequence_b: str,
    aligner: Align.PairwiseAligner,
    matrix: object,
    output_path: Path | None = None,
) -> tuple[Align.Alignment, dict[str, float | int]]:
    alignment = aligner.align(sequence_a, sequence_b)[0]
    row_a = str(alignment[0])
    row_b = str(alignment[1])
    if row_a.replace("-", "") != sequence_a or row_b.replace("-", "") != sequence_b:
        raise AssertionError("Alignment rows do not reconstruct the complete input sequences")
    independently_scored = independently_recalculate_score(row_a, row_b, matrix)
    if abs(independently_scored - float(alignment.score)) > 1e-6:
        raise AssertionError(
            f"Independent score {independently_scored} != aligner score {alignment.score}"
        )
    stats = alignment_stats(alignment, matrix)
    stats["independently_recalculated_score"] = independently_scored
    if output_path is not None:
        output_path.write_text(
            readable_pairwise(key_a, key_b, alignment, matrix, stats),
            encoding="utf-8",
        )
    return alignment, stats


def audit_score_tied_optimal_paths(
    sequence_a: str,
    sequence_b: str,
    aligner: Align.PairwiseAligner,
    matrix: object,
) -> dict[str, object]:
    """Summarize metric variants across every score-tied optimal path."""
    alignments = aligner.align(sequence_a, sequence_b)
    variant_counts: dict[tuple[int, int, int, int], int] = {}
    for alignment in alignments:
        stats = alignment_stats(alignment, matrix)
        key = (
            int(stats["aligned_length"]),
            int(stats["identity_n"]),
            int(stats["similarity_n"]),
            int(stats["gap_columns_n"]),
        )
        variant_counts[key] = variant_counts.get(key, 0) + 1
    variants = []
    for (length, identities, similarities, gaps), count in sorted(variant_counts.items()):
        variants.append(
            {
                "path_count": count,
                "aligned_length": length,
                "identity_n": identities,
                "identity_pct": 100.0 * identities / length,
                "similarity_n": similarities,
                "similarity_pct": 100.0 * similarities / length,
                "gap_columns_n": gaps,
                "gap_columns_pct": 100.0 * gaps / length,
            }
        )
    return {
        "optimal_path_count": len(alignments),
        "reported_path": "first optimal path returned by Biopython PairwiseAligner",
        "metric_variants": variants,
    }


def fasta_write(records: Iterable[tuple[str, str, str]], path: Path) -> None:
    lines: list[str] = []
    for identifier, description, sequence in records:
        lines.append(f">{identifier} {description}")
        lines.extend(sequence[i : i + 60] for i in range(0, len(sequence), 60))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def msa_position_maps(msa: Align.MultipleSeqAlignment) -> dict[str, list[int | None]]:
    maps: dict[str, list[int | None]] = {}
    for record in msa:
        current = 0
        mapped: list[int | None] = []
        for char in str(record.seq):
            if char == "-":
                mapped.append(None)
            else:
                current += 1
                mapped.append(current)
        maps[record.id] = mapped
    return maps


def columns_for_range(position_map: list[int | None], start: int, end: int) -> set[int]:
    return {
        index
        for index, coordinate in enumerate(position_map)
        if coordinate is not None and start <= coordinate <= end
    }


def fragment_coordinates(position_map: list[int | None], start_col: int, end_col: int) -> str:
    coordinates = [x for x in position_map[start_col : end_col + 1] if x is not None]
    if not coordinates:
        return "-"
    return f"{min(coordinates)}-{max(coordinates)}"


def msa_feature_block(
    msa_rows: dict[str, str],
    position_maps: dict[str, list[int | None]],
    feature_name: str,
    feature_ranges: dict[str, tuple[int, int]],
    context: int = 4,
) -> str:
    feature_columns: dict[str, set[int]] = {}
    for key, residue_range in feature_ranges.items():
        feature_columns[key] = columns_for_range(position_maps[key], *residue_range)
    union = set().union(*feature_columns.values())
    if not union:
        raise AssertionError(f"No MSA columns found for {feature_name}")
    start_col = max(0, min(union) - context)
    end_col = min(len(next(iter(msa_rows.values()))) - 1, max(union) + context)
    consensus_mark = "".join(
        "^" if column in union else " " for column in range(start_col, end_col + 1)
    )
    lines = [
        f"[{feature_name}] MSA columns {start_col + 1}-{end_col + 1}",
        f"{'feature':<18} {'':>11}  {consensus_mark}",
    ]
    for key in PROTEIN_KEYS:
        fragment = msa_rows[key][start_col : end_col + 1]
        coordinates = fragment_coordinates(position_maps[key], start_col, end_col)
        lines.append(f"{key:<18} {coordinates:>11}  {fragment}")
    return "\n".join(lines)


def longest_forward_primer_match(primer: str, cds: str) -> str:
    matches = [primer[-n:] for n in range(1, len(primer) + 1) if cds.startswith(primer[-n:])]
    return max(matches, key=len, default="")


def longest_reverse_primer_match(primer: str, coding_without_stop: str) -> str:
    matches = [
        primer[-n:]
        for n in range(1, len(primer) + 1)
        if coding_without_stop.endswith(str(Seq(primer[-n:]).reverse_complement()))
    ]
    return max(matches, key=len, default="")


def validate_inputs(records: dict[str, object], sequences: dict[str, str]) -> dict[str, object]:
    validations: dict[str, object] = {}
    metadata: list[dict[str, object]] = []
    for spec in PROTEINS:
        path = SEQUENCE_DIR / spec.fasta_name
        sequence = sequences[spec.key]
        checksum = sha256_file(path)
        invalid = sorted(set(sequence) - CANONICAL_AA)
        if len(sequence) != spec.expected_length:
            raise AssertionError(f"{spec.key}: expected {spec.expected_length} aa, got {len(sequence)}")
        if checksum != spec.expected_sha256:
            raise AssertionError(f"{spec.key}: FASTA SHA256 changed: {checksum}")
        if invalid:
            raise AssertionError(f"{spec.key}: noncanonical/invalid residues: {invalid}")
        metadata.append(
            {
                "protein": spec.key,
                "species": spec.species,
                "protein_name": spec.protein_name,
                "database": spec.database,
                "accession": spec.accession,
                "length": len(sequence),
                "fasta_header": first_header(path),
                "url": spec.url,
                "sha256": checksum,
                "fasta_path": str(path.relative_to(ROOT)),
            }
        )

    p08539_text = (RECORD_DIR / "P08539_uniprot.txt").read_text(encoding="utf-8")
    p10823_text = (RECORD_DIR / "P10823_uniprot.txt").read_text(encoding="utf-8")
    ao_text = (RECORD_DIR / "TGJ64397.1_genbank.txt").read_text(encoding="utf-8")
    afgasa_uniprot_text = (RECORD_DIR / "A0A436ZRX2_uniprot.txt").read_text(encoding="utf-8")
    afgasa_ncbi_text = (RECORD_DIR / "RVD81648.1_genbank.txt").read_text(encoding="utf-8")
    required_record_strings = {
        "P08539": (
            "Reviewed;         472 AA.",
            "OS   Saccharomyces cerevisiae",
            "Guanine nucleotide-binding protein alpha-1 subunit",
            'FT                   /note="G-alpha"',
            'FT                   /note="Insert; not present in other G proteins"',
        ),
        "P10823": (
            "Reviewed;         449 AA.",
            "OS   Saccharomyces cerevisiae",
            "Guanine nucleotide-binding protein alpha-2 subunit",
            'FT                   /note="G-alpha"',
            'FT                   /note="Disordered"',
        ),
        "TGJ64397.1": (
            "LOCUS       TGJ64397                 356 aa",
            "VERSION     TGJ64397.1",
            "Orbilia oligospora",
            '/strain="TWF154"',
            '/gene="GPA2"',
            '/locus_tag="EYR41_010456"',
            '/region_name="G-alpha"',
            '/note="putative receptor binding site [active]"',
        ),
        "A0A436ZRX2": (
            "ID   GASA_ARTFL              Reviewed;         353 AA.",
            "AC   A0A436ZRX2;",
            "GN   Name=gasA",
            "ORFNames=DFL_009501;",
            "OS   Arthrobotrys flagrans",
            "DR   EMBL; SAEB01000012; RVD81648.1;",
            "FT   DOMAIN          32..353",
            "FT   REGION          323..328",
        ),
        "RVD81648.1": (
            "LOCUS       RVD81648                 353 aa",
            "VERSION     RVD81648.1",
            "DEFINITION  hypothetical protein DFL_009501 [Arthrobotrys flagrans].",
            "BioProject: PRJNA494930",
            "BioSample: SAMN10185917",
            '/strain="CBS H-5679"',
            '/locus_tag="DFL_009501"',
            '/region_name="G-alpha"',
            '/note="putative receptor binding site [active]"',
        ),
    }
    for needle in required_record_strings["P08539"]:
        if needle not in p08539_text:
            raise AssertionError(f"P08539 record missing: {needle}")
    for needle in required_record_strings["P10823"]:
        if needle not in p10823_text:
            raise AssertionError(f"P10823 record missing: {needle}")
    for needle in required_record_strings["TGJ64397.1"]:
        if needle not in ao_text:
            raise AssertionError(f"TGJ64397.1 record missing: {needle}")
    for needle in required_record_strings["A0A436ZRX2"]:
        if needle not in afgasa_uniprot_text:
            raise AssertionError(f"A0A436ZRX2 record missing: {needle}")
    for needle in required_record_strings["RVD81648.1"]:
        if needle not in afgasa_ncbi_text:
            raise AssertionError(f"RVD81648.1 record missing: {needle}")

    cds_record = SeqIO.read(RECORD_DIR / "TGJ64397.1_cds.fna", "fasta")
    cds = str(cds_record.seq).upper()
    translated = str(Seq(cds).translate())
    if not translated.endswith("*"):
        raise AssertionError("AoGpa2 CDS lacks a terminal stop codon")
    if "*" in translated[:-1]:
        raise AssertionError("AoGpa2 CDS contains an internal stop codon")
    if translated[:-1] != sequences["AoGpa2"]:
        raise AssertionError("AoGpa2 CDS translation does not exactly equal TGJ64397.1")

    afgasa_cds_record = SeqIO.read(RECORD_DIR / "RVD81648.1_cds.fna", "fasta")
    afgasa_cds = str(afgasa_cds_record.seq).upper()
    afgasa_translated = str(Seq(afgasa_cds).translate())
    if not afgasa_translated.endswith("*"):
        raise AssertionError("AfGasA CDS lacks a terminal stop codon")
    if "*" in afgasa_translated[:-1]:
        raise AssertionError("AfGasA CDS contains an internal stop codon")
    if afgasa_translated[:-1] != sequences["AfGasA"]:
        raise AssertionError("AfGasA CDS translation does not exactly equal A0A436ZRX2")

    ncbi_gasa = str(SeqIO.read(RECORD_DIR / "RVD81648.1_ncbi.fasta", "fasta").seq).upper()
    if ncbi_gasa != sequences["AfGasA"]:
        raise AssertionError("NCBI RVD81648.1 does not exactly equal UniProt A0A436ZRX2")

    hu2024_html = (ROOT / "sources" / "Hu2024_PMC11222155.html").read_text(encoding="utf-8")
    hu2024_text = " ".join(
        html.unescape(re.sub(r"<[^>]+>", " ", hu2024_html)).split()
    )
    hu2024_identity_patterns = (
        r"gasA\s*\(\s*dfl_009501\s*\)",
        r"G-protein alpha subunit GasA",
        r"CBS\s+349\.94",
        r"PRJNA494930",
        r"PMC11222155",
    )
    for pattern in hu2024_identity_patterns:
        if re.search(pattern, hu2024_text, flags=re.IGNORECASE) is None:
            raise AssertionError(f"Hu2024 full text missing GasA identity evidence: {pattern}")

    y2019_xml = (ROOT / "sources" / "Youssar2019_PMC6453484.xml").read_text(encoding="utf-8")
    biosample_xml = (ROOT / "sources" / "SAMN10185917.xml").read_text(encoding="utf-8")
    for needle in ("CBS 349.94", "SAEB01000000", "PMC6453484"):
        if needle not in y2019_xml:
            raise AssertionError(f"Youssar2019 full text missing strain provenance evidence: {needle}")
    for needle in ("SAMN10185917", "CBS H-5679", "CBS:H-5679", "A. Rubner, A.R. 9125"):
        if needle not in biosample_xml:
            raise AssertionError(f"SAMN10185917 BioSample missing provenance evidence: {needle}")

    primer_4207 = "ATATAAAACAGCTAGCATGGGTGGCTGCATGTCG"
    primer_4208 = (
        "AATTCAATTCAATGGCGCGCCGAGGTCTTCTTCGGAAATCAACTTCTGTTCTGACCCACCGCCACC"
        "TAATATACCGGAGTCCTTGAGGGC"
    )
    forward_match = longest_forward_primer_match(primer_4207, cds)
    reverse_match = longest_reverse_primer_match(primer_4208, cds[:-3])
    if len(forward_match) != 18:
        raise AssertionError(f"Unexpected primer 4207 gene-specific match: {forward_match}")
    if len(reverse_match) != 24:
        raise AssertionError(f"Unexpected primer 4208 gene-specific match: {reverse_match}")

    motif_checks: dict[str, dict[str, object]] = {}
    for key, sequence in sequences.items():
        g1_hits = [(match.start() + 1, match.group()) for match in re.finditer(r"G....GK[ST]", sequence)]
        g3_hits = [(match.start() + 1, match.group()) for match in re.finditer(r"D..G", sequence)]
        g4_hits = [(match.start() + 1, match.group()) for match in re.finditer(r"NK.D", sequence)]
        if not g1_hits or not g3_hits or not g4_hits:
            raise AssertionError(f"{key}: one or more canonical G-alpha motif signatures missing")
        motif_checks[key] = {
            "G1_signature_hits": g1_hits,
            "G3_DxxG_hits": g3_hits,
            "G4_NKxD_hits": g4_hits,
            "annotated_features": {
                name: {
                    "start": start,
                    "end": end,
                    "sequence": subseq(sequence, start, end),
                }
                for name, (start, end) in DIRECT_FEATURES[key].items()
            },
            "sequence_level_truncation_check": (
                "pass: canonical amino acids, expected length, G1/G3/G4/G5 and native C terminus present"
            ),
        }

    validations["metadata"] = metadata
    validations["record_identity_checks"] = {
        "P08539": "pass: reviewed S. cerevisiae Gpa1 and G-alpha domain record",
        "P10823": "pass: reviewed S. cerevisiae Gpa2 and G-alpha domain record",
        "TGJ64397.1": (
            "pass: NCBI record links GPA2, EYR41_010456, TWF154, Orbilia oligospora, "
            "complete G-alpha CDD domain and receptor-binding feature"
        ),
        "A0A436ZRX2_RVD81648.1": (
            "pass: Hu2024 gasA/dfl_009501 links to reviewed UniProt A0A436ZRX2; "
            "UniProt cross-references NCBI RVD81648.1, whose record and protein sequence "
            "carry the same DFL_009501 locus tag and complete G-alpha CDD domain"
        ),
    }
    validations["AoGpa2_CDS_translation"] = {
        "cds_length_nt": len(cds),
        "translation_length_before_stop": len(translated) - 1,
        "terminal_stop": translated[-1],
        "exactly_matches_TGJ64397.1": True,
    }
    validations["AfGasA_CDS_translation"] = {
        "cds_length_nt": len(afgasa_cds),
        "translation_length_before_stop": len(afgasa_translated) - 1,
        "terminal_stop": afgasa_translated[-1],
        "exactly_matches_A0A436ZRX2": True,
        "exactly_matches_RVD81648.1": True,
    }
    validations["AfGasA_strain_provenance"] = {
        "Hu2024_experimental_strain": "CBS 349.94",
        "Hu2024_genome_database": "PRJNA494930",
        "RVD81648.1_BioProject": "PRJNA494930",
        "RVD81648.1_BioSample": "SAMN10185917",
        "sequence_database_strain_label": "CBS H-5679",
        "equivalence_status": (
            "unresolved: the inspected primary articles and sequence records do not "
            "provide an authoritative cross-reference equating CBS 349.94 and CBS H-5679"
        ),
        "sequence_identity_impact": (
            "none: DFL_009501, A0A436ZRX2, RVD81648.1, scaffold SAEB01000012, "
            "the genomic CDS translation, and the protein residues remain directly linked"
        ),
    }
    validations["Kuo2024_primer_matches"] = {
        "primer_4207_full": primer_4207,
        "primer_4207_gene_specific_3prime": forward_match,
        "primer_4207_match_length_nt": len(forward_match),
        "primer_4207_matches_CDS_start": True,
        "primer_4208_full": primer_4208,
        "primer_4208_gene_specific_3prime": reverse_match,
        "primer_4208_match_length_nt": len(reverse_match),
        "primer_4208_reverse_complement": str(Seq(reverse_match).reverse_complement()),
        "primer_4208_matches_coding_end_before_stop": True,
    }
    validations["motif_checks"] = motif_checks
    return validations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clustalo",
        default="clustalo",
        help="Path to the Clustal Omega 1.2.4 executable",
    )
    args = parser.parse_args()

    ALIGNMENT_DIR.mkdir(parents=True, exist_ok=True)
    PAIRWISE_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    records: dict[str, object] = {}
    sequences: dict[str, str] = {}
    for spec in PROTEINS:
        record = SeqIO.read(SEQUENCE_DIR / spec.fasta_name, "fasta")
        records[spec.key] = record
        sequences[spec.key] = str(record.seq).upper()

    validations = validate_inputs(records, sequences)

    checksums = [
        f"{sha256_file(SEQUENCE_DIR / spec.fasta_name)}  sequences/{spec.fasta_name}"
        for spec in PROTEINS
    ]
    (ROOT / "checksums.sha256").write_text("\n".join(checksums) + "\n", encoding="utf-8")

    aligner, matrix = make_aligner()
    pairwise_stats: dict[str, dict[str, float | int]] = {}
    global_tie_audit: dict[str, dict[str, object]] = {}
    for key_a, key_b in PAIR_KEYS:
        pair_name = f"{key_a}_vs_{key_b}"
        _, stats = run_pair(
            key_a,
            sequences[key_a],
            key_b,
            sequences[key_b],
            aligner,
            matrix,
            PAIRWISE_DIR / f"{pair_name}_global.txt",
        )
        pairwise_stats[pair_name] = stats
        global_tie_audit[pair_name] = audit_score_tied_optimal_paths(
            sequences[key_a], sequences[key_b], aligner, matrix
        )

    # Diagnostic 1: delete only the documented ScGpa1-specific 109-aa insert,
    # then re-run global alignments against each complete comparator.
    scgpa1_no_insert = sequences["ScGpa1"][:126] + sequences["ScGpa1"][235:]
    insertion_deleted_stats: dict[str, dict[str, float | int]] = {}
    for key_b in ("ScGpa2", "AoGpa2", "AfGasA"):
        pair_name = f"ScGpa1_delta127_235_vs_{key_b}"
        _, stats = run_pair(
            "ScGpa1_delta127_235",
            scgpa1_no_insert,
            key_b,
            sequences[key_b],
            aligner,
            matrix,
            PAIRWISE_DIR / f"{pair_name}.txt",
        )
        insertion_deleted_stats[pair_name] = stats

    # Diagnostic 2: compare the aligned G-alpha core from the directly
    # annotated domain start through each native C terminus, with the ScGpa1
    # insert removed.  This is explicitly not a whole-protein global identity.
    core_sequences = {
        "ScGpa1": sequences["ScGpa1"][G_ALPHA_STARTS["ScGpa1"] - 1 : 126]
        + sequences["ScGpa1"][235:],
        "ScGpa2": sequences["ScGpa2"][G_ALPHA_STARTS["ScGpa2"] - 1 :],
        "AoGpa2": sequences["AoGpa2"][G_ALPHA_STARTS["AoGpa2"] - 1 :],
        "AfGasA": sequences["AfGasA"][G_ALPHA_STARTS["AfGasA"] - 1 :],
    }
    core_stats: dict[str, dict[str, float | int]] = {}
    for key_a, key_b in PAIR_KEYS:
        pair_name = f"{key_a}_vs_{key_b}"
        _, stats = run_pair(
            f"{key_a}_core",
            core_sequences[key_a],
            f"{key_b}_core",
            core_sequences[key_b],
            aligner,
            matrix,
            PAIRWISE_DIR / f"{pair_name}_g_alpha_core.txt",
        )
        core_stats[pair_name] = stats

    combined_path = SEQUENCE_DIR / "four_Galpha_combined.fasta"
    fasta_write(
        (
            (spec.key, f"{spec.accession} | {spec.species}", sequences[spec.key])
            for spec in PROTEINS
        ),
        combined_path,
    )

    msa_clustal_path = ALIGNMENT_DIR / "four_Galpha_clustalo.clustal"
    msa_fasta_path = ALIGNMENT_DIR / "four_Galpha_clustalo.fasta"
    clustalo_command = [
        str(Path(args.clustalo).resolve()),
        "--infile",
        str(combined_path),
        "--outfile",
        str(msa_clustal_path),
        "--outfmt=clu",
        "--seqtype=Protein",
        "--threads=1",
        "--output-order=input-order",
        "--force",
    ]
    completed = subprocess.run(clustalo_command, text=True, capture_output=True, check=True)
    (ALIGNMENT_DIR / "clustalo_run.log").write_text(
        "COMMAND\n" + " ".join(clustalo_command) + "\n\nSTDOUT\n" + completed.stdout
        + "\nSTDERR\n" + completed.stderr,
        encoding="utf-8",
    )
    msa = AlignIO.read(msa_clustal_path, "clustal")
    AlignIO.write(msa, msa_fasta_path, "fasta")

    msa_rows = {record.id: str(record.seq) for record in msa}
    expected_ids = {spec.key for spec in PROTEINS}
    if set(msa_rows) != expected_ids:
        raise AssertionError(f"Unexpected MSA IDs: {sorted(msa_rows)}")
    position_maps = msa_position_maps(msa)

    switch_ii_columns = columns_for_range(
        position_maps["AoGpa2"], *DIRECT_FEATURES["AoGpa2"]["Switch_II"]
    )
    mapped_switch_ii: dict[str, tuple[int, int]] = {}
    for key in PROTEIN_KEYS:
        coordinates = [position_maps[key][column] for column in sorted(switch_ii_columns)]
        present = [coordinate for coordinate in coordinates if coordinate is not None]
        mapped_switch_ii[key] = (min(present), max(present))

    motif_rows: list[dict[str, object]] = []
    for key in PROTEIN_KEYS:
        feature_ranges = dict(DIRECT_FEATURES[key])
        if "Switch_II" not in feature_ranges:
            feature_ranges["Switch_II_MSA_mapped_from_Ao_CDD"] = mapped_switch_ii[key]
        feature_ranges["alpha5_operational"] = ALPHA5_REGIONS[key]
        for name, (start, end) in feature_ranges.items():
            motif_rows.append(
                {
                    "protein": key,
                    "feature": name,
                    "start": start,
                    "end": end,
                    "sequence": subseq(sequences[key], start, end),
                    "basis": (
                        "MSA-mapped from AoGpa2 CDD Switch II"
                        if "MSA_mapped" in name
                        else "operational G5-to-C-terminal alpha5 boundary"
                        if name == "alpha5_operational"
                        else "direct database annotation"
                    ),
                }
            )

    motif_tsv_lines = ["protein\tfeature\tstart\tend\tsequence\tbasis"]
    for row in motif_rows:
        motif_tsv_lines.append(
            "\t".join(str(row[column]) for column in ("protein", "feature", "start", "end", "sequence", "basis"))
        )
    (RESULTS_DIR / "motifs.tsv").write_text("\n".join(motif_tsv_lines) + "\n", encoding="utf-8")

    key_blocks = []
    for feature_name in ("G1_P_loop", "Switch_I_G2", "G3", "G4", "G5"):
        feature_ranges = {key: DIRECT_FEATURES[key][feature_name] for key in expected_ids}
        key_blocks.append(
            msa_feature_block(msa_rows, position_maps, feature_name, feature_ranges, context=4)
        )
    key_blocks.insert(
        2,
        msa_feature_block(
            msa_rows,
            position_maps,
            "Switch_II (Ao CDD direct; Sc MSA-mapped)",
            mapped_switch_ii,
            context=3,
        ),
    )
    (ALIGNMENT_DIR / "four_Galpha_key_regions.txt").write_text(
        "\n\n".join(key_blocks) + "\n", encoding="utf-8"
    )

    alpha5_sequences = {
        key: subseq(sequences[key], *ALPHA5_REGIONS[key])
        for key in PROTEIN_KEYS
    }
    alpha5_stats: dict[str, dict[str, float | int]] = {}
    for key_a, key_b in PAIR_KEYS:
        pair_name = f"{key_a}_vs_{key_b}"
        _, stats = run_pair(
            f"{key_a}_alpha5",
            alpha5_sequences[key_a],
            f"{key_b}_alpha5",
            alpha5_sequences[key_b],
            aligner,
            matrix,
            PAIRWISE_DIR / f"{pair_name}_alpha5.txt",
        )
        alpha5_stats[pair_name] = stats

    alpha5_start_columns = [
        min(columns_for_range(position_maps[key], start, start))
        for key, (start, _) in ALPHA5_REGIONS.items()
    ]
    alpha5_start_column = min(alpha5_start_columns)
    msa_length = len(next(iter(msa_rows.values())))
    alpha5_rows = {
        key: msa_rows[key][alpha5_start_column:msa_length]
        for key in PROTEIN_KEYS
    }
    alpha5_lines = [
        "# Operational alpha5 / GPCR-contacting C-terminal region",
        "# Boundary: conserved Asp immediately after aligned three-residue G5 core through native C terminus",
        "# Coordinates: ScGpa1 446-472; ScGpa2 422-449; AoGpa2 330-356; AfGasA 327-353",
        "# The four rows below are the corresponding Clustal Omega MSA columns.",
        "",
    ]
    for key in PROTEIN_KEYS:
        start, end = ALPHA5_REGIONS[key]
        alpha5_lines.append(f"{key:<8} {start:>3}-{end:<3}  {alpha5_rows[key]}")
    alpha5_lines.extend(["", "# Pairwise regional alignments use: | exact; : BLOSUM62 > 0; . non-conservative; blank gap"])
    for key_a, key_b in PAIR_KEYS:
        alignment, stats = run_pair(
            key_a,
            alpha5_sequences[key_a],
            key_b,
            alpha5_sequences[key_b],
            aligner,
            matrix,
        )
        row_a = str(alignment[0])
        row_b = str(alignment[1])
        marks = "".join(marker(a, b, matrix) for a, b in zip(row_a, row_b))
        alpha5_lines.extend(
            [
                "",
                f"{key_a:<8}  {row_a}",
                f"{'':<8}  {marks}",
                f"{key_b:<8}  {row_b}",
                (
                    f"identity {stats['identity_n']}/{stats['aligned_length']} "
                    f"({stats['identity_pct']:.3f}%); positive similarity "
                    f"{stats['similarity_n']}/{stats['aligned_length']} "
                    f"({stats['similarity_pct']:.3f}%)"
                ),
            ]
        )
    (ALIGNMENT_DIR / "alpha5_C_terminal_alignment.txt").write_text(
        "\n".join(alpha5_lines) + "\n", encoding="utf-8"
    )

    version_result = subprocess.run(
        [str(Path(args.clustalo).resolve()), "--version"],
        text=True,
        capture_output=True,
        check=True,
    )
    versions = {
        "python": platform.python_version(),
        "biopython": Bio.__version__,
        "pairwise_implementation": "Bio.Align.PairwiseAligner global mode (Needleman-Wunsch equivalent)",
        "clustal_omega": (version_result.stdout or version_result.stderr).strip(),
        "clustal_omega_executable": str(Path(args.clustalo).resolve()),
        "platform": platform.platform(),
    }
    (ROOT / "software_versions.txt").write_text(
        "\n".join(f"{key}: {value}" for key, value in versions.items()) + "\n",
        encoding="utf-8",
    )

    tie_lines = [
        "pair\toptimal_path_count\tpath_count_for_variant\taligned_length\tidentity_n\tidentity_pct\tsimilarity_n\tsimilarity_pct\tgap_columns_n\tgap_columns_pct"
    ]
    for pair_name, audit in global_tie_audit.items():
        for variant in audit["metric_variants"]:
            tie_lines.append(
                "\t".join(
                    [
                        pair_name,
                        str(audit["optimal_path_count"]),
                        str(variant["path_count"]),
                        str(variant["aligned_length"]),
                        str(variant["identity_n"]),
                        f"{variant['identity_pct']:.6f}",
                        str(variant["similarity_n"]),
                        f"{variant['similarity_pct']:.6f}",
                        str(variant["gap_columns_n"]),
                        f"{variant['gap_columns_pct']:.6f}",
                    ]
                )
            )
    (RESULTS_DIR / "global_optimal_path_tie_audit.tsv").write_text(
        "\n".join(tie_lines) + "\n", encoding="utf-8"
    )

    result = {
        "method": {
            "global_algorithm": "Needleman-Wunsch equivalent via Biopython PairwiseAligner mode=global",
            "substitution_matrix": "BLOSUM62",
            "gap_open": -10.0,
            "gap_extend": -0.5,
            "terminal_gaps_penalized": True,
            "identity_denominator": "all global alignment columns, including gap columns",
            "similarity_definition": "all nongap residue pairs with BLOSUM62 score > 0, including exact matches",
            "gap_definition": "columns containing a gap in either sequence",
            "optimal_path_tie_rule": "report the first score-tied optimal path returned by Biopython; all optimal paths are audited separately",
            "msa": "Clustal Omega protein MSA, one thread, input order retained",
        },
        "software": versions,
        "validation": validations,
        "global_pairwise": pairwise_stats,
        "global_optimal_path_tie_audit": global_tie_audit,
        "ScGpa1_insertion_deleted_diagnostic": {
            "definition": "delete ScGpa1 residues 127-235, then globally align to each complete comparator; not whole-protein identity",
            "ScGpa1_delta_length": len(scgpa1_no_insert),
            "pairs": insertion_deleted_stats,
        },
        "G_alpha_core_diagnostic": {
            "definition": (
                "directly annotated G-alpha domain start through native C terminus; "
                "ScGpa1 residues 127-235 deleted; not whole-protein identity"
            ),
            "sequence_lengths": {key: len(value) for key, value in core_sequences.items()},
            "pairs": core_stats,
        },
        "alpha5_C_terminal": {
            "boundary_definition": (
                "conserved Asp immediately after the aligned three-residue G5 core through native C terminus"
            ),
            "regions": {
                key: {
                    "start": ALPHA5_REGIONS[key][0],
                    "end": ALPHA5_REGIONS[key][1],
                    "length": len(alpha5_sequences[key]),
                    "sequence": alpha5_sequences[key],
                }
                for key in alpha5_sequences
            },
            "pairs": alpha5_stats,
        },
        "mapped_switch_II": {
            key: {"start": start, "end": end, "basis": "Ao CDD 205-221 mapped through four-way MSA"}
            for key, (start, end) in mapped_switch_ii.items()
        },
        "artifacts": {
            "combined_fasta": str(combined_path.relative_to(ROOT)),
            "msa_fasta": str(msa_fasta_path.relative_to(ROOT)),
            "msa_human_readable": str(msa_clustal_path.relative_to(ROOT)),
            "msa_key_regions": "alignments/four_Galpha_key_regions.txt",
            "alpha5_alignment": "alignments/alpha5_C_terminal_alignment.txt",
            "pairwise_directory": "alignments/pairwise",
            "motifs_tsv": "results/motifs.tsv",
            "global_optimal_path_tie_audit": "results/global_optimal_path_tie_audit.tsv",
        },
    }
    (RESULTS_DIR / "sequence_comparison.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    tsv_header = (
        "scope\tpair\taligned_length\tidentity_n\tidentity_pct\t"
        "similarity_n\tsimilarity_pct\tgap_columns_n\tgap_columns_pct\tscore"
    )
    tsv_lines = [tsv_header]
    for scope, collection in (
        ("whole_protein_global", pairwise_stats),
        ("alpha5_C_terminal", alpha5_stats),
        ("G_alpha_core_diagnostic", core_stats),
        ("ScGpa1_insertion_deleted_diagnostic", insertion_deleted_stats),
    ):
        for pair_name, stats in collection.items():
            tsv_lines.append(
                "\t".join(
                    [
                        scope,
                        pair_name,
                        str(stats["aligned_length"]),
                        str(stats["identity_n"]),
                        f"{stats['identity_pct']:.6f}",
                        str(stats["similarity_n"]),
                        f"{stats['similarity_pct']:.6f}",
                        str(stats["gap_columns_n"]),
                        f"{stats['gap_columns_pct']:.6f}",
                        f"{stats['score']:.6f}",
                    ]
                )
            )
    (RESULTS_DIR / "pairwise_stats.tsv").write_text("\n".join(tsv_lines) + "\n", encoding="utf-8")

    print(json.dumps({
        "global_pairwise": pairwise_stats,
        "alpha5_C_terminal": alpha5_stats,
        "G_alpha_core_diagnostic": core_stats,
        "ScGpa1_insertion_deleted_diagnostic": insertion_deleted_stats,
    }, indent=2))


if __name__ == "__main__":
    main()
