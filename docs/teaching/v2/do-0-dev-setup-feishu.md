# DO-0：开发环境搭建
> **前置条件**：无
> **预计耗时**：30 分钟（Mac）/ 45-60 分钟（Windows，含 WSL 安装）
> **学完能做**：打开终端、在 VS Code 里浏览项目代码、用 Copilot 读代码
---
## 1. 安装 VS Code
**Mac**：
1. 打开浏览器，搜索 "Visual Studio Code" 或直接访问 code.visualstudio.com
2. 下载 Mac 版（Apple Silicon / Intel 会自动识别）
3. 打开 `.dmg`，把 VS Code 拖进"应用程序"文件夹
4. 从 Launchpad 打开 VS Code
**Windows**：
1. 搜索 "Visual Studio Code" 或直接访问 code.visualstudio.com
2. 下载 Windows 版安装包
3. 运行安装程序，一路下一步
4. 从开始菜单打开 VS Code
### 安装扩展
打开 VS Code 后，点左侧栏的 **Extensions**（四个方块图标），搜索并安装：
1. **Python** — Microsoft 出品，Python 语法高亮 + 运行支持
2. **GitHub Copilot** — AI 代码助手（需要 GitHub 账号，下面说怎么申请免费）
3. **GitHub Copilot Chat** — Copilot 的聊天界面
### 申请 GitHub Copilot 学生免费
1. 用你的 **.edu 邮箱** 注册 GitHub 账号（如果已有账号，在 Settings → Emails 里添加 .edu 邮箱）
2. 访问 education.github.com → 点 "Join GitHub Education"
3. 按提示上传学生证或在读证明
4. 审批通过后（通常 1-3 天），Copilot 自动解锁
> 等审批期间不影响后续步骤。Copilot 是加速工具，不是必须的——没有它也能正常跑 pipeline。

> 使用 GitHub 没有梯子或节点超时时，建议使用 Watt Toolkit 加速 GitHub：https://github.com/lanyongjia/watt-toolkit.git ⚠️ 注意：学生认证时必须用 Watt，用梯子的 ip 跟 NKU 地址不一致很难通过，参考 http://xhslink.com/o/9wEaZTjezOL
---
## 2. Mac 用户：打开终端
终端（Terminal）是你和电脑"对话"的文字界面。后面所有 DO 轨的命令都在终端里执行。
**打开方式（任选一种）**：
- Spotlight 搜索：按 `Cmd + Space`，输入 "Terminal"，回车
- Launchpad → "其他" 文件夹 → 终端
打开后你会看到一个黑色/白色窗口，有一行类似 `yourname@MacBook ~ %` 的提示符。这就是命令行——你在这里输入命令，按回车执行。
### 基础命令速查
这些是 DO 轨会用到的命令，现在不需要背，用到时回来查：
| 命令 | 做什么 | 示例 |
|------|--------|------|
| `pwd` | 显示你当前在哪个目录 | `pwd` → `/Users/yourname` |
| `cd 目录名` | 进入某个目录 | `cd drylab` |
| `cd ..` | 回到上一级目录 | `cd ..` |
| `ls` | 列出当前目录下的文件 | `ls` |
| `cat 文件名` | 显示文件全部内容 | `cat config.yaml` |
| `head -30 文件名` | 显示文件前 30 行 | `head -30 results.json` |
| `mkdir -p 目录` | 创建目录（含中间目录） | `mkdir -p data/output` |
> 详细解释和更多命令见 **REF-E §1**。
---
## 3. Windows 用户：安装 WSL2
Windows 不自带和 Mac/Linux 一样的终端环境。我们用 **WSL2**（Windows Subsystem for Linux）在 Windows 里装一个 Linux 环境——装完之后，你在 WSL 终端里执行的命令和 Mac 终端 **完全一致**。
### 第 1 步：安装 WSL
以**管理员身份**打开 PowerShell（右键开始菜单 → "Windows PowerShell (管理员)"），执行：
```powershell
wsl --install
```
这条命令会自动：
- 开启 WSL 功能
- 下载并安装 Ubuntu（默认 Linux 发行版）
安装完成后**重启电脑**。
### 第 2 步：首次启动 Ubuntu
重启后，从开始菜单打开 "Ubuntu"。首次启动会要求设置：
- 用户名（建议用英文，不带空格）
- 密码（输入时不会显示字符，正常现象）
设置完成后你会看到类似 `yourname@DESKTOP:~$` 的提示符——这就是 Linux 终端。
### 第 3 步：VS Code 安装 Remote-WSL 扩展
回到 VS Code → Extensions → 搜索 **"WSL"**（Microsoft 出品）→ 安装。
安装后：
1. 按 `Ctrl + Shift + P` 打开命令面板
2. 输入 "WSL: Connect to WSL"
3. VS Code 底部状态栏会显示 "WSL: Ubuntu"
现在 VS Code 的终端（`` Ctrl + ` ``）会直接打开 WSL 终端。
### 第 4 步：验证
在 WSL 终端里执行：
```bash
pwd
ls
```
如果正常输出路径和文件列表，WSL 环境就绑好了。
> **从现在起，所有 DO 轨命令都在 WSL 终端里执行，和 Mac 完全一致。** 你不需要区分"Mac 命令"和"Windows 命令"——WSL 就是 Linux，命令通用。
---
## 4. 用 Copilot 读代码
拿到项目代码后（DO-1 §2 会讲怎么拿），你可以用 Copilot 帮你理解 pipeline 代码：
**方法 1：选中代码 → 右键 → Copilot → "Explain This"**
在 VS Code 里打开任意 `.py` 文件，选中一段你想理解的代码，右键菜单里选 "Copilot" → "Explain This"。Copilot 会用自然语言解释这段代码在做什么。
**方法 2：Copilot Chat**
点 VS Code 侧栏的 Copilot Chat 图标，直接用自然语言提问：
- "这个函数在做什么？"
- "`dock_pair_singlestage()` 的参数分别是什么意思？"
- "`config.yaml` 里的 `exhaustiveness` 是什么？"
**示例**：打开 `src/modeling/docking-repro/run_wt_singlestage.py`，选中 `dock_pair_singlestage()` 函数调用那一行，右键 → Copilot → Explain This。Copilot 会告诉你这个函数接收受体和配体的 PDBQT 路径，调用 Vina 做对接，返回打分结果。
> ⚠️ **Copilot 会犯错**。把它当导游，不当裁判——遇到拿不准的解释，用第二个 AI 工具交叉验证（推荐搭配 Claude.ai 或 Kimi），或直接看代码本身。
