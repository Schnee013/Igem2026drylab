# SwissDock `.dock4` 通用可视化与二维接触分析

本教程适用于 ChimeraX 1.12。一个 `.dock4` 文件中的全部 poses 由 ViewDock 统一浏览；选定 pose 后，再运行相同的显示和接触分析命令。

## 1. 直接打开两个现有 AF2 中性作业

在 macOS Terminal 中每次运行一条命令。命令会同时打开对应的受体和完整 `.dock4`，并启动 ViewDock。

### Gpr2 AF2，中性主作业

```zsh
/Applications/ChimeraX-1.12.app/Contents/bin/ChimeraX --cmd 'open "/Users/yangruoxi/Projects/Docking Lab/swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/gpr2-ascr3/swissdock-neutral-rerun-20260811/files/receptor.pdb"; open "/Users/yangruoxi/Projects/Docking Lab/swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/gpr2-ascr3/swissdock-neutral-rerun-20260811/result.dock4" format swissdock'
```

### Gpr3 AF2，中性

```zsh
/Applications/ChimeraX-1.12.app/Contents/bin/ChimeraX --cmd 'open "/Users/yangruoxi/Projects/Docking Lab/swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/gpr3-ascr3/swissdock-job-13135222/files/receptor.pdb"; open "/Users/yangruoxi/Projects/Docking Lab/swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/gpr3-ascr3/swissdock-job-13135222/result.dock4" format swissdock'
```

## 2. 在 ViewDock 中浏览全部 poses

ViewDock 表格中每一行对应一个 pose：

- 单击一行：只显示该 pose；
- Mac 按住 `Command` 再单击：同时选择多个 poses；
- 单击评分列标题：按该列排序；
- `good`、`maybe`、`bad`：记录人工判断；
- 上下方向键：切换到相邻 pose。

打开作业后先在 ChimeraX 命令行运行：

```chimerax
info models
```

本教程以下用受体 `#1`、第一个 pose `#2.1` 举例。每次切换 pose 后，将所有命令中的 `#2.1` 替换成 `info models` 显示的实际子模型编号。

## 3. 推荐的基础显示

### Cartoon 蛋白 + stick 配体

```chimerax
hide #1 atoms
show #1 cartoons
color #1 light gray
show #2.1 atoms
style #2.1 stick
color #2.1 orange
view #1
```

### 半透明蛋白表面 + 不透明配体

最适合判断配体位于口袋内部、受体表面还是 TM 束外侧。

```chimerax
surface #1
transparency #1 70 surfaces
transparency #2.1 0 atoms
```

恢复表面不透明或隐藏表面：

```chimerax
transparency #1 0 surfaces
hide #1 surfaces
```

### 透明 Cartoon

```chimerax
transparency #1 70 cartoons
```

恢复不透明：

```chimerax
transparency #1 0 cartoons
```

### 只显示原子级蛋白 backbone

这里的 backbone 指 N、CA、C、O 等主链原子，不是 cartoon。

```chimerax
hide #1 cartoons
hide #1 atoms
show (#1 & backbone) atoms
style (#1 & backbone) stick
color (#1 & backbone) light gray
```

恢复为 cartoon：

```chimerax
hide #1 atoms
show #1 cartoons
```

## 4. 显示当前 pose 的局部结合环境

默认使用统一的 4.5 Å 几何阈值：

```chimerax
select clear
select zone #2.1 4.5 #1 residues true
show sel atoms
style sel stick
color sel cyan
label sel residues
view sel
```

`select zone` 返回至少有一个原子进入 4.5 Å 范围的完整受体残基。它回答“哪些残基靠近配体”，不等同于氢键或特定相互作用。

清除选择和残基标签：

```chimerax
select clear
label delete all residues
```

## 5. 输出接触残基和原子接触明细

以下示例把结果写到桌面。先替换 pose 编号和文件名。

### 去重的 4.5 Å 接触残基清单

```chimerax
select zone #2.1 4.5 #1 residues true
info residues sel saveFile /Users/yangruoxi/Desktop/pose1_contact_residues.txt
```

### ChimeraX 原子接触明细

```chimerax
contacts #2.1 restrict #1 intraModel false interModel true makePseudobonds true reveal true showDist true namingStyle residue saveFile /Users/yangruoxi/Desktop/pose1_contacts.txt
```

`contacts` 使用原子范德华半径和重叠阈值；它与固定 4.5 Å 邻近列表是两种互补判据。

清除接触虚线：

```chimerax
contacts delete
```

## 6. 氢键、盐桥和碰撞

### 配体—受体氢键

```chimerax
hbonds #2.1 restrict #1 reveal true showDist true log true saveFile /Users/yangruoxi/Desktop/pose1_hbonds.txt
```

### 配体—受体盐桥候选

```chimerax
hbonds #2.1 restrict #1 saltOnly true reveal true showDist true name "pose1 salt bridges" saveFile /Users/yangruoxi/Desktop/pose1_salt_bridges.txt
```

### 不合理空间碰撞

```chimerax
clashes #2.1 restrict #1 reveal true showDist true saveFile /Users/yangruoxi/Desktop/pose1_clashes.txt
```

清除相应虚线：

```chimerax
hbonds delete
clashes delete
```

ChimeraX 与 PLIP 的加氢方式和几何阈值可能不同，因此两者的氢键清单可以不完全一致。

## 7. 对标指定文献残基

Gpr2 文献锚点 Y168：

```chimerax
show #1:168 atoms
style #1:168 stick
color #1:168 hot pink
label #1:168 residues
```

显示一个已知原子对的距离时，必须写明两个原子。例如：

```chimerax
distance #1:168@CB #2.1@C color magenta dashes 4 radius 0.08
```

上例中的配体原子 `@C` 只是命令模板。先在图形界面拾取实际最近原子，再替换原子名。距离线只说明几何接近；相互作用类型应结合 PLIP、氢键几何和局部化学环境判断。

清除距离线：

```chimerax
distance delete
```

## 8. 导出当前 pose 的受体—配体复合物

PLIP 和 PoseView 每次只分析一个 pose。假设当前 pose 是 `#2.1`：

```chimerax
combine #1#2.1 modelId #99 name pose1_complex
save /Users/yangruoxi/Desktop/pose1_complex.pdb format pdb models #99
```

导出后用文本编辑器检查：

1. 蛋白原子以 `ATOM` 开头；
2. ascr#3 原子以 `HETATM` 开头；
3. 文件中只有一个受体和一个配体 pose；
4. 配体有独立残基名和链标识，例如 `LIG1` 或 `LIG`。

如果 `#99` 已被占用，换成一个未使用的模型编号。合并模型只用于导出，不改变原始 `.dock4` 文件。

## 9. 用 PLIP 判定相互作用

打开 [PLIP Web](https://plip-tool.biotec.tu-dresden.de/plip-web/plip/index)：

1. 上传 `pose1_complex.pdb`；
2. 选择默认的 protein–ligand 分析；
3. 保留默认相互作用阈值；
4. 运行分析；
5. 下载 `report.xml`、`report.txt`、会话文件和可视化文件。

PLIP 用于报告氢键、疏水接触、盐桥、π 相互作用等满足其几何规则的相互作用。报告中的相互作用类型和距离适合与 ChimeraX 接触结果交叉核对。结果页应选择 ascr#3 对应的 `LIG-Z-1`；`HSD`、`HSE` 等条目是 PLIP 识别出的非标准蛋白残基，不是 ascr#3。

PLIP 从 PDB 坐标重新推断自定义配体的化学结构。配体身份、质子化状态与净电荷应回到 SwissDock 输入及服务器参数文件确认。

## 10. 用 PoseView 生成二维接触图

打开 [ProteinsPlus](https://proteins.plus/)：

1. 上传 `pose1_complex.pdb`；
2. 选择 **PoseView**；
3. 在配体列表中选择 ascr#3 对应的 `LIG1` 或 `LIG`；
4. 运行计算；
5. 在浏览器检查二维蛋白—配体相互作用图；
6. 下载 PDF 结果。

二维图生成后至少检查：

- 配体骨架与 ascr#3 一致；
- 中性或去质子化羧基状态与该 docking 作业一致；
- 图中的残基编号与受体 PDB 一致；
- 关键相互作用与 PLIP/ChimeraX 输出可以相互追溯。

若 PoseView 从复合物 PDB 推断出的 ascr#3 键级、立体化学或质子化状态错误，应改用保留正确化学信息和 docking 坐标的 ligand SDF 作为附加配体输入，再生成二维图。

## 11. 手动保存图片和会话

### 当前画面

```chimerax
save /Users/yangruoxi/Desktop/pose1_view.png width 1600 height 1200 supersample 3
```

### ChimeraX 会话

```chimerax
save /Users/yangruoxi/Desktop/pose1_analysis.cxs
```

会话文件保留当前显示、选择、标签和测量，适合以后继续人工检查。

## 12. 切换下一个 pose 前清理显示

```chimerax
contacts delete
hbonds delete
clashes delete
distance delete
label delete all residues
select clear
close #99
hide #1 atoms
show #1 cartoons
hide #1 surfaces
transparency #1 0 cartoons
```

随后在 ViewDock 中选择下一个 pose，并把命令中的子模型编号和输出文件名一起替换。

## 最小判读记录

每个候选 pose 记录以下内容即可：

| 字段 | 内容 |
|---|---|
| 作业 | 受体、AF2/AF3、配体实际质子化状态 |
| pose | ViewDock 子模型编号及 SwissDock 分数 |
| 全局位置 | 胞外口袋、TM 束内部、受体侧面或其他表面 |
| 文献残基 | 是否进入 4.5 Å 范围；最近原子距离 |
| ChimeraX | 接触残基、氢键、碰撞 |
| PLIP | 相互作用类型、残基和距离 |
| PoseView | 二维图文件名及配体化学结构核对结果 |
| 结论 | 文献一致、部分一致或不一致 |
