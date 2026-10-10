# Gpr2/Gpr3–ascr#3 SwissDock AC 聚焦 4×2 矩阵

## 目的

用同一个胞外同源口袋小盒比较四个受体结构与 ascr#3 的两种末端羧基状态：

- Gpr2 AF2 rank 1
- Gpr2 AF3 model 0
- Gpr3 AF2 rank 1
- Gpr3 AF3 model 0
- 中性羧酸 `C(=O)O`
- 去质子化羧酸盐 `C(=O)[O-]`，形式电荷 −1

共 4 × 2 = 8 个 SwissDock AC 作业。

本矩阵是文献胞外位置引导的 focused docking。它用于比较指定口袋中的 pose，不用于宣称复现全蛋白 blind docking 搜索过程。

## 受体文件

上传文件目录：

```text
../inputs/receptors/swissdock-focused-4x2/
```

| 受体 | 上传文件 | 说明 |
|---|---|---|
| Gpr2 AF2 rank 1 | `Gpr2_TGJ68930.1_AF2_rank1_focused_ref.pdb` | 参考坐标；与原始 AF2 rank-1 PDB 完全相同 |
| Gpr2 AF3 model 0 | `Gpr2_TGJ68930.1_AF3_model0_focused_aligned.pdb` | AF3 CIF 转 PDB后，以高置信度核心刚体对齐到 Gpr2 AF2 rank 1 |
| Gpr3 AF2 rank 1 | `Gpr3_TGJ67963.1_AF2_rank1_focused_aligned.pdb` | 以高置信度同源非柔性核心刚体对齐到 Gpr2 AF2 rank 1 |
| Gpr3 AF3 model 0 | `Gpr3_TGJ67963.1_AF3_model0_focused_aligned.pdb` | 先对齐 Gpr3 AF2 rank 1，再进入共同参考坐标系 |

刚体对齐只改变整体旋转和平移，保留每个预测模型的内部构象。

## 统一搜索盒

四个受体均使用：

```text
Box center: 17.98, -14.93, -13.29 Å
Box size:   24, 24, 24 Å
```

中心来自现有 Gpr2 文献一致 pose 的 ascr#3 重原子质心；Gpr3 通过高置信度 TM/结构核心同源对齐映射到该胞外区域。

## ascr#3 SMILES

### 中性羧酸

```text
C[C@H](CCCC/C=C/C(=O)O)O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O
```

### 去质子化羧酸盐

```text
C[C@H](CCCC/C=C/C(=O)[O-])O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O
```

## SwissDock AC 固定设置

```text
Engine: Attracting Cavities 2.0
Random Initial Conditions: 1
Sampling: medium / 90°
Cavity prioritization: buried / 70
Box center: 17.98, -14.93, -13.29
Box size: 24, 24, 24
```

若 24 Å 盒仍未通过运行时间检查，八个作业统一改为 `22, 22, 22 Å`，中心保持不变。

## 八个作业

| # | 建议 job 名 | 受体文件 | ascr#3 状态 | job ID |
|---:|---|---|---|---|
| 1 | `Gpr2_AF2_r1_ascr3_neutral_AC_focus24` | `Gpr2_TGJ68930.1_AF2_rank1_focused_ref.pdb` | 中性 | ________ |
| 2 | `Gpr2_AF2_r1_ascr3_carboxylate_AC_focus24` | `Gpr2_TGJ68930.1_AF2_rank1_focused_ref.pdb` | −1 | ________ |
| 3 | `Gpr2_AF3_m0_ascr3_neutral_AC_focus24` | `Gpr2_TGJ68930.1_AF3_model0_focused_aligned.pdb` | 中性 | ________ |
| 4 | `Gpr2_AF3_m0_ascr3_carboxylate_AC_focus24` | `Gpr2_TGJ68930.1_AF3_model0_focused_aligned.pdb` | −1 | ________ |
| 5 | `Gpr3_AF2_r1_ascr3_neutral_AC_focus24` | `Gpr3_TGJ67963.1_AF2_rank1_focused_aligned.pdb` | 中性 | ________ |
| 6 | `Gpr3_AF2_r1_ascr3_carboxylate_AC_focus24` | `Gpr3_TGJ67963.1_AF2_rank1_focused_aligned.pdb` | −1 | ________ |
| 7 | `Gpr3_AF3_m0_ascr3_neutral_AC_focus24` | `Gpr3_TGJ67963.1_AF3_model0_focused_aligned.pdb` | 中性 | ________ |
| 8 | `Gpr3_AF3_m0_ascr3_carboxylate_AC_focus24` | `Gpr3_TGJ67963.1_AF3_model0_focused_aligned.pdb` | −1 | ________ |

## CLI 提交命令

接口依据：[SwissDock command-line documentation](https://www.swissdock.ch/command-line.php)。以下命令在项目根目录运行；每个作业使用独立 session，并将 session ID 和服务器回执保存到 `runs/swissdock-focused-4x2-cli/`。

### 1. 定义公共参数与提交函数

将整个代码块一次性粘贴到 zsh：

```zsh
cd "/Users/yangruoxi/Projects/Docking Lab"

SD_BASE="https://swissdock.ch:8443"
REC_DIR="swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/swissdock-focused-4x2"
OUT_DIR="swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/swissdock-focused-4x2-cli"
SMILES_NEUTRAL='C[C@H](CCCC/C=C/C(=O)O)O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O'
SMILES_CARBOXYLATE='C[C@H](CCCC/C=C/C(=O)[O-])O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O'

mkdir -p "$OUT_DIR"

submit_ac () {
  local job="$1"
  local receptor="$2"
  local smiles="$3"
  local reply session parameters

  reply=$(curl -fsS -G \
    --data-urlencode "mySMILES=$smiles" \
    "$SD_BASE/preplig") || return 1
  print -r -- "$reply" | tee "$OUT_DIR/$job.preplig.txt"

  session=$(print -r -- "$reply" | sed -nE \
    's/.*Session number:[[:space:]]*([0-9]+).*/\1/p' | head -n 1)
  if [[ -z "$session" ]]; then
    print -u2 -- "未取得 session ID：$job"
    return 1
  fi
  print -r -- "$session" > "$OUT_DIR/$job.session"

  curl -fsS \
    -F "myTarget=@$REC_DIR/$receptor" \
    "$SD_BASE/preptarget?sessionNumber=$session" \
    | tee "$OUT_DIR/$job.preptarget.txt" || return 1

  parameters=$(curl -fsS -G \
    --data-urlencode "sessionNumber=$session" \
    --data-urlencode "exhaust=90" \
    --data-urlencode "cavity=70" \
    --data-urlencode "ric=1" \
    --data-urlencode "boxCenter=17.98_-14.93_-13.29" \
    --data-urlencode "boxSize=24_24_24" \
    --data-urlencode "name=$job" \
    "$SD_BASE/setparameters") || return 1
  print -r -- "$parameters" | tee "$OUT_DIR/$job.parameters.txt"

  if ! print -r -- "$parameters" | grep -q "Your session can be submitted"; then
    print -u2 -- "参数检查未通过，未启动：$job；请查看 $OUT_DIR/$job.parameters.txt"
    return 1
  fi

  curl -fsS "$SD_BASE/startdock?sessionNumber=$session" \
    | tee "$OUT_DIR/$job.start.txt"
  print -- "$job session=$session 已提交"
}
```

### 2. 提交 8 个作业

依次运行以下 8 条命令。某条命令参数检查失败时，该作业不会启动；先查看对应的 `*.parameters.txt`。

```zsh
submit_ac \
  Gpr2_AF2_r1_ascr3_neutral_AC_focus24 \
  Gpr2_TGJ68930.1_AF2_rank1_focused_ref.pdb \
  "$SMILES_NEUTRAL"

submit_ac \
  Gpr2_AF2_r1_ascr3_carboxylate_AC_focus24 \
  Gpr2_TGJ68930.1_AF2_rank1_focused_ref.pdb \
  "$SMILES_CARBOXYLATE"

submit_ac \
  Gpr2_AF3_m0_ascr3_neutral_AC_focus24 \
  Gpr2_TGJ68930.1_AF3_model0_focused_aligned.pdb \
  "$SMILES_NEUTRAL"

submit_ac \
  Gpr2_AF3_m0_ascr3_carboxylate_AC_focus24 \
  Gpr2_TGJ68930.1_AF3_model0_focused_aligned.pdb \
  "$SMILES_CARBOXYLATE"

submit_ac \
  Gpr3_AF2_r1_ascr3_neutral_AC_focus24 \
  Gpr3_TGJ67963.1_AF2_rank1_focused_aligned.pdb \
  "$SMILES_NEUTRAL"

submit_ac \
  Gpr3_AF2_r1_ascr3_carboxylate_AC_focus24 \
  Gpr3_TGJ67963.1_AF2_rank1_focused_aligned.pdb \
  "$SMILES_CARBOXYLATE"

submit_ac \
  Gpr3_AF3_m0_ascr3_neutral_AC_focus24 \
  Gpr3_TGJ67963.1_AF3_model0_focused_aligned.pdb \
  "$SMILES_NEUTRAL"

submit_ac \
  Gpr3_AF3_m0_ascr3_carboxylate_AC_focus24 \
  Gpr3_TGJ67963.1_AF3_model0_focused_aligned.pdb \
  "$SMILES_CARBOXYLATE"
```

### 3. 查询全部作业状态

```zsh
for session_file in "$OUT_DIR"/*.session; do
  job=${session_file:t:r}
  session=$(<"$session_file")
  print -- "===== $job | session=$session ====="
  curl -fsS "$SD_BASE/checkstatus?sessionNumber=$session"
  print
done
```

### 4. 下载状态为 finished 的作业

确认某个作业状态为 `Calculation is finished` 后，用其 job 名运行：

```zsh
job=Gpr2_AF2_r1_ascr3_neutral_AC_focus24
session=$(<"$OUT_DIR/$job.session")
curl -fS \
  "$SD_BASE/retrievesession?sessionNumber=$session" \
  -o "$OUT_DIR/${job}_session-${session}.tar.gz"
```

其余作业只需替换第一行的 `job=`。下载完成后保留原始 `tar.gz`，再进行解压和电荷验收。

## 结果保存与电荷验收

每个作业保存原始 ZIP、job ID、`parameters`、`result.dock4` 和 `files/` 目录。

四个羧酸盐作业的有效状态由服务器最终参数文件判定：

- `files/extra.rtf` 中 `RESI LIG1` 总电荷应为 `-1.000`；
- 羧酸盐氧上应无新增羧基氢；
- 最终 ligand 原子电荷之和应为 −1。

若服务器给出 `RESI LIG1 0.000` 或给羧基氧加氢，该作业记录为“服务器中和”，并按实际中性状态解释。

## 输入验收

| 检查 | Gpr2 AF2 | Gpr2 AF3 | Gpr3 AF2 | Gpr3 AF3 |
|---|---:|---:|---:|---:|
| 残基数 | 406 | 406 | 401 | 401 |
| 链 | A | A | A | A |
| 与冻结 FASTA 一致 | 是 | 是 | 是 | 是 |
| 24 Å 盒内残基数 | 54 | 58 | 50 | 47 |

结构核心对齐 RMSD：Gpr2 AF3→AF2 为 0.54 Å；Gpr3 AF3→AF2 为 0.55 Å；Gpr3 AF2→Gpr2 AF2 同源核心为 0.92 Å。
