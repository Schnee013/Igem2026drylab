# Gpr2/Gpr3 AF3 model_0–ascr#3 SwissDock AC 全蛋白复现

## 最小任务

使用 AF3 Server 返回的 `model_0` 结构分别完成：

1. Gpr2 AF3 model_0–中性 ascr#3；
2. Gpr3 AF3 model_0–中性 ascr#3。

两个作业均优先采用覆盖全部受体原子的搜索盒。这里的 AF3 第一候选名为 `model_0`。

## 配体化学状态验收

SMILES 用于提交；AC 实际使用的化学状态以返回结果中的 `files/extra.rtf` 和 prepared ligand 为准。中性羧酸应为 `RESI LIG1 0.000` 并含羧基 O–H；pH 7 羧酸根应为 `RESI LIG1 -1.000`、部分电荷总和 −1.0000 且无羧基 O–H。

## 已准备受体

目录：

```text
swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/swissdock-af3-model0-full/
```

| 受体 | 上传文件 | 验收 |
|---|---|---|
| Gpr2 AF3 model_0 | `Gpr2_TGJ68930.1_AF3_model0_full.pdb` | 406 aa，链 A，3159 atoms，与冻结 FASTA 一致 |
| Gpr3 AF3 model_0 | `Gpr3_TGJ67963.1_AF3_model0_full.pdb` | 401 aa，链 A，3160 atoms，与冻结 FASTA 一致 |

两个 PDB 由原始 AF3 `model_0.cif` 只做 CIF→PDB 格式转换，原子坐标不变；未做受体截断、同源对齐或口袋导向移动。结构可用性仍需由序列、原子数及后续 docking 输入验收独立判断。

## 配体

使用中性 isomeric SMILES：

```text
C[C@H](CCCC/C=C/C(=O)O)O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O
```

## 全蛋白搜索盒

搜索盒按每个 AF3 PDB 的全部受体原子边界构建，并在六个方向各增加约 5 Å：

| 受体 | Center x, y, z (Å) | Size x, y, z (Å) |
|---|---|---|
| Gpr2 AF3 model_0 | `-2.7, -3.7, -11.0` | `78.6, 81.7, 125.8` |
| Gpr3 AF3 model_0 | `-12.6, -12.5, 1.1` | `105.6, 126.2, 76.0` |

## SwissDock AC 参数

首选设置：

```text
Engine: Attracting Cavities 2.0
Random Initial Conditions: 1
Sampling exhaustivity: medium / 90°
Cavity prioritization: buried / 70
```

服务器参数检查必须返回 `Your session can be submitted`，脚本才会启动作业。

若完整盒因估算时间超限而未通过，先保持相同完整盒，将 sampling 改为 low / `180°`。这会降低采样密度，但继续搜索全蛋白。只有服务器同时拒绝 `90°` 和 `180°` 时，才另行决定搜索空间拆分。

## CLI 提交教程

接口依据：[SwissDock command-line documentation](https://www.swissdock.ch/command-line.php)。以下命令在 zsh 中运行。

### 1. 检查服务

```zsh
curl -fsS "https://swissdock.ch:8443/"
```

正常返回：

```text
Hello World!
```

### 2. 定义提交函数

将整个代码块一次性粘贴到 zsh：

```zsh
cd "/Users/yangruoxi/Projects/Docking Lab"

SD_BASE="https://swissdock.ch:8443"
REC_DIR="swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/swissdock-af3-model0-full"
OUT_DIR="swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/swissdock-af3-model0-full-cli"
ASCR3_NEUTRAL='C[C@H](CCCC/C=C/C(=O)O)O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O'

mkdir -p "$OUT_DIR"

set_and_start_ac () {
  local session="$1"
  local job="$2"
  local center="$3"
  local size="$4"
  local exhaust="$5"
  local reply

  reply=$(curl -fsS -G \
    --data-urlencode "sessionNumber=$session" \
    --data-urlencode "exhaust=$exhaust" \
    --data-urlencode "cavity=70" \
    --data-urlencode "ric=1" \
    --data-urlencode "boxCenter=$center" \
    --data-urlencode "boxSize=$size" \
    --data-urlencode "name=$job" \
    "$SD_BASE/setparameters") || return 1
  print -r -- "$reply" | tee "$OUT_DIR/$job.parameters-exhaust${exhaust}.txt"

  if ! print -r -- "$reply" | grep -q "Your session can be submitted"; then
    print -u2 -- "参数检查未通过，未启动：$job"
    return 1
  fi

  curl -fsS "$SD_BASE/startdock?sessionNumber=$session" \
    | tee "$OUT_DIR/$job.start.txt"
}

prepare_and_submit_ac () {
  local job="$1"
  local receptor="$2"
  local center="$3"
  local size="$4"
  local reply session

  reply=$(curl -fsS -G \
    --data-urlencode "mySMILES=$ASCR3_NEUTRAL" \
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

  set_and_start_ac "$session" "$job" "$center" "$size" 90
}
```

### 3. 提交两个作业

```zsh
prepare_and_submit_ac \
  Gpr2_AF3_m0_ascr3_neutral_AC_full \
  Gpr2_TGJ68930.1_AF3_model0_full.pdb \
  '-2.7_-3.7_-11.0' \
  '78.6_81.7_125.8'

prepare_and_submit_ac \
  Gpr3_AF3_m0_ascr3_neutral_AC_full \
  Gpr3_TGJ67963.1_AF3_model0_full.pdb \
  '-12.6_-12.5_1.1' \
  '105.6_126.2_76.0'
```

参数检查通过的作业会立即进入队列。失败的作业会保留 session ID 和服务器回执，并停在启动之前。

### 4. 完整盒的低采样后备命令

只对因时间估算未通过的作业运行。下面以 Gpr3 为例：

```zsh
job=Gpr3_AF3_m0_ascr3_neutral_AC_full
session=$(<"$OUT_DIR/$job.session")
set_and_start_ac \
  "$session" "$job" \
  '-12.6_-12.5_1.1' \
  '105.6_126.2_76.0' \
  180
```

Gpr2 后备参数为：

```zsh
job=Gpr2_AF3_m0_ascr3_neutral_AC_full
session=$(<"$OUT_DIR/$job.session")
set_and_start_ac \
  "$session" "$job" \
  '-2.7_-3.7_-11.0' \
  '78.6_81.7_125.8' \
  180
```

### 5. 查询状态

```zsh
for session_file in "$OUT_DIR"/*.session; do
  job=${session_file:t:r}
  session=$(<"$session_file")
  print -- "===== $job | session=$session ====="
  curl -fsS "$SD_BASE/checkstatus?sessionNumber=$session"
  print
done
```

### 6. 下载结果

状态显示 `Calculation is finished` 后，设置 job 名并下载：

```zsh
job=Gpr2_AF3_m0_ascr3_neutral_AC_full
session=$(<"$OUT_DIR/$job.session")
curl -fS \
  "$SD_BASE/retrievesession?sessionNumber=$session" \
  -o "$OUT_DIR/${job}_session-${session}.tar.gz"
```

Gpr3 只需替换第一行的 `job=`。

## 结果验收

每个作业保留：

- `*.session`；
- `*.preplig.txt`；
- `*.preptarget.txt`；
- `*.parameters-exhaust*.txt`；
- `*.start.txt`；
- 原始 `tar.gz`。

解压后检查：

1. `parameters` 中的受体、盒子和 AC 参数正确；
2. `files/extra.rtf` 为 `RESI LIG1 0.000`，并含羧基氢；
3. `result.dock4` 可解析；
4. 代表 pose 仍按最低 AC `MEMBER_SCORE` 选择；
5. Gpr2 用胞外位置和 Y168 判断文献一致性；Gpr3 用胞外位置判断文献一致性。

## 追加单作业：Gpr3 AF3 model_0 + 去质子化 ascr#3

将整个代码块一次性粘贴到 zsh。该命令新建一个 pH 7 session，使用 Gpr3 的完整搜索盒，并保存所有服务器回执。

```zsh
submit_gpr3_deprot_ac () {
  local base="https://swissdock.ch:8443"
  local receptor_dir="swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/inputs/receptors/swissdock-af3-model0-full"
  local out_dir="swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/swissdock-af3-model0-full-cli"
  local job="Gpr3_AF3_m0_ascr3_deprot_pH7_AC_full"
  local smiles='C[C@H](CCCC/C=C/C(=O)[O-])O[C@@H]1O[C@@H](C)[C@H](O)C[C@H]1O'
  local reply session

  mkdir -p "$out_dir"

  reply=$(curl -fsS -G \
    --data-urlencode "mySMILES=$smiles" \
    --data-urlencode "pH=7" \
    "$base/preplig") || return 1
  print -r -- "$reply" | tee "$out_dir/$job.preplig.txt"

  session=$(print -r -- "$reply" | sed -nE \
    's/.*Session number:[[:space:]]*([0-9]+).*/\1/p' | head -n 1)
  if [[ -z "$session" ]]; then
    print -u2 -- "未取得 session ID"
    return 1
  fi
  print -r -- "$session" > "$out_dir/$job.session"

  reply=$(curl -fsS \
    -F "myTarget=@$receptor_dir/Gpr3_TGJ67963.1_AF3_model0_full.pdb" \
    "$base/preptarget?sessionNumber=$session") || return 1
  print -r -- "$reply" | tee "$out_dir/$job.preptarget.txt"
  if ! print -r -- "$reply" | grep -q "Your target has been prepared"; then
    print -u2 -- "受体准备未通过，未启动作业：session=$session"
    return 1
  fi

  reply=$(curl -fsS -G \
    --data-urlencode "sessionNumber=$session" \
    --data-urlencode "exhaust=90" \
    --data-urlencode "cavity=70" \
    --data-urlencode "ric=1" \
    --data-urlencode "boxCenter=-12.6_-12.5_1.1" \
    --data-urlencode "boxSize=105.6_126.2_76.0" \
    --data-urlencode "name=$job" \
    "$base/setparameters") || return 1
  print -r -- "$reply" | tee "$out_dir/$job.parameters-exhaust90.txt"
  if ! print -r -- "$reply" | grep -q "Your session can be submitted"; then
    print -u2 -- "参数检查未通过，未启动作业：session=$session"
    return 1
  fi

  reply=$(curl -fsS \
    "$base/startdock?sessionNumber=$session") || return 1
  print -r -- "$reply" | tee "$out_dir/$job.start.txt"
  print -r -- "Gpr3 去质子化作业 session=$session"
}

cd "/Users/yangruoxi/Projects/Docking Lab"
submit_gpr3_deprot_ac
unset -f submit_gpr3_deprot_ac
```

提交后，从命令输出或 `.session` 文件取得 session ID，再查询：

```zsh
job=Gpr3_AF3_m0_ascr3_deprot_pH7_AC_full
session=$(<"swissdock-Kuo2024/tasks/001-gpr2-gpr3-ascr3-reproduction/runs/swissdock-af3-model0-full-cli/$job.session")
curl -fsS "https://swissdock.ch:8443/checkstatus?sessionNumber=$session"
```

结果可用性需要以 `files/extra.rtf` 中的 `RESI LIG1 -1.000`、部分电荷总和 −1.0000 及无羧基 O–H 键为拓扑验收条件。
