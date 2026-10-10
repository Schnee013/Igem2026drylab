reinitialize
set retain_order, 1

load alignment/inputs/structures/TWF154_Gpr2_TGJ68930.1_AF2.pdb, twf_gpr2
create twf_gpr2_tmcore, twf_gpr2 and chain A and (resi 30-50+62-83+101-126+144-164+182-201+326-346+358-380)
save alignment/tm_core/TWF154_Gpr2_TGJ68930.1_TMcore.pdb, twf_gpr2_tmcore

load alignment/inputs/structures/TWF154_Gpr3_TGJ67963.1_AF2.pdb, twf_gpr3
create twf_gpr3_tmcore, twf_gpr3 and chain A and (resi 15-37+48-68+87-112+129-149+169-189+295-315+328-349)
save alignment/tm_core/TWF154_Gpr3_TGJ67963.1_TMcore.pdb, twf_gpr3_tmcore

load alignment/inputs/structures/ATCC24927_Gpr2_G1X9E2_AFDB_v6.pdb, atcc_gpr2
create atcc_gpr2_tmcore, atcc_gpr2 and chain A and (resi 30-50+62-83+101-126+144-164+182-201+326-346+358-380)
save alignment/tm_core/ATCC24927_Gpr2_G1X9E2_TMcore.pdb, atcc_gpr2_tmcore

load alignment/inputs/structures/ATCC24927_Gpr3_G1XJN1_AFDB_v6.pdb, atcc_gpr3
create atcc_gpr3_tmcore, atcc_gpr3 and chain A and (resi 15-37+48-68+87-112+129-149+168-188+295-315+328-349)
save alignment/tm_core/ATCC24927_Gpr3_G1XJN1_TMcore.pdb, atcc_gpr3_tmcore

load alignment/inputs/structures/Aflagrans_GprC_A0A437AGY2_AFDB_v6.pdb, gprc
create gprc_tmcore, gprc and chain A and (resi 9-34+45-65+84-107+125-145+168-188+374-397+406-427)
save alignment/tm_core/Aflagrans_GprC_A0A437AGY2_TMcore.pdb, gprc_tmcore

load alignment/inputs/structures/Celegans_N2_SRBC64_G5ECV4_AFDB_v6.pdb, srbc64
create srbc64_tmcore, srbc64 and chain A and (resi 11-31+45-65+85-105+126-146+178-193+218-238+246-266)
save alignment/tm_core/Celegans_N2_SRBC64_G5ECV4_TMcore.pdb, srbc64_tmcore

quit
