#!/usr/bin/env python3
"""Draw a chemistry-preserving 2D contact map from frozen PLIP results."""

from __future__ import annotations

import argparse
from collections import defaultdict
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw, ImageFont
from rdkit import Chem
from rdkit.Chem import Draw, rdDepictor


CANVAS = (1400, 900)
MOL_SIZE = (840, 560)
MOL_OFFSET = (280, 145)
BLUE = (42, 111, 190)
GREEN = (25, 145, 84)
MAGENTA = (186, 45, 121)
DARK = (32, 36, 42)
MUTED = (101, 110, 120)
LIGHT_GREY = (238, 241, 244)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "Arial Bold.ttf" if bold else "Arial.ttf"
    path = Path("/System/Library/Fonts/Supplemental") / name
    return ImageFont.truetype(str(path), size)


def read_plddt(pdb_path: Path) -> dict[int, float]:
    result: dict[int, float] = {}
    for line in pdb_path.read_text().splitlines():
        if line.startswith("ATOM") and line[12:16].strip() == "CA":
            result[int(line[22:26])] = float(line[60:66])
    return result


def ligand_atom_for_coordinate(mol: Chem.Mol, xyz: tuple[float, float, float]) -> int:
    conf = mol.GetConformer()
    distances = []
    for idx in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(idx)
        distance2 = (pos.x - xyz[0]) ** 2 + (pos.y - xyz[1]) ** 2 + (pos.z - xyz[2]) ** 2
        distances.append((distance2, idx))
    distance2, idx = min(distances)
    if distance2 > 0.01:
        raise ValueError(f"PLIP coordinate did not map to a ligand atom: {distance2 ** 0.5:.3f} A")
    return idx


def coordinate(node: ET.Element) -> tuple[float, float, float]:
    return tuple(float(node.findtext(axis)) for axis in ("x", "y", "z"))  # type: ignore[return-value]


def read_interactions(xml_path: Path, mol: Chem.Mol) -> list[dict[str, object]]:
    root = ET.parse(xml_path).getroot()
    result: list[dict[str, object]] = []
    for node in root.findall(".//hydrophobic_interaction"):
        result.append(
            {
                "type": "hydrophobic",
                "residue": f"{node.findtext('restype')}{node.findtext('resnr')}",
                "distance": float(node.findtext("dist")),
                "atom": ligand_atom_for_coordinate(mol, coordinate(node.find("ligcoo"))),
            }
        )
    for node in root.findall(".//hydrogen_bond"):
        result.append(
            {
                "type": "hbond",
                "residue": f"{node.findtext('restype')}{node.findtext('resnr')}",
                "distance": float(node.findtext("dist_d-a")),
                "angle": float(node.findtext("don_angle")),
                "atom": ligand_atom_for_coordinate(mol, coordinate(node.find("ligcoo"))),
            }
        )
    return result


def dashed_line(draw: ImageDraw.ImageDraw, start: tuple[float, float], end: tuple[float, float], fill, width=4, dash=12, gap=8) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = (dx * dx + dy * dy) ** 0.5
    if length == 0:
        return
    ux, uy = dx / length, dy / length
    position = 0.0
    while position < length:
        stop = min(position + dash, length)
        draw.line(
            (start[0] + ux * position, start[1] + uy * position, start[0] + ux * stop, start[1] + uy * stop),
            fill=fill,
            width=width,
        )
        position += dash + gap


def svg_text(x: float, y: float, value: str, size: int, weight: str = "normal", color: str = "#20242a", anchor: str = "start") -> str:
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("ligand_sdf", type=Path)
    parser.add_argument("plip_xml", type=Path)
    parser.add_argument("receptor_pdb", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    pose_mol = Chem.SDMolSupplier(str(args.ligand_sdf), removeHs=False)[0]
    if pose_mol is None:
        raise ValueError("Could not read ligand SDF")
    interactions = read_interactions(args.plip_xml, pose_mol)
    plddt = read_plddt(args.receptor_pdb)

    mol2d = Chem.Mol(pose_mol)
    mol2d.RemoveAllConformers()
    rdDepictor.Compute2DCoords(mol2d)

    cairo = Draw.MolDraw2DCairo(*MOL_SIZE)
    cairo.drawOptions().padding = 0.14
    cairo.drawOptions().addStereoAnnotation = True
    cairo.DrawMolecule(mol2d)
    atom_points = {
        idx: (
            cairo.GetDrawCoords(idx).x + MOL_OFFSET[0],
            cairo.GetDrawCoords(idx).y + MOL_OFFSET[1],
        )
        for idx in range(mol2d.GetNumAtoms())
    }
    cairo.FinishDrawing()
    molecule_png = Image.open(__import__("io").BytesIO(cairo.GetDrawingText())).convert("RGB")

    svg_drawer = Draw.MolDraw2DSVG(*MOL_SIZE)
    svg_drawer.drawOptions().padding = 0.14
    svg_drawer.drawOptions().addStereoAnnotation = True
    svg_drawer.DrawMolecule(mol2d)
    svg_drawer.FinishDrawing()
    molecule_svg = svg_drawer.GetDrawingText()
    molecule_inner = molecule_svg[molecule_svg.find(">") + 1 : molecule_svg.rfind("</svg>")]

    positions = {
        "ASP9": (25, 205),
        "LEU92": (25, 405),
        "TYR166": (25, 605),
        "ARG96": (1115, 205),
        "TYR168": (1115, 405),
        "THR176": (1115, 605),
    }
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in interactions:
        grouped[str(item["residue"])].append(item)

    image = Image.new("RGB", CANVAS, "white")
    image.paste(molecule_png, MOL_OFFSET)
    draw = ImageDraw.Draw(image)
    draw.text((35, 30), "Gpr2–ascr#3 WT top1 — PLIP contact map", font=font(34, True), fill=DARK)
    draw.text((35, 78), "Neutral ascr#3 | SwissDock AC | PLIP v2.4.0", font=font(22), fill=MUTED)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS[0]}" height="{CANVAS[1]}" viewBox="0 0 {CANVAS[0]} {CANVAS[1]}">',
        '<rect width="100%" height="100%" fill="white"/>',
        svg_text(35, 55, "Gpr2–ascr#3 WT top1 — PLIP contact map", 34, "bold"),
        svg_text(35, 90, "Neutral ascr#3 | SwissDock AC | PLIP v2.4.0", 22, color="#656e78"),
        f'<g transform="translate({MOL_OFFSET[0]} {MOL_OFFSET[1]})">{molecule_inner}</g>',
    ]

    for residue, items in grouped.items():
        x, y = positions[residue]
        box_w, box_h = 260, 132
        anchor_x = x + box_w if x < CANVAS[0] / 2 else x
        anchor_y = y + box_h / 2
        for item in items:
            atom = atom_points[int(item["atom"])]
            color = BLUE if item["type"] == "hbond" else GREEN
            dashed_line(draw, (anchor_x, anchor_y), atom, color, width=4)
            color_hex = "#2a6fbe" if item["type"] == "hbond" else "#199154"
            svg_parts.append(
                f'<line x1="{anchor_x}" y1="{anchor_y}" x2="{atom[0]:.1f}" y2="{atom[1]:.1f}" stroke="{color_hex}" stroke-width="4" stroke-dasharray="12 8"/>'
            )

        is_anchor = residue == "TYR168"
        border = MAGENTA if is_anchor else DARK
        fill = (253, 240, 248) if is_anchor else (255, 255, 255)
        draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=14, fill=fill, outline=border, width=4)
        label = residue.replace("ASP", "D").replace("LEU", "L").replace("ARG", "R").replace("TYR", "Y").replace("THR", "T")
        if is_anchor:
            label += "  Kuo anchor"
        draw.text((x + 16, y + 14), label, font=font(24, True), fill=border)
        yy = y + 51
        for item in sorted(items, key=lambda value: str(value["type"])):
            if item["type"] == "hbond":
                text_value = f'H-bond  {item["distance"]:.2f} Å'
                color = BLUE
            else:
                text_value = f'Hydrophobic  {item["distance"]:.2f} Å'
                color = GREEN
            draw.text((x + 16, yy), text_value, font=font(19), fill=color)
            yy += 27
        resnum = int("".join(character for character in residue if character.isdigit()))
        confidence = plddt[resnum]
        confidence_text = f"AF2 pLDDT {confidence:.1f}"
        if confidence < 70:
            confidence_text += "  low confidence"
        draw.text((x + 16, y + 105), confidence_text, font=font(16), fill=MUTED)

        border_hex = "#ba2d79" if is_anchor else "#20242a"
        fill_hex = "#fdf0f8" if is_anchor else "#ffffff"
        svg_parts.append(f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" rx="14" fill="{fill_hex}" stroke="{border_hex}" stroke-width="4"/>')
        svg_parts.append(svg_text(x + 16, y + 34, label, 24, "bold", border_hex))
        yy = y + 63
        for item in sorted(items, key=lambda value: str(value["type"])):
            if item["type"] == "hbond":
                text_value = f'H-bond  {item["distance"]:.2f} Å'
                color_hex = "#2a6fbe"
            else:
                text_value = f'Hydrophobic  {item["distance"]:.2f} Å'
                color_hex = "#199154"
            svg_parts.append(svg_text(x + 16, yy, text_value, 19, color=color_hex))
            yy += 27
        svg_parts.append(svg_text(x + 16, y + 121, confidence_text, 16, color="#656e78"))

    legend_y = 825
    dashed_line(draw, (360, legend_y), (440, legend_y), BLUE, width=4)
    draw.text((455, legend_y - 13), "Hydrogen bond", font=font(19), fill=DARK)
    dashed_line(draw, (650, legend_y), (730, legend_y), GREEN, width=4)
    draw.text((745, legend_y - 13), "Hydrophobic contact", font=font(19), fill=DARK)
    draw.text((35, 862), "Distances and interaction types are taken directly from PLIP; no contacts were recalculated.", font=font(16), fill=MUTED)
    svg_parts.extend(
        [
            '<line x1="360" y1="825" x2="440" y2="825" stroke="#2a6fbe" stroke-width="4" stroke-dasharray="12 8"/>',
            svg_text(455, 832, "Hydrogen bond", 19),
            '<line x1="650" y1="825" x2="730" y2="825" stroke="#199154" stroke-width="4" stroke-dasharray="12 8"/>',
            svg_text(745, 832, "Hydrophobic contact", 19),
            svg_text(35, 873, "Distances and interaction types are taken directly from PLIP; no contacts were recalculated.", 16, color="#656e78"),
            "</svg>",
        ]
    )

    png_path = args.output_dir / "Gpr2_ascr3_neutral_AC_top1_PLIP_2D_contact_map.png"
    svg_path = args.output_dir / "Gpr2_ascr3_neutral_AC_top1_PLIP_2D_contact_map.svg"
    image.save(png_path, dpi=(300, 300))
    svg_path.write_text("\n".join(svg_parts))
    print(f"PNG: {png_path}")
    print(f"SVG: {svg_path}")


if __name__ == "__main__":
    main()
