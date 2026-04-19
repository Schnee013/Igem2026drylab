# ascr3 CGenFF Penalty Summary

- **Source**: CHARMM-GUI Ligand Reader & Modeler (Job ID: 7627823396)
- **Input**: `experiments/docking/ligands/ascr3_CID16066476.sdf` (PubChem CID 16066476)
- **CGenFF version**: 4.0 (topology/parameter files v5.0)
- **Residue name**: ASC3

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
| C6 | CG311 | +0.169 | 1.063 |
| O1 | OG3C61 | -0.383 | 0.656 |

## Structural Differences from ascr18
- Shorter fatty acid chain (C7 vs C11 in ascr18)
- Contains C=C double bond (CG2DC1 atoms C13, C14) near carboxyl terminus
- All penalty scores identical to ascr18 — shared ascarylose + glycoside scaffold

## Conclusion

All penalties < 10. No QM validation or torsion scan needed.
Same as ascr18: ascarylose sugar head well-covered by CHARMM36, fatty acid + glycoside in CGenFF range.
