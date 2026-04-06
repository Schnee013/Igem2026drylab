# iGEM 2026 — Dry Lab (Computational Modeling)

> **Team**: Schnee013 · **Track**: Biotechnology / Environmental  
> **Goal**: Early detection of plant-parasitic nematodes via GPCR-based biosensors

This repository contains all computational modeling code, documentation, and analysis for the iGEM 2026 dry lab module.

---

## Project Overview

Plant-parasitic nematodes (PPN) release ascaroside pheromones into soil. The nematode-trapping fungus *Arthrobotrys oligospora* / *A. flagrans* senses these signals via specific GPCRs (Gpr2, Gpr3, GprC) to trigger trap formation. We use computational modeling to:

1. Characterize the receptor-ligand binding specificity (→ informs biosensor design)
2. Model the intracellular signaling cascade (ODE model)
3. Predict detection thresholds in soil environments

---

## Modeling Directions

| Priority | Direction | Status | Doc |
|----------|-----------|--------|-----|
| **P0** | Receptor-Ligand Docking | `in_progress` | [P0-molecular-docking.md](docs/modeling/P0-molecular-docking.md) |
| **P0** | Signal Pathway ODE | `not_started` | [P0-signal-pathway-ode.md](docs/modeling/P0-signal-pathway-ode.md) |
| **P1** | Soil Ascaroside Diffusion | `not_started` | [P1-soil-diffusion.md](docs/modeling/P1-soil-diffusion.md) |
| **P1** | Bayesian Nematode Abundance Inference | `not_started` | [P1-bayesian-inference.md](docs/modeling/P1-bayesian-inference.md) |
| **P2** | Economic Benefit Model | `not_started` | [P2-economic-benefit.md](docs/modeling/P2-economic-benefit.md) |
| **P2** | Dose-Response (Nematicides) | `not_started` | [P2-dose-response.md](docs/modeling/P2-dose-response.md) |
| **P2** | Biocontrol Lotka-Volterra | `not_started` | [P2-biocontrol-lv.md](docs/modeling/P2-biocontrol-lv.md) |
| **P3** | Chimeric Gpa1 Homology Modeling | `not_started` | [P3-chimeric-gprotein.md](docs/modeling/P3-chimeric-gprotein.md) |

---

## P0: Molecular Docking

We dock three ascarosides (ascr#3, ascr#7, ascr#18) against three fungal GPCRs (Gpr2, Gpr3, GprC) using AutoDock Vina, to reproduce and extend Kuo et al. (2024) and Hu et al. (2024).

### Two Pipeline Variants

| Pipeline | Tools | Purpose |
|----------|-------|---------|
| **v2** (main) | OpenBabel + RDKit MMFF + Meeko | Ranking validation (Kuo2024 ✓) |
| **docking-repro** | ADFR Suite + Orca DFT B3LYP/def2-TZVP | Exact Hu2024 reproduction (absolute values) |

#### v2 Results (production, exhaustiveness=200)

| Receptor | ascr#18 | ascr#3 | ascr#7 |
|----------|---------|--------|--------|
| Gpr2 | -6.51 | -6.28 | **-6.65** |
| Gpr3 | -5.96 | **-6.28** | -6.24 |
| GprC | -6.05 | **-6.45** | -6.27 |

- Kuo2024 Gpr2 ranking (ascr#7 > ascr#3): **PASS** ✓
- Kuo2024 Gpr3 ranking (ascr#3 > ascr#7): **PASS** ✓

### Quick Start (v2)

```bash
# Create conda environment
conda create -n docking python=3.11
conda activate docking
conda install -c conda-forge openbabel biopython
pip install vina meeko rdkit-pypi plip pyyaml

# Run full pipeline (~2–4 h on M1 Mac)
cd src/modeling/docking
python run_pipeline.py --step all

# Fast mode for testing (~30 min)
python run_pipeline.py --step all --fast
```

### docking-repro (Hu2024 Exact Reproduction + In Silico Mutagenesis)

Requires **ADFR Suite** and **Orca** (see [scripts/win-setup/](scripts/win-setup/) for Windows installation).  
Two-stage docking: Stage 1 (40 Å / spacing=0.25) → Stage 2 (20 Å / spacing=0.1) to work around Vina grid limits.

**Alanine scan complete (2026-04-05)**: 27 mutations across 3 receptors. Key finding: Gpr2 Y200A (ΔΔG_sel=+1.12) and Y378A (+0.92) are high-confidence wet-lab candidates. See [mutagenesis report](experiments/docking-repro/mutagenesis/mutagenesis_report.md).

```bash
cd src/modeling/docking-repro
python run_pipeline.py --dry-run   # Preview plan
python run_pipeline.py --step all  # Full run (requires ADFR + Orca installed)
```

---

## Repository Structure

```
.
├── docs/
│   ├── INDEX.md              # Global project status
│   ├── DOCMAP.md             # Documentation rules
│   ├── modeling/             # One .md per modeling direction (P0–P3)
│   ├── prd/                  # Strategy, chassis decision
│   ├── papers/
│   │   ├── summaries/        # Literature summaries (17 papers)
│   │   └── literature-matrix.md
│   ├── decisions/            # Technical decision records
│   └── logs/                 # Daily work logs
│
├── src/modeling/
│   ├── docking/              # v2 pipeline (AutoDock Vina)
│   └── docking-repro/        # Hu2024 exact reproduction pipeline
│
├── experiments/
│   ├── docking/
│   │   ├── receptors/        # AlphaFold PDB structures (Gpr2, Gpr3, GprC)
│   │   ├── ligands/          # PubChem SDF (ascr#3, #7, #18)
│   │   ├── prepared/         # Generated PDBQT (git-ignored)
│   │   ├── results/          # Docking poses & interactions (git-ignored)
│   │   └── analysis/         # Affinity matrix, heatmap, validation reports
│   └── docking-repro/        # Reproduction pipeline outputs
│
├── scripts/
│   └── win-setup/            # PowerShell scripts for Windows compute node setup
│
└── configs/                  # Shared configuration files
```

---

## Key Literature

| Paper | Relevance |
|-------|-----------|
| Kuo et al. (2024) | Gpr2/Gpr3 docking with ascarosides; ranking reference |
| Hu et al. (2024) *Nat Microbiol* | GprC structure-function; exact docking parameters reference |
| Hsueh et al. (2013) | NTF ascaroside sensing (foundational) |
| Chen et al. (2021, 2022) | MAPK and cAMP-PKA downstream signaling |

Full literature matrix: [docs/papers/literature-matrix.md](docs/papers/literature-matrix.md) (47 entries, 6 tiers)

---

## Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11 | All pipelines |
| AutoDock Vina | 1.2.6 | Molecular docking engine |
| RDKit | 2024.3 | Ligand preparation |
| Meeko | 0.7 | Ligand PDBQT generation |
| OpenBabel | 3.1 | Receptor preparation (v2) |
| BioPython | ≥1.81 | PDB parsing, TM domain extraction |
| PLIP | ≥2.3 | Protein-ligand interaction analysis |
| ADFR Suite | 1.0 | Receptor/ligand preparation (docking-repro) |
| Orca | 5.x | DFT ligand geometry optimization (docking-repro) |

---

## Documentation System

This project follows a structured documentation system defined in [docs/DOCMAP.md](docs/DOCMAP.md):
- `docs/INDEX.md` — single source of truth for project status
- Each modeling direction has its own `docs/modeling/P{N}-*.md` with frontmatter status
- Technical decisions are recorded in `docs/decisions/NNN-title.md`
- Daily logs in `docs/logs/YYYY-MM-DD.md`

---

*iGEM 2026 · Dry Lab · Last updated: 2026-04-04*
