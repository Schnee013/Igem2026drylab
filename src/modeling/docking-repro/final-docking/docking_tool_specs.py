from __future__ import annotations

import argparse
import importlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

from af2_amber_relax_engine import PROTOCOL_ID as AF2_AMBER_RELAX_PROTOCOL_ID

IGNORED_DESTS = {
    "generate_maestro_lid": {"_engine"},
}

COLLAPSED_SECTIONS = {"高级参数"}
SOURCE_ID_PATTERN = re.compile(r"^(?:argparse:[a-z0-9_]+:[a-z0-9_]+|S[1-8]:[A-Za-z0-9_.-]+)$")


@dataclass(frozen=True)
class GroupPresentation:
    group_id: str
    label: str


@dataclass(frozen=True)
class FieldPresentation:
    label: str
    help: str
    section: str
    control: str
    unit: str = ""
    minimum: float | int | None = None
    maximum: float | int | None = None
    step: float | int | None = None
    path_kind: str = ""
    file_filter: str = ""
    default_suffix: str = ""
    dialog_title: str = ""
    placeholder: str = ""
    label_source: str = "product"
    unit_source: str = ""
    range_source: str = ""
    step_source: str = ""
    value_source: str = "user"
    value_key: str = ""
    preset: Any = None


@dataclass(frozen=True)
class ToolField:
    dest: str
    option: str
    kind: str
    required: bool
    presentation: FieldPresentation
    default: Any = None
    choices: tuple[str, ...] = ()
    repeatable: bool = False

    @property
    def label(self) -> str:
        return self.presentation.label

    @property
    def help(self) -> str:
        return self.presentation.help

    @property
    def advanced(self) -> bool:
        return self.presentation.section in COLLAPSED_SECTIONS

    @property
    def user_editable(self) -> bool:
        return self.presentation.value_source == "user"


@dataclass(frozen=True)
class InputModePresentation:
    key: str
    label: str
    visible_dests: tuple[str, ...]
    required_dests: tuple[str, ...]
    guidance: str


@dataclass(frozen=True)
class OutputDerivation:
    output_dest: str
    source_dest: str
    name_template: str
    directory_mode: str = "source_parent"


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    group_id: str
    group: str
    title: str
    module: str
    script: str
    summary: str
    fields: tuple[ToolField, ...]
    input_modes: tuple[InputModePresentation, ...] = ()
    output_derivations: tuple[OutputDerivation, ...] = ()
    custom_panel: str = ""


@dataclass(frozen=True)
class ProgramArgs:
    program: str
    args: tuple[str, ...]

    def argv(self) -> tuple[str, ...]:
        return (self.program, *self.args)


def fp(
    label: str,
    help: str,
    section: str,
    control: str,
    *,
    unit: str = "",
    unit_source: str = "",
    minimum: float | int | None = None,
    maximum: float | int | None = None,
    range_source: str = "",
    step: float | int | None = None,
    step_source: str = "",
    path_kind: str = "",
    file_filter: str = "",
    default_suffix: str = "",
    dialog_title: str = "",
    placeholder: str = "",
    value_source: str = "user",
    value_key: str = "",
    preset: Any = None,
) -> FieldPresentation:
    return FieldPresentation(
        label=label,
        help=help,
        section=section,
        control=control,
        unit=unit,
        unit_source=unit_source,
        minimum=minimum,
        maximum=maximum,
        range_source=range_source,
        step=step,
        step_source=step_source,
        path_kind=path_kind,
        file_filter=file_filter,
        default_suffix=default_suffix,
        dialog_title=dialog_title,
        placeholder=placeholder,
        value_source=value_source,
        value_key=value_key,
        preset=preset,
    )


GROUP_ROWS: tuple[GroupPresentation, ...] = (
    GroupPresentation("structure_confidence", "结构与置信度"),
    GroupPresentation("tm_topology", "跨膜拓扑"),
    GroupPresentation("geometry_relaxation", "几何检查与结构优化"),
    GroupPresentation("ppm_orientation", "PPM 膜定位"),
    GroupPresentation("chemistry_preparation", "受体与配体准备"),
    GroupPresentation("vina_docking", "Vina 对接"),
    GroupPresentation("export_lid", "结果导出与 LID"),
)

GROUPS = {group.group_id: group for group in GROUP_ROWS}

TOOL_ROWS: tuple[tuple[str, str, str, str, str], ...] = (
    ("cif_to_pdb", "structure_confidence", "CIF 转换为 PDB", "cif_to_pdb", "把单个或一批 mmCIF 结构转换为 PDB 文件。"),
    ("report_af_confidence", "structure_confidence", "查看 AlphaFold 置信度", "report_af_confidence", "查看完整逐残基置信度，并可附加人工指定区域统计。"),
    ("make_tm_topology_review_pml", "tm_topology", "在 PyMOL 中复核跨膜拓扑", "make_tm_topology_review_pml", "临时生成跨膜标注并在 PyMOL 中打开；需要时可保留复核脚本。"),
    ("run_geometry_validation", "geometry_relaxation", "检查并汇总几何", "run_geometry_validation", "在暂存区运行已配置的检查器，并统一保存原生结果、日志、运行信息和机械摘要。"),
    ("summarize_geometry_validation", "geometry_relaxation", "汇总几何检查结果", "summarize_geometry_validation", "从几何检查 JSON 中提取人工指定的数值项。"),
    ("run_restrained_minimization", "geometry_relaxation", "AF2 Amber relax 并复核", "run_restrained_minimization", "按固定的 DeepMind AF2 c77e5d2 / OpenMM 8.2 CPU 协议运行 Amber99SB 局部几何清理：HBonds 约束、非氢原子 10.0 kcal/mol/A^2 restraints、2.39 kcal/mol/nm RMS force tolerance、内层无迭代上限、最多三轮外循环。随后生成数值比较并在 PyMOL 中复核；工具不自动判定 relaxed 结构更好。"),
    ("compare_raw_relaxed", "geometry_relaxation", "对比原始与优化结构", "compare_raw_relaxed", "计算两个结构在指定原子集合上的位移和 RMSD。"),
    ("make_raw_relaxed_review_pml", "geometry_relaxation", "在 PyMOL 中复核优化前后结构", "make_raw_relaxed_review_pml", "临时生成优化前后对照视图并在 PyMOL 中打开；需要时可保留复核脚本。"),
    ("make_ppm_review_pml", "ppm_orientation", "在 PyMOL 中复核 PPM 膜定位", "make_ppm_review_pml", "临时生成膜平面与跨膜区标注并在 PyMOL 中打开；需要时可保留复核脚本。"),
    ("extract_ppm_protein_pdb", "ppm_orientation", "提取 PPM 蛋白结构", "extract_ppm_protein_pdb", "从 PPM 结果中去除 DUM 记录并保留指定蛋白链。"),
    ("report_receptor_chemistry", "chemistry_preparation", "查看受体化学信息", "report_receptor_chemistry", "读取受体 PDB 并列出可观察的化学检查项。"),
    ("report_ligand_chemistry", "chemistry_preparation", "查看配体化学信息", "report_ligand_chemistry", "读取配体 SDF 并列出电荷、键和立体信息。"),
    ("prepare_receptor_pdbqt", "chemistry_preparation", "准备受体 PDBQT", "prepare_receptor_pdbqt", "用 Meeko 生成受体 PDBQT。"),
    ("prepare_ligand_pdbqt", "chemistry_preparation", "准备并核对配体 PDBQT", "prepare_ligand_pdbqt", "用 Meeko 暂存配体 PDBQT，按显式映射核对后同时发布结构与报告。"),
    ("check_sdf_pdbqt_mapping", "chemistry_preparation", "核对 SDF 与 PDBQT 映射", "check_sdf_pdbqt_mapping", "按显式映射文件核对配体转换前后的原子对应。"),
    ("define_vina_box", "vina_docking", "定义 Vina 搜索盒", "define_vina_box", "用人工填写的中心、尺寸和运行参数写出 Vina 配置。"),
    ("generate_vina_server_command", "vina_docking", "生成 Vina 服务器命令", "generate_vina_server_command", "验证服务器路径、搜索盒和运行参数，并把原生服务器 Vina shell 命令写到标准输出。"),
    ("summarize_vina_results", "vina_docking", "汇总 Vina 结果", "summarize_vina_results", "从 Vina 日志和姿势文件提取模式与分数表。"),
    ("export_receptor_pdbqt_to_pdb", "export_lid", "导出受体 PDB", "export_receptor_pdbqt_to_pdb", "把准备好的受体 PDBQT 转为 LID 可用的 PDB。"),
    ("export_ligand_pdbqt_to_sdf", "export_lid", "导出配体 SDF", "export_ligand_pdbqt_to_sdf", "把准备好的配体 PDBQT 转为 LID 可用的 SDF。"),
    ("generate_maestro_lid", "export_lid", "生成 Maestro LID 图", "generate_maestro_lid", "临时转换受体和选定 pose 后，调用 Schrödinger Maestro 生成一张 LID 相互作用图。"),
)

CUSTOM_PANEL_BY_TOOL_ID = {
    "generate_vina_server_command": "vina_server_command",
}


TOOL_INPUT_MODES: dict[str, tuple[InputModePresentation, ...]] = {
    "cif_to_pdb": (
        InputModePresentation(
            "single",
            "单个 CIF 文件",
            ("input_file", "output_file"),
            ("input_file",),
            "选择一个 CIF；可指定单个 PDB 输出文件，留空则写在输入文件旁边。",
        ),
        InputModePresentation(
            "batch",
            "批量 CIF 文件夹",
            ("input_dir", "output_dir", "pattern"),
            ("input_dir",),
            "选择一个文件夹；扫描范围只作用于批量模式，输出文件夹可留空。",
        ),
    ),
    "report_af_confidence": (
        InputModePresentation(
            "single",
            "单个置信度 JSON",
            ("input", "output"),
            ("input",),
            "JSON 格式自动识别；报告输出文件会按输入文件名自动生成，也可修改或清空。",
        ),
        InputModePresentation(
            "batch",
            "批量 JSON 文件夹",
            ("input_dir", "output_dir", "pattern"),
            ("input_dir", "output_dir"),
            "递归识别候选 JSON；每个输入生成独立报告，并汇总成功、跳过与失败。",
        ),
    ),
}

OUTPUT_DERIVATIONS: dict[str, tuple[OutputDerivation, ...]] = {
    "cif_to_pdb": (
        OutputDerivation("output_file", "input_file", "{stem}.pdb"),
        OutputDerivation("output_dir", "input_dir", "{name}", "source_directory"),
    ),
    "report_af_confidence": (
        OutputDerivation("output", "input", "{stem}.confidence-report.json"),
        OutputDerivation("output_dir", "input_dir", "{name}.confidence-reports", "source_sibling"),
    ),
    "make_tm_topology_review_pml": (
        OutputDerivation("output", "topology_source", "{stem}.tm-review.pml"),
    ),
    "run_geometry_validation": (
        OutputDerivation("output_dir", "structure", "{stem}.geometry-validation"),
    ),
    "summarize_geometry_validation": (
        OutputDerivation("output", "input", "{stem}.geometry-summary.json"),
    ),
    "run_restrained_minimization": (
        OutputDerivation("output_structure", "input_structure", "{stem}.af2-amber-relaxed.pdb"),
        OutputDerivation("report_json", "input_structure", "{stem}.af2-amber-relax-report.json"),
        OutputDerivation("comparison_json", "input_structure", "{stem}.raw-vs-af2-relaxed.json"),
        OutputDerivation("review_pml", "input_structure", "{stem}.raw-vs-af2-relaxed.pml"),
    ),
    "compare_raw_relaxed": (
        OutputDerivation("output", "raw", "{stem}.raw-relaxed-comparison.json"),
    ),
    "make_raw_relaxed_review_pml": (
        OutputDerivation("output", "raw", "{stem}.raw-relaxed-review.pml"),
    ),
    "make_ppm_review_pml": (
        OutputDerivation("output", "ppm_pdb", "{stem}.ppm-review.pml"),
    ),
    "extract_ppm_protein_pdb": (
        OutputDerivation("output", "input", "{stem}.protein.pdb"),
    ),
    "prepare_receptor_pdbqt": (
        OutputDerivation("output_pdbqt", "receptor_pdb", "{stem}.pdbqt"),
    ),
    "prepare_ligand_pdbqt": (
        OutputDerivation("output_pdbqt", "ligand_sdf", "{stem}.pdbqt"),
        OutputDerivation(
            "mapping_output", "ligand_sdf", "{stem}.pdbqt-mapping.json"
        ),
    ),
    "check_sdf_pdbqt_mapping": (
        OutputDerivation("output", "sdf", "{stem}.pdbqt-mapping.json"),
    ),
    "define_vina_box": (
        OutputDerivation("output", "receptor", "{stem}.vina-config.txt"),
    ),
    "summarize_vina_results": (
        OutputDerivation("output", "log", "{stem}.vina-summary.json"),
    ),
    "export_receptor_pdbqt_to_pdb": (
        OutputDerivation("output", "input", "{stem}.pdb"),
    ),
    "export_ligand_pdbqt_to_sdf": (
        OutputDerivation("output", "input", "{stem}.sdf"),
    ),
    "generate_maestro_lid": (
        OutputDerivation("output", "receptor", "{stem}.lid.png"),
    ),
}


FIELD_HELP_TEXT: dict[tuple[str, str], str] = {
    ('cif_to_pdb', 'input_file'): '选择单个 .cif 或 .mmcif 文件；切换到批量模式后此字段不会进入命令。',
    ('cif_to_pdb', 'input_dir'): '选择批量 CIF 文件夹；默认扫描根层和任意嵌套层，且不会走出该文件夹。',
    ('cif_to_pdb', 'output_file'): '指定单文件模式的 PDB 输出路径；留空时写在输入 CIF 旁边。',
    ('cif_to_pdb', 'output_dir'): '指定批量 PDB 输出文件夹；留空时写在各 CIF 旁边，是否提供不影响输入发现。',
    ('cif_to_pdb', 'pattern'): "填写相对批量输入文件夹的 glob；默认 **/*.cif，包含根层和任意嵌套层。",
    ('cif_to_pdb', 'overwrite'): '勾选后允许替换同名 PDB；未勾选时保留已有文件并在结果中标记为跳过。',
    ('report_af_confidence', 'input'): '选择单个 AlphaFold/ColabFold 置信度 JSON；工具自动识别受支持的逐残基格式。',
    ('report_af_confidence', 'input_dir'): '选择批量 JSON 文件夹；工具递归检查候选文件并逐项报告成功、跳过或失败原因。',
    ('report_af_confidence', 'input_format'): '专家兼容覆盖：填写带版本的自定义格式来源标签，并同时填写逐残基 pLDDT 位置；这不是输出文件名。',
    ('report_af_confidence', 'plddt_pointer'): '专家兼容覆盖：仅填写已由格式规范确认的逐残基 pLDDT JSON Pointer，并同时填写格式来源；不会猜测。',
    ('report_af_confidence', 'region'): '可选附加区域统计；省略时仍报告完整序列，不需要为了查看置信度手工划区域。',
    ('report_af_confidence', 'pae_pointer'): '专家兼容覆盖：填写与逐残基层级一致的方阵 PAE Pointer；自动模式无需填写。',
    ('report_af_confidence', 'output'): '单文件报告输出路径；自动按输入文件名生成。清空后不创建文件，内容显示在“技术详情 → 标准输出”中。',
    ('report_af_confidence', 'output_dir'): '选择不同于批量输入文件夹的报告输出文件夹；每个输入保留相对层级并使用稳定、无碰撞的报告名。',
    ('report_af_confidence', 'pattern'): '填写相对批量输入文件夹的 glob；默认 **/*.json，包含根层和任意嵌套层。',
    ('report_af_confidence', 'force'): '勾选后允许替换已有置信度报告；未勾选时保留已有文件。',
    ('make_tm_topology_review_pml', 'topology_source'): '选择 DeepTMHMM 或 Phyre 2.2 MEMSAT-SVM 拓扑来源文件；格式默认自动识别。',
    ('make_tm_topology_review_pml', 'fasta'): '选择对应 FASTA，用于核对跨膜区间和结构残基编号。',
    ('make_tm_topology_review_pml', 'structure'): '选择要在 PyMOL 中标注的 PDB 或 mmCIF 结构文件。',
    ('make_tm_topology_review_pml', 'chain'): '填写结构中的蛋白链 ID，脚本只标注这一条链。',
    ('make_tm_topology_review_pml', 'output'): '仅在勾选保留复核脚本时使用；默认由 GUI 写入会话临时目录并直接在 PyMOL 中打开。',
    ('make_tm_topology_review_pml', 'topology_format'): '专家兼容覆盖：仅在自动识别失败但你明确知道来源格式时选择。',
    ('make_tm_topology_review_pml', 'object_name'): 'PyMOL 对象名默认自动使用 receptor；通常无需修改。',
    ('make_tm_topology_review_pml', 'base_color'): '蛋白基础颜色默认由工具提供；仅在调整 PyMOL 显示外观时修改。',
    ('make_tm_topology_review_pml', 'tm_colors'): '跨膜区颜色默认按片段数量生成；仅在需要固定颜色方案时填写逗号分隔列表。',
    ('make_tm_topology_review_pml', 'force'): '勾选后允许替换已有 PyMOL 脚本；未勾选时保留已有文件。',
    ('run_geometry_validation', 'backend'): '自动运行配置中的几何检查程序名称和版本；普通使用不需要填写。',
    ('run_geometry_validation', 'executable'): '自动运行配置中的几何检查程序路径；普通使用不需要填写。',
    ('run_geometry_validation', 'structure'): '选择待提交给几何检查程序的结构文件。',
    ('run_geometry_validation', 'output_dir'): '保存几何检查结果、日志和运行记录的文件夹。',
    ('run_geometry_validation', 'manifest'): '运行记录由工具自动保存为检查结果输出文件夹中的 manifest.json；普通用户无需填写。',
    ('run_geometry_validation', 'arg'): '自动运行配置中的原生检查程序参数；普通使用不需要填写。',
    ('run_geometry_validation', 'native_result'): '安装适配器声明的原生 JSON 相对路径；检查器只在隐藏暂存目录写入该文件。',
    ('run_geometry_validation', 'result_format'): '安装适配器声明的版本化原生 JSON 格式；普通用户无需选择。',
    ('run_geometry_validation', 'metric'): '安装适配器声明的指标名与 JSON Pointer 映射；缺失指标会让摘要失败，不会解释为 0。',
    ('run_geometry_validation', 'metric_unit'): '安装适配器为每个几何指标声明单位；指标名必须与 JSON Pointer 映射逐项一致。',
    ('run_geometry_validation', 'summary_output'): '几何摘要固定保存为检查结果文件夹中的 geometry-summary.json。',
    ('run_geometry_validation', 'force'): '勾选后允许替换本次检查的标准输出、标准错误和运行信息 JSON；未勾选时保留已有文件。',
    ('summarize_geometry_validation', 'input'): '选择几何检查 JSON，汇总器从中提取指定指标。',
    ('summarize_geometry_validation', 'result_format'): '填写几何结果格式，汇总器按该格式解释输入 JSON。',
    ('summarize_geometry_validation', 'metric'): '逐行填写“指标名=/JSON/位置”映射，每一行生成一个输出字段。',
    ('summarize_geometry_validation', 'output'): '指定几何摘要 JSON 的保存位置。',
    ('summarize_geometry_validation', 'force'): '勾选后允许替换已有几何摘要；未勾选时保留已有文件。',
    ('run_restrained_minimization', 'protocol'): '内部固定为 DeepMind AF2 c77e5d2、OpenMM 8.2 CPU 和 Amber99SB 的版本化协议；普通用户不能修改科学参数。',
    ('run_restrained_minimization', 'input_structure'): '选择一个明确的、尚未 relax 的 AF2/ColabFold protein-only PDB；工具不按文件名、rank 或目录自动选择结构。',
    ('run_restrained_minimization', 'output_structure'): '保存 DeepMind AF2 Amber relax 产生的派生 PDB；不会覆盖原始结构。',
    ('run_restrained_minimization', 'report_json'): '保存输入输出哈希、AF2/OpenMM/PDBFixer 版本、力场哈希、固定参数、能量、AF2 内部 RMSD 和剩余 violations。',
    ('run_restrained_minimization', 'comparison_json'): '保存原始结构与 relaxed 结构在统一原子范围上的 RMSD 和最大位移；只作机械比较，不作合格判断。',
    ('run_restrained_minimization', 'review_pml'): '仅在勾选保留复核脚本时使用；默认在会话临时目录生成并直接用 PyMOL 打开。',
    ('run_restrained_minimization', 'review_atom_selection'): '同一个原子范围同时用于 relax 前后数值比较和 PyMOL 对齐：CA 或主链；它不改变 Amber relax 本身的固定 restraints。全部重原子严格比较请使用独立结构对比工具。',
    ('run_restrained_minimization', 'force'): '勾选后允许替换本次 AF2 Amber relax 输出；未勾选时保留已有文件。',
    ('compare_raw_relaxed', 'raw'): '选择优化前结构，用作对照坐标来源。',
    ('compare_raw_relaxed', 'relaxed'): '选择优化后结构，用作比较坐标来源。',
    ('compare_raw_relaxed', 'atom_selection'): '选择用于对齐和位移计算的原子集合。',
    ('compare_raw_relaxed', 'output'): '指定结构对比 JSON 报告保存位置。',
    ('compare_raw_relaxed', 'force'): '勾选后允许替换已有对比报告；未勾选时保留已有文件。',
    ('make_raw_relaxed_review_pml', 'raw'): '选择优化前结构，脚本会把它作为对照对象。',
    ('make_raw_relaxed_review_pml', 'relaxed'): '选择优化后结构，脚本会把它作为比较对象。',
    ('make_raw_relaxed_review_pml', 'raw_object'): '填写原始结构在 PyMOL 脚本中的对象名。',
    ('make_raw_relaxed_review_pml', 'relaxed_object'): '填写优化结构在 PyMOL 脚本中的对象名。',
    ('make_raw_relaxed_review_pml', 'raw_color'): '填写原始结构颜色，生成脚本用它显示对照结构。',
    ('make_raw_relaxed_review_pml', 'relaxed_color'): '填写优化结构颜色，生成脚本用它显示优化后结构。',
    ('make_raw_relaxed_review_pml', 'atom_selection'): '选择对照显示和数值对齐使用的原子集合。',
    ('make_raw_relaxed_review_pml', 'output'): '仅在勾选保留复核脚本时使用；默认由 GUI 写入会话临时目录并直接在 PyMOL 中打开。',
    ('make_raw_relaxed_review_pml', 'force'): '勾选后允许替换已有 PyMOL 脚本；未勾选时保留已有文件。',
    ('make_ppm_review_pml', 'ppm_pdb'): '选择 PPM 输出结构，脚本会从中读取蛋白和 DUM 平面。',
    ('make_ppm_review_pml', 'fasta'): '选择对应 FASTA，用于辅助定位跨膜区。',
    ('make_ppm_review_pml', 'topology_source'): '选择 DeepTMHMM 或 Phyre 2.2 MEMSAT-SVM 原始拓扑来源文件；格式默认自动识别，不需要先生成中间 JSON。',
    ('make_ppm_review_pml', 'topology_json'): '历史兼容入口：仅命令行旧流程使用的已验证中间 JSON；普通 GUI 不再要求选择该中间产物。',
    ('make_ppm_review_pml', 'topology_format'): '专家兼容覆盖：仅在自动识别原始拓扑来源失败但你明确知道格式时选择。',
    ('make_ppm_review_pml', 'chain'): '填写 PPM 结构中的蛋白链 ID，脚本只标注这一条链。',
    ('make_ppm_review_pml', 'object_name'): 'PyMOL 对象名默认由工具提供；普通使用不需要修改。',
    ('make_ppm_review_pml', 'base_color'): '填写蛋白基础颜色名，脚本用它显示主体结构。',
    ('make_ppm_review_pml', 'tm_colors'): '填写跨膜区颜色序列，脚本按顺序标注跨膜片段。',
    ('make_ppm_review_pml', 'z_low_color'): '填写下侧 DUM 膜平面颜色，脚本用它显示低 Z 平面。',
    ('make_ppm_review_pml', 'z_high_color'): '填写上侧 DUM 膜平面颜色，脚本用它显示高 Z 平面。',
    ('make_ppm_review_pml', 'output'): '仅在勾选保留复核脚本时使用；默认由 GUI 写入会话临时目录并直接在 PyMOL 中打开。',
    ('make_ppm_review_pml', 'force'): '勾选后允许替换已有 PyMOL 脚本；未勾选时保留已有文件。',
    ('extract_ppm_protein_pdb', 'input'): '选择 PPM 输入结构，提取器会从中移除 DUM 记录。',
    ('extract_ppm_protein_pdb', 'chain'): '填写要保留的蛋白链 ID，提取时会删除其它链和 DUM 记录。',
    ('extract_ppm_protein_pdb', 'output'): '指定提取后的蛋白 PDB 保存位置。',
    ('extract_ppm_protein_pdb', 'force'): '勾选后允许替换已有蛋白 PDB；未勾选时保留已有文件。',
    ('report_receptor_chemistry', 'receptor_pdb'): '选择受体 PDB，报告器从 ATOM 和 HETATM 记录读取可观察项。',
    ('report_receptor_chemistry', 'format'): 'GUI 固定读取 JSON 标准输出，再生成会话临时 HTML 与 PML；该内部格式不需要用户选择。',
    ('report_receptor_chemistry', 'output'): 'GUI 不向底层报告器传入输出路径；人工检查材料由 GUI 写入会话临时目录。',
    ('report_receptor_chemistry', 'overwrite'): 'GUI 不生成持久化化学报告，因此不会覆盖报告文件。',
    ('report_receptor_chemistry', 'pocket_ligand'): '可选。用受体 PDB 里已有的异源组分（如共晶配体）锚定结合位点，检查页只列其邻近的可离子化残基；不填则列全结构。',
    ('report_receptor_chemistry', 'pocket_center'): '可选。用 X,Y,Z 坐标锚定结合位点，与锚定组分二选一；不填则列全结构。',
    ('report_receptor_chemistry', 'pocket_radius'): '口袋邻近半径，默认 5 Å；只有填写了锚定组分或锚定坐标时生效。',
    ('report_ligand_chemistry', 'ligand_sdf'): '选择配体 SDF，报告器从分子记录读取电荷、键和立体信息。',
    ('report_ligand_chemistry', 'format'): 'GUI 固定读取 JSON 标准输出，再生成会话临时 HTML 与 PML；该内部格式不需要用户选择。',
    ('report_ligand_chemistry', 'output'): 'GUI 不向底层报告器传入输出路径；人工检查材料由 GUI 写入会话临时目录。',
    ('report_ligand_chemistry', 'overwrite'): 'GUI 不生成持久化化学报告，因此不会覆盖报告文件。',
    ('prepare_receptor_pdbqt', 'receptor_pdb'): '选择已人工确认化学状态的受体 PDB。',
    ('prepare_receptor_pdbqt', 'output_pdbqt'): '指定受体 PDBQT 输出路径。',
    ('prepare_receptor_pdbqt', 'meeko_executable'): '填写可从 PATH 查找的程序名或可执行文件路径；若使用 Python，需在 Meeko 启动项中保留明确入口。',
    ('prepare_receptor_pdbqt', 'meeko_entrypoint'): '逐行填写 Meeko 启动项，用于组合模块或脚本入口。',
    ('prepare_receptor_pdbqt', 'input_flag'): '填写 Meeko 接收受体 PDB 的选项名。',
    ('prepare_receptor_pdbqt', 'output_flag'): '填写 Meeko 写出受体 PDBQT 的选项名。',
    ('prepare_receptor_pdbqt', 'charge_model'): '选择 Meeko 计算受体原子部分电荷时使用的模型。',
    ('prepare_receptor_pdbqt', 'meeko_arg'): '逐行填写额外 Meeko 参数，每个非空行作为一个独立参数传入；空行忽略。',
    ('prepare_receptor_pdbqt', 'overwrite'): '勾选后允许替换已有受体 PDBQT；未勾选时保留已有文件。',
    ('prepare_ligand_pdbqt', 'ligand_sdf'): '选择已人工确认微观态的配体 SDF。',
    ('prepare_ligand_pdbqt', 'output_pdbqt'): '指定配体 PDBQT 输出路径。',
    ('prepare_ligand_pdbqt', 'atom_map'): '选择独立准备的显式原子映射 JSON；GUI 不会从 Meeko 输出反推或自动猜测映射。',
    ('prepare_ligand_pdbqt', 'mapping_output'): '指定映射核对报告；只有核对无差异时，它才会与配体 PDBQT 一起发布。',
    ('prepare_ligand_pdbqt', 'coordinate_tolerance'): '填写映射坐标容差；超过该距离会阻止 PDBQT 和报告进入正式输出路径。',
    ('prepare_ligand_pdbqt', 'meeko_executable'): '填写可从 PATH 查找的程序名或可执行文件路径；若使用 Python，需在 Meeko 启动项中保留明确入口。',
    ('prepare_ligand_pdbqt', 'meeko_entrypoint'): '逐行填写 Meeko 启动项，用于组合模块或脚本入口。',
    ('prepare_ligand_pdbqt', 'input_flag'): '填写 Meeko 接收配体 SDF 的选项名。',
    ('prepare_ligand_pdbqt', 'output_flag'): '填写 Meeko 写出配体 PDBQT 的选项名。',
    ('prepare_ligand_pdbqt', 'charge_model'): '选择 Meeko 计算配体原子部分电荷时使用的模型。',
    ('prepare_ligand_pdbqt', 'meeko_arg'): '逐行填写额外 Meeko 参数，每个非空行作为一个独立参数传入；空行忽略。',
    ('prepare_ligand_pdbqt', 'overwrite'): '勾选后允许成组替换配体 PDBQT 与映射报告；未勾选时保留已有文件。',
    ('check_sdf_pdbqt_mapping', 'sdf'): '选择转换前的配体 SDF，核对器按它读取原始原子顺序。',
    ('check_sdf_pdbqt_mapping', 'pdbqt'): '选择准备后的 PDBQT，核对器按它读取转换后记录。',
    ('check_sdf_pdbqt_mapping', 'atom_map'): '选择显式原子映射 JSON，核对器按该映射配对原子。',
    ('check_sdf_pdbqt_mapping', 'coordinate_tolerance'): '填写坐标距离容差，核对器用它标记映射偏差。',
    ('check_sdf_pdbqt_mapping', 'output'): '指定映射核对报告输出文件；留空时不创建文件，内容显示在“技术详情 → 标准输出”中。',
    ('check_sdf_pdbqt_mapping', 'overwrite'): '勾选后允许替换已有报告；未勾选时保留已有文件。',
    ('define_vina_box', 'receptor'): '选择受体 PDBQT，用于写入 Vina 配置中的受体路径。',
    ('define_vina_box', 'ligand'): '选择配体 PDBQT，用于写入 Vina 配置中的配体路径。',
    ('define_vina_box', 'center_x'): '填写搜索盒中心 X 坐标数值。',
    ('define_vina_box', 'center_y'): '填写搜索盒中心 Y 坐标数值。',
    ('define_vina_box', 'center_z'): '填写搜索盒中心 Z 坐标数值。',
    ('define_vina_box', 'size_x'): '填写搜索盒 X 方向尺寸数值。',
    ('define_vina_box', 'size_y'): '填写搜索盒 Y 方向尺寸数值。',
    ('define_vina_box', 'size_z'): '填写搜索盒 Z 方向尺寸数值。',
    ('define_vina_box', 'exhaustiveness'): '填写 Vina 搜索强度，配置文件会写入该数值。',
    ('define_vina_box', 'num_modes'): '填写保留姿势数量，配置文件会写入该数值。',
    ('define_vina_box', 'energy_range'): '填写能量窗口，配置文件会写入该数值。',
    ('define_vina_box', 'seed'): '填写随机种子，配置文件会写入该数值。',
    ('define_vina_box', 'output'): '指定 Vina 配置文件保存位置。',
    ('define_vina_box', 'force'): '勾选后允许替换已有配置；未勾选时保留已有文件。',
    ('generate_vina_server_command', 'server_workdir'): '填写服务器上本次运行的绝对工作目录；命令会先进入该目录。',
    ('generate_vina_server_command', 'vina_executable'): '填写服务器上 Vina 可执行文件的绝对路径；默认值来自独立命令生成器。',
    ('generate_vina_server_command', 'receptor'): '填写服务器上的受体 PDBQT，可使用相对工作目录路径或绝对路径。',
    ('generate_vina_server_command', 'ligand'): '填写服务器上的配体 PDBQT，可使用相对工作目录路径或绝对路径。',
    ('generate_vina_server_command', 'center_x'): '填写搜索盒中心 X；按原始文本验证并传给 Vina，不舍入。',
    ('generate_vina_server_command', 'center_y'): '填写搜索盒中心 Y；按原始文本验证并传给 Vina，不舍入。',
    ('generate_vina_server_command', 'center_z'): '填写搜索盒中心 Z；按原始文本验证并传给 Vina，不舍入。',
    ('generate_vina_server_command', 'size_x'): '填写大于零的搜索盒 X 尺寸；按原始文本传给 Vina。',
    ('generate_vina_server_command', 'size_y'): '填写大于零的搜索盒 Y 尺寸；按原始文本传给 Vina。',
    ('generate_vina_server_command', 'size_z'): '填写大于零的搜索盒 Z 尺寸；按原始文本传给 Vina。',
    ('generate_vina_server_command', 'cpu'): '填写大于零的 Vina CPU 线程数。',
    ('generate_vina_server_command', 'exhaustiveness'): '填写大于零的 Vina 搜索强度。',
    ('generate_vina_server_command', 'num_modes'): '填写大于零的保留姿势数量。',
    ('generate_vina_server_command', 'energy_range'): '填写大于零的 Vina 能量窗口。',
    ('generate_vina_server_command', 'seed'): '填写 Vina 整数随机种子。',
    ('generate_vina_server_command', 'pose_output'): '填写服务器上的 pose PDBQT 输出路径；输出目录必须预先存在。',
    ('generate_vina_server_command', 'log_output'): '填写服务器上的日志输出路径；不得与 pose 输出指向同一路径。',
    ('summarize_vina_results', 'log'): '选择 Vina 日志，汇总器从中读取模式和分数表。',
    ('summarize_vina_results', 'pose'): '选择对接姿势 PDBQT，汇总器从中读取模式记录。',
    ('summarize_vina_results', 'format'): '选择 Vina 日志格式，汇总器按该格式读取分数表。',
    ('summarize_vina_results', 'output'): '指定 Vina 结果摘要 JSON 保存位置。',
    ('summarize_vina_results', 'force'): '勾选后允许替换已有结果摘要；未勾选时保留已有文件。',
    ('export_receptor_pdbqt_to_pdb', 'input'): '选择受体 PDBQT，导出器从中读取受体坐标记录。',
    ('export_receptor_pdbqt_to_pdb', 'output'): '指定导出的受体 PDB 保存位置。',
    ('export_receptor_pdbqt_to_pdb', 'overwrite'): '勾选后允许替换已有受体 PDB；未勾选时保留已有文件。',
    ('export_ligand_pdbqt_to_sdf', 'input'): '选择配体 PDBQT，导出器从中读取配体记录。',
    ('export_ligand_pdbqt_to_sdf', 'output'): '指定导出的配体 SDF 保存位置。',
    ('export_ligand_pdbqt_to_sdf', 'meeko_python'): '选择带 Meeko 和 RDKit 的 Python，用于执行配体格式导出。',
    ('export_ligand_pdbqt_to_sdf', 'overwrite'): '勾选后允许替换已有配体 SDF；未勾选时保留已有文件。',
    ('generate_maestro_lid', 'schrodinger_run'): '选择 Schrödinger run 程序，用于启动 Maestro LID 导出。',
    ('generate_maestro_lid', 'meeko_python'): '自动使用同时提供 Meeko 与 RDKit 的 Docking Python，把选定 pose 临时恢复为 SDF。',
    ('generate_maestro_lid', 'receptor'): '选择受体 PDBQT；GUI 会在临时目录转为 PDB，也兼容已经准备好的 PDB。',
    ('generate_maestro_lid', 'ligand'): '选择包含一个或多个 Vina pose 的 PDBQT；GUI 会先识别数量，再只把所选 pose 临时恢复为 SDF。也兼容已经准备好的 SDF。',
    ('generate_maestro_lid', 'output'): '默认按“受体名-配体名-pose序号.png”保存到配体文件旁；也可自行选择其他位置或图片格式。',
    ('generate_maestro_lid', 'receptor_index'): '填写受体结构序号，用于选择 Maestro 会话中的受体条目。',
    ('generate_maestro_lid', 'ligand_index'): '选择要绘图的 pose 序号。PDBQT 的可选范围会在选中文件后自动识别；已准备的 SDF 则按内部结构位置读取。',
    ('generate_maestro_lid', 'export_width'): '填写图片最大宽度，导出图片时使用该像素上限。',
    ('generate_maestro_lid', 'export_height'): '填写图片最大高度，导出图片时使用该像素上限。',
    ('generate_maestro_lid', 'bond_labels'): '勾选后在 LID 图中显示键标签。',
    ('generate_maestro_lid', 'salt_bridges'): '勾选后在 LID 图中显示盐桥标注。',
    ('generate_maestro_lid', 'h_bonds'): '勾选后在 LID 图中显示氢键标注。',
    ('generate_maestro_lid', 'pi_pi'): '勾选后在 LID 图中显示 π-π 相互作用标注。',
    ('generate_maestro_lid', 'pi_cation'): '勾选后在 LID 图中显示 π-阳离子相互作用标注。',
    ('generate_maestro_lid', 'overwrite'): '勾选后允许替换已有 LID 图片；未勾选时保留已有文件。',
}


def _field_help(module: str, dest: str) -> str:
    try:
        return FIELD_HELP_TEXT[(module, dest)]
    except KeyError as exc:
        raise ValueError(f"missing explicit field help for {module}.{dest}") from exc


ADVANCED_FIELD_KEYS = {
    ("report_af_confidence", "input_format"),
    ("report_af_confidence", "plddt_pointer"),
    ("report_af_confidence", "pae_pointer"),
    ("report_af_confidence", "region"),
    ("make_tm_topology_review_pml", "topology_format"),
    ("make_tm_topology_review_pml", "object_name"),
    ("make_tm_topology_review_pml", "base_color"),
    ("make_tm_topology_review_pml", "tm_colors"),
    ("run_geometry_validation", "backend"),
    ("run_geometry_validation", "executable"),
    ("run_geometry_validation", "arg"),
    ("run_geometry_validation", "manifest"),
    ("run_geometry_validation", "native_result"),
    ("run_geometry_validation", "result_format"),
    ("run_geometry_validation", "metric"),
    ("run_geometry_validation", "metric_unit"),
    ("run_geometry_validation", "summary_output"),
    ("make_raw_relaxed_review_pml", "raw_color"),
    ("make_raw_relaxed_review_pml", "relaxed_color"),
    ("make_raw_relaxed_review_pml", "atom_selection"),
    ("make_ppm_review_pml", "topology_format"),
    ("make_ppm_review_pml", "object_name"),
    ("make_ppm_review_pml", "base_color"),
    ("make_ppm_review_pml", "tm_colors"),
    ("make_ppm_review_pml", "z_low_color"),
    ("make_ppm_review_pml", "z_high_color"),
    ("prepare_receptor_pdbqt", "meeko_executable"),
    ("prepare_receptor_pdbqt", "meeko_entrypoint"),
    ("prepare_receptor_pdbqt", "input_flag"),
    ("prepare_receptor_pdbqt", "output_flag"),
    ("prepare_ligand_pdbqt", "meeko_executable"),
    ("prepare_ligand_pdbqt", "meeko_entrypoint"),
    ("prepare_ligand_pdbqt", "input_flag"),
    ("prepare_ligand_pdbqt", "output_flag"),
    ("prepare_receptor_pdbqt", "meeko_arg"),
    ("prepare_receptor_pdbqt", "charge_model"),
    ("prepare_ligand_pdbqt", "meeko_arg"),
    ("prepare_ligand_pdbqt", "charge_model"),
    ("define_vina_box", "exhaustiveness"),
    ("define_vina_box", "num_modes"),
    ("define_vina_box", "energy_range"),
    ("define_vina_box", "seed"),
    ("generate_maestro_lid", "receptor_index"),
    ("generate_maestro_lid", "export_width"),
    ("generate_maestro_lid", "export_height"),
    ("generate_maestro_lid", "bond_labels"),
    ("generate_maestro_lid", "salt_bridges"),
    ("generate_maestro_lid", "h_bonds"),
    ("generate_maestro_lid", "pi_pi"),
    ("generate_maestro_lid", "pi_cation"),
}

def fr(
    module: str,
    dest: str,
    label: str,
    section: str,
    control: str,
    *,
    unit: str = "",
    unit_source: str = "",
    minimum: float | int | None = None,
    maximum: float | int | None = None,
    range_source: str = "",
    step: float | int | None = None,
    step_source: str = "",
    path_kind: str = "",
    file_filter: str = "",
    default_suffix: str = "",
    placeholder: str = "",
    value_source: str = "user",
    value_key: str = "",
    preset: Any = None,
) -> tuple[str, str, FieldPresentation]:
    section = "高级参数" if (module, dest) in ADVANCED_FIELD_KEYS else section
    return (
        module,
        dest,
        fp(
            label,
            _field_help(module, dest),
            section,
            control,
            unit=unit,
            unit_source=unit_source,
            minimum=minimum,
            maximum=maximum,
            range_source=range_source,
            step=step,
            step_source=step_source,
            path_kind=path_kind,
            file_filter=file_filter,
            default_suffix=default_suffix,
            dialog_title=(f"保存{label}" if path_kind == "save" else f"选择{label}") if path_kind else "",
            placeholder=placeholder,
            value_source=value_source,
            value_key=value_key,
            preset=preset,
        ),
    )


PDB = "PDB (*.pdb);;所有文件 (*)"
PDBQT = "PDBQT (*.pdbqt);;所有文件 (*)"
PDBQT_OR_PDB = "受体结构 (*.pdbqt *.pdb);;所有文件 (*)"
SDF = "SDF (*.sdf *.sd);;所有文件 (*)"
PDBQT_OR_SDF = "配体 pose (*.pdbqt *.sdf *.sd);;所有文件 (*)"
SDF_STRICT = "SDF (*.sdf);;所有文件 (*)"
JSON = "JSON (*.json);;所有文件 (*)"
PML = "PyMOL 脚本 (*.pml);;所有文件 (*)"
MMCIF = "mmCIF (*.cif *.mmcif);;所有文件 (*)"
STRUCTURE = "结构文件 (*.pdb *.ent *.cif *.mmcif);;所有文件 (*)"
ANY = "所有文件 (*)"
DIR = "文件夹"

FIELD_PRESENTATION_ROWS: tuple[tuple[str, str, FieldPresentation], ...] = (
    fr("cif_to_pdb", "input_file", "单个 CIF 文件", "输入", "path", path_kind="open", file_filter=MMCIF),
    fr("cif_to_pdb", "input_dir", "批量 CIF 文件夹", "输入", "path", path_kind="directory", file_filter=DIR),
    fr("cif_to_pdb", "output_file", "单个 PDB 输出文件", "输出", "path", path_kind="save", file_filter=PDB, default_suffix=".pdb"),
    fr("cif_to_pdb", "output_dir", "批量 PDB 输出文件夹", "输出", "path", path_kind="directory", file_filter=DIR),
    fr("cif_to_pdb", "pattern", "扫描范围", "高级参数", "text", placeholder="例如：**/*.cif"),
    fr("cif_to_pdb", "overwrite", "允许覆盖已有 PDB", "输出", "checkbox"),
    fr("report_af_confidence", "input", "单个置信度 JSON", "输入", "path", path_kind="open", file_filter=JSON),
    fr("report_af_confidence", "input_dir", "批量 JSON 文件夹", "输入", "path", path_kind="directory", file_filter=DIR),
    fr("report_af_confidence", "input_format", "JSON 解析格式覆盖（专家）", "高级参数", "text", placeholder="例如：custom-confidence-json-v1"),
    fr("report_af_confidence", "plddt_pointer", "逐残基 pLDDT 位置覆盖（专家）", "高级参数", "text", placeholder="例如：/model/plddt"),
    fr("report_af_confidence", "region", "附加区域统计（可选）", "科学参数", "repeat", placeholder="例如：tm1:1-20"),
    fr("report_af_confidence", "pae_pointer", "PAE 位置覆盖（专家）", "高级参数", "text", placeholder="例如：/model/pae"),
    fr("report_af_confidence", "output", "置信度报告输出文件", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("report_af_confidence", "output_dir", "批量报告输出文件夹", "输出", "path", path_kind="directory", file_filter=DIR),
    fr("report_af_confidence", "pattern", "JSON 扫描范围", "高级参数", "text", placeholder="例如：**/*.json"),
    fr("report_af_confidence", "force", "允许覆盖报告", "输出", "checkbox"),
    fr("make_tm_topology_review_pml", "topology_source", "拓扑来源文件", "输入", "path", path_kind="open", file_filter="拓扑文件 (*.gff3 *.txt *.memsat_svm);;所有文件 (*)"),
    fr("make_tm_topology_review_pml", "fasta", "对应 FASTA", "输入", "path", path_kind="open", file_filter="FASTA (*.fasta *.fa);;所有文件 (*)"),
    fr("make_tm_topology_review_pml", "structure", "结构文件", "输入", "path", path_kind="open", file_filter=STRUCTURE),
    fr("make_tm_topology_review_pml", "chain", "蛋白链 ID", "输入", "text"),
    fr("make_tm_topology_review_pml", "output", "PyMOL 复核脚本输出文件", "输出", "path", path_kind="save", file_filter=PML, default_suffix=".pml"),
    fr("make_tm_topology_review_pml", "topology_format", "拓扑来源格式覆盖（专家）", "高级参数", "choice"),
    fr("make_tm_topology_review_pml", "object_name", "PyMOL 对象名", "高级参数", "text", value_source="fixed"),
    fr("make_tm_topology_review_pml", "base_color", "蛋白基础颜色", "高级参数", "text"),
    fr("make_tm_topology_review_pml", "tm_colors", "跨膜区颜色", "高级参数", "text"),
    fr("make_tm_topology_review_pml", "force", "允许覆盖脚本", "输出", "checkbox"),
    fr("run_geometry_validation", "backend", "检查程序名称", "运行环境与兼容性", "text", value_source="runtime", value_key="DOCKING_GEOMETRY_BACKEND"),
    fr("run_geometry_validation", "executable", "检查程序", "运行环境与兼容性", "path", path_kind="open", file_filter=ANY, value_source="runtime", value_key="DOCKING_GEOMETRY_EXECUTABLE"),
    fr("run_geometry_validation", "structure", "待检查结构", "输入", "path", path_kind="open", file_filter=STRUCTURE),
    fr("run_geometry_validation", "output_dir", "检查结果输出文件夹", "输出", "path", path_kind="directory", file_filter=DIR),
    fr("run_geometry_validation", "manifest", "运行信息 JSON 输出文件", "高级参数", "path", path_kind="save", file_filter=JSON, default_suffix=".json", value_source="fixed"),
    fr("run_geometry_validation", "arg", "检查程序参数", "运行参数", "repeat", value_source="runtime", value_key="DOCKING_GEOMETRY_ARGS"),
    fr("run_geometry_validation", "native_result", "原生结果相对路径", "运行环境与兼容性", "text", value_source="runtime", value_key="DOCKING_GEOMETRY_NATIVE_RESULT"),
    fr("run_geometry_validation", "result_format", "原生结果解析格式", "运行环境与兼容性", "text", value_source="fixed"),
    fr("run_geometry_validation", "metric", "已配置的几何指标", "运行环境与兼容性", "repeat", value_source="runtime", value_key="DOCKING_GEOMETRY_METRICS"),
    fr("run_geometry_validation", "metric_unit", "已配置的指标单位", "运行环境与兼容性", "repeat", value_source="runtime", value_key="DOCKING_GEOMETRY_METRIC_UNITS"),
    fr("run_geometry_validation", "summary_output", "几何摘要输出文件", "高级参数", "path", path_kind="save", file_filter=JSON, default_suffix=".json", value_source="fixed"),
    fr("run_geometry_validation", "force", "允许覆盖检查结果", "输出", "checkbox"),
    fr("summarize_geometry_validation", "input", "几何检查 JSON", "输入", "path", path_kind="open", file_filter=JSON),
    fr("summarize_geometry_validation", "result_format", "几何结果解析格式", "输入", "text", value_source="fixed"),
    fr("summarize_geometry_validation", "metric", "已配置的几何指标", "科学参数", "repeat", value_source="runtime", value_key="geometry_metrics"),
    fr("summarize_geometry_validation", "output", "几何摘要输出文件", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("summarize_geometry_validation", "force", "允许覆盖几何摘要", "输出", "checkbox"),
    fr("run_restrained_minimization", "protocol", "固定 AF2 Amber relax 协议", "运行环境与兼容性", "text", value_source="fixed", preset=AF2_AMBER_RELAX_PROTOCOL_ID),
    fr("run_restrained_minimization", "input_structure", "输入 PDB 结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("run_restrained_minimization", "output_structure", "AF2 Amber relaxed PDB", "输出", "path", path_kind="save", file_filter=PDB, default_suffix=".pdb"),
    fr("run_restrained_minimization", "report_json", "AF2 Amber relax 报告", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("run_restrained_minimization", "comparison_json", "relax 前后数值比较", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("run_restrained_minimization", "review_pml", "PyMOL 复核脚本输出文件", "输出", "path", path_kind="save", file_filter=PML, default_suffix=".pml"),
    fr("run_restrained_minimization", "review_atom_selection", "复核原子范围", "科学参数", "choice"),
    fr("run_restrained_minimization", "force", "允许覆盖最小化输出", "输出", "checkbox"),
    fr("compare_raw_relaxed", "raw", "原始结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("compare_raw_relaxed", "relaxed", "优化后结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("compare_raw_relaxed", "atom_selection", "对齐原子集合", "科学参数", "choice"),
    fr("compare_raw_relaxed", "output", "数值对比报告输出文件", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("compare_raw_relaxed", "force", "允许覆盖对比报告", "输出", "checkbox"),
    fr("make_raw_relaxed_review_pml", "raw", "原始结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("make_raw_relaxed_review_pml", "relaxed", "优化后结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("make_raw_relaxed_review_pml", "raw_object", "原始结构对象名", "显示设置", "text", value_source="fixed"),
    fr("make_raw_relaxed_review_pml", "relaxed_object", "优化结构对象名", "显示设置", "text", value_source="fixed"),
    fr("make_raw_relaxed_review_pml", "raw_color", "原始结构颜色", "显示设置", "text"),
    fr("make_raw_relaxed_review_pml", "relaxed_color", "优化结构颜色", "显示设置", "text"),
    fr("make_raw_relaxed_review_pml", "atom_selection", "对齐原子集合", "科学参数", "choice"),
    fr("make_raw_relaxed_review_pml", "output", "PyMOL 复核脚本输出文件", "输出", "path", path_kind="save", file_filter=PML, default_suffix=".pml"),
    fr("make_raw_relaxed_review_pml", "force", "允许覆盖脚本", "输出", "checkbox"),
    fr("make_ppm_review_pml", "ppm_pdb", "PPM 结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("make_ppm_review_pml", "fasta", "对应 FASTA", "输入", "path", path_kind="open", file_filter="FASTA (*.fasta *.fa);;所有文件 (*)"),
    fr("make_ppm_review_pml", "chain", "蛋白链 ID", "输入", "text"),
    fr("make_ppm_review_pml", "topology_source", "拓扑来源文件", "输入", "path", path_kind="open", file_filter="拓扑文件 (*.gff3 *.txt *.memsat_svm);;所有文件 (*)"),
    fr("make_ppm_review_pml", "topology_json", "拓扑 JSON（旧命令行兼容）", "高级参数", "path", path_kind="open", file_filter=JSON, value_source="fixed"),
    fr("make_ppm_review_pml", "topology_format", "拓扑来源格式覆盖（专家）", "高级参数", "choice"),
    fr("make_ppm_review_pml", "object_name", "PyMOL 对象名", "高级参数", "text", value_source="fixed"),
    fr("make_ppm_review_pml", "base_color", "蛋白基础颜色", "显示设置", "text"),
    fr("make_ppm_review_pml", "tm_colors", "跨膜区颜色", "显示设置", "text"),
    fr("make_ppm_review_pml", "z_low_color", "下侧膜平面颜色", "显示设置", "text"),
    fr("make_ppm_review_pml", "z_high_color", "上侧膜平面颜色", "显示设置", "text"),
    fr("make_ppm_review_pml", "output", "PyMOL 复核脚本输出文件", "输出", "path", path_kind="save", file_filter=PML, default_suffix=".pml"),
    fr("make_ppm_review_pml", "force", "允许覆盖脚本", "输出", "checkbox"),
    fr("extract_ppm_protein_pdb", "input", "PPM 输入结构", "输入", "path", path_kind="open", file_filter=PDB),
    fr("extract_ppm_protein_pdb", "chain", "保留链 ID", "科学参数", "text"),
    fr("extract_ppm_protein_pdb", "output", "蛋白 PDB 输出文件", "输出", "path", path_kind="save", file_filter=PDB, default_suffix=".pdb"),
    fr("extract_ppm_protein_pdb", "force", "允许覆盖蛋白 PDB", "输出", "checkbox"),
    fr("report_receptor_chemistry", "receptor_pdb", "受体 PDB", "输入", "path", path_kind="open", file_filter=PDB),
    fr("report_receptor_chemistry", "format", "内部报告格式", "输出", "choice", value_source="fixed", preset="json"),
    fr("report_receptor_chemistry", "output", "内部报告输出文件", "输出", "path", value_source="fixed"),
    fr("report_receptor_chemistry", "overwrite", "内部覆盖开关", "输出", "checkbox", value_source="fixed"),
    fr("report_receptor_chemistry", "pocket_ligand", "口袋锚定组分", "科学参数", "text", placeholder="例如：A:STI:1（异源组分表里的 ID）"),
    fr("report_receptor_chemistry", "pocket_center", "口袋锚定坐标", "科学参数", "text", placeholder="例如：12.5,-3.0,44.25"),
    fr("report_receptor_chemistry", "pocket_radius", "口袋邻近半径", "科学参数", "number_float", unit="Angstrom", unit_source="argparse:report_receptor_chemistry:pocket_radius"),
    fr("report_ligand_chemistry", "ligand_sdf", "配体 SDF", "输入", "path", path_kind="open", file_filter=SDF),
    fr("report_ligand_chemistry", "format", "内部报告格式", "输出", "choice", value_source="fixed", preset="json"),
    fr("report_ligand_chemistry", "output", "内部报告输出文件", "输出", "path", value_source="fixed"),
    fr("report_ligand_chemistry", "overwrite", "内部覆盖开关", "输出", "checkbox", value_source="fixed"),
    fr("prepare_receptor_pdbqt", "receptor_pdb", "确认后的受体 PDB", "输入", "path", path_kind="open", file_filter=PDB),
    fr("prepare_receptor_pdbqt", "output_pdbqt", "受体 PDBQT 输出文件", "输出", "path", path_kind="save", file_filter=PDBQT, default_suffix=".pdbqt"),
    fr("prepare_receptor_pdbqt", "meeko_executable", "Meeko 启动命令", "运行环境与兼容性", "text", value_source="runtime", value_key="DOCKING_MEEKO_RECEPTOR_EXECUTABLE"),
    fr("prepare_receptor_pdbqt", "meeko_entrypoint", "Meeko 启动项", "高级参数", "repeat", value_source="fixed"),
    fr("prepare_receptor_pdbqt", "input_flag", "Meeko 输入选项", "高级参数", "text", value_source="fixed"),
    fr("prepare_receptor_pdbqt", "output_flag", "Meeko 输出选项", "高级参数", "text", value_source="fixed"),
    fr("prepare_receptor_pdbqt", "charge_model", "电荷模型", "科学参数", "choice"),
    fr("prepare_receptor_pdbqt", "meeko_arg", "额外 Meeko 参数", "高级参数", "repeat", value_source="fixed"),
    fr("prepare_receptor_pdbqt", "overwrite", "允许覆盖受体 PDBQT", "输出", "checkbox"),
    fr("prepare_ligand_pdbqt", "ligand_sdf", "确认后的配体 SDF", "输入", "path", path_kind="open", file_filter=SDF_STRICT),
    fr("prepare_ligand_pdbqt", "output_pdbqt", "配体 PDBQT 输出文件", "输出", "path", path_kind="save", file_filter=PDBQT, default_suffix=".pdbqt"),
    fr("prepare_ligand_pdbqt", "atom_map", "显式原子映射 JSON", "输入", "path", path_kind="open", file_filter=JSON),
    fr("prepare_ligand_pdbqt", "mapping_output", "映射核对报告输出文件", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("prepare_ligand_pdbqt", "coordinate_tolerance", "坐标容差", "科学参数", "number_float", unit="Angstrom", unit_source="argparse:prepare_ligand_pdbqt:coordinate_tolerance"),
    fr("prepare_ligand_pdbqt", "meeko_executable", "Meeko 启动命令", "运行环境与兼容性", "text", value_source="runtime", value_key="DOCKING_MEEKO_LIGAND_EXECUTABLE"),
    fr("prepare_ligand_pdbqt", "meeko_entrypoint", "Meeko 启动项", "高级参数", "repeat", value_source="fixed"),
    fr("prepare_ligand_pdbqt", "input_flag", "Meeko 输入选项", "高级参数", "text", value_source="fixed"),
    fr("prepare_ligand_pdbqt", "output_flag", "Meeko 输出选项", "高级参数", "text", value_source="fixed"),
    fr("prepare_ligand_pdbqt", "charge_model", "电荷模型", "科学参数", "choice"),
    fr("prepare_ligand_pdbqt", "meeko_arg", "额外 Meeko 参数", "高级参数", "repeat", value_source="fixed"),
    fr("prepare_ligand_pdbqt", "overwrite", "允许覆盖配体 PDBQT", "输出", "checkbox"),
    fr("check_sdf_pdbqt_mapping", "sdf", "原始配体 SDF", "输入", "path", path_kind="open", file_filter=SDF),
    fr("check_sdf_pdbqt_mapping", "pdbqt", "准备后的 PDBQT", "输入", "path", path_kind="open", file_filter=PDBQT),
    fr("check_sdf_pdbqt_mapping", "atom_map", "原子映射 JSON", "输入", "path", path_kind="open", file_filter=JSON),
    fr("check_sdf_pdbqt_mapping", "coordinate_tolerance", "坐标容差", "科学参数", "number_float", unit="Angstrom", unit_source="argparse:check_sdf_pdbqt_mapping:coordinate_tolerance"),
    fr("check_sdf_pdbqt_mapping", "output", "映射核对报告输出文件", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("check_sdf_pdbqt_mapping", "overwrite", "允许覆盖报告", "输出", "checkbox"),
    fr("define_vina_box", "receptor", "受体 PDBQT", "输入", "path", path_kind="open", file_filter=PDBQT),
    fr("define_vina_box", "ligand", "配体 PDBQT", "输入", "path", path_kind="open", file_filter=PDBQT),
    fr("define_vina_box", "center_x", "搜索盒中心 X", "搜索盒", "number_float", unit="Angstrom", unit_source="argparse:define_vina_box:center_x"),
    fr("define_vina_box", "center_y", "搜索盒中心 Y", "搜索盒", "number_float", unit="Angstrom", unit_source="argparse:define_vina_box:center_y"),
    fr("define_vina_box", "center_z", "搜索盒中心 Z", "搜索盒", "number_float", unit="Angstrom", unit_source="argparse:define_vina_box:center_z"),
    fr("define_vina_box", "size_x", "搜索盒尺寸 X", "搜索盒", "number_float", unit="Angstrom", unit_source="argparse:define_vina_box:size_x"),
    fr("define_vina_box", "size_y", "搜索盒尺寸 Y", "搜索盒", "number_float", unit="Angstrom", unit_source="argparse:define_vina_box:size_y"),
    fr("define_vina_box", "size_z", "搜索盒尺寸 Z", "搜索盒", "number_float", unit="Angstrom", unit_source="argparse:define_vina_box:size_z"),
    fr("define_vina_box", "exhaustiveness", "搜索强度", "运行参数", "number_int", minimum=1, range_source="argparse:define_vina_box:exhaustiveness", step=1, step_source="argparse:define_vina_box:exhaustiveness"),
    fr("define_vina_box", "num_modes", "保留姿势数量", "运行参数", "number_int", minimum=1, range_source="argparse:define_vina_box:num_modes", step=1, step_source="argparse:define_vina_box:num_modes"),
    fr("define_vina_box", "energy_range", "能量窗口", "运行参数", "number_float", unit="kcal/mol", unit_source="argparse:define_vina_box:energy_range"),
    fr("define_vina_box", "seed", "随机种子", "运行参数", "number_int", step=1, step_source="argparse:define_vina_box:seed"),
    fr("define_vina_box", "output", "Vina 配置输出文件", "输出", "path", path_kind="save", file_filter="配置文件 (*.txt *.conf);;所有文件 (*)", default_suffix=".txt"),
    fr("define_vina_box", "force", "允许覆盖配置", "输出", "checkbox"),
    fr("generate_vina_server_command", "server_workdir", "服务器工作目录", "服务器环境", "text", placeholder="例如：/ifs1/User/dengwei/project/run-001"),
    fr("generate_vina_server_command", "vina_executable", "服务器 Vina 绝对路径", "服务器环境", "text"),
    fr("generate_vina_server_command", "receptor", "受体 PDBQT", "服务器输入", "text", placeholder="相对服务器工作目录，或填写服务器绝对路径"),
    fr("generate_vina_server_command", "ligand", "配体 PDBQT", "服务器输入", "text", placeholder="相对服务器工作目录，或填写服务器绝对路径"),
    fr("generate_vina_server_command", "center_x", "搜索盒中心 X", "搜索盒", "text", unit="Angstrom", unit_source="argparse:generate_vina_server_command:center_x"),
    fr("generate_vina_server_command", "center_y", "搜索盒中心 Y", "搜索盒", "text", unit="Angstrom", unit_source="argparse:generate_vina_server_command:center_y"),
    fr("generate_vina_server_command", "center_z", "搜索盒中心 Z", "搜索盒", "text", unit="Angstrom", unit_source="argparse:generate_vina_server_command:center_z"),
    fr("generate_vina_server_command", "size_x", "搜索盒尺寸 X", "搜索盒", "text", unit="Angstrom", unit_source="argparse:generate_vina_server_command:size_x"),
    fr("generate_vina_server_command", "size_y", "搜索盒尺寸 Y", "搜索盒", "text", unit="Angstrom", unit_source="argparse:generate_vina_server_command:size_y"),
    fr("generate_vina_server_command", "size_z", "搜索盒尺寸 Z", "搜索盒", "text", unit="Angstrom", unit_source="argparse:generate_vina_server_command:size_z"),
    fr("generate_vina_server_command", "cpu", "CPU 线程数", "运行参数", "text"),
    fr("generate_vina_server_command", "exhaustiveness", "搜索强度", "运行参数", "text"),
    fr("generate_vina_server_command", "num_modes", "保留姿势数量", "运行参数", "text"),
    fr("generate_vina_server_command", "energy_range", "能量窗口", "运行参数", "text", unit="kcal/mol", unit_source="argparse:generate_vina_server_command:energy_range"),
    fr("generate_vina_server_command", "seed", "随机种子", "运行参数", "text"),
    fr("generate_vina_server_command", "pose_output", "对接姿势输出 PDBQT", "服务器输出", "text", placeholder="例如：outputs/poses.pdbqt"),
    fr("generate_vina_server_command", "log_output", "Vina 日志输出", "服务器输出", "text", placeholder="例如：outputs/vina.log"),
    fr("summarize_vina_results", "log", "Vina 日志", "输入", "path", path_kind="open", file_filter="日志文件 (*.log *.txt);;所有文件 (*)"),
    fr("summarize_vina_results", "pose", "对接姿势 PDBQT", "输入", "path", path_kind="open", file_filter=PDBQT),
    fr("summarize_vina_results", "format", "Vina 日志解析格式", "输入", "choice", value_source="fixed"),
    fr("summarize_vina_results", "output", "Vina 结果摘要输出文件", "输出", "path", path_kind="save", file_filter=JSON, default_suffix=".json"),
    fr("summarize_vina_results", "force", "允许覆盖结果摘要", "输出", "checkbox"),
    fr("export_receptor_pdbqt_to_pdb", "input", "受体 PDBQT", "输入", "path", path_kind="open", file_filter=PDBQT),
    fr("export_receptor_pdbqt_to_pdb", "output", "受体 PDB 输出文件", "输出", "path", path_kind="save", file_filter=PDB, default_suffix=".pdb"),
    fr("export_receptor_pdbqt_to_pdb", "overwrite", "允许覆盖受体 PDB", "输出", "checkbox"),
    fr("export_ligand_pdbqt_to_sdf", "input", "配体 PDBQT", "输入", "path", path_kind="open", file_filter=PDBQT),
    fr("export_ligand_pdbqt_to_sdf", "output", "配体 SDF 输出文件", "输出", "path", path_kind="save", file_filter=SDF, default_suffix=".sdf"),
    fr("export_ligand_pdbqt_to_sdf", "meeko_python", "Meeko/RDKit Python 程序", "运行环境与兼容性", "path", path_kind="open", file_filter=ANY, value_source="runtime", value_key="DOCKING_MEEKO_PYTHON"),
    fr("export_ligand_pdbqt_to_sdf", "overwrite", "允许覆盖配体 SDF", "输出", "checkbox"),
    fr("generate_maestro_lid", "schrodinger_run", "Schrödinger run 程序", "运行环境与兼容性", "path", path_kind="open", file_filter=ANY, value_source="runtime", value_key="DOCKING_SCHRODINGER_RUN"),
    fr("generate_maestro_lid", "meeko_python", "Meeko/RDKit Python 程序", "运行环境与兼容性", "path", path_kind="open", file_filter=ANY, value_source="runtime", value_key="DOCKING_MEEKO_PYTHON"),
    fr("generate_maestro_lid", "receptor", "受体 PDBQT 或 PDB", "输入", "path", path_kind="open", file_filter=PDBQT_OR_PDB),
    fr("generate_maestro_lid", "ligand", "配体 PDBQT 或 SDF", "输入", "path", path_kind="open", file_filter=PDBQT_OR_SDF),
    fr("generate_maestro_lid", "output", "LID 图片输出文件", "输出", "path", path_kind="save", file_filter="图片 (*.png *.jpg *.jpeg *.svg);;所有文件 (*)", default_suffix=".png"),
    fr("generate_maestro_lid", "receptor_index", "受体结构序号", "高级参数", "number_int", minimum=1, range_source="argparse:generate_maestro_lid:receptor_index", step=1, step_source="argparse:generate_maestro_lid:receptor_index"),
    fr("generate_maestro_lid", "ligand_index", "Pose / 结构序号", "输入", "number_int", minimum=1, range_source="argparse:generate_maestro_lid:ligand_index", step=1, step_source="argparse:generate_maestro_lid:ligand_index"),
    fr("generate_maestro_lid", "export_width", "图片最大宽度", "显示设置", "number_int", unit="px", unit_source="argparse:generate_maestro_lid:export_width", minimum=1, range_source="argparse:generate_maestro_lid:export_width", step=1, step_source="argparse:generate_maestro_lid:export_width"),
    fr("generate_maestro_lid", "export_height", "图片最大高度", "显示设置", "number_int", unit="px", unit_source="argparse:generate_maestro_lid:export_height", minimum=1, range_source="argparse:generate_maestro_lid:export_height", step=1, step_source="argparse:generate_maestro_lid:export_height"),
    fr("generate_maestro_lid", "bond_labels", "显示键标签", "显示设置", "checkbox"),
    fr("generate_maestro_lid", "salt_bridges", "显示盐桥", "显示设置", "checkbox"),
    fr("generate_maestro_lid", "h_bonds", "显示氢键", "显示设置", "checkbox"),
    fr("generate_maestro_lid", "pi_pi", "显示 π-π 相互作用", "显示设置", "checkbox"),
    fr("generate_maestro_lid", "pi_cation", "显示 π-阳离子相互作用", "显示设置", "checkbox"),
    fr("generate_maestro_lid", "overwrite", "允许覆盖 LID 图片", "输出", "checkbox"),
)

def tool_specs() -> tuple[ToolSpec, ...]:
    specs = tuple(_spec_from_row(row) for row in TOOL_ROWS)
    _validate_product_contract(specs)
    return specs


def get_tool_spec(tool_id: str) -> ToolSpec:
    for spec in tool_specs():
        if spec.tool_id == tool_id:
            return spec
    raise KeyError(tool_id)


def grouped_tool_specs() -> dict[str, tuple[ToolSpec, ...]]:
    grouped: dict[str, list[ToolSpec]] = {}
    for spec in tool_specs():
        grouped.setdefault(spec.group, []).append(spec)
    return {key: tuple(value) for key, value in grouped.items()}


def build_program_args(
    spec: ToolSpec,
    values: dict[str, Any],
    *,
    python_executable: str | None = None,
    source_root: Path | None = None,
) -> ProgramArgs:
    program = python_executable or sys.executable
    root = source_root or Path(__file__).resolve().parent
    args: list[str] = [str(root / spec.script)]
    for field in spec.fields:
        value = values.get(field.dest, field.default)
        args.extend(_field_argv(field, value))
    return ProgramArgs(program=program, args=tuple(args))


def default_values(spec: ToolSpec) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for field in spec.fields:
        if field.repeatable:
            values[field.dest] = [] if field.default is None else list(field.default)
        elif field.kind == "bool":
            values[field.dest] = bool(field.default)
        elif field.default is None:
            values[field.dest] = ""
        else:
            values[field.dest] = field.default
    return values


def parser_actions(spec: ToolSpec) -> dict[str, argparse.Action]:
    return {action.dest: action for action in _included_parser_actions(spec.module)}


def group_presentations() -> tuple[GroupPresentation, ...]:
    return GROUP_ROWS


def _spec_from_row(row: tuple[str, str, str, str, str]) -> ToolSpec:
    tool_id, group_id, title, module, summary = row
    if group_id not in GROUPS:
        raise ValueError(f"unknown group id for {tool_id}: {group_id}")
    field_presentations = _presentations_for_module(module)
    fields = tuple(_field_from_action(module, action, field_presentations) for action in parser_actions_for_module(module))
    return ToolSpec(
        tool_id=tool_id,
        group_id=group_id,
        group=GROUPS[group_id].label,
        title=title,
        module=module,
        script=f"{module}.py",
        summary=summary,
        fields=fields,
        input_modes=TOOL_INPUT_MODES.get(module, ()),
        output_derivations=OUTPUT_DERIVATIONS.get(module, ()),
        custom_panel=CUSTOM_PANEL_BY_TOOL_ID.get(tool_id, ""),
    )


def parser_actions_for_module(module: str) -> tuple[argparse.Action, ...]:
    return tuple(_included_parser_actions(module))


def _included_parser_actions(module: str) -> list[argparse.Action]:
    parser = _load_parser(module)
    ignored = IGNORED_DESTS.get(module, set())
    return [
        action
        for action in parser._actions
        if action.option_strings and not isinstance(action, argparse._HelpAction) and action.dest not in ignored
    ]


def _load_parser(module: str) -> argparse.ArgumentParser:
    source_path = str(Path(__file__).resolve().parent)
    sys.path.insert(0, source_path)
    try:
        imported = importlib.import_module(module)
    finally:
        try:
            sys.path.remove(source_path)
        except ValueError:
            pass
    return imported.build_parser()


def _presentations_for_module(module: str) -> dict[str, FieldPresentation]:
    result: dict[str, FieldPresentation] = {}
    for row_module, dest, presentation in FIELD_PRESENTATION_ROWS:
        if row_module != module:
            continue
        if dest in result:
            raise ValueError(f"duplicate field presentation for {module}.{dest}")
        result[dest] = presentation
    return result


def _field_from_action(
    module: str,
    action: argparse.Action,
    presentations: dict[str, FieldPresentation],
) -> ToolField:
    if action.dest not in presentations:
        raise ValueError(f"missing field presentation for {module}.{action.dest}")
    kind = _kind_for_action(action)
    choices = tuple(str(choice) for choice in action.choices) if action.choices is not None else ()
    option = _primary_option(action.option_strings)
    default = None if action.default is argparse.SUPPRESS else action.default
    repeatable = isinstance(action, argparse._AppendAction)
    return ToolField(
        dest=action.dest,
        option=option,
        kind=kind,
        required=bool(getattr(action, "required", False)),
        default=tuple(default) if repeatable and isinstance(default, list) else default,
        choices=choices,
        repeatable=repeatable,
        presentation=presentations[action.dest],
    )


def _kind_for_action(action: argparse.Action) -> str:
    if isinstance(action, (argparse._StoreTrueAction, argparse.BooleanOptionalAction)):
        return "bool"
    if isinstance(action, argparse._AppendAction):
        return "repeat"
    if action.choices is not None:
        return "choice"
    type_name = getattr(action.type, "__name__", "")
    if type_name == "Path":
        return "path"
    if type_name in {"int", "positive_int", "integer", "_positive_int"}:
        return "int"
    if type_name in {"float", "finite_float", "positive_float"}:
        return "float"
    return "text"


def _primary_option(option_strings: Sequence[str]) -> str:
    long_options = [option for option in option_strings if option.startswith("--") and not option.startswith("--no-")]
    return long_options[0] if long_options else option_strings[0]


def _validate_product_contract(specs: tuple[ToolSpec, ...]) -> None:
    if len(specs) != 21:
        raise ValueError(f"expected 21 tool specs, got {len(specs)}")
    if len({spec.tool_id for spec in specs}) != len(specs):
        raise ValueError("duplicate tool id in tool specs")
    if len({group.group_id for group in GROUP_ROWS}) != 7:
        raise ValueError("group presentations must define exactly seven group ids")
    if len({(module, dest) for module, dest, _presentation in FIELD_PRESENTATION_ROWS}) != len(FIELD_PRESENTATION_ROWS):
        raise ValueError("duplicate field presentation rows are not allowed")
    known_modules = {spec.module for spec in specs}
    if set(CUSTOM_PANEL_BY_TOOL_ID) - {spec.tool_id for spec in specs}:
        raise ValueError("custom-panel mapping references an unknown tool")
    if set(CUSTOM_PANEL_BY_TOOL_ID.values()) != {"vina_server_command"}:
        raise ValueError("unknown custom-panel contract")
    for module, dest, presentation in FIELD_PRESENTATION_ROWS:
        if module not in known_modules:
            raise ValueError(f"field presentation uses unknown module: {module}.{dest}")
        _validate_presentation_sources(module, dest, presentation)

    for spec in specs:
        actions = {action.dest: action for action in parser_actions_for_module(spec.module)}
        fields = {field.dest: field for field in spec.fields}
        if set(actions) != set(fields):
            raise ValueError(f"{spec.tool_id} field set does not match argparse")
        for field in spec.fields:
            action = actions[field.dest]
            raw_label = field.dest.replace("_", " ")
            if field.presentation.label == raw_label:
                raise ValueError(f"{spec.tool_id}.{field.dest} uses raw dest label")
            if action.help and field.presentation.help == action.help:
                raise ValueError(f"{spec.tool_id}.{field.dest} uses raw argparse help")
            if field.presentation.label_source != "product":
                raise ValueError(f"{spec.tool_id}.{field.dest} label source must be product")
            if field.presentation.value_source not in {"user", "fixed", "derived", "runtime"}:
                raise ValueError(
                    f"{spec.tool_id}.{field.dest} has invalid value source: "
                    f"{field.presentation.value_source}"
                )
        mode_keys = [mode.key for mode in spec.input_modes]
        if len(mode_keys) != len(set(mode_keys)):
            raise ValueError(f"{spec.tool_id} contains duplicate input mode keys")
        mode_dests = {
            dest
            for mode in spec.input_modes
            for dest in (*mode.visible_dests, *mode.required_dests)
        }
        unknown_mode_dests = mode_dests - set(fields)
        if unknown_mode_dests:
            raise ValueError(
                f"{spec.tool_id} input modes reference unknown fields: {sorted(unknown_mode_dests)}"
            )
        for mode in spec.input_modes:
            if not set(mode.required_dests).issubset(mode.visible_dests):
                raise ValueError(
                    f"{spec.tool_id}.{mode.key} requires fields hidden by the same mode"
                )
        for rule in spec.output_derivations:
            if rule.output_dest not in fields or rule.source_dest not in fields:
                raise ValueError(f"{spec.tool_id} output rule references an unknown field")
            if fields[rule.output_dest].presentation.path_kind not in {"save", "directory"}:
                raise ValueError(f"{spec.tool_id}.{rule.output_dest} is not an output path")
            if fields[rule.source_dest].presentation.path_kind not in {"open", "directory"}:
                raise ValueError(f"{spec.tool_id}.{rule.source_dest} is not an input path")
            if rule.directory_mode not in {"source_parent", "source_parent_named", "source_directory", "source_sibling"}:
                raise ValueError(f"{spec.tool_id}.{rule.output_dest} has invalid directory mode")


def _validate_presentation_sources(module: str, dest: str, presentation: FieldPresentation) -> None:
    for value, source, source_name in (
        (presentation.unit, presentation.unit_source, "unit_source"),
        ((presentation.minimum, presentation.maximum), presentation.range_source, "range_source"),
        (presentation.step, presentation.step_source, "step_source"),
    ):
        has_value = value not in ("", None, (None, None))
        if has_value and not source:
            raise ValueError(f"{module}.{dest} missing {source_name}")
        if source and not SOURCE_ID_PATTERN.match(source):
            raise ValueError(f"{module}.{dest} invalid {source_name}: {source}")


def _field_argv(field: ToolField, value: Any) -> list[str]:
    if field.repeatable:
        return _repeat_argv(field, value)
    if field.kind == "bool":
        return _bool_argv(field, value)
    if value is None or value == "":
        return []
    return _option_value_argv(field.option, value)


def _repeat_argv(field: ToolField, value: Any) -> list[str]:
    if value is None or value == "":
        return []
    values: Iterable[Any]
    if isinstance(value, str):
        values = value.splitlines()
    else:
        values = value
    result: list[str] = []
    for item in values:
        if item is None:
            continue
        result.extend(_option_value_argv(field.option, item))
    return result


def _option_value_argv(option: str, value: Any) -> list[str]:
    text = str(value)
    if option.startswith("--") and (not text or text.startswith("-")):
        return [f"{option}={text}"]
    return [option, text]


def _bool_argv(field: ToolField, value: Any) -> list[str]:
    enabled = bool(value)
    if field.default is True:
        if enabled:
            return [field.option]
        return [_negative_option(field.option)]
    if enabled:
        return [field.option]
    return []


def _negative_option(option: str) -> str:
    if option.startswith("--"):
        return "--no-" + option[2:]
    return option
