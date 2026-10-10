# 安装 Docking GUI 依赖与 AF2 Amber relax

这套安装采用一个 Python 环境：PyQt6、OpenMM、PDBFixer、Meeko 和 AF2 relax runtime 都位于同一个环境中。GUI 与本仓库 CLI 不另行打包安装，始终直接运行当前仓库 `src/modeling/docking-repro/final-docking/` 下的源码。

`environment.yml` 中 OpenMM、JAX、Meeko 等二进制依赖由 Conda 安装；PyQt6 及其 Qt wheel 使用该环境自己的 pip 安装并固定版本。它们最终仍位于同一个 Conda 环境中。

## 新机器安装

在仓库根目录运行：

```bash
conda env create -f environments/final-docking/environment.yml
conda activate docking
python scripts/final-docking/build_af2_relax_runtime.py --output-dir ../drylab-payloads/final-docking/runtime
python -m pip install --no-deps --force-reinstall ../drylab-payloads/final-docking/runtime/docking_af2_runtime-0.1.0+c77e5d2-py3-none-any.whl
python src/modeling/docking-repro/final-docking/af2_amber_relax_engine.py --self-check
python -m openmm.testInstallation
python src/modeling/docking-repro/final-docking/docking_gui.py
```

`docking` 只是 `environment.yml` 提供的默认环境名。别人可以在创建环境时改名；代码不会查找或写死这个名字。

第一次构建 runtime wheel 时，构建器会检出固定的 AlphaFold commit，并下载 DeepMind Dockerfile 指定的 `stereo_chemical_props.txt`。两者都会被校验。构建完成后的 `docking_af2_runtime-0.1.0+c77e5d2-py3-none-any.whl` 可以直接交给使用相同平台依赖环境的其他人，不需要每个人重新下载 AlphaFold 源码。

如果已经有固定 commit 的干净 AlphaFold checkout，也可离线复用其中已校验的 stereochemical 文件：

```bash
python scripts/final-docking/build_af2_relax_runtime.py \
  --source-dir /path/to/alphafold-checkout \
  --output-dir ../drylab-payloads/final-docking/runtime
```

这里的 `/path/to/...` 是运行命令的人自己填写的构建输入，不会写进 GUI、CLI 或 wheel。

## 当前机器更新现有环境

```bash
conda env update -n docking -f environments/final-docking/environment.yml
conda activate docking
python scripts/final-docking/build_af2_relax_runtime.py --output-dir ../drylab-payloads/final-docking/runtime
python -m pip install --no-deps --force-reinstall ../drylab-payloads/final-docking/runtime/docking_af2_runtime-0.1.0+c77e5d2-py3-none-any.whl
python src/modeling/docking-repro/final-docking/af2_amber_relax_engine.py --self-check
```

## 怎么运行

GUI 入口是：

```bash
conda activate docking
python src/modeling/docking-repro/final-docking/docking_gui.py
```

AF2 relax 的独立 CLI 入口是：

```bash
python src/modeling/docking-repro/final-docking/run_restrained_minimization.py \
  --protocol deepmind-af2-c77e5d2-openmm8.2-cpu/v1 \
  --input-structure input.pdb \
  --output-structure input.relaxed.pdb \
  --report-json input.relax-report.json
```

输入必须是用户明确选择的 protein-only PDB。程序不会按目录、文件名或 AF2/AF3 来源自动挑选结构。

最小化成功后生成：

- 一个新的 relaxed PDB，不覆盖原始 PDB；
- 一个 JSON 报告，记录输入输出哈希、固定协议、运行版本、力场与 stereochemical 参数哈希、能量和 violations；
- JSON 旁边的标准输出与标准错误日志；
- GUI 中可选的 relax 前后数值比较 JSON 和 PyMOL 复核脚本。

## 为什么换机器不会失效

- GUI 默认用 `sys.executable`，也就是启动 GUI 的同一个 Python；
- GUI 根据自身文件位置找到同仓库 `src/modeling/docking-repro/final-docking/` 中的 CLI，不写死用户名、Conda 根目录或仓库绝对路径；
- AF2 源码和 `stereo_chemical_props.txt` 位于可安装 wheel 中，由 Python 包系统定位；
- 科学版本固定在协议和 runtime manifest 中，但 Conda 根目录、环境名和用户名不属于协议；
- 只有需要双环境兼容时才显式设置 `DOCKING_CLI_PYTHON=/path/to/python`；程序不会扫描本机 Conda 环境；
- Schrödinger 是外部商业软件，只能由用户显式设置 `DOCKING_SCHRODINGER_RUN`，GUI 不猜测其安装位置。
