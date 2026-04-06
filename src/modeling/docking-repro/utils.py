"""工具函数（docking-repro）：配置加载、日志、路径管理。

与 v2 utils.py 相同，仅 logger 名改为 "docking-repro"。
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml


def load_config(config_path: str | Path) -> dict:
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_project_root(config: dict) -> Path:
    return Path(config["paths"]["project_root"])


def resolve_path(config: dict, key: str) -> Path:
    return get_project_root(config) / config["paths"][key]


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
