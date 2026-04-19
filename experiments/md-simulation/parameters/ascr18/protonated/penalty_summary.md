# ascr18 CGenFF Penalty Summary

- **Source**: CHARMM-GUI Ligand Reader & Modeler (Job ID: 7627791619)
- **Input**: `experiments/docking/ligands/ascr18_CID71514784.sdf` (PubChem CID 71514784)
- **CGenFF version**: 4.0 (topology/parameter files v5.0)
- **Residue name**: ASC18

## Overall

| Metric | Value | Threshold |
|--------|-------|-----------|
| Param penalty (max) | **5.500** | < 10 = fair analogy |
| Charge penalty (max) | **3.365** | < 10 = fair analogy |

## Parameter Penalties

### BONDS
No new bond parameters needed — all covered by existing CGenFF types.

### ANGLES
| Type | Penalty | Source analogy |
|------|---------|---------------|
| CG311-OG301-CG311 | 0.6 | from CG311-OG301-CG321 (glycosidic bond angle) |

### DIHEDRALS (highest penalty section)
| Type | Penalty | Source analogy |
|------|---------|---------------|
| OG301-CG311-CG311-OG311 | **5.5** | from OG311-CG311-CG321-OG303 (sugar ring–glycoside) |
| OG3C61-CG311-OG301-CG311 | 1.5 | from OG3C61-CG311-OG301-CG331 |
| All others | 0.6 | close analogies |

### IMPROPERS
None.

## Charge Penalties (top 5)
| Atom | Type | Charge | Penalty |
|------|------|--------|---------|
| C1 | CG311 | +0.043 | 3.365 |
| C4 | CG311 | +0.232 | 3.194 |
| O2 | OG301 | -0.367 | 2.935 |
| C17 | CG2O2 | +0.735 | 2.191 |
| O5 | OG311 | -0.600 | 1.952 |

## Conclusion

All penalties < 10. No QM validation or torsion scan needed.
The ascarylose sugar head is well-covered by CHARMM36 carbohydrate parameters,
and the fatty acid chain + alpha-O-glycoside bridge falls within CGenFF drug-like range.
