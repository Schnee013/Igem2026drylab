"""工具函数（docking-repro）：配置加载、日志、路径管理、结果持久化。

与 v2 utils.py 相同，仅 logger 名改为 "docking-repro"。
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml

AF3_REC_NAME_MAP = {"gprc": "GprC", "gpr2": "Gpr2", "gpr3": "Gpr3"}


def load_config(config_path: str | Path) -> dict:
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_project_root(config: dict) -> Path:
    return Path(config["paths"]["project_root"])


def ensure_dirs(config: dict) -> None:
    root = get_project_root(config)
    for key in ["prepared_dir", "results_dir", "analysis_dir", "log_dir", "orca_dir"]:
        (root / config["paths"][key]).mkdir(parents=True, exist_ok=True)
    base = root / config["paths"]["results_dir"]
    for sub in ["poses", "interactions"]:
        (base / sub).mkdir(parents=True, exist_ok=True)
    (root / config["paths"]["analysis_dir"] / "pymol_scripts").mkdir(parents=True, exist_ok=True)
    (root / config["paths"]["prepared_dir"] / "receptors").mkdir(parents=True, exist_ok=True)
    (root / config["paths"]["prepared_dir"] / "ligands").mkdir(parents=True, exist_ok=True)


def generate_run_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def parse_af3_job_name(job_name: str) -> tuple[str, str]:
    """Parse an AF3 Server job name like ``gpr3_d100p`` into ``(Gpr3, D100P)``."""
    parts = job_name.split("_", 1)
    if len(parts) != 2:
        raise ValueError(f"无法解析 AF3 job 名称: {job_name}")
    rec_key, label = parts
    rec_name = AF3_REC_NAME_MAP.get(rec_key.lower(), rec_key)
    return rec_name, label.upper()


def load_af3_job_filter(job_name_files: list[str] | None = None) -> set[tuple[str, str]] | None:
    """Load ``(receptor, label)`` filters from AF3 batch JSON files.

    The AlphaFold Server batch format used in this repo is a JSON list where
    each item has a ``name`` field such as ``gpr3_d100p``. Returning ``None``
    means no filter was requested.
    """
    if not job_name_files:
        return None

    selected: set[tuple[str, str]] = set()
    for file in job_name_files:
        path = Path(file)
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError(f"AF3 batch JSON 必须是 list: {path}")
        for item in raw:
            if not isinstance(item, dict) or "name" not in item:
                raise ValueError(f"AF3 batch JSON 缺少 name 字段: {path}")
            selected.add(parse_af3_job_name(str(item["name"])))

    return selected


def setup_logging(log_dir: Path, run_id: str) -> logging.Logger:
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"run_{run_id}.log"

    logger = logging.getLogger("docking-repro")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"日志文件: {log_file}")
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("docking-repro")


def get_results_subdir(config: dict, subdir_key: str) -> Path:
    """从 config 构建结果子目录的完整路径。

    Args:
        config: pipeline 配置
        subdir_key: config["paths"] 中的子目录键名（如 "wt_singlestage_subdir"）

    Returns:
        root / results_dir / subdir
    """
    root = get_project_root(config)
    results_dir = root / config["paths"]["results_dir"]
    subdir = config["paths"][subdir_key]
    full = results_dir / subdir
    full.mkdir(parents=True, exist_ok=True)
    return full


def save_results_json(
    data, out_dir: Path, run_id: str, config: dict,
    filename: str | None = None,
) -> Path:
    """保存结果 JSON：时间戳副本（历史）+ latest 文件（向后兼容）。

    Args:
        data: 可序列化数据（list 或 dict）
        out_dir: 输出目录
        run_id: 运行 ID（YYYYMMDD_HHMMSS 格式，用作时间戳后缀）
        config: pipeline 配置（读取 results_filename）
        filename: 自定义文件名（默认 None → 从 config 读取 results_filename）

    Returns:
        latest 文件路径
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, indent=2, ensure_ascii=False)

    if filename is None:
        filename = config["paths"].get("results_filename", "docking_results.json")
    filename = Path(filename).name  # strip any directory components
    stem = Path(filename).stem
    suffix = Path(filename).suffix

    # 时间戳副本
    ts_path = out_dir / f"{stem}_{run_id}{suffix}"
    ts_path.write_text(content, encoding="utf-8")

    # latest 副本（覆写，但历史已保留）
    latest_path = out_dir / filename
    latest_path.write_text(content, encoding="utf-8")

    get_logger().info(f"结果已保存: {latest_path} (历史副本: {ts_path.name})")
    return latest_path


def preflight_check(checks: list[dict], logger: logging.Logger) -> None:
    """
    通用启动前检查。任一检查不通过则 log ERROR + sys.exit(1)。

    checks 格式（每项为 dict）：
      {"type": "file_exists",   "path": Path(...),        "hint": "说明"}
      {"type": "dir_not_empty", "path": Path(...),        "hint": "说明"}
      {"type": "file_not_stale","path": Path(...), "marker": "MMFF_voided", "hint": "说明"}
      {"type": "names_match",   "expected": ["a.pdbqt"],
                                "actual_dir": Path(...), "hint": "说明"}

    type 说明：
      file_exists   — 文件或目录必须存在
      dir_not_empty — 目录必须存在且至少含一个文件
      file_not_stale— 若文件名包含 marker 字符串则视为作废文件，拒绝运行
      names_match   — actual_dir 下必须包含 expected 中所有文件名
    """
    failed = False
    for chk in checks:
        kind = chk["type"]
        hint = chk.get("hint", "")

        if kind == "file_exists":
            p = Path(chk["path"])
            if not p.exists():
                logger.error(f"[preflight] 文件不存在: {p}  →  {hint}")
                failed = True

        elif kind == "dir_not_empty":
            p = Path(chk["path"])
            if not p.exists() or not any(p.iterdir()):
                logger.error(f"[preflight] 目录为空或不存在: {p}  →  {hint}")
                failed = True

        elif kind == "file_not_stale":
            p = Path(chk["path"])
            marker = chk.get("marker", "MMFF_voided")
            if p.exists() and marker in p.name:
                logger.error(f"[preflight] 检测到已作废文件: {p}  →  {hint}")
                failed = True

        elif kind == "names_match":
            actual_dir = Path(chk["actual_dir"])
            expected = chk["expected"]
            if not actual_dir.exists():
                logger.error(f"[preflight] 目录不存在: {actual_dir}  →  {hint}")
                failed = True
            else:
                actual = {f.name for f in actual_dir.iterdir()}
                missing = [e for e in expected if e not in actual]
                if missing:
                    logger.error(
                        f"[preflight] 目录 {actual_dir} 缺少文件: {missing}  →  {hint}"
                    )
                    failed = True

        else:
            logger.warning(f"[preflight] 未知检查类型: {kind}，已跳过")

    if failed:
        logger.error("[preflight] 启动前检查失败，请修复上述问题后重试")
        sys.exit(1)
    else:
        logger.info("[preflight] 启动前检查全部通过")
