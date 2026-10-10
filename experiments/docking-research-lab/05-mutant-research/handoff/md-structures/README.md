# N84V / V368R：MD结构交付

两种突变体均来自05批次，使用AF3 model_0。每个突变体分别提供与ascr#3、ascr#18对接的配体构象，共四组。

```text
05_n84v/ 或 05_v368r/
├── af3_original/
│   ├── fold_…_model_0.cif  AF3原始全长结构（406 aa）
│   └── raw_model0.pdb     同一原始模型转换成的全长PDB
├── docking_receptor/
│   ├── input.pdb         删段并对齐后的受体（370 aa）
│   ├── prepared.pdb      Meeko制备后的受体PDB
│   └── alignment.json    原始坐标系到对接坐标系的旋转、平移记录
├── ascr3/
│   ├── poses.pdbqt       Vina输出的全部9个配体pose
│   ├── top1.sdf          最低评分配体pose，保留键级、电荷及立体化学信息
│   ├── top1.pdbqt        同一最低评分pose的PDBQT版本
│   └── selection.json    pose选择记录及评分
└── ascr18/               文件结构同ascr3
```

四组最低评分pose均为MODEL 1：

| 受体 | ascr#3 | ascr#18 |
|---|---:|---:|
| N84V | −6.264 | −6.856 |
| V368R | −7.013 | −6.293 |

表中为Vina评分（kcal/mol），用于对接排序。

**构建复合物时注意坐标系：** 配体pose与`docking_receptor/`中的受体处于同一坐标系。对接受体删除了原始编号1–21和164–178，保留原始残基编号。若MD采用全长受体，需先依据`alignment.json`将原始全长结构变换到对接坐标系（或对配体施加逆变换），再组合；原始AF3文件不能直接与当前pose按坐标拼接。

这些文件是结构起点，MD体系及力场参数仍需另行制备。所有结构和pose均原样复制，已逐文件校验一致。JSON中的绝对路径保留原始记录，队友使用本文件夹内对应文件即可。
