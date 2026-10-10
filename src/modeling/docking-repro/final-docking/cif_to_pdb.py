"""将单个或一批 mmCIF 结构转为 PDB；所有运行信息均由命令行参数提供。"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Sequence

from docking_tool_result import ToolArtifact, write_tool_result

DEFAULT_CIF_PATTERN = "**/*.cif"


class ArgumentParser(argparse.ArgumentParser):
    """在参数错误后给出可操作的中文提示。"""

    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        self.exit(
            2,
            f"{self.prog}: 参数错误: {message}\n"
            f"请运行 '{self.prog} -h' 查看完整用法。\n",
        )


def convert_one(cif_path: Path, pdb_path: Path) -> Path:
    """转换单个 CIF，并返回实际写入的 PDB 路径。"""
    try:
        from Bio.PDB import MMCIFParser, PDBIO
        from Bio.PDB.PDBExceptions import PDBConstructionWarning
    except ModuleNotFoundError as exc:
        if exc.name == "Bio" or (exc.name and exc.name.startswith("Bio.")):
            raise RuntimeError(
                "缺少运行依赖 Biopython（Python 包名: biopython）"
            ) from exc
        raise

    parser = MMCIFParser(QUIET=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PDBConstructionWarning)
        structure = parser.get_structure(cif_path.stem, str(cif_path))

    pdb_path.parent.mkdir(parents=True, exist_ok=True)
    io = PDBIO()
    io.set_structure(structure)
    io.save(str(pdb_path))
    return pdb_path


def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description=(
            "将单个或一批 mmCIF 结构转为 PDB。脚本不读取配置文件，"
            "输入位置、扫描规则和输出位置均由本次命令指定。"
        ),
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
输入与输出规则:
  1. 单文件模式使用 --input-file，可用 --output-file 指定 PDB；省略时写在 CIF 旁边。
     输入后缀必须是 .cif 或 .mmcif，输出后缀必须是 .pdb。
  2. 批量模式使用 --input-dir；--pattern 是相对于 INPUT_DIR 的 glob；默认 {DEFAULT_CIF_PATTERN!r}，
     同时扫描 INPUT_DIR 根层和任意嵌套子目录中的 .cif 文件。
     pattern 必须是相对路径，且不得包含 '..' 跨出 INPUT_DIR。
  3. 批量模式未给 --output-dir 时，PDB 写在每个 CIF 旁边；给定后，
     在 OUTPUT_DIR 下保留相对 INPUT_DIR 的目录结构。
  4. --output-file 只属于单文件模式；--output-dir 和 --pattern 只属于批量模式。
  5. 已存在的 PDB 默认跳过；只有 --overwrite 会允许重写。
Examples:
  # 转换单个文件
  python src/cif_to_pdb.py --input-file model.cif --output-file model.pdb

  # --pattern 是相对 glob；默认 '**/*.cif'，包含根层和任意嵌套层。
  # 按默认递归范围扫描，PDB 写回 CIF 旁边
  python src/cif_to_pdb.py --input-dir /data/af3_structures

  # 递归扫描所有 CIF，将结果写入独立目录
  python src/cif_to_pdb.py -i /data/af3 -o /data/pdb
""",
    )
    required = parser.add_argument_group("输入模式（二选一）")
    input_mode = required.add_mutually_exclusive_group(required=True)
    input_mode.add_argument(
        "--input-file",
        type=Path,
        metavar="INPUT_FILE",
        help="单个 .cif 或 .mmcif 输入文件。",
    )
    input_mode.add_argument(
        "-i", "--input-dir",
        type=Path,
        metavar="INPUT_DIR",
        help=(
            "待扫描的 CIF 根目录；必须是已存在的目录。"
            "扫描范围由 --pattern 决定。"
        ),
    )

    optional = parser.add_argument_group("可选参数")
    optional.add_argument(
        "-h", "--help",
        action="help",
        help="显示完整帮助信息并退出。",
    )
    optional.add_argument(
        "--output-file",
        type=Path,
        metavar="OUTPUT_FILE",
        help="单文件模式的 .pdb 输出；默认写在输入文件旁边。",
    )
    optional.add_argument(
        "-o", "--output-dir",
        type=Path,
        metavar="OUTPUT_DIR",
        help=(
            "PDB 输出根目录。目录不存在时自动创建；"
            "默认将 PDB 写在对应 CIF 旁边。"
        ),
    )
    optional.add_argument(
        "--pattern",
        default=DEFAULT_CIF_PATTERN,
        metavar="GLOB",
        help=(
            f"相对 INPUT_DIR 的 glob 扫描模式（默认: {DEFAULT_CIF_PATTERN!r}）。"
            "使用 ** 时请在 shell 中加引号。"
        ),
    )
    optional.add_argument(
        "--overwrite",
        action="store_true",
        help="覆盖已存在的 PDB；默认跳过已存在文件。",
    )
    return parser


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    pattern_was_provided = any(
        token == "--pattern" or token.startswith("--pattern=")
        for token in raw_argv
    )
    args = parser.parse_args(raw_argv)

    if args.input_file is not None:
        args.input_file = args.input_file.expanduser()
        if not args.input_file.exists():
            parser.error(f"输入文件不存在: {args.input_file}")
        if not args.input_file.is_file():
            parser.error(f"--input-file 必须指向文件: {args.input_file}")
        if args.input_file.suffix.casefold() not in {".cif", ".mmcif"}:
            parser.error(f"--input-file 必须使用 .cif 或 .mmcif 后缀: {args.input_file}")
        if args.output_dir is not None:
            parser.error("--output-dir 只能与 --input-dir 一起使用")
        if pattern_was_provided:
            parser.error("--pattern 只能与 --input-dir 一起使用")
        if args.output_file is not None:
            args.output_file = args.output_file.expanduser()
            if args.output_file.suffix.casefold() != ".pdb":
                parser.error(f"--output-file 必须使用 .pdb 后缀: {args.output_file}")
            if args.output_file.resolve() == args.input_file.resolve():
                parser.error("--output-file 不得与 --input-file 相同")
    else:
        if args.output_file is not None:
            parser.error("--output-file 只能与 --input-file 一起使用")
        args.input_dir = args.input_dir.expanduser()
        if not args.input_dir.exists():
            parser.error(f"输入目录不存在: {args.input_dir}")
        if not args.input_dir.is_dir():
            parser.error(f"--input-dir 必须指向目录: {args.input_dir}")

        pattern_path = Path(args.pattern)
        if pattern_path.is_absolute():
            parser.error("--pattern 必须是相对于 --input-dir 的 glob")
        if ".." in pattern_path.parts:
            parser.error("--pattern 不得包含 '..' 或跨出 --input-dir")

        if args.output_dir is not None:
            args.output_dir = args.output_dir.expanduser()
            if args.output_dir.exists() and not args.output_dir.is_dir():
                parser.error(f"--output-dir 已存在但不是目录: {args.output_dir}")

    return args


def find_cif_files(input_dir: Path, pattern: str) -> list[Path]:
    """按相对 glob 查找文件，拒绝越界结果并去除符号链接重复项。"""
    root = input_dir.resolve()
    found: list[Path] = []
    seen_targets: set[Path] = set()
    for path in sorted(input_dir.glob(pattern)):
        if not path.is_file():
            continue
        resolved = path.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ValueError(f"扫描结果越过输入目录: {path}") from exc
        if resolved in seen_targets:
            continue
        seen_targets.add(resolved)
        found.append(path)
    return found


def output_path_for(cif_path: Path, input_dir: Path, output_dir: Path | None) -> Path:
    """计算输出路径；独立输出目录下保留输入的相对层级。"""
    if output_dir is None:
        return cif_path.with_suffix(".pdb")
    return (output_dir / cif_path.relative_to(input_dir)).with_suffix(".pdb")


def convert_one_atomic(cif_path: Path, pdb_path: Path, overwrite: bool) -> Path:
    """只在转换完整成功后发布目标 PDB。"""
    if pdb_path.exists() and not overwrite:
        return pdb_path

    pdb_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{pdb_path.name}.", suffix=".tmp", dir=pdb_path.parent
        )
        os.close(descriptor)
        descriptor = None
        temporary_path = Path(temporary_name)
        convert_one(cif_path, temporary_path)
        if overwrite:
            os.replace(temporary_path, pdb_path)
            temporary_path = None
        else:
            os.link(temporary_path, pdb_path)
            temporary_path.unlink()
            temporary_path = None
    except FileExistsError:
        if not overwrite:
            raise RuntimeError(f"输出文件已存在: {pdb_path}") from None
        raise
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass
    return pdb_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    parser = build_parser()

    if args.input_file is not None:
        input_dir = args.input_file.parent
        cif_files = [args.input_file]
    else:
        input_dir = args.input_dir
        try:
            cif_files = find_cif_files(input_dir, args.pattern)
        except (NotImplementedError, ValueError) as exc:
            parser.error(f"--pattern 无效: {args.pattern!r} ({exc})")

    if not cif_files:
        parser.error(
            f"未找到待转换文件: "
            f"INPUT_DIR={input_dir}, pattern={args.pattern!r}"
        )

    print(f"找到 {len(cif_files)} 个 CIF 文件\n", flush=True)

    converted = 0
    skipped = 0
    artifacts: list[ToolArtifact] = []
    for cif in cif_files:
        relative_cif = cif.relative_to(input_dir)
        pdb_path = (
            args.output_file or cif.with_suffix(".pdb")
            if args.input_file is not None
            else output_path_for(cif, input_dir, args.output_dir)
        )
        display_pdb = (
            Path(pdb_path.name)
            if args.input_file is not None
            else pdb_path.relative_to(args.output_dir or input_dir)
        )
        artifact_label = f"输出 PDB: {display_pdb}"
        if pdb_path.exists() and not args.overwrite:
            print(f"  {relative_cif}: 已存在，跳过（加 --overwrite 可重写）")
            artifacts.append(ToolArtifact(pdb_path, artifact_label))
            skipped += 1
            continue

        try:
            pdb = convert_one_atomic(cif, pdb_path, args.overwrite)
        except Exception as exc:
            print(f"错误: 转换失败 {cif}: {exc}", file=sys.stderr)
            return 1

        print(f"  {relative_cif} -> {pdb}")
        artifacts.append(ToolArtifact(pdb, artifact_label))
        converted += 1

    print(f"\n转换完成: 新写入 {converted} 个，跳过 {skipped} 个")
    write_tool_result(artifacts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
