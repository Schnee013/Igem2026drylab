"""工具函数：配置加载、日志、路径管理。"""

import logging
import sys
from datetime import datetime
from pathlib import Path

import yaml


def load_config(config_path: str | Path) -> dict:
    """加载并返回 YAML 配置字典。"""
    config_path = Path(config_path)
    if not config_path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config


def get_project_root(config: dict) -> Path:
    return Path(config["paths"]["project_root"])


def resolve_path(config: dict, key: str) -> Path:
    """将配置中的相对路径解析为绝对路径。"""
    root = get_project_root(config)
    return root / config["paths"][key]


def ensure_dirs(config: dict) -> None:
    """创建所有输出目录（已存在则跳过）。"""
    root = get_project_root(config)
    keys = ["prepared_dir", "results_dir", "analysis_dir", "log_dir"]
    subdirs = [
        "prepared/receptors",
        "prepared/ligands",
        "results/poses",
        "results/interactions",
        "analysis/pymol_scripts",
    ]
    for key in keys:
        (root / config["paths"][key]).mkdir(parents=True, exist_ok=True)
    for sub in subdirs:
        (root / config["paths"]["results_dir"].replace("results", "") / sub
         if "results" in sub else root / sub).mkdir(parents=True, exist_ok=True)

    # 更直接的方式：逐个创建
    base = root / "experiments/docking"
    for d in [
        "prepared/receptors",
        "prepared/ligands",
        "results/poses",
        "results/interactions",
        "analysis/pymol_scripts",
        "logs",
    ]:
        (base / d).mkdir(parents=True, exist_ok=True)


def generate_run_id() -> str:
    """生成基于时间戳的运行 ID，用于日志文件命名。"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def setup_logging(log_dir: Path, run_id: str) -> logging.Logger:
    """配置同时写入文件和控制台的 logger。"""
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / f"run_{run_id}.log"

    logger = logging.getLogger("docking")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # 文件 handler：记录 DEBUG 及以上
    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    ))

    # 控制台 handler：记录 INFO 及以上
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(f"日志文件: {log_file}")
    return logger


def get_logger() -> logging.Logger:
    return logging.getLogger("docking")
