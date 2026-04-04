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
    with open(config_path) as f:
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
