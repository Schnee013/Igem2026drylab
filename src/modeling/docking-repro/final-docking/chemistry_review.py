"""Render temporary human-review material from chemistry report JSON."""

from __future__ import annotations

import hashlib
import html
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


RECEPTOR_TOOL_ID = "report_receptor_chemistry"
LIGAND_TOOL_ID = "report_ligand_chemistry"
CHEMISTRY_TOOL_IDS = {RECEPTOR_TOOL_ID, LIGAND_TOOL_ID}
OBSERVABLE_GROUP_LABELS = {
    "carboxylate_side_chain": "羧酸 / 羧酸根侧链",
    "imidazole_side_chain": "咪唑侧链",
    "thiol_or_thiolate_side_chain": "硫醇 / 硫负离子侧链",
    "amine_side_chain": "胺侧链",
    "guanidinium_side_chain": "胍基侧链",
    "phenol_side_chain": "酚羟基侧链",
}
FORMAL_CHARGE_SOURCE_LABELS = {
    "M_CHG_overrides_atom_block": "M  CHG 记录（覆盖原子块电荷码）",
    "atom_block_charge_code": "V2000 原子块电荷码",
}
BOND_ORDER_LABELS = {
    "1": "单键",
    "2": "双键",
    "3": "三键",
    "4": "芳香键",
}
ATOM_STEREO_LABELS = {
    "0": "非立体中心",
    "1": "奇数（odd）",
    "2": "偶数（even）",
    "3": "未指定（either）",
}
# util.cbag 的元素着色（CPK 色），供配体检查页的 PyMOL 图例使用。
ELEMENT_COLOR_LABELS = (
    ("H", "氢", "white"),
    ("C", "碳", "carbon"),
    ("N", "氮", "nitrogen"),
    ("O", "氧", "oxygen"),
    ("S", "硫", "sulfur"),
    ("P", "磷", "phosphorus"),
    ("F", "氟", "fluorine"),
    ("Cl", "氯", "chlorine"),
)


class ChemistryReviewError(ValueError):
    """The structured report cannot be rendered safely."""


@dataclass(frozen=True)
class ChemistryReviewBundle:
    html_path: Path
    pml_path: Path


def create_chemistry_review_bundle(
    tool_id: str,
    report: Mapping[str, Any],
    source_path: Path,
    output_directory: Path,
) -> ChemistryReviewBundle:
    """Write one self-contained HTML page and one PyMOL script atomically."""

    if tool_id not in CHEMISTRY_TOOL_IDS:
        raise ChemistryReviewError(f"不支持的化学检查工具：{tool_id}")
    source = source_path.expanduser().resolve()
    if not source.is_file():
        raise ChemistryReviewError(f"化学检查输入文件不存在：{source}")
    if not isinstance(report, Mapping):
        raise ChemistryReviewError("化学检查 JSON 顶层必须是对象。")
    _required_text(report, "source_file")

    directory = output_directory.expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    if not directory.is_dir():
        raise ChemistryReviewError(f"临时检查目录不可用：{directory}")

    stem = "receptor" if tool_id == RECEPTOR_TOOL_ID else "ligand"
    html_path = directory / f"{stem}-chemistry-review.html"
    pml_path = directory / f"{stem}-chemistry-review.pml"
    if tool_id == RECEPTOR_TOOL_ID:
        html_text = render_receptor_html(report, source)
        pml_text = render_receptor_pml(source)
    else:
        html_text = render_ligand_html(report, source)
        pml_text = render_ligand_pml(source)
    _atomic_write_text(html_path, html_text)
    _atomic_write_text(pml_path, pml_text)
    return ChemistryReviewBundle(html_path=html_path, pml_path=pml_path)


def _neighbor_tables(report: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]:
    pocket = report.get("pocket")
    has_pocket = isinstance(pocket, Mapping) and isinstance(pocket.get("neighbors"), list)
    distance_header = ("距锚点 Å",) if has_pocket else ()
    return has_pocket, distance_header


def render_receptor_html(report: Mapping[str, Any], source_path: Path) -> str:
    atom_records = _required_mapping(report, "atom_record_count")
    ionizable = _required_rows(report, "ionizable_residues")
    histidines = _required_rows(report, "histidines")
    cysteines = _required_rows(report, "cysteines")
    waters = _required_sequence(report, "water_residues")
    hetero = _required_rows(report, "hetero_components")
    chains = _required_rows(report, "chains")
    polymer_residue_count = _required_int(report, "polymer_residue_count")
    water_count = _required_int(report, "water_residue_count")

    has_pocket, distance_header = _neighbor_tables(report)

    summary = _definition_list(
        (
            ("原子记录", _compact_mapping(atom_records)),
            ("蛋白残基", polymer_residue_count),
            ("蛋白链", len(chains)),
            ("可离子化残基", len(ionizable)),
            ("组氨酸", len(histidines)),
            ("半胱氨酸", len(cysteines)),
            ("水分子残基", water_count),
            ("非水异源组分", len(hetero)),
        )
    )
    decision_items = (
        "按下方链清单确认要保留的蛋白链，并逐行确认每个非水异源组分保留或删除。",
        "逐行确认每个 HIS 为 HID、HIE 或 HIP；逐行确认每个 CYS 为游离、二硫键或配位。",
        "若下方锚定了结合位点，逐个确认其邻近残基是否需要特殊质子化；未锚定时在 PyMOL 中自行圈定。",
        "回到 Docking 工具台，只在这些化学状态已有明确答案时批准继续。",
    )
    chain_table = _table(
        ("链", "蛋白残基", "水", "异源组分", "异源组分名"),
        (
            (
                row.get("chain_id", ""),
                row.get("polymer_residue_count", ""),
                row.get("water_residue_count", ""),
                row.get("hetero_component_count", ""),
                "、".join(_text(name) for name in row.get("hetero_residue_names", [])),
            )
            for row in chains
        ),
        "输入中没有观察到蛋白链。",
        row_marks={
            index: _checkbox("chain", row.get("chain_id", ""), f"保留链 {row.get('chain_id', '')}")
            for index, row in enumerate(chains)
        },
    )

    if has_pocket:
        pocket = report["pocket"]
        anchor_kind = pocket.get("anchor_kind")
        anchor_label = _text(pocket.get("anchor_label", ""))
        anchor_text = (
            f"手动坐标 {_escape(anchor_label)}"
            if anchor_kind == "manual_center"
            else f"组分 {_escape(anchor_label)}"
        )
        pocket_intro = (
            f"<p>锚点：{anchor_text}；半径 {_escape(pocket.get('radius', ''))} Å。</p>"
            "<p class=\"aside\">距离是锚点到残基原子的最近原子间距。表格只列半径内"
            "的可离子化残基；完整列表见下方可折叠区。</p>"
        )
        neighbor_rows = pocket.get("neighbors", [])
        neighbor_table = _table(
            ("残基", "重原子数",) + distance_header,
            (
                (
                    row.get("residue_id", ""),
                    _heavy_atom_text(row),
                    _distance_text(row.get("distance_to_anchor")),
                )
                for row in neighbor_rows
            ),
            "锚点半径内没有可离子化残基。",
            row_marks={
                index: _checkbox("pocket", row.get("residue_id", ""), f"检查 {row.get('residue_id', '')}")
                for index, row in enumerate(neighbor_rows)
            },
        )
    else:
        pocket_intro = (
            "<p>没有锚定结合位点，本页无法判断哪些可离子化残基在预期位点附近。</p>"
            "<p class=\"aside\">在工具的参数里填写“口袋锚定组分”（如共晶配体的 ID，"
            "见下方异源组分表）或“口袋锚定坐标”，重新运行即可得到邻近残基表；"
            "也可以直接在 PyMOL 视图里圈定。</p>"
        )
        neighbor_table = ""

    histidine_table = _table(
        ("残基", "重原子数",) + distance_header,
        (
            (
                row.get("residue_id", ""),
                _heavy_atom_text(row),
                _distance_text(row.get("distance_to_anchor")),
            )
            for row in histidines
        ),
        "输入中没有观察到 HIS 残基。",
        row_marks={
            index: _checkbox("his", row.get("residue_id", ""), f"检查 {row.get('residue_id', '')}")
            for index, row in enumerate(histidines)
        },
    )
    cysteine_table = _table(
        ("残基", "重原子数",) + distance_header,
        (
            (
                row.get("residue_id", ""),
                _heavy_atom_text(row),
                _distance_text(row.get("distance_to_anchor")),
            )
            for row in cysteines
        ),
        "输入中没有观察到 CYS 残基。",
        row_marks={
            index: _checkbox("cys", row.get("residue_id", ""), f"检查 {row.get('residue_id', '')}")
            for index, row in enumerate(cysteines)
        },
    )
    hetero_table = _table(
        ("组分", "残基名", "原子数", "元素"),
        (
            (
                row.get("component_id", ""),
                row.get("residue_name", ""),
                row.get("atom_count", ""),
                _compact_mapping(row.get("elements", {})),
            )
            for row in hetero
        ),
        "输入中没有观察到非水 HETATM 组分。",
        row_marks={
            index: _checkbox("hetero", row.get("component_id", ""), f"保留 {row.get('component_id', '')}")
            for index, row in enumerate(hetero)
        },
    )
    ionizable_table = _table(
        ("残基", "残基类型", "可观察基团", "重原子数",) + distance_header,
        (
            (
                row.get("residue_id", ""),
                row.get("residue_name", ""),
                _observable_group_text(row.get("observable_group", "")),
                _heavy_atom_text(row),
                _distance_text(row.get("distance_to_anchor")),
            )
            for row in ionizable
        ),
        "没有观察到预设列表中的可离子化残基。",
    )
    if waters:
        preview = "、".join(_text(item) for item in waters[:5])
        if len(waters) > 5:
            preview += f" ……（共 {len(waters)} 个）"
        water_text = preview
    else:
        water_text = "未观察到水残基。"
    body = f"""
      <header>
        <h1>受体化学检查</h1>
        <p class="source"><strong>输入：</strong>{_escape(source_path)}</p>
        <p class="notice">该页面只整理输入结构中可观察到的事实，不会替你选择质子化状态、HIS 互变异构体、二硫键或保留水。</p>
      </header>
      <section aria-labelledby="decision-title">
        <h2 id="decision-title">需要你给出的答案</h2>
        {_decisions(decision_items)}
        <p class="aside">下方每行行首的勾选框用于目视进度，不持久化，也不会自动解锁下一步。</p>
      </section>
      <section aria-labelledby="summary-title">
        <h2 id="summary-title">输入摘要</h2>
        {summary}
      </section>
      <section aria-labelledby="chain-title">
        <h2 id="chain-title">蛋白链</h2>
        {chain_table}
      </section>
      <section aria-labelledby="pocket-title">
        <h2 id="pocket-title">结合位点邻近</h2>
        {pocket_intro}
        {neighbor_table}
      </section>
      <section aria-labelledby="visual-title">
        <h2 id="visual-title">PyMOL 视图怎么读</h2>
        <ul class="legend">
          <li><span class="swatch cyan"></span><strong>青色：</strong>HIS，逐个判断 HID / HIE / HIP。</li>
          <li><span class="swatch orange"></span><strong>橙色：</strong>CYS，检查游离、二硫键或配位状态。</li>
          <li><span class="swatch yellow"></span><strong>黄色：</strong>其它常见可离子化侧链。</li>
          <li><span class="swatch blue"></span><strong>蓝色球：</strong>水；<span class="swatch magenta"></span><strong>洋红：</strong>非水异源组分。</li>
        </ul>
      </section>
      <section aria-labelledby="his-title">
        <h2 id="his-title">HIS 状态</h2>
        <p>逐个决定每个 HIS 为 HID、HIE 或 HIP；重原子数与期望值不符的残基需要先检查侧链是否完整。</p>
        {histidine_table}
      </section>
      <section aria-labelledby="cys-title">
        <h2 id="cys-title">CYS 状态</h2>
        <p>逐个决定每个 CYS 为游离、二硫键或配位；重原子数与期望值不符的残基需要先检查侧链是否完整。</p>
        {cysteine_table}
      </section>
      <section aria-labelledby="component-title">
        <h2 id="component-title">水与异源组分</h2>
        <p><strong>水残基（{water_count}）：</strong>{_escape(water_text)}</p>
        <p>逐个决定每个非水异源组分保留或删除（“元素”为“无”时表示输入 PDB 没有元素列，请在 PyMOL 中核对组分）。</p>
        {hetero_table}
      </section>
      <details>
        <summary>查看全部可离子化残基（{len(ionizable)}）</summary>
        {ionizable_table}
      </details>
      {_raw_json_details(report)}
    """
    return _page("受体化学检查", body)


def render_ligand_html(report: Mapping[str, Any], source_path: Path) -> str:
    atom_count = _required_int(report, "atom_count")
    heavy_atom_count = _required_int(report, "heavy_atom_count")
    explicit_h = _required_int(report, "explicit_hydrogen_atom_count")
    element_counts = _required_mapping(report, "element_counts")
    bond_count = _required_int(report, "bond_count")
    bond_orders = _required_mapping(report, "bond_order_counts")
    total_charge = _required_int(report, "total_formal_charge_from_records")
    charge_source = _required_text(report, "formal_charge_source")
    charge_rows = _required_rows(report, "formal_charge_records")
    stereo_atoms = _required_rows(report, "atom_stereo_parities")
    stereo_bonds = _required_rows(report, "stereo_bonds")
    fragments = _required_rows(report, "fragments")
    fragment_count = _required_int(report, "fragment_count")

    summary = _definition_list(
        (
            ("总形式电荷", total_charge),
            ("原子总数", atom_count),
            ("重原子", heavy_atom_count),
            ("显式氢", explicit_h),
            ("元素组成", _compact_mapping(element_counts)),
            ("化学键", bond_count),
            ("键级分布", _bond_order_summary(bond_orders)),
            ("连通断片", fragment_count),
            ("原子立体标记", len(stereo_atoms)),
            ("键立体标记", len(stereo_bonds)),
        )
    )
    decision_items = (
        f"确认计划用于 docking 的微观态总形式电荷就是 {total_charge}。",
        "确认当前质子化态和互变异构体符合实验条件与研究假设。",
        "确认显式氢、键级、芳香性和立体化学与参考结构一致。",
        "确认输入中没有应当移除的盐、对离子或溶剂片段（见下方“连通断片”）。",
        "回到 Docking 工具台，只在当前 SDF 就是目标微观态时批准继续。",
    )
    charge_table = _table(
        ("原子序号", "形式电荷"),
        (
            (
                row.get("atom", ""),
                row.get("charge", ""),
            )
            for row in charge_rows
        ),
        "输入记录中没有非零形式电荷。",
    )

    if fragment_count > 1:
        fragment_intro = (
            "<p class=\"notice\">文件里有多个连通断片：除主体分子外，其余通常是"
            "盐、对离子或溶剂。确认要保留哪些，或者在输入前移除。</p>"
        )
    else:
        fragment_intro = "<p>只有一个连通断片：输入中不含孤立的盐、对离子或溶剂分子。</p>"
    fragment_table = _table(
        ("断片", "分子式", "重原子", "形式电荷", "原子序号（预览）"),
        (
            (
                f"{row.get('index', '')}{'（主体候选）' if row.get('index') == 1 else ''}",
                row.get("formula", ""),
                row.get("heavy_atom_count", ""),
                row.get("formal_charge", ""),
                ", ".join(_text(index) for index in row.get("atom_indices", [])[:10]),
            )
            for row in fragments
        ),
        "输入中没有原子。",
        row_marks={
            index: _checkbox(
                "fragment",
                f"fragment-{row.get('index', index + 1)}",
                f"保留断片 {row.get('index', index + 1)}",
            )
            for index, row in enumerate(fragments)
        },
    )
    stereo_atom_table = _table(
        ("原子序号", "元素", "立体标记", "说明", "坐标 (x, y, z)"),
        (
            (
                row.get("index", ""),
                row.get("element", ""),
                row.get("stereo_parity", ""),
                _parity_text(row.get("stereo_parity", "")),
                _coordinate_text(row),
            )
            for row in stereo_atoms
        ),
        "原子块中没有非零立体标记。",
    )
    stereo_bond_table = _table(
        ("键序号", "原子 1", "原子 2", "键级", "立体标记"),
        (
            (
                row.get("index", ""),
                row.get("atom_1", ""),
                row.get("atom_2", ""),
                row.get("order", ""),
                row.get("stereo", ""),
            )
            for row in stereo_bonds
        ),
        "键记录中没有非零立体标记。",
    )
    coordinates = (
        "存在非零三维坐标"
        if bool(report.get("any_nonzero_coordinate"))
        else "没有观察到非零三维坐标"
    )
    legend_parts = []
    for element, label, _css in ELEMENT_COLOR_LABELS:
        if element == "H":
            suffix = "重原子按此着色，氢为白色小球。"
        else:
            suffix = ""
        legend_parts.append(
            f'<li><span class="swatch {_escape(element)}"></span>'
            f"<strong>{_escape(label)}（{_escape(element)}）</strong>{suffix}</li>"
        )
    legend_items = "".join(legend_parts)
    body = f"""
      <header>
        <h1>配体化学检查</h1>
        <p class="source"><strong>输入：</strong>{_escape(source_path)}</p>
        <p class="notice">该页面只整理当前 SDF 中可观察到的电荷、氢、键和立体信息，不会替你选择质子化态、互变异构体或构象。</p>
      </header>
      <section aria-labelledby="decision-title">
        <h2 id="decision-title">需要你给出的答案</h2>
        {_decisions(decision_items)}
        <p class="aside">下方每行行首的勾选框用于目视进度，不持久化，也不会自动解锁下一步。</p>
      </section>
      <section aria-labelledby="summary-title">
        <h2 id="summary-title">输入摘要</h2>
        {summary}
        <p><strong>坐标：</strong>{_escape(coordinates)}</p>
      </section>
      <section aria-labelledby="visual-title">
        <h2 id="visual-title">PyMOL 视图怎么读</h2>
        <p>重原子按元素着色（下方图例）并标出“元素 + 原子序号”，显式氢以白色小球显示。用原子序号把三维位置与下方电荷、立体标记表对应起来。</p>
        <ul class="legend">
          {legend_items}
        </ul>
        <p class="aside">PyMOL 适合核对连通关系、氢的位置、明显的几何异常和预期立体构型；总电荷、质子化态及互变异构体是否符合研究条件，仍以检查页和参考化学知识为准。</p>
      </section>
      <section aria-labelledby="charge-title">
        <h2 id="charge-title">形式电荷</h2>
        <p>记录来源：{_escape(_formal_charge_source_text(charge_source))}（原始标识：<code>{_escape(charge_source)}</code>）</p>
        {charge_table}
      </section>
      <section aria-labelledby="fragment-title">
        <h2 id="fragment-title">连通断片</h2>
        {fragment_intro}
        {fragment_table}
      </section>
      <section aria-labelledby="stereo-title">
        <h2 id="stereo-title">立体信息</h2>
        <p class="aside">这里列的是 SDF V2000 中实际存在的数值标记，用于定位需要目视核对的原子和键；它本身不是自动给出的 R/S 或 E/Z 结论。</p>
        <h3>原子立体标记</h3>
        {stereo_atom_table}
        <h3>键立体标记</h3>
        {stereo_bond_table}
      </section>
      {_raw_json_details(report)}
    """
    return _page("配体化学检查", body)


def render_receptor_pml(source_path: Path) -> str:
    suffix = _object_suffix(source_path)
    obj = f"chem_receptor_{suffix}"
    histidines = f"chem_his_{suffix}"
    cysteines = f"chem_cys_{suffix}"
    ionizable = f"chem_ionizable_{suffix}"
    waters = f"chem_waters_{suffix}"
    hetero = f"chem_hetero_{suffix}"
    group = f"chem_review_{suffix}"
    return "\n".join(
        (
            "# Temporary receptor chemistry review. Visual evidence only.",
            f"load {_pymol_quote(str(source_path.resolve()))}, {obj}",
            f"hide everything, {obj}",
            f"show cartoon, {obj} and polymer.protein",
            f"color gray70, {obj} and polymer.protein",
            f"select {histidines}, {obj} and resn HIS+HID+HIE+HIP",
            f"show sticks, {histidines}",
            f"color cyan, {histidines}",
            f"select {cysteines}, {obj} and resn CYS+CYX+CYM",
            f"show sticks, {cysteines}",
            f"color orange, {cysteines}",
            f"select {ionizable}, {obj} and resn ASP+GLU+LYS+ARG+TYR",
            f"show sticks, {ionizable}",
            f"color yellow, {ionizable}",
            f"select {waters}, {obj} and solvent",
            f"show spheres, {waters}",
            f"set sphere_scale, 0.28, {waters}",
            f"color marine, {waters}",
            f"select {hetero}, {obj} and hetatm and not solvent",
            f"show sticks, {hetero}",
            f"color magenta, {hetero}",
            f"show sticks, {obj} and hydro",
            f"label ({histidines} or {cysteines}) and name CA, \"%s %s/%s\" % (resn, resi, chain)",
            "set label_color, black",
            "set label_size, 14",
            "set cartoon_transparency, 0.15",
            "set stick_radius, 0.18",
            "bg_color white",
            f"group {group}, {obj} {histidines} {cysteines} {ionizable} {waters} {hetero}",
            f"orient {obj}",
            "deselect",
        )
    ) + "\n"


def render_ligand_pml(source_path: Path) -> str:
    suffix = _object_suffix(source_path)
    obj = f"chem_ligand_{suffix}"
    group = f"chem_review_{suffix}"
    return "\n".join(
        (
            "# Temporary ligand chemistry review. Visual evidence only.",
            f"load {_pymol_quote(str(source_path.resolve()))}, {obj}",
            f"hide everything, {obj}",
            f"show sticks, {obj}",
            f"show spheres, {obj} and hydro",
            f"set sphere_scale, 0.20, {obj} and hydro",
            f"set stick_radius, 0.18, {obj}",
            f"set valence, 1, {obj}",
            f"util.cbag({_pymol_quote(obj)})",
            f"label {obj} and not hydro, \"%s%s\" % (elem, index)",
            "set label_color, black",
            "set label_size, 14",
            "bg_color white",
            f"group {group}, {obj}",
            f"orient {obj}",
            "deselect",
        )
    ) + "\n"


def _page(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{_escape(title)}</title>
  <style>
    :root {{ color-scheme: light; --ink: #182230; --muted: #4b5563; --line: #cbd5e1; --paper: #ffffff; --wash: #f8fafc; --attention: #8a3b12; --attention-bg: #fff7ed; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--wash); color: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", sans-serif; font-size: 16px; line-height: 1.65; }}
    main {{ width: min(74rem, calc(100% - 2rem)); margin: 0 auto; padding: 3rem 0 5rem; }}
    header, section, details {{ background: var(--paper); border: 1px solid var(--line); border-radius: 10px; padding: 1.4rem 1.6rem; margin: 0 0 1.25rem; }}
    h1 {{ font-size: clamp(1.8rem, 4vw, 2.6rem); line-height: 1.15; margin: 0 0 1rem; letter-spacing: -0.025em; }}
    h2 {{ font-size: 1.35rem; margin: 0 0 0.85rem; }}
    h3 {{ font-size: 1.05rem; margin: 1.4rem 0 0.6rem; }}
    p {{ max-width: 75ch; }}
    .source {{ overflow-wrap: anywhere; color: var(--muted); }}
    .notice {{ max-width: none; color: var(--attention); background: var(--attention-bg); border: 1px solid #fdba74; border-radius: 7px; padding: 0.8rem 1rem; }}
    .aside {{ color: var(--muted); font-size: 0.92rem; }}
    .decisions {{ display: grid; gap: 0.6rem; padding-left: 1.4rem; }}
    .legend {{ display: grid; gap: 0.55rem; padding-left: 1.4rem; }}
    .swatch {{ display: inline-block; inline-size: 0.85rem; block-size: 0.85rem; margin: 0 0.35rem 0 0.15rem; border: 1px solid #475569; border-radius: 50%; vertical-align: -0.05rem; }}
    .swatch.cyan {{ background: #22d3ee; }}
    .swatch.orange {{ background: #fb923c; }}
    .swatch.yellow {{ background: #fde047; }}
    .swatch.blue {{ background: #3b82f6; }}
    .swatch.magenta {{ background: #d946ef; }}
    .swatch.H {{ background: #f8fafc; }}
    .swatch.C {{ background: #334155; }}
    .swatch.N {{ background: #3b82f6; }}
    .swatch.O {{ background: #dc2626; }}
    .swatch.S {{ background: #eab308; }}
    .swatch.P {{ background: #f97316; }}
    .swatch.F {{ background: #86efac; }}
    .swatch.Cl {{ background: #16a34a; }}
    .row-check {{ inline-size: 1.1rem; block-size: 1.1rem; accent-color: #1d4ed8; vertical-align: -0.15rem; }}
    .row-check-cell {{ width: 1%; white-space: nowrap; }}
    .check-col {{ width: 1%; }}
    tr:has(.row-check:checked) td {{ opacity: 0.55; }}
    td.warn {{ color: var(--attention); font-weight: 650; background: var(--attention-bg); }}
    dl {{ display: grid; grid-template-columns: minmax(11rem, 0.8fr) minmax(12rem, 2fr); margin: 0; }}
    dt, dd {{ margin: 0; padding: 0.55rem 0; border-bottom: 1px solid #e2e8f0; }}
    dt {{ color: var(--muted); }}
    dd {{ font-variant-numeric: tabular-nums; overflow-wrap: anywhere; }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-variant-numeric: tabular-nums; }}
    th, td {{ padding: 0.65rem 0.75rem; border-bottom: 1px solid #e2e8f0; text-align: left; vertical-align: top; }}
    th {{ color: #334155; background: #f1f5f9; font-weight: 650; }}
    tr:focus-within, tbody tr:hover {{ background: #f8fafc; }}
    .empty {{ color: var(--muted); font-style: italic; }}
    summary {{ cursor: pointer; font-weight: 650; }}
    details[open] summary {{ margin-bottom: 1rem; }}
    pre {{ max-height: 32rem; overflow: auto; padding: 1rem; background: #0f172a; color: #f8fafc; border-radius: 7px; font-size: 0.84rem; }}
    code, pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    :focus-visible {{ outline: 3px solid #2563eb; outline-offset: 3px; }}
    ::selection {{ background: #bfdbfe; color: #172554; }}
    @media (max-width: 42rem) {{ main {{ width: min(100% - 1rem, 74rem); padding-top: 0.5rem; }} header, section, details {{ border-radius: 6px; padding: 1rem; }} dl {{ grid-template-columns: 1fr; }} dt {{ padding-bottom: 0; border-bottom: 0; }} dd {{ padding-top: 0.1rem; }} }}
    @media print {{ body {{ background: white; }} main {{ width: 100%; padding: 0; }} header, section, details {{ break-inside: avoid; box-shadow: none; }} }}
  </style>
</head>
<body>
  <main>
    {body}
    <p class="aside">该 HTML 与配套 PML 都是当前 Docking 工具台会话的临时检查材料；退出工具台后会被清理。</p>
  </main>
</body>
</html>
"""


def _definition_list(items: Iterable[tuple[str, object]]) -> str:
    rows = "".join(
        f"<dt>{_escape(label)}</dt><dd>{_escape(value)}</dd>" for label, value in items
    )
    return f"<dl>{rows}</dl>"


def _decisions(items: Sequence[str]) -> str:
    """A read-only answer outline; the actionable marks live on the rows below."""

    rows = "".join(f"<li>{_escape(item)}</li>" for item in items)
    return f'<ol class="decisions">{rows}</ol>'


@dataclass(frozen=True)
class _MarkupCell:
    """Pre-rendered HTML for one table cell, with an optional CSS class."""

    html: str
    css_class: str = ""


def _checkbox(table: str, row_key: str, label: str) -> str:
    """A per-row visual-progress checkbox.

    The page is a session temporary and is rewritten on every run, so marks
    intentionally do not persist; they exist only to keep the reviewer's place.
    """

    safe = "".join(
        character if character.isalnum() or character in "-_" else "_"
        for character in row_key
    )
    return (
        f'<input type="checkbox" class="row-check" id="chk-{table}-{safe}" '
        f'aria-label="{_escape(label)}">'
    )


def _distance_text(value: object) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{float(value):.3f}"
    return "—"


def _heavy_atom_text(row: Mapping[str, Any]) -> _MarkupCell:
    observed = row.get("heavy_atom_count")
    expected = row.get("expected_heavy_atom_count")
    if not isinstance(observed, int) or not isinstance(expected, int):
        return _MarkupCell(_escape(row.get("atom_count", "")))
    difference = observed - expected
    text = f"{observed} / 期望 {expected}"
    if difference != 0:
        sign = "+" if difference > 0 else ""
        text += f"（{sign}{difference}）"
    css_class = "warn" if difference != 0 else ""
    return _MarkupCell(_escape(text), css_class)


def _parity_text(value: object) -> str:
    key = _text(value)
    return ATOM_STEREO_LABELS.get(key, key)


def _table(
    headers: Sequence[str],
    rows: Iterable[Sequence[object]],
    empty_message: str,
    *,
    row_marks: Mapping[int, str] | None = None,
) -> str:
    """Render a data table.

    ``row_marks`` maps a row index to pre-escaped HTML inserted before the
    first cell, e.g. a per-row checkbox. Cells that are ``_MarkupCell``
    instances are inserted as-is instead of being escaped.
    """

    materialized = [tuple(row) for row in rows]
    if not materialized:
        return f'<p class="empty">{_escape(empty_message)}</p>'
    marks = row_marks or {}
    # 行首的勾选单元格同样占一列，表头必须有对应空 <th>，否则数据整体右移一列。
    check_head = '<th scope="col" class="check-col"></th>' if marks else ""
    head = check_head + "".join(f"<th scope=\"col\">{_escape(item)}</th>" for item in headers)
    body_parts = []
    for row_index, row in enumerate(materialized):
        cells = []
        for cell in row:
            if isinstance(cell, _MarkupCell):
                tag = f'<td class="{cell.css_class}">{cell.html}</td>' if cell.css_class else f"<td>{cell.html}</td>"
                cells.append(tag)
            else:
                cells.append(f"<td>{_escape(cell)}</td>")
        mark = marks.get(row_index, "")
        mark_cell = f'<td class="row-check-cell">{mark}</td>' if mark else ""
        body_parts.append("<tr>" + mark_cell + "".join(cells) + "</tr>")
    return (
        '<div class="table-wrap"><table><thead><tr>'
        + head
        + "</tr></thead><tbody>"
        + "".join(body_parts)
        + "</tbody></table></div>"
    )


def _raw_json_details(report: Mapping[str, Any]) -> str:
    raw = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    return (
        "<details><summary>查看原始结构化数据</summary><pre>"
        + html.escape(raw, quote=False)
        + "</pre></details>"
    )


def _required_text(report: Mapping[str, Any], key: str) -> str:
    value = report.get(key)
    if not isinstance(value, str) or not value:
        raise ChemistryReviewError(f"化学检查 JSON 缺少文本字段：{key}")
    return value


def _required_int(report: Mapping[str, Any], key: str) -> int:
    value = report.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ChemistryReviewError(f"化学检查 JSON 缺少整数字段：{key}")
    return value


def _required_mapping(report: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = report.get(key)
    if not isinstance(value, Mapping):
        raise ChemistryReviewError(f"化学检查 JSON 缺少对象字段：{key}")
    return value


def _required_sequence(report: Mapping[str, Any], key: str) -> Sequence[Any]:
    value = report.get(key)
    if not isinstance(value, list):
        raise ChemistryReviewError(f"化学检查 JSON 缺少数组字段：{key}")
    return value


def _required_rows(report: Mapping[str, Any], key: str) -> list[Mapping[str, Any]]:
    values = _required_sequence(report, key)
    if any(not isinstance(value, Mapping) for value in values):
        raise ChemistryReviewError(f"化学检查 JSON 的 {key} 必须只包含对象。")
    return list(values)


def _compact_mapping(value: object) -> str:
    if not isinstance(value, Mapping) or not value:
        return "无"
    return " · ".join(f"{_text(key)} {_text(item)}" for key, item in value.items())


def _observable_group_text(value: object) -> str:
    key = _text(value)
    return OBSERVABLE_GROUP_LABELS.get(key, key)


def _formal_charge_source_text(value: object) -> str:
    key = _text(value)
    return FORMAL_CHARGE_SOURCE_LABELS.get(key, key)


def _bond_order_summary(value: Mapping[str, Any]) -> str:
    if not value:
        return "无"
    return " · ".join(
        f"{BOND_ORDER_LABELS.get(_text(order), f'类型 {_text(order)}')} {_text(count)}"
        for order, count in value.items()
    )


def _coordinate_text(row: Mapping[str, Any]) -> str:
    values = (row.get("x"), row.get("y"), row.get("z"))
    if all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values):
        return ", ".join(f"{float(value):.4f}" for value in values)
    return ""


def _text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "是" if value else "否"
    return str(value)


def _escape(value: object) -> str:
    return html.escape(_text(value), quote=True)


def _object_suffix(source_path: Path) -> str:
    digest = hashlib.sha1(str(source_path.resolve()).encode("utf-8")).hexdigest()
    return digest[:8]


def _pymol_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _atomic_write_text(path: Path, content: str) -> None:
    descriptor: int | None = None
    temporary_path: Path | None = None
    try:
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
        )
        temporary_path = Path(temporary_name)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            descriptor = None
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except OSError as exc:
        raise ChemistryReviewError(f"无法写入临时检查文件 {path}：{exc}") from exc
    finally:
        if descriptor is not None:
            os.close(descriptor)
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
