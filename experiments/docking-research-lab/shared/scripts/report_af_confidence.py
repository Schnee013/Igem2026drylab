#!/usr/bin/env python3
"""Report whole-sequence AlphaFold confidence with optional named regions."""

from __future__ import annotations

import argparse
import json
import math
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

from docking_tool_result import ToolArtifact, write_tool_result
from parse_tm_topology import (
    InputError,
    MinimalArgumentParser,
    atomic_write_text,
    ensure_output_available,
    read_text_file,
)


DEFAULT_JSON_PATTERN = "**/*.json"
REPORT_SUFFIX = ".confidence-report.json"
AUTO_FORMAT_CONTRACT = "alphafold-colabfold-top-level-plddt-pae/v1"


@dataclass(frozen=True)
class ConfidenceSchema:
    name: str
    contract: str
    plddt_pointer: str
    pae_pointer: str | None
    detection: str
    matched_fields: tuple[str, ...]


def _json_pointer(data: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise InputError(f"JSON pointer must start with '/': {pointer!r}")
    value = data
    for raw_part in pointer.split("/")[1:]:
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            try:
                value = value[int(part)]
            except (ValueError, IndexError) as exc:
                raise InputError(f"JSON pointer not found: {pointer}") from exc
        elif isinstance(value, dict):
            if part not in value:
                raise InputError(f"JSON pointer not found: {pointer}")
            value = value[part]
        else:
            raise InputError(f"JSON pointer crosses a scalar value: {pointer}")
    return value


def _number_list(value: Any, label: str) -> list[float]:
    if not isinstance(value, list) or not value:
        raise InputError(f"{label} must be a non-empty numeric list")
    numbers: list[float] = []
    for index, item in enumerate(value, start=1):
        if not isinstance(item, (int, float)) or isinstance(item, bool):
            raise InputError(f"{label}[{index}] is not numeric")
        number = float(item)
        if not math.isfinite(number):
            raise InputError(f"{label}[{index}] is not finite")
        numbers.append(number)
    return numbers


def _matrix(value: Any, label: str) -> list[list[float]]:
    if not isinstance(value, list) or not value:
        raise InputError(f"{label} must be a non-empty numeric matrix")
    rows = [_number_list(row, f"{label}[{index}]") for index, row in enumerate(value, start=1)]
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise InputError(f"{label} rows must have equal length")
    return rows


def parse_region(raw: str) -> tuple[str, int, int]:
    name, separator, interval = raw.partition(":")
    if not separator or not name:
        raise argparse.ArgumentTypeError("region must be NAME:START-END")
    start_text, dash, end_text = interval.partition("-")
    if not dash:
        raise argparse.ArgumentTypeError("region must be NAME:START-END")
    try:
        start = int(start_text)
        end = int(end_text)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("region coordinates must be integers") from exc
    if start < 1 or end < start:
        raise argparse.ArgumentTypeError("region coordinates must be 1-based START<=END")
    return name, start, end


def summarize_region(
    name: str,
    start: int,
    end: int,
    plddt: list[float],
    pae: list[list[float]] | None,
) -> dict[str, Any]:
    if end > len(plddt):
        raise InputError(
            f"region {name!r} ends at {end}, beyond pLDDT length {len(plddt)}"
        )
    values = plddt[start - 1 : end]
    summary: dict[str, Any] = {
        "name": name,
        "start": start,
        "end": end,
        "length": len(values),
        "plddt_min": min(values),
        "plddt_mean": sum(values) / len(values),
        "plddt_max": max(values),
    }
    if pae is not None:
        if len(pae) != len(plddt) or any(len(row) != len(plddt) for row in pae):
            raise InputError("PAE matrix dimensions must equal pLDDT length")
        cells = [pae[row][col] for row in range(start - 1, end) for col in range(start - 1, end)]
        summary["pae_self_mean"] = sum(cells) / len(cells)
        summary["pae_self_max"] = max(cells)
    return summary


def _list_length(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    return str(len(value)) if isinstance(value, list) else "不是数组"


def _matrix_shape(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, list):
        return "不是矩阵"
    width = len(value[0]) if value and isinstance(value[0], list) else "?"
    return f"{len(value)}x{width}"


def _detected_fields(data: Any) -> str:
    if not isinstance(data, dict):
        return f"顶层类型={type(data).__name__}"
    keys = sorted(str(key) for key in data)
    preview = keys[:16]
    suffix = ", …" if len(keys) > len(preview) else ""
    return f"顶层字段={', '.join(preview)}{suffix}"


def detect_confidence_schema(data: Any) -> ConfidenceSchema:
    """Recognize only schemas whose confidence coordinate level is unambiguous."""
    if not isinstance(data, dict):
        raise InputError(
            "不支持的置信度 JSON：需要对象形式；" + _detected_fields(data)
        )

    if "plddt" in data and "atom_plddts" in data:
        raise InputError(
            "置信度 JSON 同时含有 plddt 与 atom_plddts，层级存在歧义；"
            + _detected_fields(data)
        )

    if "plddt" in data:
        matched = ["plddt"]
        pae_pointer = None
        if "pae" in data:
            matched.append("pae")
            pae_pointer = "/pae"
        return ConfidenceSchema(
            name="AlphaFold/ColabFold 顶层 plddt/pae JSON",
            contract=AUTO_FORMAT_CONTRACT,
            plddt_pointer="/plddt",
            pae_pointer=pae_pointer,
            detection="自动识别",
            matched_fields=tuple(matched),
        )

    if "atom_plddts" in data:
        raise InputError(
            "检测到 AlphaFold 3 full-data 风格 JSON，但当前不能生成逐残基报告："
            f"atom_plddts={_list_length(data, 'atom_plddts')}（atom-level），"
            f"pae={_matrix_shape(data, 'pae')}、"
            f"token_res_ids={_list_length(data, 'token_res_ids')}（token-level）。"
            "该 JSON 未提供无歧义的 atom→token/residue 映射；工具不会自行采用 mean、"
            "max、first atom 或其它聚合规则。"
        )

    summary_markers = {"chain_ptm", "chain_iptm", "ranking_score", "fraction_disordered"}
    if summary_markers.intersection(data):
        raise InputError(
            "检测到 AlphaFold 3 summary_confidences 风格 JSON；该文件只有模型/链级摘要，"
            "不含逐残基 pLDDT，不能用于区域置信度报告；" + _detected_fields(data)
        )

    raise InputError(
        "不支持的置信度 JSON：未识别到可证明为逐残基的顶层 plddt 数组；"
        + _detected_fields(data)
    )


def default_report_path(input_path: Path) -> Path:
    """Return the stable single-file report name shown by the GUI."""
    return input_path.with_name(f"{input_path.stem}{REPORT_SUFFIX}")


def batch_report_path(input_path: Path, input_dir: Path, output_dir: Path) -> Path:
    relative = input_path.relative_to(input_dir)
    return output_dir / relative.parent / f"{relative.stem}{REPORT_SUFFIX}"


def output_collision_key(path: Path) -> str:
    """Return a conservative portable key for case/Unicode-equivalent paths."""
    return unicodedata.normalize("NFC", str(path.resolve())).casefold()


def find_json_files(
    input_dir: Path,
    pattern: str,
    *,
    output_dir: Path | None = None,
) -> list[Path]:
    """Find unique in-root JSON candidates and exclude a nested output tree."""
    root = input_dir.resolve()
    excluded = output_dir.resolve() if output_dir is not None else None
    found: list[Path] = []
    seen_targets: set[Path] = set()
    for path in sorted(input_dir.glob(pattern)):
        if not path.is_file():
            continue
        resolved = path.resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise InputError(f"扫描结果越过输入目录: {path}") from exc
        if excluded is not None and (resolved == excluded or resolved.is_relative_to(excluded)):
            continue
        if resolved in seen_targets:
            continue
        seen_targets.add(resolved)
        found.append(path)
    return found


def build_report(
    input_path: Path,
    regions: Sequence[tuple[str, int, int]] | None = None,
    *,
    input_format: str | None = None,
    plddt_pointer: str | None = None,
    pae_pointer: str | None = None,
) -> dict[str, Any]:
    text = read_text_file(input_path, "AlphaFold confidence JSON")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InputError(
            f"{input_path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if plddt_pointer is None:
        if input_format is not None or pae_pointer is not None:
            raise InputError(
                "专家兼容覆盖必须同时提供 --input-format 与 --plddt-pointer；"
                "自动识别模式不接受单独的格式或 PAE pointer"
            )
        schema = detect_confidence_schema(data)
    else:
        if not input_format:
            raise InputError(
                "使用 --plddt-pointer 时必须提供 --input-format，记录自定义格式来源"
            )
        if plddt_pointer == "/atom_plddts":
            raise InputError(
                "--plddt-pointer=/atom_plddts 指向 atom-level 数值，不能声明为逐残基 pLDDT"
            )
        schema = ConfidenceSchema(
            name=input_format,
            contract=input_format,
            plddt_pointer=plddt_pointer,
            pae_pointer=pae_pointer,
            detection="专家兼容覆盖",
            matched_fields=(),
        )

    plddt = _number_list(
        _json_pointer(data, schema.plddt_pointer),
        f"{schema.plddt_pointer} 的逐残基 pLDDT",
    )
    pae = (
        _matrix(_json_pointer(data, schema.pae_pointer), f"{schema.pae_pointer} 的 PAE")
        if schema.pae_pointer
        else None
    )
    whole_sequence = summarize_region(
        "whole_sequence",
        1,
        len(plddt),
        plddt,
        pae,
    )
    return {
        "input_format": schema.name,
        "input_format_contract": schema.contract,
        "producer_version": None,
        "format_detection": schema.detection,
        "matched_fields": list(schema.matched_fields),
        "source_file": str(input_path.resolve()),
        "confidence_level": "residue",
        "coordinate_system": "1-based-inclusive",
        "plddt_pointer": schema.plddt_pointer,
        "pae_pointer": schema.pae_pointer,
        "sequence_length": len(plddt),
        "whole_sequence": whole_sequence,
        "regions": [
            summarize_region(name, start, end, plddt, pae)
            for name, start, end in regions or ()
        ],
        "scope": (
            "This report presents numeric confidence values across the whole residue "
            "sequence and any explicitly requested regions. It does not infer regions, "
            "does not select a model, and does not apply a confidence threshold."
        ),
    }


def build_parser() -> MinimalArgumentParser:
    template = (
        "report_af_confidence.py (--input <confidence.json> | --input-dir <folder> "
        "--output-dir <folder>) [--region <name:start-end>] "
        "[--output <report.json>] [--force]"
    )
    parser = MinimalArgumentParser(
        short_usage=template,
        add_help=False,
        description=(
            "自动识别受支持的 AlphaFold/ColabFold 置信度 JSON，默认报告完整逐残基序列，"
            "并可附加人工指定的 1-based 区域统计。支持单文件和递归批量目录；"
            "不推断区域，也不应用阈值或接受/拒绝判断。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Call template:\n  {template}\n\n"
            "自动识别支持顶层 plddt 与可选 pae 的 AF2/ColabFold scores JSON。\n"
            "AF3 summary_confidences 没有逐残基 pLDDT；AF3 full-data 的 atom_plddts "
            "与 token-level PAE 不会被猜测聚合。\n"
            f"批量扫描默认 {DEFAULT_JSON_PATTERN!r}，输出名为 <input-stem>{REPORT_SUFFIX}。"
        ),
    )
    required = parser.add_argument_group("输入模式（二选一）")
    input_mode = required.add_mutually_exclusive_group(required=True)
    input_mode.add_argument("--input", type=Path, help="单个 AlphaFold/ColabFold 置信度 JSON")
    input_mode.add_argument("--input-dir", type=Path, help="递归扫描候选 JSON 的批量输入文件夹")
    optional = parser.add_argument_group("optional arguments")
    optional.add_argument(
        "--region",
        action="append",
        type=parse_region,
        help=(
            "可重复的附加区域 NAME:START-END（1-based inclusive）；"
            "省略时仍报告完整序列"
        ),
    )
    optional.add_argument("--output", type=Path, help="单文件报告输出；省略时仅写入 stdout")
    optional.add_argument("--output-dir", type=Path, help="批量报告输出文件夹；批量模式必填")
    optional.add_argument(
        "--pattern",
        default=DEFAULT_JSON_PATTERN,
        help=f"相对批量输入文件夹的 glob（默认: {DEFAULT_JSON_PATTERN!r}）",
    )
    optional.add_argument("--input-format", help="专家兼容覆盖：自定义 JSON 格式来源标签")
    optional.add_argument("--plddt-pointer", help="专家兼容覆盖：已确认的逐残基 pLDDT JSON Pointer")
    optional.add_argument("--pae-pointer", help="专家兼容覆盖：同一逐残基层级的方阵 PAE JSON Pointer")
    optional.add_argument("--force", action="store_true", help="overwrite an existing --output")
    optional.add_argument("-h", "--help", action="help", help="show this help and exit")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    pattern_was_provided = any(
        token == "--pattern" or token.startswith("--pattern=")
        for token in raw_argv
    )
    args = parser.parse_args(raw_argv)
    try:
        pattern_path = Path(args.pattern)
        if pattern_path.is_absolute() or ".." in pattern_path.parts:
            raise InputError("--pattern 必须是批量输入文件夹内的相对 glob，且不得包含 '..'")

        if args.input is not None:
            if args.output_dir is not None:
                raise InputError("--output-dir 只用于 --input-dir 批量模式")
            if pattern_was_provided:
                raise InputError("--pattern 只用于 --input-dir 批量模式")
            input_path = args.input.expanduser()
            output_path = args.output.expanduser() if args.output else None
            if output_path is not None:
                if output_path.resolve() == input_path.resolve():
                    raise InputError("--output must differ from --input")
                ensure_output_available(output_path, args.force)
            report = build_report(
                input_path,
                args.region,
                input_format=args.input_format,
                plddt_pointer=args.plddt_pointer,
                pae_pointer=args.pae_pointer,
            )
            content = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
            if output_path is None:
                print(content, end="")
            else:
                atomic_write_text(output_path, content, args.force)
                print(f"成功: {input_path} -> {output_path}")
            artifacts = (
                [ToolArtifact(output_path, "AlphaFold 置信度报告")]
                if output_path is not None
                else []
            )
            write_tool_result(artifacts)
            return 0

        if args.output is not None:
            raise InputError("--output 只用于 --input 单文件模式")
        if args.output_dir is None:
            raise InputError("--input-dir 批量模式必须提供 --output-dir")
        input_dir = args.input_dir.expanduser()
        if not input_dir.exists() or not input_dir.is_dir():
            raise InputError(f"--input-dir 必须是已存在的文件夹: {input_dir}")
        output_dir = args.output_dir.expanduser()
        if output_dir.exists() and not output_dir.is_dir():
            raise InputError(f"--output-dir 已存在但不是文件夹: {output_dir}")
        if output_dir.resolve() == input_dir.resolve():
            raise InputError("--output-dir 不得与 --input-dir 是同一个文件夹")
        output_dir.mkdir(parents=True, exist_ok=True)

        candidates = find_json_files(input_dir, args.pattern, output_dir=output_dir)
        if not candidates:
            raise InputError(
                f"批量输入中没有候选 JSON: input_dir={input_dir}, pattern={args.pattern!r}"
            )

        targets = [batch_report_path(path, input_dir, output_dir) for path in candidates]
        if len({output_collision_key(path) for path in targets}) != len(targets):
            raise InputError("批量输出命名发生碰撞；未写入任何报告")

        artifacts: list[ToolArtifact] = []
        succeeded = skipped = failed = 0
        for input_path, output_path in zip(candidates, targets):
            relative = input_path.relative_to(input_dir)
            if output_path.exists() and not args.force:
                print(f"跳过: {relative} -> {output_path}（输出已存在；加 --force 可覆盖）")
                artifacts.append(ToolArtifact(output_path, f"置信度报告: {relative}"))
                skipped += 1
                continue
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                report = build_report(
                    input_path,
                    args.region,
                    input_format=args.input_format,
                    plddt_pointer=args.plddt_pointer,
                    pae_pointer=args.pae_pointer,
                )
                content = json.dumps(
                    report, indent=2, sort_keys=True, ensure_ascii=False
                ) + "\n"
                atomic_write_text(output_path, content, args.force)
            except InputError as exc:
                print(f"失败: {relative}: {exc}", file=sys.stderr)
                failed += 1
                continue
            print(f"成功: {relative} -> {output_path}")
            artifacts.append(ToolArtifact(output_path, f"置信度报告: {relative}"))
            succeeded += 1

        print(
            f"批量汇总: 候选 {len(candidates)}，成功 {succeeded}，"
            f"跳过 {skipped}，失败 {failed}"
        )
        write_tool_result(artifacts)
        return 1 if failed else 0
    except InputError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
