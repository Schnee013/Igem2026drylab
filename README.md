# iGEM 2026 — Dry Lab (Computational Modeling)

> **Team**: Schnee013 · **Track**: Biotechnology / Environmental
> **Chassis**: *S. cerevisiae* + STE2 pathway (locked 2026-04-11)
> **Goal**: Early detection of plant-parasitic nematodes via GPCR-based biosensors

---

## Project Overview

Plant-parasitic nematodes (PPN) release characteristic ascaroside pheromones (ascr#18, ascr#3) into soil. The nematode-trapping fungi *Arthrobotrys oligospora* / *A. flagrans* sense these signals via GPCRs (Gpr2, Gpr3, GprC). We heterologously express these receptors in *S. cerevisiae*, couple them through chimeric Gpa1 to the endogenous STE2 MAPK cascade, and produce a visible colorimetric readout for field detection.

### Signal Chain

```
Soil PPNs → ascr#18/ascr#3 → Gpr2/Gpr3/GprC (heterologous)
  → Chimeric Gpa1 → STE2 pathway (Ste11→Ste7→Fus3→Ste12)
  → Colorimetric reporter → Field-level visual readout
```

Computational modeling supports this chain at every stage: receptor-ligand binding specificity, G-protein coupling, intracellular signaling dynamics, and detection threshold prediction.

---

## Modeling Directions

| Priority | Direction | Status | Doc |
|----------|-----------|--------|-----|
| **P0** | Receptor-Ligand Docking | completed | [P0-molecular-docking.md](docs/modeling/P0-molecular-docking.md) |
| **P0** | Chimeric Gpa1 Design | in_progress | [P3-chimeric-gprotein.md](docs/modeling/P3-chimeric-gprotein.md) |
| **P0** | Signal Pathway ODE (STE2) | in_progress | [P0-signal-pathway-ode.md](docs/modeling/P0-signal-pathway-ode.md) |
| **P0** | MD Simulation | learning | [P0-md-simulation.md](docs/modeling/P0-md-simulation.md) |
| **P1** | Soil Ascaroside Diffusion | not_started | [P1-soil-diffusion.md](docs/modeling/P1-soil-diffusion.md) |
| **P1** | Bayesian Nematode Inference | not_started | [P1-bayesian-inference.md](docs/modeling/P1-bayesian-inference.md) |
| **P2** | Economic Benefit Model | not_started | [P2-economic-benefit.md](docs/modeling/P2-economic-benefit.md) |
| **P2** | Dose-Response (Nematicides) | not_started | [P2-dose-response.md](docs/modeling/P2-dose-response.md) |

**Execution order**: Chimeric Gpa1 (blocks wet lab) → ODE (parallel) → MD (last, pending CHARMM-GUI + server)

---

## P0: Molecular Docking (Completed)

Three ascarosides (ascr#3, ascr#7, ascr#18) docked against three fungal GPCRs (Gpr2, Gpr3, GprC) using AutoDock Vina, reproducing Kuo et al. (2024) and Hu et al. (2024).

### Two Pipeline Variants

| Pipeline | Tools | Purpose |
|----------|-------|---------|
| **v2** (main) | OpenBabel + RDKit MMFF + Meeko | Ranking validation (Kuo2024 PASS) |
| **docking-repro** | ADFR Suite + Orca DFT B3LYP/def2-TZVP | Exact Hu2024 reproduction |

### Key Results

- **Alanine scan**: 27 mutations across 3 receptors
- **Saturation mutagenesis**: Channel A core sites x 18 AA
- **Dual-channel ranking**: 122 entries, [ratio_channel_report.md](experiments/docking-repro/analysis/ratio_channel_report.md)
- **Top 6 candidates** selected for wet-lab validation → [wet-lab-handoff-P0-docking.md](docs/modeling/wet-lab-handoff-P0-docking.md)
- High-confidence hits: Gpr2 Y200A (DDG_sel=+1.12), Y378A (+0.92)

### Quick Start (v2)

```bash
conda create -n docking python=3.11
conda activate docking
conda install -c conda-forge openbabel biopython
pip install vina meeko rdkit-pypi plip pyyaml

cd src/modeling/docking
python run_pipeline.py --step all        # Full (~2-4 h on M1 Mac)
python run_pipeline.py --step all --fast # Fast mode (~30 min)
```

### docking-repro (Hu2024 Reproduction)

Requires **ADFR Suite** and **Orca**. Two-stage docking: Stage 1 (40 A / spacing=0.25) -> Stage 2 (20 A / spacing=0.1).

```bash
cd src/modeling/docking-repro
python run_pipeline.py --dry-run   # Preview
python run_pipeline.py --step all  # Full run
```

---

## P0: Chimeric Gpa1 Design (In Progress)

Designing chimeric Gpa1 proteins that couple fungal GPCRs to the yeast STE2 pathway. C-terminal grafting from cognate fungal Ga subunits (AoGpa2, AfGasA) onto yeast Gpa1, following Hara2012/Medici1997 methodology.

- **Coupling**: Gpr2/Gpr3 -> AoGpa2; GprC -> AfGasA
- **Candidates**: 6 chimeras (3 graft lengths x 2 cognate Ga) + WT controls
- **Next**: AlphaFold 3 prediction -> iPAE/interface scoring -> wet-lab handoff

---

## P0: Signal Pathway ODE (In Progress)

Full yeast STE2 MAPK cascade ODE model with parameters from Shaw2019/Fan&Yuan2024/Ladds2005. Sensitivity analysis for 1/2/4 copy number integration.

---

## P0: MD Simulation (Learning)

Production stack: GROMACS + CHARMM36m + CGenFF + CHARMM-GUI + POPC membrane. 8 holo systems pre-registered (2 WT + Top 6 mutants). Pending PI server access.

---

## Repository Structure

```
drylab/
├── docs/
│   ├── INDEX.md              # Project status router
│   ├── DOCMAP.md             # Documentation rules
│   ├── modeling/             # One .md per direction (P0-P2)
│   ├── prd/                  # Strategy, chassis decision, project overview
│   ├── teaching/             # Team training materials (v2: DO/KNOW/REF tracks)
│   ├── papers/               # Literature matrix (47 entries) + summaries
│   ├── decisions/            # Technical decision records
│   ├── ops/                  # SSH, environment, toolchain guides
│   └── logs/                 # Daily work logs
│
├── src/modeling/
│   ├── docking/              # v2 docking pipeline
│   └── docking-repro/        # Hu2024 reproduction pipeline
│
├── experiments/
│   ├── docking/              # v2 pipeline I/O (receptors, ligands, results)
│   ├── docking-repro/        # Reproduction outputs + mutagenesis
│   ├── chimeric-gpa1/        # Chimeric design (sequences, alignment, AF3, scoring)
│   └── md-simulation/        # MD systems (CHARMM-GUI, GROMACS inputs, analysis)
│
├── environments/             # Conda env definitions (mac-docking, win-docking-repro)
└── scripts/                  # Setup scripts (Windows compute node)
```

---

## Key Literature

| Paper | Relevance |
|-------|-----------|
| Kuo et al. (2024) | Gpr2/Gpr3 docking with ascarosides; ranking reference |
| Hu et al. (2024) *Nat Microbiol* | GprC structure-function; docking parameters |
| Hara et al. (2012) | Chimeric Gpa1 C-terminal design methodology |
| Medici et al. (1997) | Chimeric Gpa1-Gsa fusion |
| Mukherjee et al. (2025) | Yeast chassis screening for fungal GPCRs |
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
| BioPython | >=1.81 | PDB parsing |
| PLIP | >=2.3 | Protein-ligand interaction analysis |
| ADFR Suite | 1.0 | Receptor/ligand preparation (docking-repro) |
| Orca | 5.x | DFT ligand optimization (docking-repro) |
| GROMACS | 2024.x | MD simulation (planned) |

---

## Documentation

This project follows a structured documentation system: [docs/DOCMAP.md](docs/DOCMAP.md)

- `docs/INDEX.md` -- project status router (single entry point)
- `docs/modeling/P{N}-*.md` -- per-direction docs with frontmatter
- `docs/decisions/NNN-title.md` -- technical decision records
- `docs/logs/YYYY-MM-DD.md` -- daily work logs

---

*iGEM 2026 · Dry Lab · Last updated: 2026-04-14*
