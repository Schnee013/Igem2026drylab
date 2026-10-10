#!/usr/bin/env python3
"""Stack completed ProLIF CSV files without analysing their contents.

The script keeps every source CSV block in its original row order and byte
content.  It only inserts source/section labels and one blank row between
blocks so that the merged file remains readable in a spreadsheet or editor.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from project_paths import resolve_paths, resolve_recorded_path


LIGAND_ORDER = (
    "ascr3_deprotonated",
    "ascr18_deprotonated",
)

KIND_TO_FILENAME = {
    "frequency": "interaction_frequency.csv",
    "presence": "ifp_presence.csv",
    "counts": "ifp_counts.csv",
}

OUTPUT_KIND_NAME = {
    "frequency": "interaction_frequency",
    "presence": "ifp_presence",
    "counts": "ifp_counts",
}

FREQUENCY_HEADER = [
    "protein",
    "interaction",
    "poses_with_interaction",
    "pose_frequency",
    "total_geometries",
]


@dataclass(frozen=True)
class ResultBlock:
    receptor: str
    model_rel: str
    ligand: str
    run_name: str
    output_dir: Path


def parse_args() -> argparse.Namespace:
    default_batch_root = resolve_paths()["prolif_results"]

    parser = argparse.ArgumentParser(
        description=(
            "Stack completed ProLIF result CSVs with source labels and blank "
            "rows. No sorting, filtering, aggregation, weighting, or residue "
            "analysis is performed."
        )
    )
    parser.add_argument(
        "--batch-root",
        type=Path,
        default=default_batch_root,
        help=(
            "Directory containing batch_manifest.csv "
            f"(default: {default_batch_root})."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: BATCH_ROOT/merged).",
    )
    parser.add_argument(
        "--layout",
        choices=("by-ligand", "by-receptor", "both"),
        default="by-ligand",
        help=(
            "by-ligand writes all ASCR3 blocks followed by all ASCR18 blocks; "
            "by-receptor keeps the two ligands together for each receptor "
            "model; both writes both layouts (default: by-ligand)."
        ),
    )
    parser.add_argument(
        "--kinds",
        nargs="+",
        choices=tuple(KIND_TO_FILENAME),
        default=("frequency",),
        help=(
            "CSV types to merge into separate output files "
            "(default: frequency). Example: --kinds frequency presence"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace merged output files if they already exist.",
    )
    return parser.parse_args()


def fail(message: str) -> None:
    raise RuntimeError(message)


def is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes"}


def load_manifest(batch_root: Path) -> tuple[list[ResultBlock], list[str]]:
    manifest_path = batch_root / "batch_manifest.csv"
    if not manifest_path.is_file():
        fail(f"Batch manifest not found: {manifest_path}")

    with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {
            "model_rel",
            "ligand",
            "run_name",
            "output_dir",
            "selected",
            "status",
        }
        fields = set(reader.fieldnames or ())
        missing = sorted(required - fields)
        if missing:
            fail(
                f"Manifest is missing required columns {missing}: "
                f"{manifest_path}"
            )
        rows = list(reader)

    if not rows:
        fail(f"Batch manifest has no result rows: {manifest_path}")

    incomplete = [
        (index, row.get("model_rel", ""), row.get("ligand", ""), row.get("status", ""))
        for index, row in enumerate(rows, start=2)
        if not is_true(row.get("selected", ""))
        or row.get("status", "").strip() != "completed"
    ]
    if incomplete:
        preview = "; ".join(
            f"line {line}: {model}/{ligand} status={status!r}"
            for line, model, ligand, status in incomplete[:5]
        )
        fail(
            "Manifest contains unselected or incomplete rows; refusing to "
            f"silently omit them. {preview}"
        )

    observed_ligands = {row["ligand"].strip() for row in rows}
    expected_ligands = set(LIGAND_ORDER)
    if observed_ligands != expected_ligands:
        fail(
            "Expected exactly these ligand names: "
            f"{sorted(expected_ligands)}; observed: {sorted(observed_ligands)}"
        )

    blocks: list[ResultBlock] = []
    model_order: list[str] = []
    seen_models: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()

    for row in rows:
        model_rel = row["model_rel"].strip()
        ligand = row["ligand"].strip()
        run_name = row["run_name"].strip()
        if not model_rel or not run_name:
            fail(f"Manifest contains an empty model_rel or run_name: {manifest_path}")

        pair = (model_rel, ligand)
        if pair in seen_pairs:
            fail(f"Duplicate model/ligand pair in manifest: {pair}")
        seen_pairs.add(pair)

        if model_rel not in seen_models:
            seen_models.add(model_rel)
            model_order.append(model_rel)

        output_dir = resolve_recorded_path(row["output_dir"].strip(), anchor=batch_root)

        blocks.append(
            ResultBlock(
                receptor=Path(model_rel).parts[0],
                model_rel=model_rel,
                ligand=ligand,
                run_name=run_name,
                output_dir=output_dir,
            )
        )

    by_model: dict[str, set[str]] = {model: set() for model in model_order}
    for block in blocks:
        by_model[block.model_rel].add(block.ligand)
    bad_models = [
        model
        for model, ligands in by_model.items()
        if ligands != expected_ligands
    ]
    if bad_models:
        fail(
            "Every receptor model must have one ASCR3 and one ASCR18 result; "
            f"incomplete models: {bad_models[:5]}"
        )

    return blocks, model_order


def read_and_validate_source(path: Path, kind: str) -> bytes:
    if not path.is_file():
        fail(f"Missing source CSV: {path}")

    raw = path.read_bytes()
    if not raw:
        fail(f"Empty source CSV: {path}")

    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        fail(f"Source CSV is not UTF-8: {path}: {error}")

    rows = list(csv.reader(io.StringIO(text, newline="")))
    if not rows:
        fail(f"Source CSV has no rows: {path}")

    if kind == "frequency":
        if rows[0] != FREQUENCY_HEADER:
            fail(
                f"Unexpected interaction_frequency.csv header in {path}: "
                f"{rows[0]}"
            )
    else:
        expected_first_cells = ["ligand", "protein", "interaction", "Pose"]
        observed_first_cells = [row[0] if row else "" for row in rows[:4]]
        if observed_first_cells != expected_first_cells:
            fail(
                f"Unexpected {KIND_TO_FILENAME[kind]} header rows in {path}: "
                f"{observed_first_cells}"
            )

    width = len(rows[0])
    bad_widths = [index for index, row in enumerate(rows, start=1) if len(row) != width]
    if bad_widths:
        fail(
            f"Inconsistent CSV row widths in {path}; first bad rows: "
            f"{bad_widths[:5]}"
        )

    return raw


def csv_marker(*values: str) -> bytes:
    buffer = io.StringIO(newline="")
    csv.writer(buffer, lineterminator="\n").writerow(values)
    return buffer.getvalue().encode("utf-8")


def source_path(block: ResultBlock, kind: str) -> Path:
    return block.output_dir / "ifp" / KIND_TO_FILENAME[kind]


def ordered_sections(
    blocks: list[ResultBlock],
    model_order: list[str],
    layout: str,
) -> list[tuple[tuple[str, ...], list[ResultBlock]]]:
    lookup = {(block.model_rel, block.ligand): block for block in blocks}

    if layout == "by-ligand":
        return [
            (
                ("ligand", ligand),
                [lookup[(model, ligand)] for model in model_order],
            )
            for ligand in LIGAND_ORDER
        ]

    return [
        (
            (
                "receptor",
                lookup[(model, LIGAND_ORDER[0])].receptor,
                "model_rel",
                model,
            ),
            [lookup[(model, ligand)] for ligand in LIGAND_ORDER],
        )
        for model in model_order
    ]


def write_merged_file(
    destination: Path,
    kind: str,
    layout: str,
    sections: list[tuple[tuple[str, ...], list[ResultBlock]]],
) -> int:
    destination.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.",
        suffix=".tmp",
        dir=destination.parent,
    )
    temporary_path = Path(temporary_name)
    block_count = 0

    try:
        with os.fdopen(file_descriptor, "wb") as output:
            first_section = True
            for section_label, section_blocks in sections:
                if not first_section:
                    output.write(b"\n")
                first_section = False

                output.write(
                    csv_marker(
                        "__PROLIF_SECTION__",
                        "layout",
                        layout,
                        *section_label,
                    )
                )

                for block_index, block in enumerate(section_blocks):
                    if block_index:
                        output.write(b"\n")

                    path = source_path(block, kind)
                    raw = read_and_validate_source(path, kind)
                    output.write(
                        csv_marker(
                            "__PROLIF_BLOCK__",
                            "receptor",
                            block.receptor,
                            "model_rel",
                            block.model_rel,
                            "ligand",
                            block.ligand,
                            "run_name",
                            block.run_name,
                            "source_csv",
                            str(path.resolve()),
                        )
                    )
                    output.write(raw)
                    if not raw.endswith((b"\n", b"\r")):
                        output.write(b"\n")
                    block_count += 1

            output.flush()
            os.fsync(output.fileno())

        os.replace(temporary_path, destination)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise

    return block_count


def main() -> int:
    args = parse_args()
    batch_root = args.batch_root.expanduser().resolve()
    output_dir = (
        args.output_dir.expanduser().resolve()
        if args.output_dir is not None
        else batch_root / "merged"
    )

    blocks, model_order = load_manifest(batch_root)
    layouts = (
        ("by-ligand", "by-receptor")
        if args.layout == "both"
        else (args.layout,)
    )
    kinds = tuple(dict.fromkeys(args.kinds))

    destinations = {
        (kind, layout): output_dir
        / f"prolif_{OUTPUT_KIND_NAME[kind]}_{layout.replace('-', '_')}.csv"
        for kind in kinds
        for layout in layouts
    }
    conflicts = [path for path in destinations.values() if path.exists()]
    if conflicts and not args.overwrite:
        formatted = "\n".join(f"  {path}" for path in conflicts)
        fail(
            "Output file(s) already exist; use --overwrite to replace them:\n"
            f"{formatted}"
        )

    for (kind, layout), destination in destinations.items():
        sections = ordered_sections(blocks, model_order, layout)
        block_count = write_merged_file(destination, kind, layout, sections)
        print(
            f"Wrote {destination}: {block_count} source blocks, "
            f"{len(model_order)} receptor models, kind={kind}, layout={layout}"
        )

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        raise SystemExit(f"ERROR: {error}") from error
