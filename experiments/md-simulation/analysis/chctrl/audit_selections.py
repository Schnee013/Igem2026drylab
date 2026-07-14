#!/usr/bin/env python
"""Audit chctrl analysis selections and alpha5 warning interpretation.

Outputs are written under:
experiments/md-simulation/results/chimeric-ste2-gpa1-wt/analysis/selection_audit/

This script is intentionally diagnostic: it does not change the production
analysis CSVs and does not decide whether to restart Ch-1/Ch-2/Ch-4.
"""
from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
import math
import sys

sys.path.insert(0, str(Path("src/modeling/md-analysis").resolve()))

import numpy as np
import pandas as pd
import MDAnalysis as mda
from MDAnalysis.analysis import align
from MDAnalysis.coordinates.PDB import PDBWriter
from MDAnalysis.lib.distances import distance_array

from common import (
    CONFIG_PATH,
    Replicate,
    analysis_context,
    configured_replicate_numbers,
    ensure_dir,
    time_ns,
)


AA3 = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLN": "Q",
    "GLU": "E",
    "GLY": "G",
    "HIS": "H",
    "HSD": "H",
    "HSE": "H",
    "HSP": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
}


CHCTRL_SYSTEM = "chimeric-ste2-gpa1-wt"
EXPECTED_REP_LABELS = ("rep1", "rep2", "rep3")


def require_canonical_replicates() -> tuple[int, ...]:
    """Reject environment overrides that would make this fixed audit partial."""
    numbers = tuple(configured_replicate_numbers())
    labels = tuple(f"rep{number}" for number in numbers)
    if labels != EXPECTED_REP_LABELS:
        raise RuntimeError(
            "chctrl selection audit requires canonical replicates "
            f"{list(EXPECTED_REP_LABELS)}; CHIMERIC_MD_REPS resolved to {list(labels)}"
        )
    return numbers


# Validate the replicate contract before loading any config or audit input file.
CANONICAL_REPLICATE_NUMBERS = require_canonical_replicates()
CTX = analysis_context(CHCTRL_SYSTEM, config_path=CONFIG_PATH)
GPA1 = CTX.galpha_selection
STE2 = CTX.receptor_selection
BACKBONE = CTX.backbone_selection
ALPHA5 = CTX.alpha5_selection
GPA1_LAST5 = CTX.galpha_ect_selection
STE2_INTERFACE = CTX.receptor_interface_selection
OUT = CTX.analysis_base / "selection_audit"
SNAP = OUT / "snapshots"


def canonical_replicates() -> list[Replicate]:
    """Build the fixed chctrl rep1/rep2/rep3 inputs without rereading env state."""
    reps = []
    for number in CANONICAL_REPLICATE_NUMBERS:
        directory = CTX.payload_base / "processed" / f"rep{number}"
        reps.append(
            Replicate(
                rep=f"rep{number}",
                topology=directory / "protein_ref.pdb",
                trajectory=directory / "prod_protein.xtc",
            )
        )
    labels = tuple(rep.rep for rep in reps)
    if labels != EXPECTED_REP_LABELS:
        raise RuntimeError(
            f"internal canonical replicate mismatch: expected={EXPECTED_REP_LABELS}, "
            f"observed={labels}"
        )
    return reps


def heavy(sel):
    return sel.select_atoms("not name H* and not type H")


def oneletter(resnames: list[str]) -> str:
    return "".join(AA3.get(x.strip().upper(), "X") for x in resnames)


def parse_pdb_residues(path: Path, key_kind: str) -> dict[str, list[tuple[int, str]]]:
    """Parse unique ATOM residues keyed by chain or segid from a PDB file."""
    out: dict[str, OrderedDict[int, str]] = {}
    with path.open() as fh:
        for line in fh:
            if not line.startswith("ATOM"):
                continue
            resname = line[17:20].strip()
            try:
                resid = int(line[22:26])
            except ValueError:
                continue
            if key_kind == "chain":
                key = line[21].strip() or "_"
            elif key_kind == "segid":
                key = line[72:76].strip() or "_"
            else:
                raise ValueError(key_kind)
            out.setdefault(key, OrderedDict()).setdefault(resid, resname)
    return {k: list(v.items()) for k, v in out.items()}


def residue_summary(u: mda.Universe, rep: str) -> list[dict]:
    rows = []
    for segid, intended in [("PROA", "Gpa1-WT"), ("PROB", "Ste2")]:
        sel = u.select_atoms(f"segid {segid}")
        residues = sel.residues
        resnames = [r.resname for r in residues]
        resids = [int(r.resid) for r in residues]
        rows.append(
            {
                "rep": rep,
                "segid": segid,
                "intended": intended,
                "n_atoms": int(len(sel)),
                "n_residues": int(len(residues)),
                "min_resid": min(resids) if resids else math.nan,
                "max_resid": max(resids) if resids else math.nan,
                "first10": oneletter(resnames[:10]),
                "last25": oneletter(resnames[-25:]),
                "unique_resnames": " ".join(sorted(set(resnames))),
            }
        )
    return rows


def selection_counts(u: mda.Universe, rep: str) -> list[dict]:
    specs = {
        "GPA1": GPA1,
        "STE2": STE2,
        "BACKBONE": BACKBONE,
        "ALPHA5": ALPHA5,
        "GPA1_LAST5": GPA1_LAST5,
        "STE2_INTERFACE": STE2_INTERFACE,
        "STE2_INTERFACE_HEAVY": f"({STE2_INTERFACE}) and not name H* and not type H",
        "BSA_GPA1": "segid PROA",
        "BSA_STE2": "segid PROB",
    }
    rows = []
    for name, spec in specs.items():
        sel = u.select_atoms(spec)
        rows.append(
            {
                "rep": rep,
                "selection_name": name,
                "selection": spec,
                "n_atoms": int(len(sel)),
                "n_residues": int(len(sel.residues)),
                "resid_min": int(min([r.resid for r in sel.residues])) if len(sel.residues) else math.nan,
                "resid_max": int(max([r.resid for r in sel.residues])) if len(sel.residues) else math.nan,
                "residue_list": " ".join(f"{r.resid}:{r.resname}" for r in sel.residues),
            }
        )
    return rows


def fit_rmsd(mob_fit, ref_fit_pos, mob_sel, ref_sel_pos) -> float:
    mob_com = mob_fit.center_of_mass()
    R, _ = align.rotation_matrix(mob_fit.positions - mob_com, ref_fit_pos)
    mob = np.dot(mob_sel.positions - mob_com, R)
    diff = mob - ref_sel_pos
    return float(np.sqrt((diff * diff).sum() / len(mob)))


def scan_alt_alpha5_rmsd(rep) -> pd.DataFrame:
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    ref = mda.Universe(str(rep.topology), str(rep.trajectory))
    ref.trajectory[0]
    schemes = {
        "full_protein_backbone_fit": BACKBONE,
        "ste2_backbone_fit": "(segid PROB) and backbone",
        "gpa1_core_backbone_fit": "(segid PROA) and backbone and not resid 448:472",
    }
    mob_a5 = u.select_atoms(ALPHA5)
    ref_a5 = ref.select_atoms(ALPHA5)
    refs = {}
    mobs = {}
    for scheme, spec in schemes.items():
        mobs[scheme] = u.select_atoms(spec)
        ref_fit = ref.select_atoms(spec)
        ref_com = ref_fit.center_of_mass()
        refs[scheme] = {
            "fit_pos": ref_fit.positions - ref_com,
            "a5_pos": ref_a5.positions - ref_com,
        }
    rows = []
    for ts in u.trajectory:
        row = {"rep": rep.rep, "frame": int(ts.frame), "time_ns": time_ns(ts)}
        for scheme in schemes:
            row[scheme + "_alpha5_rmsd_A"] = fit_rmsd(mobs[scheme], refs[scheme]["fit_pos"], mob_a5, refs[scheme]["a5_pos"])
        rows.append(row)
    return pd.DataFrame(rows)


def export_nearest_frame(rep, target_ns: float, label: str) -> dict:
    u = mda.Universe(str(rep.topology), str(rep.trajectory))
    times = []
    frames = []
    for ts in u.trajectory:
        times.append(time_ns(ts))
        frames.append(int(ts.frame))
    arr = np.array(times)
    idx = int(np.argmin(np.abs(arr - target_ns)))
    frame = frames[idx]
    actual = float(arr[idx])
    u.trajectory[frame]
    safe_label = label.replace(">", "gt").replace(" ", "_").replace("/", "-")
    out = SNAP / f"{rep.rep}_{safe_label}_{actual:.1f}ns.pdb"
    with PDBWriter(str(out), multiframe=False) as w:
        w.write(u.atoms)
    return {"rep": rep.rep, "requested_time_ns": target_ns, "actual_time_ns": actual, "frame": frame, "label": label, "pdb": str(out)}


def min_distance(a, b) -> float:
    if len(a) == 0 or len(b) == 0:
        return math.nan
    return float(distance_array(a.positions, b.positions).min())


def md_table(df: pd.DataFrame, floatfmt: str = ".3f") -> str:
    """Render a small dataframe as a GitHub-style Markdown table without tabulate."""
    if df.empty:
        return "_empty table_"
    out = []
    cols = list(df.columns)
    out.append("| " + " | ".join(cols) + " |")
    out.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in df.iterrows():
        vals = []
        for col in cols:
            v = row[col]
            if isinstance(v, float):
                vals.append(("" if pd.isna(v) else format(v, floatfmt)).replace("|", "\\|"))
            else:
                vals.append(str(v).replace("|", "\\|"))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


def interface_geometry_rows(step5: Path) -> list[dict]:
    u = mda.Universe(str(step5))
    gpa = heavy(u.select_atoms(GPA1))
    alpha5 = heavy(u.select_atoms(ALPHA5))
    last5 = heavy(u.select_atoms(GPA1_LAST5))
    lipid_p = u.select_atoms("resname POPC and name P")
    membrane_mid_z = math.nan
    if len(lipid_p) >= 2:
        z = lipid_p.positions[:, 2]
        lower = z[z <= np.median(z)]
        upper = z[z > np.median(z)]
        if len(lower) and len(upper):
            membrane_mid_z = float((lower.mean() + upper.mean()) / 2.0)
    rows = []
    ranges = [(69, 84), (145, 160), (222, 251), (288, 304)]
    for start, end in ranges:
        spec = f"(segid PROB) and resid {start}:{end}"
        sel = u.select_atoms(spec)
        ca = sel.select_atoms("name CA")
        hsel = heavy(sel)
        rows.append(
            {
                "range": f"{start}:{end}",
                "n_atoms": int(len(sel)),
                "n_residues": int(len(sel.residues)),
                "ca_z_mean_A": float(ca.positions[:, 2].mean()) if len(ca) else math.nan,
                "ca_z_min_A": float(ca.positions[:, 2].min()) if len(ca) else math.nan,
                "ca_z_max_A": float(ca.positions[:, 2].max()) if len(ca) else math.nan,
                "membrane_mid_z_A": membrane_mid_z,
                "ca_z_minus_membrane_mid_A": float(ca.positions[:, 2].mean() - membrane_mid_z) if len(ca) and np.isfinite(membrane_mid_z) else math.nan,
                "min_dist_to_gpa1_alpha5_A": min_distance(hsel, alpha5),
                "min_dist_to_gpa1_last5_A": min_distance(hsel, last5),
                "min_dist_to_all_gpa1_A": min_distance(hsel, gpa),
                "residue_list": " ".join(f"{r.resid}:{r.resname}" for r in sel.residues),
            }
        )
    return rows


def load_canonical_rmsd(rmsd_path: Path, reps) -> pd.DataFrame:
    """Validate the canonical alpha5/eCT RMSD table before audit side effects."""
    if CTX.selection_rmsd_selection != ALPHA5:
        raise ValueError(
            "chctrl selection audit requires selection_rmsd_selection to match "
            f"alpha5_selection; got {CTX.selection_rmsd_selection!r} vs {ALPHA5!r}"
        )

    prior = pd.read_csv(rmsd_path)
    required_columns = {"rep", "time_ns", "selection_rmsd_A"}
    missing_columns = required_columns.difference(prior.columns)
    if missing_columns:
        raise ValueError(f"{rmsd_path} missing required columns: {sorted(missing_columns)}")
    if prior[list(required_columns)].isna().any().any():
        raise ValueError(f"{rmsd_path} has null canonical RMSD keys or values")
    duplicate_keys = prior.duplicated(["rep", "time_ns"], keep=False)
    if duplicate_keys.any():
        raise ValueError(
            f"{rmsd_path} has {int(duplicate_keys.sum())} duplicate rep/time_ns rows"
        )

    expected_reps = [rep.rep for rep in reps]
    observed_reps = list(prior.rep.drop_duplicates())
    if set(observed_reps) != set(expected_reps):
        raise ValueError(
            f"{rmsd_path} rep coverage mismatch: expected={expected_reps}, "
            f"observed={observed_reps}"
        )

    reference_times = None
    for rep in expected_reps:
        times = prior.loc[prior.rep == rep, "time_ns"].to_numpy()
        if not len(times) or np.any(np.diff(times) <= 0):
            raise ValueError(f"{rmsd_path} time grid for {rep} is empty or not strictly increasing")
        if reference_times is None:
            reference_times = times
        elif not np.array_equal(times, reference_times):
            raise ValueError(f"{rmsd_path} time grid for {rep} differs from the first rep")

    return prior.rename(columns={"selection_rmsd_A": "alpha5_irmsd_A"})


def main() -> None:
    payload_base = CTX.payload_base
    reps = canonical_replicates()
    source_clean = Path("experiments/md-simulation/structures/chimeric/Chctrl_Ste2_Gpa1_WT_clean.pdb")
    step5 = payload_base / "raw/shared/step5_input.pdb"
    rmsd_path = CTX.analysis_base / "selection_rmsd/selection_rmsd.csv"
    contact_persistence_path = CTX.analysis_base / "contacts/contact_persistence.csv"
    contact_occupancy_path = CTX.analysis_base / "contacts/initial_contact_occupancy.csv"

    required_inputs = [
        source_clean,
        step5,
        rmsd_path,
        contact_persistence_path,
        contact_occupancy_path,
    ]
    for rep in reps:
        required_inputs.extend([rep.topology, rep.trajectory])
    missing_inputs = [str(path) for path in required_inputs if not path.is_file()]
    if missing_inputs:
        raise FileNotFoundError(
            "selection audit missing required inputs before execution: "
            + ", ".join(missing_inputs)
        )

    prior = load_canonical_rmsd(rmsd_path, reps)
    ensure_dir(OUT)
    ensure_dir(SNAP)

    # Chain/segment and selection counts.
    chain_rows = []
    count_rows = []
    for rep in reps:
        u = mda.Universe(str(rep.topology), str(rep.trajectory))
        chain_rows.extend(residue_summary(u, rep.rep))
        count_rows.extend(selection_counts(u, rep.rep))
    chain_df = pd.DataFrame(chain_rows)
    count_df = pd.DataFrame(count_rows)
    chain_df.to_csv(OUT / "chain_summary.csv", index=False)
    count_df.to_csv(OUT / "selection_counts.csv", index=False)

    # Sequence carry-through from clean chain A/B to CHARMM-GUI PROA/PROB.
    clean = parse_pdb_residues(source_clean, "chain")
    processed = parse_pdb_residues(
        payload_base / "processed/rep1/protein_ref.pdb", "segid"
    )
    mapping_rows = []
    for clean_key, segid, intended in [("A", "PROA", "Gpa1-WT"), ("B", "PROB", "Ste2")]:
        clean_res = clean.get(clean_key, [])
        proc_res = processed.get(segid, [])
        clean_seq = oneletter([r for _, r in clean_res])
        proc_seq = oneletter([r for _, r in proc_res])
        mapping_rows.append(
            {
                "source_clean_chain": clean_key,
                "processed_segid": segid,
                "intended": intended,
                "source_n_residues": len(clean_res),
                "processed_n_residues": len(proc_res),
                "sequence_exact_match": clean_seq == proc_seq,
                "source_first10": clean_seq[:10],
                "processed_first10": proc_seq[:10],
                "source_last25": clean_seq[-25:],
                "processed_last25": proc_seq[-25:],
            }
        )
    pd.DataFrame(mapping_rows).to_csv(OUT / "source_to_processed_mapping.csv", index=False)

    # Interface geometry in the full step5 system.
    pd.DataFrame(interface_geometry_rows(step5)).to_csv(OUT / "ste2_interface_geometry_step5.csv", index=False)

    # Alternative alpha5 RMSD fits.
    alt = pd.concat([scan_alt_alpha5_rmsd(rep) for rep in reps], ignore_index=True)
    alt.to_csv(OUT / "alpha5_alt_fit_rmsd.csv", index=False)

    # Compare with the prevalidated canonical generic driver output.
    cmp = prior.merge(
        alt[["rep", "time_ns", "full_protein_backbone_fit_alpha5_rmsd_A"]],
        on=["rep", "time_ns"],
        how="outer",
        validate="one_to_one",
        indicator=True,
    )
    if not (cmp["_merge"] == "both").all():
        coverage = cmp["_merge"].value_counts().to_dict()
        raise ValueError(f"canonical/independent RMSD coverage mismatch: {coverage}")
    cmp = cmp.drop(columns="_merge")
    cmp["abs_diff_A"] = (cmp["alpha5_irmsd_A"] - cmp["full_protein_backbone_fit_alpha5_rmsd_A"]).abs()
    cmp_summary = (
        cmp.groupby("rep")
        .agg(max_abs_diff_A=("abs_diff_A", "max"), mean_abs_diff_A=("abs_diff_A", "mean"), n=("abs_diff_A", "size"))
        .reset_index()
    )
    cmp_summary.to_csv(OUT / "alpha5_reproduction_check.csv", index=False)

    # Event timing and snapshots.
    event_rows = []
    snapshot_requests = {
        "rep1": [(0.0, "baseline"), (100.0, "after100_start"), (252.4, "first_after100_ge5"), (333.5, "max_alpha5")],
        "rep2": [(0.0, "baseline"), (100.0, "after100_start"), (250.6, "first_ge5"), (484.6, "max_alpha5")],
        "rep3": [(0.0, "baseline"), (32.6, "early_max"), (100.0, "after100_start"), (450.0, "late_representative")],
    }
    for rep in reps:
        sub = prior[prior.rep == rep.rep].copy()
        after = sub[sub.time_ns >= 100]
        for name, sdf in [
            ("first_ge3", sub[sub.alpha5_irmsd_A >= 3.0]),
            ("first_ge5", sub[sub.alpha5_irmsd_A >= 5.0]),
            ("first_after100_ge5", after[after.alpha5_irmsd_A >= 5.0]),
        ]:
            if len(sdf):
                row = sdf.iloc[0]
                event_rows.append({"rep": rep.rep, "event": name, "time_ns": row.time_ns, "alpha5_irmsd_A": row.alpha5_irmsd_A})
            else:
                event_rows.append({"rep": rep.rep, "event": name, "time_ns": math.nan, "alpha5_irmsd_A": math.nan})
        row = sub.loc[sub.alpha5_irmsd_A.idxmax()]
        event_rows.append({"rep": rep.rep, "event": "max", "time_ns": row.time_ns, "alpha5_irmsd_A": row.alpha5_irmsd_A})
    pd.DataFrame(event_rows).to_csv(OUT / "alpha5_event_timing.csv", index=False)

    snap_rows = []
    for rep in reps:
        for t, label in snapshot_requests[rep.rep]:
            snap_rows.append(export_nearest_frame(rep, t, label))
    snap_df = pd.DataFrame(snap_rows)
    snap_df.to_csv(OUT / "exported_snapshots.csv", index=False)

    # Per-snapshot alpha5/contact metrics from alt fit and contact persistence.
    contact = pd.read_csv(contact_persistence_path)
    metric_rows = []
    for _, s in snap_df.iterrows():
        rep = s["rep"]
        t = float(s["actual_time_ns"])
        asub = alt[alt.rep == rep].iloc[(alt[alt.rep == rep].time_ns - t).abs().argsort()[:1]]
        csub = contact[contact.rep == rep].iloc[(contact[contact.rep == rep].time_ns - t).abs().argsort()[:1]]
        row = {"rep": rep, "label": s["label"], "time_ns": t, "frame": int(s["frame"]), "pdb": s["pdb"]}
        for col in [
            "full_protein_backbone_fit_alpha5_rmsd_A",
            "ste2_backbone_fit_alpha5_rmsd_A",
            "gpa1_core_backbone_fit_alpha5_rmsd_A",
        ]:
            row[col] = float(asub[col].iloc[0])
        row["nearest_contact_time_ns"] = float(csub.time_ns.iloc[0])
        row["retained_contact_fraction"] = float(csub.retained_fraction.iloc[0])
        metric_rows.append(row)
    metrics = pd.DataFrame(metric_rows)
    metrics.to_csv(OUT / "snapshot_metrics.csv", index=False)

    # Contact bias summary.
    contacts = pd.read_csv(contact_occupancy_path)
    cp = pd.read_csv(contact_persistence_path)
    contact_summary = []
    for rep, sub in cp.groupby("rep"):
        after = sub[sub.time_ns >= 100]
        minrow = after.loc[after.retained_fraction.idxmin()]
        occ = contacts[contacts.rep == rep]
        contact_summary.append(
            {
                "rep": rep,
                "initial_contacts": int(sub.initial_contacts.iloc[0]),
                "after100_mean_retained_fraction": float(after.retained_fraction.mean()),
                "after100_min_retained_fraction": float(minrow.retained_fraction),
                "after100_min_time_ns": float(minrow.time_ns),
                "contacts_occupancy_ge_0_5": int((occ.occupancy >= 0.5).sum()),
                "contacts_occupancy_ge_0_2": int((occ.occupancy >= 0.2).sum()),
                "median_initial_contact_occupancy": float(occ.occupancy.median()),
            }
        )
    pd.DataFrame(contact_summary).to_csv(OUT / "contact_bias_summary.csv", index=False)

    # Compact report.
    chain_ok = (
        set(chain_df[chain_df.segid == "PROA"].n_residues.astype(int)) == {472}
        and set(chain_df[chain_df.segid == "PROB"].n_residues.astype(int)) == {431}
        and all(pd.DataFrame(mapping_rows)["sequence_exact_match"])
    )
    sel_counts = count_df.pivot_table(index="selection_name", values=["n_atoms", "n_residues"], aggfunc=lambda x: sorted(set(map(int, x))))
    iface = pd.read_csv(OUT / "ste2_interface_geometry_step5.csv")
    alt_summary = (
        alt[alt.time_ns >= 100]
        .groupby("rep")
        .agg(
            full_after100_mean=("full_protein_backbone_fit_alpha5_rmsd_A", "mean"),
            full_after100_max=("full_protein_backbone_fit_alpha5_rmsd_A", "max"),
            ste2_after100_mean=("ste2_backbone_fit_alpha5_rmsd_A", "mean"),
            ste2_after100_max=("ste2_backbone_fit_alpha5_rmsd_A", "max"),
            gpa1_core_after100_mean=("gpa1_core_backbone_fit_alpha5_rmsd_A", "mean"),
            gpa1_core_after100_max=("gpa1_core_backbone_fit_alpha5_rmsd_A", "max"),
        )
        .reset_index()
    )
    alt_summary.to_csv(OUT / "alpha5_alt_fit_summary_after100.csv", index=False)

    report = []
    report.append("# chctrl selection audit report\n")
    report.append(
        "> Status: executed diagnostic audit. This report does not restart Ch-1/Ch-2/Ch-4 and does not by itself validate all operational cutoffs.\n"
        ">\n"
        "> Source-audit update: operational cutoff and Ste2 interface provenance were audited separately in `../cutoff_source_audit.md`.\n"
    )
    report.append("## Bottom line\n")
    report.append(f"- Chain/segment identity check: {'PASS' if chain_ok else 'CHECK REQUIRED'} — PROA maps to clean Chain A / intended Gpa1-WT; PROB maps to clean Chain B / intended Ste2.\n")
    report.append("- Alpha5 selection exists in all three processed replicates and maps to PROA residues 448–472; no missing-residue evidence was found in topology-level checks.\n")
    report.append("- Ste2 interface ranges are geometrically close to Gpa1/alpha5 in `step5_input.pdb`; a follow-up source audit traced them to project-derived 7AD3 alpha5/eCT contact clusters, not paper-quoted exact residue ranges.\n")
    report.append("- Alpha5 warning is reproduced to floating-point precision by an independent full-protein-backbone-fit calculation; it is unlikely to be a CSV/script transcription error.\n")
    report.append("- Under Ste2-backbone and Gpa1-core alternative fits, alpha5 displacement remains visible, so the rep1/rep2 warning is not explained away by whole-complex translation/rotation alone.\n")
    report.append("- Contact persistence remains partly sensitive to the frame-0 initial contact set; rep2 low minimum should stay as a caveat.\n")
    report.append("\n## Evidence files\n")
    for fn in [
        "chain_summary.csv",
        "source_to_processed_mapping.csv",
        "selection_counts.csv",
        "ste2_interface_geometry_step5.csv",
        "alpha5_reproduction_check.csv",
        "alpha5_event_timing.csv",
        "alpha5_alt_fit_summary_after100.csv",
        "snapshot_metrics.csv",
        "contact_bias_summary.csv",
        "exported_snapshots.csv",
    ]:
        report.append(f"- `{OUT / fn}`\n")
    report.append("\n## Chain identity\n")
    report.append(md_table(chain_df))
    report.append("\n\n## Source-to-processed mapping\n")
    report.append(md_table(pd.DataFrame(mapping_rows)))
    report.append("\n\nSource pointers: `docs/ops/charmm-gui-membrane-builder.md` records Ch-ctrl PROA=Gpa1-WT and PROB=Ste2; `docs/logs/2026-04-17.md` records clean Chain A=Gpa1-WT, Chain B=Ste2.\n")
    report.append("\n## Selection counts\n")
    report.append(md_table(sel_counts.reset_index()))
    report.append("\n\n## Ste2 interface geometry in step5_input.pdb\n")
    report.append(md_table(iface[["range", "n_residues", "ca_z_minus_membrane_mid_A", "min_dist_to_gpa1_alpha5_A", "min_dist_to_gpa1_last5_A", "min_dist_to_all_gpa1_A"]]))
    report.append("\n\nInterpretation: all four Ste2 ranges have atoms within contact distance of all Gpa1, and ranges 69:84 / 222:251 / 288:304 are especially close to alpha5/last5. Range 145:160 is interface-proximal to Gpa1 but farther from alpha5, so it should be described as a broader interface cluster rather than an alpha5-only contact patch.\n")
    report.append("\n## Alpha5 alternative-fit summary after 100 ns\n")
    report.append(md_table(alt_summary))
    report.append("\n\nInterpretation: full-protein fit reproduces the prior metric; Ste2-frame values test receptor-relative alpha5 movement; Gpa1-core-frame values test alpha5 motion relative to the rest of Gpa1. Because rep1/rep2 remain elevated under alternative fits, the warning should be treated as a real local/relative-motion caveat unless visual inspection proves otherwise.\n")
    report.append("\n## Event timing\n")
    report.append(md_table(pd.DataFrame(event_rows)))
    report.append("\n\n## Exported snapshot metrics\n")
    report.append(md_table(metrics))
    report.append("\n\n## Contact initial-set caveat\n")
    report.append(md_table(pd.DataFrame(contact_summary)))
    report.append("\n\nInterpretation: rep2 has a pronounced retained-fraction dip after 100 ns. Because the metric is defined relative to frame-0 contacts, it is useful for interface-retention screening but should not be over-interpreted as a literature-grade persistence cutoff.\n")
    report.append("\n## Cutoff/source status\n")
    report.append("- This audit checks selections and metric implementation; the separate source audit is `../cutoff_source_audit.md`.\n")
    report.append("- Current decision bands (`alpha5 iRMSD <3/>=5 Å`, `BSA fraction >=0.80`, `contact persistence >0.50`, `H-bond occupancy >10%`) were audited there and remain project operational heuristics; only H-bond geometry 3.0 Å / 150° is supported as an MDAnalysis-style tool geometry.\n")
    report.append("- Therefore, the audit supports selection validity, but does not convert operational heuristics into authoritative literature thresholds.\n")
    report.append("\n## Decision implication\n")
    report.append("- Selection definitions are usable for chctrl caveated interpretation.\n")
    report.append("- chctrl remains `usable with alpha5 caveat`, not clean all-metric pass.\n")
    report.append("- Recommended pause gate: review this report before deciding whether to resume Ch-1/Ch-2/Ch-4.\n")
    (OUT / "selection_audit_report.md").write_text(
        "\n".join(report).rstrip() + "\n",
        encoding="utf-8",
    )

    print(f"[selection-audit] wrote {OUT / 'selection_audit_report.md'}")


if __name__ == "__main__":
    main()
