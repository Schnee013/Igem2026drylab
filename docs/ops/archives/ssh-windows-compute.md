# SSH 远程调用 Windows 计算节点操作指南

> ⚠️ **[已弃用 — 2026-04-18]** Windows 7500F 计算节点已停用，所有计算任务已迁移至 Slurm GPU 集群。  
> 本文档仅作历史参考，**不再维护**。当前操作规范见 [docs/ops/slurm-md-server.md](../slurm-md-server.md)。
>
> **例外**：部分 docking 阶段的结构文件（PDBQT、结果 JSON、AF3 预测）仍存于 Windows 节点 `D:\drylab-tools\workspace\`。  
> 需要访问这些文件时，参考本文档的 SSH 调用规范（§标准模板）和 §环境信息。

---

> 适用环境: Mac M1 → Windows 7500F (100.87.153.84) via Tailscale SSH  
> 更新日期: 2026-04-06  
> 教训来源: S1 WT 重对接启动过程中踩的坑（详见 [2026-04-06 日志](../../logs/2026-04-06.md)）

---

## 根本原因分析

### 现象

以下命令在 SSH 中返回 **exit code 127**（command not found）：

```bash
# ❌ 失败：用完整路径运行 Python + 脚本路径
ssh Administrator@100.87.153.84 "D:\\path\\python.exe D:\\path\\script.py"
# ❌ 失败：cmd /c 包裹
ssh Administrator@100.87.153.84 "cmd /c \"D:\\path\\python.exe D:\\path\\script.py\""
```

但以下命令**成功**：

```bash
# ✓ 成功：用 PATH 中的 python（但 numpy 未安装，所以报 ImportError）
ssh Administrator@100.87.153.84 "python D:/path/script.py"
# ✓ 成功：只带一个参数的完整路径
ssh Administrator@100.87.153.84 "D:\\path\\python.exe --version"
```

### 根本原因

**Windows OpenSSH 默认 Shell 不是 cmd.exe，而是 MobaXterm 提供的 POSIX bash**。

MobaXterm 在用户 PATH 中注入了自己的 bash（`C:\Users\Administrator\AppData\Roaming\MobaXterm\slash\mx86_64b\bin`），Windows OpenSSH 在启动非交互式 SSH session 时会用 PATH 中排在最前面的 shell。

在 POSIX bash 中：
- 反斜杠 `\x` 是转义前缀（`\d` → `d`，`\r` → `r`，`\e` → `e`，…）
- 当 Mac bash 将 `"D:\\path\\script.py"` 发送给 SSH 时，Mac bash 先处理一次：`\\` → `\`
- 远端 bash 收到 `D:\path\script.py`，再处理一次：`\p` → `p`，`\s` → `s`，…
- 路径变成乱码，Python 找不到文件，返回 127

**为什么单参数（`--version`）不失败？**  
`--version` 不含反斜杠，不受影响。bash 成功调用了 Windows EXE（bash 可以通过 CreateProcess 执行 `.exe`），Python 输出版本号。

**为什么 `set PATH=...;%PATH% && python script.py` 成功？**  
实际上是 bash 也能处理这种形式（`&&` 是 bash 语法，`python` 在 PATH 中可被找到），或者 conda activate 会切换到 cmd.exe 子进程。关键是 **`python`（不带路径前缀）+ `D:/path/script.py`（正斜杠）** 的组合不含被 bash 错误处理的反斜杠。

---

## 经验一览

### ❌ 不要这样做

```bash
# 完整 Windows 路径的 python + 完整路径的脚本 → exit 127
ssh host "D:\\path\\python.exe D:\\path\\script.py"

# conda run 有 GBK 编码问题（中文 Windows），会 UnicodeEncodeError
ssh host "conda run --prefix D:\\env python script.py"

# start + 嵌套重定向 → bat 无法正常启动
ssh host "start \"Title\" /MIN cmd /c \"bat.bat > log.txt 2>&1\""

# call conda activate 在非交互式 SSH 中无效（conda hook 未初始化）
ssh host "call C:\\conda\\Scripts\\activate env && python script.py"
```

### ✓ 正确做法

```bash
# 方法 1（推荐）：PATH 前置 + python（不带完整路径）
ssh host "set PATH=D:\\env;D:\\env\\Scripts;D:\\env\\Library\\bin;%PATH% && set PYTHONIOENCODING=utf-8 && python D:\\path\\script.py --arg value"

# 方法 2：conda activate（需用 C:\conda\Scripts\activate，不用 call）
ssh host "C:\\Users\\Administrator\\miniconda3\\Scripts\\activate D:\\env && set PYTHONIOENCODING=utf-8 && python script.py"

# 方法 3（⚠️ 不推荐，会导致 Python 30s 内静默退出）：PowerShell Start-Process
# 仅在极少数不需要日志输出的场景考虑；长 Python 任务请用方法 run_in_background
ssh host "powershell -Command \"Start-Process cmd -ArgumentList '/c','D:\\path\\run.bat' -RedirectStandardOutput 'D:\\path\\out.log' -RedirectStandardError 'D:\\path\\err.log' -WindowStyle Hidden\""
```

---

## 标准模板

### bat 文件模板（准备好后通过 SSH 触发）

所有长任务写成 `.bat` 文件，存放在 `D:\drylab-tools\workspace\`。bat 文件自包含，不依赖外部 activate：

```batch
@echo off
set PATH=D:\drylab-tools\envs\docking-repro;D:\drylab-tools\envs\docking-repro\Scripts;D:\drylab-tools\envs\docking-repro\Library\bin;%PATH%
set PYTHONIOENCODING=utf-8
python D:\drylab-tools\workspace\run_xxx.py --project-root D:\drylab-tools\workspace
```

写 bat 文件（从 Mac SSH）—— **推荐复制已有 bat 再改最后一行**（避免 echo 转义坑）：

```bash
# ✅ 推荐：基于已有 bat 复制修改
ssh host "cmd /c copy D:\drylab-tools\workspace\run_s1.bat D:\drylab-tools\workspace\run_new.bat /y"
ssh host "powershell -Command \"\$s=Get-Content 'D:\drylab-tools\workspace\run_new.bat'; \$s[-1]='python D:\drylab-tools\workspace\run_xxx.py --project-root D:\drylab-tools\workspace'; Set-Content 'D:\drylab-tools\workspace\run_new.bat' \$s\""
```

⚠️ 不推荐 `echo` 方式写 bat（`\r\n` 成字面量、`%%PATH%%` 被 Mac bash 展开为完整路径导致解析失败，详见踩坑快查表）。

### 后台启动模板（PowerShell Start-Process）

⚠️ **重要限制**：Start-Process `-RedirectStandardOutput` 在某些情况下会导致 Python 进程静默退出（约 30 秒内）。根本原因：PowerShell 父进程退出后，stdout redirect pipe 可能关闭，Python 的 logging.StreamHandler 写失败后静默退出。

推荐用同步 SSH 背景任务代替（见下方）：

```bash
ssh host "powershell -Command \"Start-Process cmd -ArgumentList '/c','D:\\workspace\\run_xxx.bat' -RedirectStandardOutput 'D:\\workspace\\experiments\\docking-repro\\logs\\xxx_stdout.log' -RedirectStandardError 'D:\\workspace\\experiments\\docking-repro\\logs\\xxx_stderr.log' -WindowStyle Hidden; Write-Host 'STARTED'\""
```

### ✅ 推荐：同步 SSH 背景任务（最可靠，适合所有长任务）

```bash
# 在 Claude Code 中用 run_in_background=true 启动，SSH 连接全程保活
ssh host "cmd /c D:\\workspace\\run_xxx.bat" 2>&1
```

- 进程绑定到 SSH 连接，连接存活则进程存活
- 输出实时写入 Claude Code 背景任务 output 文件，可随时用 TaskOutput 查看
- 任务完成时收到 task-notification

验证是否真正启动：

```bash
ssh host "tasklist /fi \"IMAGENAME eq python.exe\""
```

### 查看进度

**原则：合并成一次 SSH，不要多次独立连接；用通配符找最新日志，不要猜文件名。**

日志命名格式：`run_{脚本名}_{YYYYMMDD}_{HHMMSS}.log`，例如 `run_multiseed_20260406_072954.log`。

> **引号规则**：外层用**单引号** `'...'`，PowerShell 命令用双引号 `"..."`。  
> ❌ 不要用双引号包外层再 `\"` 转义——Mac bash 会展开 `\$` 变量，PowerShell 收到的命令残缺，返回空。  
> ✅ 单引号内 Mac bash 完全不处理，`$ms`、`\`、`"` 原样传给远端。

```bash
# ✅ 推荐：一次 SSH 同时查多个任务进度（单引号外层）
ssh Administrator@100.87.153.84 'powershell -Command "
  $ms  = Get-ChildItem D:\drylab-tools\workspace\experiments\docking-repro\logs\run_multiseed_*.log      | Sort-Object LastWriteTime -Desc | Select-Object -First 1;
  $sat = Get-ChildItem D:\drylab-tools\workspace\experiments\docking-repro\logs\run_saturation_gpr2_*.log | Sort-Object LastWriteTime -Desc | Select-Object -First 1;
  $wt  = Get-ChildItem D:\drylab-tools\workspace\experiments\docking-repro\logs\run_wt_twostage_*.log    | Sort-Object LastWriteTime -Desc | Select-Object -First 1;
  Write-Host multiseed:;    if ($ms)  { Get-Content $ms.FullName  -Tail 8 } else { Write-Host NO_LOG };
  Write-Host saturation:;  if ($sat) { Get-Content $sat.FullName -Tail 8 } else { Write-Host NO_LOG };
  Write-Host wt_twostage:; if ($wt)  { Get-Content $wt.FullName  -Tail 8 } else { Write-Host NO_LOG };
  Write-Host processes:;
  Get-Process python,vina -ErrorAction SilentlyContinue | Select-Object Id,CPU,StartTime | Format-Table -AutoSize;
"'

# 检查结果文件是否生成
ssh Administrator@100.87.153.84 'powershell -Command "
  Get-ChildItem D:\drylab-tools\workspace\experiments\docking-repro\results\ -Recurse -Filter *.json |
  Sort-Object LastWriteTime -Desc | Select-Object -First 10 Name,LastWriteTime,Length | Format-Table -AutoSize
"'
```

> ⚠️ 单引号限制：命令内不能再出现单引号（`'`）。如果 PowerShell 命令本身需要单引号（如 `Write-Host '=== xxx ==='`），改用 `Write-Host xxx:` 或双引号字符串代替。
>
> ⚠️ **多行命令静默失败**：PowerShell 命令中含有换行符（heredoc 换行或 `\n`）时，SSH 会静默返回空输出。**必须用分号 `;` 代替换行**，所有语句写在一行内。

---

## 脚本部署规则（强制）

### 单向流：Mac → Windows，禁止反向修改

- **Mac `src/modeling/docking-repro/` 是唯一权威源**，Windows `D:\drylab-tools\workspace\` 是部署目标
- **禁止在 Windows 端新建或修改 `.py` 脚本**，所有改动必须在 Mac 端完成后同步
- 上下文丢失后，模型应读 Mac `src/` 的文件，而非依赖 Windows workspace 中的副本

### 标准同步命令（每次运行脚本前执行）

```bash
# 一条命令同步全部 .py + config.yaml 到 Windows
# ⚠️ 包含 grid_box.py（来自 docking/ 模块，dock.py 的共享依赖，不可省略）
scp src/modeling/docking-repro/*.py src/modeling/docking-repro/config.yaml \
    src/modeling/docking/grid_box.py \
    Administrator@100.87.153.84:'D:/drylab-tools/workspace/'
```

### 同步后清理旧文件

Windows workspace 可能存在已从 Mac src/ 删除的旧 `.py`（如 `test_step.py`、`test_mutagenesis.py`、`run_mutagenesis_*.py` 等遗留文件）。同步后检查并删除：

```bash
# 列出 Windows workspace 根目录的所有 .py
ssh Administrator@100.87.153.84 'powershell -Command "Get-ChildItem D:/drylab-tools/workspace/*.py | Select-Object -ExpandProperty Name"'
# 对比 Mac src/ 文件列表，删除 Windows 上多余的
ssh Administrator@100.87.153.84 'powershell -Command "Remove-Item D:/drylab-tools/workspace/test_step.py, D:/drylab-tools/workspace/test_mutagenesis.py -EA SilentlyContinue"'
```

### Windows 独占文件（同步时不可覆盖）

| 路径 | 说明 |
|------|------|
| `experiments/` 下全部子目录 | 计算产出（results/、logs/、prepared/、ligands/orca/） |
| `run_*.bat` | 硬编码 Windows PATH 的启动脚本 |
| `D:\orca\`、`D:\ADFRsuite\` | 工具二进制 |
| `D:\drylab-tools\envs\docking-repro\` | conda 环境 |

### Windows → Mac（拉回计算结果）

```bash
scp Administrator@100.87.153.84:"D:/drylab-tools/workspace/output.json" \
    ./experiments/docking-repro/results/
```

---

## 环境信息

| 项目 | 值 |
|------|-----|
| Windows 主机 | 100.87.153.84 (Tailscale) |
| 用户 | Administrator |
| 项目根目录（Windows） | `D:\drylab-tools\workspace` |
| conda 环境 | `D:\drylab-tools\envs\docking-repro` |
| vina.exe | `D:\drylab-tools\vina.exe` |
| Orca | `D:\orca\orca.exe` |
| ADFR Suite | `D:\ADFRsuite\bin` |
| 日志目录 | `D:\drylab-tools\workspace\experiments\docking-repro\logs\` |
| 配体 PDBQT | `experiments/docking-repro/prepared/ligands/`（⚠️ 可能为空，需从 `experiments/docking/prepared/ligands/` 复制 ascr18/ascr3） |

---

## 踩坑快查表

| 现象 | 根因 | 解决 |
|------|------|------|
| `exit code 127` | POSIX bash 处理 `D:\path` 反斜杠 | 用 `set PATH=...&&python script.py` 方式 |
| `UnicodeEncodeError: 'gbk'` | `conda run` 用 GBK 输出，脚本含中文 | 不用 `conda run`；用 PATH 方式 + `PYTHONIOENCODING=utf-8` |
| bat 文件启动即退出，log 为 0 bytes | `call conda activate` 在非交互 SSH 无效 | bat 文件改用 `set PATH=...` 方式 |
| `start "..." /MIN cmd /c "... > log 2>&1"` 失败 | SSH 中嵌套引号和重定向符号转义冲突 | 用 PowerShell `Start-Process -RedirectStandardOutput` |
| Python 进程未出现在 `tasklist` | 进程闪退，log 为空 | 先检查 bat 文件是否正确；先手动跑一次 bat 确认无误再后台运行 |
| SSH 前台任务断网后被杀 | SSH 断开 → SIGHUP 传递到子进程 | 后台任务必须用 `Start-Process` 完全 detach |
| Start-Process Python 30s 内静默退出，.err 为空 | PowerShell 父进程退出时 stdout pipe 关闭，Python StreamHandler 写失败静默退出 | 改用同步 SSH + Claude Code `run_in_background=true` |
| bat 文件写入 `\r\n` 成字面量（一整行） | PowerShell `Set-Content` 不处理 `\r\n` 转义序列 | 用 `copy existing.bat new.bat` + PowerShell `Get-Content`/`Set-Content` 替换最后一行 |
| bat 中 `%%PATH%%` 被 Mac bash 展开成完整路径，导致 `%C:\...\bin%` 无法解析 | Mac bash 解析双百分号为单百分号后，cmd 再次展开 `%PATH%` | 直接 copy S1 bat 模板（硬编码完整 PATH），只改最后的 python 命令 |
| S3 运行后 `mutagenesis_results.json = []` | `experiments/docking-repro/prepared/ligands/` 为空，缺少配体 PDBQT | 从 `experiments/docking/prepared/ligands/` 复制 ascr18/ascr3 PDBQT 过来 |
| `ModuleNotFoundError: No module named 'prepare_receptor'` | prepare_receptor.py 等文件未同步到 Windows | `scp prepare_receptor.py prepare_ligand.py run_pipeline.py validate.py host:"D:/workspace/"` |
