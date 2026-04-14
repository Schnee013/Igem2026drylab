# REF-B：常见坑速查
> 碰到问题先来这里查。每条格式：**症状 → 根因 → 修复**。
---
### 坑 1：`ModuleNotFoundError: No module named 'prolif'`
**根因**：忘记激活 conda 环境，当前在 `base` 里。
**修复**：`conda activate docking`
---
### 坑 2：PDBQT 原子数不对（配体被截断）
**根因**：旧版 `freeze_terminal_torsions()` 的 bug 会删除 ATOM 行。
**修复**：
1. 检查 ATOM/HETATM 行数（ascr18 应 ≥ 26）
2. 确认用 `experiments/docking-repro/prepared/` 下的文件
3. 不对则用 `fix_ascr18.py` 重新生成
---
### 坑 3：相对路径运行失败
**根因**：从子目录运行脚本，相对路径指向错误位置。
**修复**：回到项目根目录再运行：
```bash
cd ~/drylab                           # 回到项目根目录
python src/modeling/docking-repro/run_wt_singlestage.py
```
---
### 坑 4：服务器和 Mac 代码版本不一致
**根因**：在服务器上改了 `.py` 或同步漏了文件。
**修复**：Mac `src/` 是唯一权威源。同步后用 `grep` 检查关键符号确认更新。
---
### 坑 5：PyMOL 里 ligand "飘在" receptor 外面
**根因**：`align` 只变换 receptor 坐标，ligand 还在旧坐标系。
**修复**：
```pml
matrix_copy rec_mut, lig_mut_18
```
---
### 坑 6：BW 编号映射错误
**根因**：锚点选错导致整条映射链偏移。
**修复**：从 TM 内保守残基定位锚点（如 D2.50=ASP53），推导后**交叉验证氨基酸类型**。
---
### 坑 7：PyMOL 加载 complex PDB 分不清受体配体
**修复**：用分离的文件加载：
```pml
load receptors/Gpr3_WT.pdb, rec_wt
load ligands/Gpr3_WT_ascr18.pdb, lig_wt_18
```
---
### 坑 8：Vina 每次结果不一样
**根因**：没固定 seed。
**修复**：`config.yaml` 里 `vina.seed: 42`。Pipeline 脚本自动读取。
---
### 坑 9：pose 里配体和残基"碰在一起"
区分两种情况：
- **情况 A（真的碰了）**：pose 对接本身有问题 → 检查 box / exh / 残基柔性
- **情况 B（坐标系不对）**：align 后没 `matrix_copy` → 屏幕坐标系错觉
**区分方法**：查 ligand 和 receptor 的坐标范围是否重叠。不重叠 = 情况 B。
