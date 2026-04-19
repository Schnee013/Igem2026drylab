#!/usr/bin/env python3
"""Generate mutant protein PDBs using PyMOL mutagenesis wizard.

Dependencies: PyMOL (/opt/homebrew/bin/pymol)
Usage: python3 generate_mutants.py [--pymol PATH] [--only V138R M327A]

Outputs to: systems/{mutant-dir}/{System}_{Name}_protein.pdb
Upload these PDBs to CHARMM-GUI PDB Reader to get PROA.itp.
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SYSTEMS_DIR = PROJECT_ROOT / "experiments" / "md-simulation" / "systems"

MUTATIONS = [
    {"system": "Gpr3", "resid": 138, "to_aa": "ARG", "name": "V138R", "outdir": "gpr3-V138R-ascr18"},
    {"system": "Gpr3", "resid": 170, "to_aa": "GLU", "name": "F170E", "outdir": "gpr3-F170E-ascr18"},
    {"system": "Gpr3", "resid": 141, "to_aa": "ALA", "name": "I141A", "outdir": "gpr3-I141A-ascr18"},
    {"system": "Gpr2", "resid": 327, "to_aa": "ALA", "name": "M327A", "outdir": "gpr2-M327A-ascr18"},
    {"system": "Gpr2", "resid": 327, "to_aa": "ASP", "name": "M327D", "outdir": "gpr2-M327D-ascr18"},
    {"system": "Gpr2", "resid": 59,  "to_aa": "PHE", "name": "R59F",  "outdir": "gpr2-R59F-ascr18"},
]


def run_mutation(pymol_bin, mut):
    """Run a single PyMOL mutation via temp .pml script."""
    wt_gro = SYSTEMS_DIR / f"{mut['system']}_WT" / "gromacs" / "step6.6.gro"
    out_dir = SYSTEMS_DIR / mut["outdir"]
    output_pdb = out_dir / f"{mut['system']}_{mut['name']}_protein.pdb"

    if not wt_gro.exists():
        print(f"  ERROR: {wt_gro} not found")
        return False

    out_dir.mkdir(parents=True, exist_ok=True)

    # PyMOL script: load full system, mutate target residue, save protein-only PDB
    pml = f"""\
load {wt_gro}, wt_system
wizard mutagenesis
cmd.get_wizard().do_select("resi {mut['resid']} and polymer")
cmd.get_wizard().set_mode("{mut['to_aa']}")
cmd.get_wizard().apply()
cmd.get_wizard().cleanup()
wizard
alter polymer, chain='A'
save {output_pdb}, polymer
quit
"""

    with tempfile.NamedTemporaryFile(suffix=".pml", mode="w", delete=False) as f:
        f.write(pml)
        pml_path = f.name

    try:
        result = subprocess.run(
            [pymol_bin, "-cq", pml_path],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode != 0:
            print(f"  ERROR: PyMOL returned {result.returncode}")
            if result.stderr:
                for line in result.stderr.strip().split("\n")[:5]:
                    print(f"    {line}")
            return False
        if not output_pdb.exists():
            print(f"  ERROR: output not found at {output_pdb}")
            return False
        n_atoms = sum(1 for line in open(output_pdb) if line.startswith(("ATOM", "HETATM")))
        print(f"  OK: {output_pdb.name} ({n_atoms} atoms)")
        return True
    except subprocess.TimeoutExpired:
        print(f"  ERROR: PyMOL timed out (300s)")
        return False
    finally:
        Path(pml_path).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pymol", default="/opt/homebrew/bin/pymol",
                        help="Path to PyMOL executable")
    parser.add_argument("--only", nargs="*", metavar="NAME",
                        help="Only generate specific mutations (e.g., V138R M327A)")
    args = parser.parse_args()

    # Verify PyMOL availability
    try:
        r = subprocess.run([args.pymol, "-cq", "-d", "quit"],
                           capture_output=True, timeout=15)
        if r.returncode != 0:
            print(f"ERROR: PyMOL test run failed (rc={r.returncode})")
            sys.exit(1)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"ERROR: PyMOL not found at {args.pymol}")
        sys.exit(1)

    print(f"PyMOL: {args.pymol}")
    print(f"Systems: {SYSTEMS_DIR}")

    targets = MUTATIONS
    if args.only:
        names = {n.upper() for n in args.only}
        targets = [m for m in MUTATIONS if m["name"].upper() in names]
        if not targets:
            print(f"ERROR: no matching mutations for {args.only}")
            sys.exit(1)

    ok = 0
    for mut in targets:
        print(f"\n=== {mut['system']}_{mut['name']} (resi {mut['resid']} -> {mut['to_aa']}) ===")
        if run_mutation(args.pymol, mut):
            ok += 1

    print(f"\n{'=' * 50}")
    print(f"Generated: {ok}/{len(targets)}")
    if ok < len(targets):
        print("Fix errors above and re-run with --only <NAME>.")
        sys.exit(1)
    print("\nNext: upload each PDB to CHARMM-GUI PDB Reader -> FF-Converter")
    print("      to generate PROA.itp for each mutant.")


if __name__ == "__main__":
    main()
