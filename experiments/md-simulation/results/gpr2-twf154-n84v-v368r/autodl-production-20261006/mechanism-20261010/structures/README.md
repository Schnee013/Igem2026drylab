# 实际代表结构

每个 `*_six_frames.pdb` 含6个MODEL，依次为0、10、25、50、75、100 ns；REMARK记录时间。坐标直接来自已核验的受体+配体processed轨迹，没有补画原子。每组保留本身坐标系，跨组查看应再按共同核心拟合。

原子名称和次序来自本组参考PDB，配体残基名受PDB格式截断为ASCR；完整名称、基团及电荷见本组ligand_atom_mapping.csv。NPZ精确坐标保存在e2_delivery各组目录。PDB为0.001 Å精度，原分析使用未舍入坐标。

所引：e2_delivery中的representative_coordinates.npz和上一轮各组protein_ref.pdb。被引：中文报告、代表构象图。
