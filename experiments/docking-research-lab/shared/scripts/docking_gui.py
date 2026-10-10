#!/usr/bin/env python3

from __future__ import annotations

import codecs
import math
import os
import shlex
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PyQt6.QtCore import (
    QObject,
    QProcess,
    QProcessEnvironment,
    QSettings,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt6.QtGui import QCloseEvent, QKeySequence, QPainter, QPen, QShortcut, QTextCursor
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QStackedWidget,
    QStyle,
    QStyleOptionToolButton,
    QStylePainter,
    QTextEdit,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from docking_tool_specs import (
    InputModePresentation,
    ProgramArgs,
    ToolField,
    ToolSpec,
    build_program_args,
    default_values,
    grouped_tool_specs,
)
from docking_tool_result import (
    RESULT_PATH_ENV,
    ToolArtifact,
    ToolResultError,
    read_tool_result,
)
from transient_paths import transient_root


SECTION_ORDER = (
    "输入",
    "输出",
    "搜索盒",
    "科学参数",
    "显示设置",
    "运行参数",
    "运行环境与兼容性",
    "高级参数",
)
COLLAPSED_SECTIONS = {"高级参数"}
PREFERRED_DOCKING_PYTHON = Path("/opt/homebrew/Caskroom/miniforge/base/envs/docking/bin/python")
KNOWN_SCHRODINGER_RUN = Path("/opt/schrodinger/suites2026-3/run")
SETTINGS_ORGANIZATION = "org.local"
SETTINGS_APPLICATION = "DockingWorkbench"
VINA_SETTINGS_GROUP = "vina-server-command/v1"
VINA_HISTORY_LIMIT = 10
E2_VINA_EXECUTABLE = "/ifs1/User/dengwei/igem/envs/docking-frame-repair-v1/bin/vina"
PYMOL_REVIEW_OUTPUT_DESTS = {
    "make_tm_topology_review_pml": "output",
    "make_raw_relaxed_review_pml": "output",
    "make_ppm_review_pml": "output",
    "run_restrained_minimization": "review_pml",
}
PYMOL_REVIEW_TOOL_IDS = set(PYMOL_REVIEW_OUTPUT_DESTS)
GUI_MERGED_HELPER_TOOL_IDS = {
    "check_sdf_pdbqt_mapping",
    "export_receptor_pdbqt_to_pdb",
    "export_ligand_pdbqt_to_sdf",
    "summarize_geometry_validation",
    "compare_raw_relaxed",
    "make_raw_relaxed_review_pml",
    "define_vina_box",
    "summarize_vina_results",
}
VINA_GROUP_ID = "vina_docking"
VINA_COMMAND_NAV_ID = "vina_server_command"


@dataclass
class RuntimeConfig:
    python_executable: str
    workdir: Path
    source_root: Path


@dataclass(frozen=True)
class VinaCommandField:
    dest: str
    label: str
    section: str
    default: str = ""
    placeholder: str = ""
    numeric_kind: str = ""
    positive: bool = False


VINA_COMMAND_FIELDS = (
    VinaCommandField(
        "server_workdir",
        "服务器工作目录",
        "E2 环境",
        placeholder="例如：/ifs1/User/dengwei/project/run-001",
    ),
    VinaCommandField(
        "vina_executable",
        "服务器 Vina 绝对路径",
        "E2 环境",
        default=E2_VINA_EXECUTABLE,
    ),
    VinaCommandField(
        "receptor",
        "受体 PDBQT",
        "服务器输入",
        placeholder="相对服务器工作目录，或填写服务器绝对路径",
    ),
    VinaCommandField(
        "ligand",
        "配体 PDBQT",
        "服务器输入",
        placeholder="相对服务器工作目录，或填写服务器绝对路径",
    ),
    VinaCommandField("center_x", "搜索盒中心 X (Angstrom)", "搜索盒", numeric_kind="float"),
    VinaCommandField("center_y", "搜索盒中心 Y (Angstrom)", "搜索盒", numeric_kind="float"),
    VinaCommandField("center_z", "搜索盒中心 Z (Angstrom)", "搜索盒", numeric_kind="float"),
    VinaCommandField(
        "size_x", "搜索盒尺寸 X (Angstrom)", "搜索盒", numeric_kind="float", positive=True
    ),
    VinaCommandField(
        "size_y", "搜索盒尺寸 Y (Angstrom)", "搜索盒", numeric_kind="float", positive=True
    ),
    VinaCommandField(
        "size_z", "搜索盒尺寸 Z (Angstrom)", "搜索盒", numeric_kind="float", positive=True
    ),
    VinaCommandField(
        "cpu", "CPU 线程数", "运行参数", default="16", numeric_kind="int", positive=True
    ),
    VinaCommandField(
        "exhaustiveness",
        "搜索强度",
        "运行参数",
        default="8",
        numeric_kind="int",
        positive=True,
    ),
    VinaCommandField(
        "num_modes",
        "保留姿势数量",
        "运行参数",
        default="9",
        numeric_kind="int",
        positive=True,
    ),
    VinaCommandField(
        "energy_range",
        "能量窗口 (kcal/mol)",
        "运行参数",
        default="3",
        numeric_kind="float",
        positive=True,
    ),
    VinaCommandField(
        "seed", "随机种子", "运行参数", default="0", numeric_kind="int"
    ),
    VinaCommandField(
        "pose_output",
        "对接姿势输出 PDBQT",
        "服务器输出",
        placeholder="例如：outputs/poses.pdbqt",
    ),
    VinaCommandField(
        "log_output",
        "Vina 日志输出",
        "服务器输出",
        placeholder="例如：outputs/vina.log",
    ),
)


def discover_cli_python() -> str:
    override = os.environ.get("DOCKING_CLI_PYTHON", "").strip()
    for candidate in (override, str(PREFERRED_DOCKING_PYTHON), sys.executable):
        resolved = _resolve_executable(candidate, Path.cwd()) if candidate else None
        if resolved is not None:
            return str(resolved)
    return sys.executable


class ToolNavigationTree(QTreeWidget):
    def keyPressEvent(self, event: Any) -> None:  # noqa: N802 - Qt API shape
        key = event.key()
        if key not in {
            Qt.Key.Key_Up,
            Qt.Key.Key_Down,
            Qt.Key.Key_Home,
            Qt.Key.Key_End,
        }:
            super().keyPressEvent(event)
            return

        items: list[QTreeWidgetItem] = []
        for group_index in range(self.topLevelItemCount()):
            group = self.topLevelItem(group_index)
            items.extend(group.child(index) for index in range(group.childCount()))
        if not items:
            return
        current = self.currentItem()
        current_index = items.index(current) if current in items else 0
        if key == Qt.Key.Key_Home:
            next_index = 0
        elif key == Qt.Key.Key_End:
            next_index = len(items) - 1
        elif key == Qt.Key.Key_Up:
            next_index = max(0, current_index - 1)
        else:
            next_index = min(len(items) - 1, current_index + 1)
        self.setCurrentItem(items[next_index])
        self.scrollToItem(items[next_index])
        event.accept()


class ChevronToolButton(QToolButton):
    """Text button with a light, platform-neutral disclosure chevron."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._expanded = False
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.setAutoRaise(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(30)
        self.setStyleSheet(
            "QToolButton { border: 0; background: transparent; padding: 0; }"
            "QToolButton:hover { background: palette(midlight); }"
            "QToolButton:pressed { background: palette(mid); }"
        )

    def setExpanded(self, expanded: bool) -> None:  # noqa: N802 - Qt API shape
        self._expanded = expanded
        self.update()

    def paintEvent(self, event: Any) -> None:  # noqa: N802 - Qt API shape
        option = QStyleOptionToolButton()
        self.initStyleOption(option)
        option.text = ""
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.ComplexControl.CC_ToolButton, option)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(self.palette().buttonText().color(), 1.35)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        center_y = self.rect().center().y()
        if self._expanded:
            points = ((7, center_y - 2), (11, center_y + 2), (15, center_y - 2))
        else:
            points = ((9, center_y - 4), (13, center_y), (9, center_y + 4))
        painter.drawLine(*points[0], *points[1])
        painter.drawLine(*points[1], *points[2])
        painter.drawText(
            self.rect().adjusted(24, 0, -6, 0),
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
            self.text(),
        )


class CollapsibleSection(QWidget):
    def __init__(
        self,
        title: str,
        content: QWidget,
        *,
        expanded: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._required_attention = False
        self.content = content
        self.toggle_button = ChevronToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setAccessibleName(title)
        self.toggle_button.toggled.connect(self._set_expanded)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(self.toggle_button)
        layout.addWidget(content)
        self.setChecked(expanded)

    def title(self) -> str:
        return self._title

    def isChecked(self) -> bool:  # noqa: N802 - mirrors Qt checkable widgets
        return self.toggle_button.isChecked()

    def setChecked(self, checked: bool) -> None:  # noqa: N802 - mirrors Qt checkable widgets
        self.toggle_button.setChecked(checked)
        self._set_expanded(checked)

    def set_required_attention(self, active: bool) -> None:
        self._required_attention = active
        visible_title = f"{self._title}（有必填项）" if active else self._title
        self.toggle_button.setText(visible_title)
        self.toggle_button.setAccessibleName(visible_title)
        self._set_expanded(self.isChecked())

    def _set_expanded(self, expanded: bool) -> None:
        self.content.setVisible(expanded)
        self.toggle_button.setExpanded(expanded)
        if self._required_attention:
            state = (
                "有必填项。已展开，按下可收起。"
                if expanded
                else "有必填项。已折叠，按下可展开并定位首个缺项。"
            )
        else:
            state = "已展开，按下可收起。" if expanded else "已折叠，按下可展开。"
        self.toggle_button.setAccessibleDescription(state)
        self.toggle_button.setToolTip(state)
        self.toggle_button.setStatusTip(state)


class PathInput(QWidget):
    def __init__(
        self,
        mode: str,
        *,
        dialog_title: str = "",
        file_filter: str = "",
        default_suffix: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.mode = mode
        self.dialog_title = dialog_title
        self.file_filter = file_filter
        self.default_suffix = default_suffix
        self.line_edit = QLineEdit()
        self.button = QPushButton("选择")
        self.button.setAccessibleName("选择路径")
        self.button.clicked.connect(self.browse)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button)

    def configure_semantics(self, label: str, help_text: str, placeholder: str) -> None:
        description = help_text or f"填写{label}。"
        self.setAccessibleName(label)
        self.setAccessibleDescription(description)
        self.setToolTip(description)
        self.setStatusTip(description)
        self.line_edit.setAccessibleName(label)
        self.line_edit.setAccessibleDescription(description)
        self.line_edit.setToolTip(description)
        self.line_edit.setStatusTip(description)
        self.line_edit.setPlaceholderText(placeholder)
        button_description = f"打开选择器以填写{label}。"
        self.button.setAccessibleName(f"选择{label}")
        self.button.setAccessibleDescription(button_description)
        self.button.setToolTip(button_description)
        self.button.setStatusTip(button_description)

    def text(self) -> str:
        return self.line_edit.text()

    def setText(self, value: str) -> None:
        self.line_edit.setText(value)

    def setPlaceholderText(self, value: str) -> None:
        self.line_edit.setPlaceholderText(value)

    def setAccessibleName(self, value: str) -> None:  # noqa: N802 - Qt API shape
        super().setAccessibleName(value)
        self.line_edit.setAccessibleName(value)

    def browse(self) -> None:
        current = self.line_edit.text()
        if self.mode == "directory":
            title = self.dialog_title or "选择文件夹"
            selected = QFileDialog.getExistingDirectory(self, title, current)
        elif self.mode == "save":
            title = self.dialog_title or "选择保存位置"
            selected, _selected_filter = QFileDialog.getSaveFileName(
                self,
                title,
                current,
                self.file_filter or "All files (*)",
            )
            if selected and self.default_suffix:
                suffix = (
                    self.default_suffix
                    if self.default_suffix.startswith(".")
                    else f".{self.default_suffix}"
                )
                if not selected.casefold().endswith(suffix.casefold()):
                    selected = f"{selected}{suffix}"
        else:
            title = self.dialog_title or "选择输入文件"
            selected, _selected_filter = QFileDialog.getOpenFileName(
                self,
                title,
                current,
                self.file_filter or "All files (*)",
            )
        if selected:
            self.line_edit.setText(selected)


class ToolProcessRunner(QObject):
    stdout_received = pyqtSignal(str)
    stderr_received = pyqtSignal(str)
    finished = pyqtSignal(int)
    failed = pyqtSignal(str)
    warning = pyqtSignal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self._read_stdout)
        self.process.readyReadStandardError.connect(self._read_stderr)
        self.process.finished.connect(self._finished)
        self.process.errorOccurred.connect(self._error)
        self.last_command: ProgramArgs | None = None
        self.last_result: tuple[ToolArtifact, ...] = ()
        self.result_error = ""
        self.last_receipt_path: Path | None = None
        self._receipt_directory: Path | None = None
        self._terminal_emitted = False
        self._reset_decoders()
        self._kill_timer = QTimer(self)
        self._kill_timer.setSingleShot(True)
        self._kill_timer.timeout.connect(self._force_kill)

    def is_running(self) -> bool:
        return self.process.state() != QProcess.ProcessState.NotRunning

    def start(self, command: ProgramArgs, *, workdir: Path) -> None:
        if self.is_running():
            raise RuntimeError("已有任务正在运行")
        self.last_command = command
        self.last_result = ()
        self.result_error = ""
        self._terminal_emitted = False
        self._reset_decoders()
        self._cleanup_receipt()
        self._receipt_directory = Path(
            tempfile.mkdtemp(prefix="docking-gui-result-", dir=transient_root())
        )
        self.last_receipt_path = self._receipt_directory / "result.json"
        environment = QProcessEnvironment.systemEnvironment()
        environment.insert(RESULT_PATH_ENV, str(self.last_receipt_path))
        self.process.setProcessEnvironment(environment)
        self.process.setProgram(command.program)
        self.process.setArguments(list(command.args))
        self.process.setWorkingDirectory(str(workdir))
        self.process.start()

    def stop(self) -> None:
        if not self.is_running():
            return
        self.process.terminate()
        self._kill_timer.start(3000)

    def _force_kill(self) -> None:
        if self.is_running():
            self.process.kill()

    def _reset_decoders(self) -> None:
        decoder = codecs.getincrementaldecoder("utf-8")
        self._stdout_decoder = decoder(errors="replace")
        self._stderr_decoder = decoder(errors="replace")

    def _read_stdout(self, *, final: bool = False) -> None:
        data = bytes(self.process.readAllStandardOutput())
        text = self._stdout_decoder.decode(data, final=final)
        if text:
            self.stdout_received.emit(text)

    def _read_stderr(self, *, final: bool = False) -> None:
        data = bytes(self.process.readAllStandardError())
        text = self._stderr_decoder.decode(data, final=final)
        if text:
            self.stderr_received.emit(text)

    def _finished(self, exit_code: int, _status: QProcess.ExitStatus) -> None:
        self._kill_timer.stop()
        self._read_stdout(final=True)
        self._read_stderr(final=True)
        if self._terminal_emitted:
            return
        self._terminal_emitted = True
        self._capture_result(exit_code)
        self._cleanup_receipt()
        self.finished.emit(exit_code)

    def _error(self, error: QProcess.ProcessError) -> None:
        if self._terminal_emitted:
            return
        if error == QProcess.ProcessError.FailedToStart and not self.is_running():
            self._terminal_emitted = True
            self._kill_timer.stop()
            self._reset_decoders()
            self._cleanup_receipt()
            self.failed.emit(str(error.name))
            return
        self.warning.emit(str(error.name))

    def _capture_result(self, exit_code: int) -> None:
        receipt_path = self.last_receipt_path
        if receipt_path is None:
            return
        if not receipt_path.is_file():
            if exit_code == 0:
                self.result_error = "工具成功结束，但没有返回产物回执。"
            return
        try:
            self.last_result = read_tool_result(receipt_path)
        except ToolResultError as exc:
            self.result_error = f"无法读取工具产物回执：{exc}"

    def _cleanup_receipt(self) -> None:
        directory = self._receipt_directory
        self._receipt_directory = None
        if directory is not None:
            shutil.rmtree(directory, ignore_errors=True)


class ToolPanel(QWidget):
    run_requested = pyqtSignal(object, object)
    run_stopped = pyqtSignal(object)
    run_succeeded = pyqtSignal(object)

    def __init__(
        self,
        spec: ToolSpec,
        runtime: RuntimeConfig,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.spec = spec
        self.runtime = runtime
        self.widgets: dict[str, QWidget] = {}
        self.error_labels: dict[str, QLabel] = {}
        self.section_disclosures: dict[str, CollapsibleSection] = {}
        self._touched_fields: set[str] = set()
        self.output_rows: dict[Path, tuple[QLabel, QPushButton, QPushButton]] = {}
        self.result_artifacts: tuple[ToolArtifact, ...] = ()
        self._result_completed = False
        self.fields_by_dest = {field.dest: field for field in spec.fields}
        self.current_command: ProgramArgs | None = None
        self._running = False
        self._stopping = False
        self._global_busy = False
        self.field_labels: dict[str, QLabel] = {}
        self.field_rows: dict[str, QWidget] = {}
        self._field_focus_order: list[QWidget] = []
        self.field_tab_order: list[str] = []
        self.input_mode_selector: QComboBox | None = None
        self.input_mode_guidance: QLabel | None = None
        self.format_detection_label: QLabel | None = None
        self._output_derivations = tuple(getattr(spec, "output_derivations", ()))
        self._output_derivations_by_dest = {
            derivation.output_dest: derivation
            for derivation in self._output_derivations
        }
        self._auto_output_values: dict[str, str] = {}
        self._manual_output_dests: set[str] = set()
        self.keep_review_script: QCheckBox | None = None
        self._pending_review_output: Path | None = None
        self._transient_review_directories: list[Path] = []
        self._completion_message = ""

        self.runner = ToolProcessRunner(self)
        self.runner.stdout_received.connect(self._append_stdout)
        self.runner.stderr_received.connect(self._append_stderr)
        self.runner.finished.connect(self._finished)
        self.runner.failed.connect(self._failed)
        self.runner.warning.connect(self._process_warning)

        self.title = QLabel(spec.title)
        self.title.setObjectName("toolTitle")
        self.title.setAccessibleName(f"当前工具：{spec.title}")
        self.summary = QLabel(spec.summary)
        self.summary.setWordWrap(True)
        self.status = QLabel()
        self._show_status("准备就绪")
        self.problem = QLabel("")
        self.problem.setWordWrap(True)
        self.problem.setVisible(False)

        self.form_widget = self._build_form()
        self._sync_derived_outputs()
        self.results_box = self._build_results()
        self.tech_box = self._build_technical_details()
        run_labels = {
            "run_restrained_minimization": "最小化并在 PyMOL 中复核",
        }
        run_label = run_labels.get(
            self.spec.tool_id,
            "在 PyMOL 中复核"
            if self.spec.tool_id in PYMOL_REVIEW_TOOL_IDS
            else "运行",
        )
        self.run_button = QPushButton(run_label)
        self.stop_button = QPushButton("停止")
        self.stop_button.setEnabled(False)
        self.run_button.setAccessibleName(f"运行 {spec.title}")
        self.stop_button.setAccessibleName(f"停止 {spec.title}")
        self.run_button.setToolTip("检查填写内容后启动该工具（Ctrl+Return）。")
        self.run_button.setStatusTip(self.run_button.toolTip())
        self.stop_button.setToolTip("停止当前任务（Ctrl+.）。")
        self.stop_button.setStatusTip(self.stop_button.toolTip())
        self.run_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.run_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.run_shortcut.activated.connect(self._run_from_shortcut)
        self.stop_shortcut = QShortcut(QKeySequence("Ctrl+."), self)
        self.stop_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.stop_shortcut.activated.connect(self._stop_from_shortcut)
        self.run_button.clicked.connect(self.run)
        self.stop_button.clicked.connect(self.stop)

        header = QWidget()
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.summary)

        scroll_body = QWidget()
        scroll_layout = QVBoxLayout(scroll_body)
        scroll_layout.addWidget(self.form_widget)
        scroll_layout.addWidget(self.results_box)
        scroll_layout.addWidget(self.tech_box)
        scroll_layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(scroll_body)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 8, 0, 0)
        actions_layout.addWidget(self.status)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.stop_button)
        actions_layout.addWidget(self.run_button)

        layout = QVBoxLayout(self)
        layout.addWidget(header)
        layout.addWidget(scroll, 1)
        layout.addWidget(self.problem)
        layout.addWidget(actions)
        self._install_tab_order()
        self._refresh_command()
        self.update_output_actions()
        self._refresh_section_attention()
        self._refresh_run_enabled()
        self._refresh_form_guidance()

    def refresh_runtime(self) -> None:
        self.workdir_label.setText(f"工作目录：{self.runtime.workdir}")
        self.python_label.setText(f"Python：{self.runtime.python_executable}")
        self._refresh_command()
        self._refresh_run_enabled()
        self._refresh_form_guidance()

    def values(self) -> dict[str, Any]:
        values = default_values(self.spec)
        for field in self.spec.fields:
            if not field.user_editable:
                values[field.dest] = self._non_user_value(field)
                continue
            if not self._field_is_active(field.dest):
                values[field.dest] = [] if field.repeatable else False if field.kind == "bool" else ""
                continue
            widget = self.widgets[field.dest]
            values[field.dest] = self._read_widget(field, widget)
        return values

    def command(self) -> ProgramArgs:
        values = self.values()
        if self._uses_temporary_review_script():
            output = self._pending_review_output or (
                transient_root()
                / f"docking-pymol-review-{os.getpid()}"
                / f"{self.spec.tool_id}.pml"
            )
            output_dest = self._review_output_dest()
            if output_dest is not None:
                values[output_dest] = str(output)
            if output_dest == "output":
                values["force"] = True
        command = build_program_args(
            self.spec,
            values,
            python_executable=self.runtime.python_executable,
            source_root=self.runtime.source_root,
        )
        self.current_command = command
        return command

    def _uses_temporary_review_script(self) -> bool:
        return (
            self.spec.tool_id in PYMOL_REVIEW_TOOL_IDS
            and (
                self.keep_review_script is None
                or not self.keep_review_script.isChecked()
            )
        )

    def _review_output_dest(self) -> str | None:
        return PYMOL_REVIEW_OUTPUT_DESTS.get(self.spec.tool_id)

    def _prepare_transient_review_run(self) -> None:
        if not self._uses_temporary_review_script():
            self._pending_review_output = None
            return
        directory = Path(
            tempfile.mkdtemp(
                prefix=f"docking-{self.spec.tool_id}-",
                dir=transient_root(),
            )
        )
        self._transient_review_directories.append(directory)
        self._pending_review_output = directory / "review.pml"

    def _discard_pending_review_output(self) -> None:
        output = self._pending_review_output
        self._pending_review_output = None
        if output is None:
            return
        directory = output.parent
        shutil.rmtree(directory, ignore_errors=True)
        try:
            self._transient_review_directories.remove(directory)
        except ValueError:
            pass

    def cleanup_transient_files(self) -> None:
        self._pending_review_output = None
        for directory in self._transient_review_directories:
            shutil.rmtree(directory, ignore_errors=True)
        self._transient_review_directories.clear()

    def run(self) -> None:
        if self._running:
            return
        if self._global_busy:
            self._show_problem("其他工具正在运行，请等待或停止后再运行。")
            return
        errors = self.validate_form(show_errors=True)
        if errors:
            first_dest = next(iter(errors))
            self._show_problem(next(iter(errors.values())))
            if first_dest in self.widgets:
                self._focus_field(first_dest)
            return
        self._prepare_transient_review_run()
        command = self._refresh_command()
        self.run_requested.emit(self, command)

    def _run_from_shortcut(self) -> None:
        if self.run_button.isEnabled():
            self.run_button.click()

    def _stop_from_shortcut(self) -> None:
        if self.stop_button.isEnabled():
            self.stop_button.click()

    def start_approved_run(self, command: ProgramArgs) -> None:
        self.stdout.clear()
        self.stderr.clear()
        self._completion_message = ""
        self._set_result_artifacts((), completed=False)
        self.exit_code.setText("尚无退出码")
        self._set_running(True)
        self._stopping = False
        self._show_status("正在运行")
        self._hide_problem()
        try:
            self.runner.start(command, workdir=self.runtime.workdir)
        except RuntimeError as exc:
            self._failed(str(exc))

    def stop(self) -> None:
        if not self.runner.is_running():
            return
        self._stopping = True
        self._show_status("正在停止")
        self.stop_button.setEnabled(False)
        self.runner.stop()

    def set_global_busy(self, busy: bool, owner_title: str = "") -> None:
        was_busy = self._global_busy
        self._global_busy = busy
        if self._running:
            return
        self._refresh_run_enabled()
        if busy and owner_title:
            self._show_status(f"{owner_title} 正在运行")
        elif was_busy:
            self._refresh_form_guidance()

    def validate_form(self, *, show_errors: bool = True) -> dict[str, str]:
        errors = self._form_errors()
        if not show_errors:
            return errors
        self._touched_fields.update(dest for dest in errors if dest in self.error_labels)
        self._refresh_touched_field_errors(errors)
        return errors

    def _form_errors(self) -> dict[str, str]:
        errors: dict[str, str] = {}
        for field in self.spec.fields:
            if field.user_editable:
                continue
            value = self._non_user_value(field)
            if self._field_is_required(field) and _is_empty(value):
                if field.presentation.value_source == "runtime":
                    errors["__runtime__"] = self._missing_runtime_message()
                else:
                    errors["__runtime__"] = (
                        f"当前安装缺少 {self.spec.title} 所需的内部固定配置；"
                        "这不是普通用户应填写的参数，请更新或修复工具安装。"
                    )
                return errors
        for dest in self.field_tab_order:
            if not self._field_is_active(dest):
                continue
            field = self.fields_by_dest[dest]
            value = self._read_widget(field, self.widgets[field.dest])
            error = self._validate_field(field, value)
            if error:
                errors[field.dest] = error
        if self.spec.tool_id == "report_af_confidence":
            input_format = str(self._read_widget(
                self.fields_by_dest["input_format"], self.widgets["input_format"]
            )).strip()
            plddt_pointer = str(self._read_widget(
                self.fields_by_dest["plddt_pointer"], self.widgets["plddt_pointer"]
            )).strip()
            pae_pointer = str(self._read_widget(
                self.fields_by_dest["pae_pointer"], self.widgets["pae_pointer"]
            )).strip()
            if input_format or plddt_pointer or pae_pointer:
                if not input_format:
                    errors["input_format"] = (
                        "专家兼容覆盖还需填写带版本的 JSON 解析格式来源。"
                    )
                if not plddt_pointer:
                    errors["plddt_pointer"] = (
                        "专家兼容覆盖还需填写已确认的逐残基 pLDDT 位置。"
                    )
        if self.spec.tool_id == "make_ppm_review_pml":
            topology_source = str(
                self._read_widget(
                    self.fields_by_dest["topology_source"],
                    self.widgets["topology_source"],
                )
            ).strip()
            topology_format = str(
                self._read_widget(
                    self.fields_by_dest["topology_format"],
                    self.widgets["topology_format"],
                )
            ).strip()
            if not topology_source:
                errors["topology_source"] = "请选择拓扑来源文件；不再需要先保存 topology JSON。"
            if topology_format and not topology_source:
                errors["topology_format"] = "拓扑来源格式覆盖只能和拓扑来源文件一起使用。"
        if self.spec.tool_id == "generate_maestro_lid":
            ligand = str(
                self._read_widget(
                    self.fields_by_dest["ligand"], self.widgets["ligand"]
                )
            ).strip()
            meeko_field = self.fields_by_dest.get("meeko_python")
            if (
                ligand.lower().endswith(".pdbqt")
                and meeko_field is not None
                and _is_empty(self._non_user_value(meeko_field))
            ):
                errors["__runtime__"] = (
                    "选定 pose 是 PDBQT，但当前安装未检测到同时提供 Meeko "
                    "和 RDKit 的 Docking Python，无法进行临时 SDF 转换。"
                )
        errors.update(self._path_conflict_errors())
        runtime_error = self._validate_runtime()
        if runtime_error:
            errors["__runtime__"] = runtime_error
        return errors

    def _path_conflict_errors(self) -> dict[str, str]:
        ordered_output_dests = tuple(
            dict.fromkeys(rule.output_dest for rule in self._output_derivations)
        )
        output_dests = set(ordered_output_dests)
        if not output_dests:
            return {}
        values = self.values()
        normalized: dict[str, Path] = {}
        for field in self.spec.fields:
            if not self._field_is_active(field.dest):
                continue
            value = values.get(field.dest)
            if _is_empty(value) or field.presentation.path_kind not in {"open", "save", "directory"}:
                continue
            path = Path(str(value)).expanduser()
            if not path.is_absolute():
                path = self.runtime.workdir / path
            normalized[field.dest] = path.resolve(strict=False)

        errors: dict[str, str] = {}
        input_dests = [
            field.dest
            for field in self.spec.fields
            if field.dest in normalized and field.dest not in output_dests
        ]
        for output_dest in ordered_output_dests:
            output_path = normalized.get(output_dest)
            if output_path is None:
                continue
            for input_dest in input_dests:
                if output_path != normalized[input_dest]:
                    continue
                if (
                    self.spec.tool_id == "cif_to_pdb"
                    and output_dest == "output_dir"
                    and input_dest == "input_dir"
                ):
                    continue
                errors[output_dest] = (
                    f"{self.fields_by_dest[output_dest].label}不能与"
                    f"{self.fields_by_dest[input_dest].label}使用同一路径；请选择另一保存位置。"
                )
                break

        ordered_outputs = [dest for dest in ordered_output_dests if dest in normalized]
        for index, first in enumerate(ordered_outputs):
            for second in ordered_outputs[index + 1 :]:
                if normalized[first] != normalized[second]:
                    continue
                errors.setdefault(
                    second,
                    f"{self.fields_by_dest[second].label}不能与"
                    f"{self.fields_by_dest[first].label}使用同一路径；请保留不同文件名。",
                )
        return errors

    def _refresh_touched_field_errors(self, errors: dict[str, str] | None = None) -> None:
        current_errors = self._form_errors() if errors is None else errors
        for dest, label in self.error_labels.items():
            error = current_errors.get(dest, "") if dest in self._touched_fields else ""
            label.setText(error)
            label.setVisible(bool(error))

    def _refresh_section_attention(self, errors: dict[str, str] | None = None) -> None:
        current_errors = self._form_errors() if errors is None else errors
        for section, disclosure in self.section_disclosures.items():
            disclosure.set_required_attention(
                any(
                    field.user_editable
                    and self._field_is_required(field)
                    and self._field_is_active(field.dest)
                    and field.presentation.section == section
                    and field.dest in current_errors
                    for field in self.spec.fields
                )
            )

    def _section_toggled(self, section: str, expanded: bool) -> None:
        if not expanded:
            return
        errors = self._form_errors()
        first_unmet = next(
            (
                field.dest
                for field in self.spec.fields
                if self._field_is_required(field)
                and self._field_is_active(field.dest)
                and field.presentation.section == section
                and field.dest in errors
            ),
            None,
        )
        if first_unmet is None:
            return
        self._touched_fields.add(first_unmet)
        self._refresh_touched_field_errors(errors)
        QTimer.singleShot(0, lambda dest=first_unmet: self._focus_field(dest))

    def open_output(self, artifact: ToolArtifact) -> None:
        self._open_output(artifact, reveal=False)

    def reveal_output(self, artifact: ToolArtifact) -> None:
        self._open_output(artifact, reveal=True)

    def update_output_actions(self) -> None:
        for artifact in self.result_artifacts:
            row = self.output_rows.get(artifact.path)
            if row is None:
                continue
            info, open_button, reveal_button = row
            valid = self._path_matches_kind(artifact.path, artifact.kind)
            info.setText(str(artifact.path) if valid else f"产物不存在：{artifact.path}")
            open_button.setEnabled(valid)
            reveal_button.setEnabled(valid)

    def _build_form(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        sections: dict[str, QFormLayout] = {}
        product_fields = tuple(field for field in self.spec.fields if field.user_editable)
        section_names = [
            section
            for section in SECTION_ORDER
            if any(field.presentation.section == section for field in product_fields)
        ]
        extra_sections = sorted({f.presentation.section for f in product_fields} - set(SECTION_ORDER))
        ordered_sections = [*section_names, *extra_sections]
        for section in ordered_sections:
            form = QFormLayout()
            form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)
            holder = QWidget()
            holder.setLayout(form)
            sections[section] = form
            if section in COLLAPSED_SECTIONS:
                disclosure = CollapsibleSection(section, holder)
                self.section_disclosures[section] = disclosure
                disclosure.toggle_button.toggled.connect(
                    lambda expanded, name=section: self._section_toggled(name, expanded)
                )
                layout.addWidget(disclosure)
            else:
                group = QGroupBox(section)
                group_layout = QVBoxLayout(group)
                group_layout.addWidget(holder)
                layout.addWidget(group)

        if self.spec.input_modes:
            self.input_mode_selector = QComboBox()
            self.input_mode_selector.setAccessibleName("输入模式")
            self.input_mode_selector.setAccessibleDescription(
                "选择单文件或批量目录模式；未选模式的字段不会进入运行命令。"
            )
            for mode in self.spec.input_modes:
                self.input_mode_selector.addItem(mode.label, mode.key)
            self.input_mode_guidance = self._make_guidance_label()
            mode_label = QLabel("输入模式 *")
            mode_label.setBuddy(self.input_mode_selector)
            mode_label.setAccessibleName("输入模式")
            sections["输入"].addRow(mode_label, self.input_mode_selector)
            sections["输入"].addRow(self._guidance_row(self.input_mode_guidance))
            if self.spec.tool_id == "report_af_confidence":
                self.format_detection_label = self._make_guidance_label(
                    "JSON 格式：自动识别。支持可证明为逐残基的 AF2/ColabFold 顶层 "
                    "plddt/pae；AF3 summary 或缺少明确 atom→token/residue 映射的 "
                    "full-data 会停止并说明原因。"
                )
                self.format_detection_label.setAccessibleName("JSON 格式自动识别说明")
                sections["输入"].addRow(self._guidance_row(self.format_detection_label))

        ordered_fields = [
            field
            for section in ordered_sections
            for field in product_fields
            if field.presentation.section == section
        ]
        initial_values = default_values(self.spec)
        for field in ordered_fields:
            widget = self._make_widget(field, initial_values[field.dest])
            label = self._label_for(field)
            label.setBuddy(widget.line_edit if isinstance(widget, PathInput) else widget)
            self._configure_field_widget(field, widget)
            error = QLabel("")
            error.setObjectName(f"{field.dest}Error")
            error.setVisible(False)
            error.setWordWrap(True)
            self.widgets[field.dest] = widget
            self.field_labels[field.dest] = label
            self.error_labels[field.dest] = error
            self.field_tab_order.append(field.dest)
            if isinstance(widget, PathInput):
                self._field_focus_order.extend((widget.line_edit, widget.button))
            else:
                self._field_focus_order.append(widget)
            row = QWidget()
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.addWidget(widget)
            if field.presentation.unit:
                unit = QLabel(field.presentation.unit)
                unit.setAccessibleName(f"{field.label}单位")
                row_layout.addWidget(unit)
            row_layout.addWidget(error)
            self.field_rows[field.dest] = row
            sections[field.presentation.section].addRow(label, row)
        if self.spec.tool_id in PYMOL_REVIEW_TOOL_IDS:
            self.keep_review_script = QCheckBox("保留复核脚本")
            review_help = (
                "默认把 PML 写入会话临时目录并立即在 PyMOL 中打开；"
                "勾选后才使用下方保存路径长期保留脚本。"
            )
            self.keep_review_script.setAccessibleName("保留 PyMOL 复核脚本")
            self.keep_review_script.setAccessibleDescription(review_help)
            self.keep_review_script.setToolTip(review_help)
            self.keep_review_script.stateChanged.connect(
                self._review_script_mode_changed
            )
            sections["输出"].addRow(self.keep_review_script)
            self._field_focus_order.append(self.keep_review_script)
            self._apply_review_script_mode()
        if self.input_mode_selector is not None:
            self.input_mode_selector.currentIndexChanged.connect(self._input_mode_changed)
            self._apply_input_mode()
        return wrapper

    def _review_script_mode_changed(self, _state: int) -> None:
        self._apply_review_script_mode()
        self._pending_review_output = None
        self._field_changed()

    def _apply_review_script_mode(self) -> None:
        if self.keep_review_script is None:
            return
        keep = self.keep_review_script.isChecked()
        output_dest = self._review_output_dest()
        dests = [output_dest] if output_dest is not None else []
        if output_dest == "output":
            dests.append("force")
        for dest in dests:
            row = self.field_rows.get(dest)
            label = self.field_labels.get(dest)
            if row is not None:
                row.setVisible(keep)
            if label is not None:
                label.setVisible(keep)

    def _make_guidance_label(self, text: str = "") -> QLabel:
        label = QLabel(text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        label.setMinimumHeight(36)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return label

    def _guidance_row(self, label: QLabel) -> QWidget:
        row = QFrame()
        row.setObjectName("guidanceRow")
        row.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout = QVBoxLayout(row)
        layout.setContentsMargins(0, 4, 0, 8)
        layout.addWidget(label)
        return row

    def _build_results(self) -> QGroupBox:
        box = QGroupBox("结果")
        self.results_layout = QVBoxLayout(box)
        self._render_results()
        return box

    def _set_result_artifacts(
        self,
        artifacts: tuple[ToolArtifact, ...],
        *,
        completed: bool,
    ) -> None:
        self.result_artifacts = artifacts
        self._result_completed = completed
        self._render_results()

    def _render_results(self) -> None:
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self.output_rows.clear()
        if not self.result_artifacts:
            message = (
                self._completion_message or "此操作未返回文件产物。"
                if self._result_completed
                else "运行成功后将在这里显示脚本返回的产物。"
            )
            self.results_layout.addWidget(QLabel(message))
            return
        if self._completion_message:
            self.results_layout.addWidget(QLabel(self._completion_message))
        for artifact in self.result_artifacts:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            label = QLabel(artifact.label)
            info = QLabel(str(artifact.path))
            info.setWordWrap(True)
            open_button = QPushButton("打开")
            reveal_button = QPushButton("在 Finder 中显示")
            open_button.setAccessibleName(f"打开{artifact.label}")
            reveal_button.setAccessibleName(f"在 Finder 中显示{artifact.label}")
            open_button.setToolTip(f"用默认应用打开：{artifact.path}")
            reveal_button.setToolTip(f"在 Finder 中显示：{artifact.path}")
            open_button.setStatusTip(open_button.toolTip())
            reveal_button.setStatusTip(reveal_button.toolTip())
            open_button.clicked.connect(
                lambda _checked=False, item=artifact: self.open_output(item)
            )
            reveal_button.clicked.connect(
                lambda _checked=False, item=artifact: self.reveal_output(item)
            )
            row_layout.addWidget(label)
            row_layout.addWidget(info, 1)
            row_layout.addWidget(open_button)
            row_layout.addWidget(reveal_button)
            self.results_layout.addWidget(row)
            self.output_rows[artifact.path] = (info, open_button, reveal_button)
        self.update_output_actions()

    def _build_technical_details(self) -> CollapsibleSection:
        holder = QWidget()
        holder_layout = QVBoxLayout(holder)
        self.copy_command_button = QPushButton("复制命令")
        self.copy_command_button.clicked.connect(self._copy_command)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.stdout = QPlainTextEdit()
        self.stdout.setReadOnly(True)
        self.stderr = QPlainTextEdit()
        self.stderr.setReadOnly(True)
        self.workdir_label = QLabel(f"工作目录：{self.runtime.workdir}")
        self.python_label = QLabel(f"Python：{self.runtime.python_executable}")
        self.exit_code = QLabel("尚无退出码")
        holder_layout.addWidget(self.workdir_label)
        holder_layout.addWidget(self.python_label)
        holder_layout.addWidget(self.copy_command_button)
        holder_layout.addWidget(QLabel("命令"))
        holder_layout.addWidget(self.preview)
        holder_layout.addWidget(QLabel("标准输出"))
        holder_layout.addWidget(self.stdout)
        holder_layout.addWidget(QLabel("错误输出"))
        holder_layout.addWidget(self.stderr)
        holder_layout.addWidget(self.exit_code)
        return CollapsibleSection("技术详情", holder)

    def _make_widget(self, field: ToolField, initial_value: Any) -> QWidget:
        presentation = field.presentation
        if field.kind == "bool" or presentation.control == "checkbox":
            widget = QCheckBox()
            widget.setChecked(bool(initial_value))
            widget.stateChanged.connect(
                lambda _state, dest=field.dest: self._field_changed(dest)
            )
            return widget
        if field.kind == "choice" or field.choices:
            widget = QComboBox()
            if field.required and _is_empty(initial_value):
                widget.addItem("")
            widget.addItems(list(field.choices))
            if not _is_empty(initial_value):
                index = widget.findText(str(initial_value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            widget.currentTextChanged.connect(
                lambda _text, dest=field.dest: self._field_changed(dest)
            )
            return widget
        if field.repeatable or presentation.control == "multiline":
            widget = QTextEdit()
            values = initial_value if isinstance(initial_value, (tuple, list)) else ()
            widget.setPlainText("\n".join(str(value) for value in values))
            widget.textChanged.connect(lambda dest=field.dest: self._field_changed(dest))
            return widget
        if _uses_path_browse(field):
            widget = PathInput(
                _browse_mode(field),
                dialog_title=presentation.dialog_title,
                file_filter=presentation.file_filter,
                default_suffix=presentation.default_suffix,
            )
            if not _is_empty(initial_value):
                widget.setText(str(initial_value))
            widget.line_edit.textChanged.connect(
                lambda _text, dest=field.dest: self._field_changed(dest)
            )
            return widget
        widget = QLineEdit()
        if not _is_empty(initial_value):
            widget.setText(str(initial_value))
        widget.textChanged.connect(lambda _text, dest=field.dest: self._field_changed(dest))
        return widget

    def _configure_field_widget(self, field: ToolField, widget: QWidget) -> None:
        help_text = field.help or f"填写{field.label}。"
        if isinstance(widget, PathInput):
            widget.configure_semantics(field.label, help_text, field.presentation.placeholder)
            return
        widget.setAccessibleName(field.label)
        widget.setAccessibleDescription(help_text)
        widget.setToolTip(help_text)
        widget.setStatusTip(help_text)
        if isinstance(widget, QLineEdit):
            widget.setPlaceholderText(field.presentation.placeholder)
        elif isinstance(widget, QTextEdit):
            widget.setPlaceholderText(field.presentation.placeholder)
        elif isinstance(widget, QComboBox):
            widget.setPlaceholderText(f"选择{field.label}")

    def _install_tab_order(self) -> None:
        sequence = [*self._field_focus_order, self.run_button, self.stop_button, self.tech_box]
        for current, following in zip(sequence, sequence[1:]):
            QWidget.setTabOrder(current, following)

    def _read_widget(self, field: ToolField, widget: QWidget) -> Any:
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if isinstance(widget, QTextEdit):
            return [line for line in widget.toPlainText().splitlines() if line]
        if isinstance(widget, PathInput):
            return widget.text()
        if isinstance(widget, QLineEdit):
            return widget.text()
        return ""

    def _non_user_value(self, field: ToolField) -> Any:
        source = field.presentation.value_source
        if source == "runtime":
            return self._runtime_field_value(field)
        if source == "derived":
            return self._derived_field_value(field)
        if source == "fixed":
            if field.presentation.preset is not None:
                return field.presentation.preset
            if field.repeatable and field.default is None:
                return []
            return field.default
        return field.default

    def _runtime_field_value(self, field: ToolField) -> Any:
        raw = os.environ.get(field.presentation.value_key, "").strip()
        if raw:
            if field.repeatable:
                lines = [line for line in raw.splitlines() if line]
                return lines if len(lines) > 1 else shlex.split(raw)
            return raw

        candidates: tuple[Path | str, ...] = ()
        if self.spec.tool_id == "prepare_receptor_pdbqt" and field.dest == "meeko_executable":
            candidates = self._meeko_script_candidates("mk_prepare_receptor.py")
        elif self.spec.tool_id == "prepare_ligand_pdbqt" and field.dest == "meeko_executable":
            candidates = self._meeko_script_candidates("mk_prepare_ligand.py")
        elif self.spec.tool_id == "export_ligand_pdbqt_to_sdf" and field.dest == "meeko_python":
            candidates = (PREFERRED_DOCKING_PYTHON,)
        elif self.spec.tool_id == "generate_maestro_lid":
            if field.dest == "schrodinger_run":
                candidates = (KNOWN_SCHRODINGER_RUN,)
            elif field.dest == "meeko_python":
                candidates = (PREFERRED_DOCKING_PYTHON,)
        for candidate in candidates:
            resolved = _resolve_executable(str(candidate), self.runtime.workdir)
            if resolved is not None and resolved.is_file() and os.access(resolved, os.X_OK):
                return str(resolved)
        return [] if field.repeatable else ""

    def _meeko_script_candidates(self, filename: str) -> tuple[Path, ...]:
        python_path = _resolve_executable(self.runtime.python_executable, self.runtime.workdir)
        candidates: list[Path] = []
        if python_path is not None:
            candidates.append(python_path.parent / filename)
        preferred = PREFERRED_DOCKING_PYTHON.parent / filename
        if preferred not in candidates:
            candidates.append(preferred)
        return tuple(candidates)

    def _derived_field_value(self, field: ToolField) -> Any:
        key = field.presentation.value_key
        if key.startswith("output_format:"):
            output_dest = key.partition(":")[2]
            output_widget = self.widgets.get(output_dest)
            output_text = output_widget.text() if isinstance(output_widget, PathInput) else ""
            if output_text:
                return "json" if Path(output_text).suffix.lower() == ".json" else "text"
        if field.presentation.preset is not None:
            return field.presentation.preset
        if field.repeatable and field.default is None:
            return []
        return field.default

    def _missing_runtime_message(self) -> str:
        messages = {
            "run_geometry_validation": (
                "当前安装未配置经过验证的几何检查适配器（程序、版本和参数模板）。"
                "普通用户表单不再要求手工填写检查程序或原始命令参数。"
            ),
            "summarize_geometry_validation": (
                "当前安装没有与几何检查格式配套的指标映射，不能安全猜测 JSON 内部位置。"
            ),
            "run_restrained_minimization": (
                "当前安装未配置经过验证的最小化适配器，不能安全生成外部程序参数。"
            ),
            "prepare_receptor_pdbqt": "当前安装未检测到可用的 Meeko 受体准备程序。",
            "prepare_ligand_pdbqt": "当前安装未检测到可用的 Meeko 配体准备程序。",
            "export_ligand_pdbqt_to_sdf": (
                "当前安装未检测到同时提供 Meeko 和 RDKit 的 Docking Python。"
            ),
            "generate_maestro_lid": "当前安装未检测到 Schrödinger run 程序。",
        }
        return messages.get(
            self.spec.tool_id,
            f"当前安装未配置 {self.spec.title} 所需的运行组件。",
        )

    def _label_for(self, field: ToolField) -> QLabel:
        suffix = " *" if self._field_is_required(field) else ""
        label = QLabel(f"{field.label}{suffix}")
        label.setAccessibleName(field.label)
        if field.help:
            label.setToolTip(field.help)
        return label

    def _validate_field(self, field: ToolField, value: Any) -> str:
        if self._field_is_required(field) and _is_empty(value):
            return f"请填写{field.label}。"
        if _is_empty(value):
            return ""
        if field.choices and str(value) not in field.choices:
            return f"{field.label}必须从列表中选择。"
        if field.kind == "int":
            try:
                int(str(value))
            except ValueError:
                return f"{field.label}必须是整数。"
        if field.kind == "float":
            try:
                float(str(value))
            except ValueError:
                return f"{field.label}必须是数字。"
        return ""

    def _validate_runtime(self) -> str:
        executable = self.runtime.python_executable.strip()
        resolved_executable = shutil.which(executable)
        if resolved_executable is None:
            candidate = Path(executable).expanduser()
            if not candidate.is_absolute():
                candidate = self.runtime.workdir / candidate
            if not candidate.is_file() or not os.access(candidate, os.X_OK):
                return "当前环境无法启动 Docking 工具。"
        if (
            not self.runtime.workdir.is_absolute()
            or not self.runtime.workdir.is_dir()
            or not os.access(self.runtime.workdir, os.X_OK)
        ):
            return "当前 Docking 工作目录不可用。"
        script = self.runtime.source_root / self.spec.script
        if not self.runtime.source_root.is_absolute() or not script.is_file() or not os.access(script, os.R_OK):
            return "当前安装中找不到这个 Docking 工具。"
        return ""

    def _field_changed(self, dest: str | None = None) -> None:
        if dest is not None:
            self._touched_fields.add(dest)
            if dest in self._output_derivations_by_dest:
                widget = self.widgets.get(dest)
                if isinstance(widget, PathInput):
                    if widget.text() == self._auto_output_values.get(dest, ""):
                        self._manual_output_dests.discard(dest)
                    else:
                        self._manual_output_dests.add(dest)
        self._sync_derived_outputs(changed_source=dest)
        if self.spec.tool_id == "report_af_confidence":
            self._update_af_format_guidance()
        self._hide_problem()
        errors = self._form_errors()
        self._refresh_touched_field_errors(errors)
        self._refresh_section_attention(errors)
        self._schedule_refresh()
        self._refresh_run_enabled()
        self._refresh_form_guidance(errors)

    def _schedule_refresh(self) -> None:
        QTimer.singleShot(0, self._refresh_command)

    def _refresh_command(self) -> ProgramArgs:
        command = self.command()
        self.preview.setPlainText(" ".join(shlex.quote(part) for part in command.argv()))
        return command

    def _append_stdout(self, text: str) -> None:
        self.stdout.moveCursor(QTextCursor.MoveOperation.End)
        self.stdout.insertPlainText(text)

    def _append_stderr(self, text: str) -> None:
        self.stderr.moveCursor(QTextCursor.MoveOperation.End)
        self.stderr.insertPlainText(text)

    def _finished(self, exit_code: int) -> None:
        succeeded = False
        if self._stopping:
            self._show_status("已取消")
            self.exit_code.setText(f"退出码：{exit_code}")
            self._discard_pending_review_output()
        elif exit_code == 0:
            self._show_status("已完成")
            self.exit_code.setText("退出码：0")
            if self.runner.result_error:
                self._set_result_artifacts(self.runner.last_result, completed=True)
                self._show_problem(self.runner.result_error)
                self._discard_pending_review_output()
            elif self.spec.tool_id in PYMOL_REVIEW_TOOL_IDS:
                succeeded = self._finish_pymol_review()
            else:
                self._set_result_artifacts(self.runner.last_result, completed=True)
                succeeded = True
        else:
            partial_status = {
                "run_restrained_minimization": "复核未完成",
                "run_geometry_validation": "检查完成、摘要失败",
            }.get(self.spec.tool_id)
            self._show_status(
                partial_status if self.runner.last_result and partial_status else "运行失败"
            )
            self.exit_code.setText(f"退出码：{exit_code}")
            self._set_result_artifacts(self.runner.last_result, completed=True)
            self._discard_pending_review_output()
            if self.runner.last_result:
                partial_problem = {
                    "run_restrained_minimization": (
                        "最小化结果已保留，但结构映射或复核材料未完成；"
                        "不要把本次结果自动用于下游，请展开技术详情处理原因。"
                    ),
                    "run_geometry_validation": (
                        "几何检查原生结果已保留，但配置指标的摘要提取失败；"
                        "缺失指标没有被当成 0，请展开技术详情处理原因。"
                    ),
                }.get(self.spec.tool_id)
                self._show_problem(
                    partial_problem
                    or "工具未全部成功；已完成的产物仍列在结果中。请展开技术详情查看逐项原因。"
                )
            else:
                self._show_problem("工具运行失败。请展开技术详情查看原始输出。")
        self._set_running(False)
        if succeeded:
            self.run_succeeded.emit(self)
        self.run_stopped.emit(self)

    def _finish_pymol_review(self) -> bool:
        temporary_output = self._pending_review_output
        review_artifact = next(
            (
                artifact
                for artifact in self.runner.last_result
                if artifact.path.suffix.lower() == ".pml"
                and (
                    temporary_output is None
                    or artifact.path.resolve() == temporary_output.resolve()
                )
            ),
            None,
        )
        if review_artifact is None or not review_artifact.path.is_file():
            self._set_result_artifacts(self.runner.last_result, completed=True)
            self._show_problem(
                "复核脚本生成成功，但产物回执中没有可打开的 PML 文件。"
            )
            self._discard_pending_review_output()
            return False

        started = QProcess.startDetached(
            "/usr/bin/open", ["-a", "PyMOL", str(review_artifact.path)]
        )
        detached_ok = started[0] if isinstance(started, tuple) else bool(started)
        if not detached_ok:
            self._set_result_artifacts(self.runner.last_result, completed=True)
            self._show_problem(
                "复核脚本已生成，但无法启动 PyMOL；可从结果区手动打开 PML。"
            )
            return False

        if temporary_output is not None:
            self._completion_message = (
                "已在 PyMOL 中打开；临时复核脚本将在退出工具台时清理。"
            )
            visible_artifacts = tuple(
                artifact
                for artifact in self.runner.last_result
                if artifact.path.resolve() != temporary_output.resolve()
            )
            self._set_result_artifacts(visible_artifacts, completed=True)
            self._pending_review_output = None
        else:
            self._completion_message = "已在 PyMOL 中打开，并保留复核脚本。"
            self._set_result_artifacts(self.runner.last_result, completed=True)
        return True

    def _failed(self, message: str) -> None:
        self.stderr.appendPlainText(message)
        self.exit_code.setText(f"启动错误：{message}")
        self._show_status("运行失败")
        self._show_problem(_friendly_process_error(message))
        self._discard_pending_review_output()
        self._set_running(False)
        self.run_stopped.emit(self)

    def _process_warning(self, message: str) -> None:
        self.stderr.appendPlainText(message)
        if self._stopping:
            return
        self._show_problem(_friendly_process_warning(message))

    def _set_running(self, running: bool) -> None:
        self._running = running
        self.stop_button.setEnabled(running)
        if self.keep_review_script is not None:
            self.keep_review_script.setEnabled(not running)
        self._refresh_run_enabled()

    def _refresh_run_enabled(self) -> None:
        errors = self._form_errors()
        self.run_button.setEnabled(not self._running and not self._global_busy and not errors)

    def _refresh_form_guidance(self, errors: dict[str, str] | None = None) -> None:
        if self._running or self._global_busy:
            return
        current_errors = self._form_errors() if errors is None else errors
        missing_required = any(
            field.user_editable
            and self._field_is_required(field)
            and self._field_is_active(field.dest)
            and _is_empty(
                self._read_widget(field, self.widgets[field.dest])
            )
            for field in self.spec.fields
        )
        if "__runtime__" in current_errors:
            self._show_status("当前安装不可用")
        elif missing_required:
            self._show_status("请先填写带 * 的必填项")
        elif current_errors:
            self._show_status("请修正有误的字段")
        elif self.status.text() in {
            "请先填写带 * 的必填项",
            "当前安装不可用",
            "请修正有误的字段",
        }:
            self._show_status("准备就绪")

    def _show_status(self, text: str) -> None:
        self.status.setText(text)
        self.status.setAccessibleName(f"运行状态：{text}")
        self.status.setAccessibleDescription(text)

    def _show_problem(self, text: str) -> None:
        self.problem.setText(text)
        self.problem.setVisible(True)

    def _hide_problem(self) -> None:
        self.problem.clear()
        self.problem.setVisible(False)

    def _focus_field(self, dest: str) -> None:
        widget = self.widgets[dest]
        target = widget.line_edit if isinstance(widget, PathInput) else widget
        target.setFocus()

    def _copy_command(self) -> None:
        QApplication.clipboard().setText(self.preview.toPlainText())

    def _open_output(self, artifact: ToolArtifact, *, reveal: bool) -> None:
        path = artifact.path
        if not self._path_matches_kind(path, artifact.kind):
            self.update_output_actions()
            return
        if reveal:
            QProcess.startDetached("/usr/bin/open", ["-R", str(path)])
        else:
            QProcess.startDetached("/usr/bin/open", [str(path)])

    def _path_matches_kind(self, path: Path | None, kind: str) -> bool:
        if path is None:
            return False
        if kind in {"directory", "dir", "folder"}:
            return path.is_dir()
        return path.is_file()

    def _current_input_mode(self) -> InputModePresentation | None:
        if self.input_mode_selector is None:
            return None
        key = self.input_mode_selector.currentData()
        return next((mode for mode in self.spec.input_modes if mode.key == key), None)

    def _current_input_mode_key(self) -> str:
        mode = self._current_input_mode()
        return mode.key if mode is not None else ""

    def _field_is_active(self, dest: str) -> bool:
        review_output_dest = self._review_output_dest()
        if (
            self.spec.tool_id in PYMOL_REVIEW_TOOL_IDS
            and self._uses_temporary_review_script()
            and (
                dest == review_output_dest
                or (review_output_dest == "output" and dest == "force")
            )
        ):
            return False
        if not self.spec.input_modes:
            return True
        mode_bound = {
            item
            for mode in self.spec.input_modes
            for item in mode.visible_dests
        }
        if dest not in mode_bound:
            return True
        mode = self._current_input_mode()
        return mode is not None and dest in mode.visible_dests

    def _field_is_required(self, field: ToolField) -> bool:
        if (
            field.dest == self._review_output_dest()
            and self._uses_temporary_review_script()
        ):
            return False
        if (
            self.spec.tool_id == "run_restrained_minimization"
            and field.dest in {"comparison_json", "review_pml"}
        ):
            return True
        if (
            self.spec.tool_id == "run_geometry_validation"
            and field.dest in {"native_result", "metric", "metric_unit"}
        ):
            return True
        if (
            self.spec.tool_id == "prepare_ligand_pdbqt"
            and field.dest in {"atom_map", "mapping_output"}
        ):
            return True
        mode = self._current_input_mode()
        return field.required or (mode is not None and field.dest in mode.required_dests)

    def _input_mode_changed(self, _index: int) -> None:
        self._apply_input_mode()
        self._field_changed()

    def _apply_input_mode(self) -> None:
        mode = self._current_input_mode()
        if mode is None:
            return
        if self.input_mode_guidance is not None:
            self.input_mode_guidance.setText(mode.guidance)
            self.input_mode_guidance.setAccessibleName(f"{mode.label}说明")
        for field in self.spec.fields:
            if not field.user_editable:
                continue
            active = self._field_is_active(field.dest)
            row = self.field_rows.get(field.dest)
            label = self.field_labels.get(field.dest)
            widget = self.widgets.get(field.dest)
            if row is not None:
                row.setVisible(active)
                row.setEnabled(active)
            if label is not None:
                label.setVisible(active)
                label.setText(f"{field.label}{' *' if self._field_is_required(field) else ''}")
            if widget is not None:
                widget.setEnabled(active)
            if not active and field.dest in self.error_labels:
                self.error_labels[field.dest].setVisible(False)

    def _sync_derived_outputs(self, *, changed_source: str | None = None) -> None:
        for derivation in self._output_derivations:
            if changed_source is not None and derivation.source_dest != changed_source:
                continue
            if (
                not self._field_is_active(derivation.source_dest)
                or not self._field_is_active(derivation.output_dest)
                or derivation.output_dest in self._manual_output_dests
            ):
                continue
            source_widget = self.widgets.get(derivation.source_dest)
            output_widget = self.widgets.get(derivation.output_dest)
            if not isinstance(source_widget, PathInput) or not isinstance(
                output_widget, PathInput
            ):
                continue
            derived = self._derived_output_value(derivation, source_widget.text())
            output_widget.line_edit.blockSignals(True)
            try:
                output_widget.setText(derived)
            finally:
                output_widget.line_edit.blockSignals(False)
            self._auto_output_values[derivation.output_dest] = derived

    @staticmethod
    def _derived_output_value(derivation: Any, source: str) -> str:
        if not source:
            return ""
        source_path = Path(source)
        mode = derivation.directory_mode
        if mode == "source_directory":
            return str(source_path)
        if mode == "source_parent_named":
            try:
                name = derivation.name_template.format(
                    stem=source_path.stem,
                    name=source_path.name,
                )
            except (KeyError, ValueError):
                return ""
            return str(source_path.parent / name) if name else ""
        if source_path.name in {"", ".", ".."}:
            return ""
        try:
            name = derivation.name_template.format(
                stem=source_path.stem,
                name=source_path.name,
            )
        except (KeyError, ValueError):
            return ""
        if not name:
            return ""
        if mode in {"source_parent", "source_parent_named", "source_sibling"}:
            return str(source_path.parent / name)
        return ""

    def _update_af_format_guidance(self) -> None:
        if self.format_detection_label is None:
            return
        input_format = str(self._read_widget(
            self.fields_by_dest["input_format"], self.widgets["input_format"]
        )).strip()
        plddt_pointer = str(self._read_widget(
            self.fields_by_dest["plddt_pointer"], self.widgets["plddt_pointer"]
        )).strip()
        pae_pointer = str(self._read_widget(
            self.fields_by_dest["pae_pointer"], self.widgets["pae_pointer"]
        )).strip()
        if not (input_format or plddt_pointer or pae_pointer):
            text = (
                "JSON 格式：自动识别。支持可证明为逐残基的 AF2/ColabFold 顶层 "
                "plddt/pae；AF3 summary 或缺少明确 atom→token/residue 映射的 "
                "full-data 会停止并说明原因。"
            )
        elif input_format and plddt_pointer:
            text = (
                f"JSON 格式：使用专家兼容覆盖（{input_format}）。工具只按已填写的逐残基 "
                "pLDDT/PAE 位置解析，不会再自动猜测。"
            )
        else:
            text = (
                "JSON 格式：专家兼容覆盖尚未填写完整。格式来源和逐残基 pLDDT 位置必须成组填写；"
                "否则不能运行。"
            )
        self.format_detection_label.setText(text)
        self.format_detection_label.setAccessibleDescription(text)


class VinaServerCommandPanel(QWidget):
    """Build and copy one native E2 Vina command without starting a process."""

    _command_options = (
        ("receptor", "--receptor"),
        ("ligand", "--ligand"),
        ("center_x", "--center_x"),
        ("center_y", "--center_y"),
        ("center_z", "--center_z"),
        ("size_x", "--size_x"),
        ("size_y", "--size_y"),
        ("size_z", "--size_z"),
        ("cpu", "--cpu"),
        ("exhaustiveness", "--exhaustiveness"),
        ("num_modes", "--num_modes"),
        ("energy_range", "--energy_range"),
        ("seed", "--seed"),
        ("pose_output", "--out"),
    )
    _path_dests = {
        "server_workdir",
        "vina_executable",
        "receptor",
        "ligand",
        "pose_output",
        "log_output",
    }

    def __init__(
        self,
        settings: QSettings | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.settings = (
            settings
            if settings is not None
            else QSettings(SETTINGS_ORGANIZATION, SETTINGS_APPLICATION)
        )
        self.field_specs = {field.dest: field for field in VINA_COMMAND_FIELDS}
        self.fields: dict[str, QComboBox] = {}

        title = QLabel("生成 E2 原生 Vina 命令")
        title.setObjectName("toolTitle")
        title.setAccessibleName("当前工具：生成 E2 原生 Vina 命令")
        summary = QLabel(
            "只生成并复制 shell 命令；本机不查找或运行 Vina，GUI 也不会通过 SSH 连接服务器。"
            "复制后请在已经登录的 E2 shell 中粘贴执行。"
        )
        summary.setWordWrap(True)
        environment_note = QLabel(
            "已只读确认：E2 默认 PATH 和模块列表中没有 Vina。下面预填的绝对路径可直接运行；"
            "其环境记录为 vina=1.2.6，程序报告 AutoDock Vina 7ac2999-mod。"
        )
        environment_note.setWordWrap(True)
        environment_note.setAccessibleName("E2 Vina 环境说明")
        history_note = QLabel(
            "每个输入框都保存当前值和最近 10 个非空值；可用右侧下拉箭头重选。"
            "离开输入框、复制命令或关闭工具台时都会保存。"
        )
        history_note.setWordWrap(True)
        history_note.setAccessibleName("Vina 字段历史说明")

        section_layouts: dict[str, QFormLayout] = {}
        form_body = QWidget()
        form_layout = QVBoxLayout(form_body)
        form_layout.setContentsMargins(0, 0, 0, 0)
        for section in ("E2 环境", "服务器输入", "搜索盒", "运行参数", "服务器输出"):
            box = QGroupBox(section)
            section_form = QFormLayout(box)
            section_form.setFieldGrowthPolicy(
                QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
            )
            section_layouts[section] = section_form
            form_layout.addWidget(box)

        for field in VINA_COMMAND_FIELDS:
            combo = QComboBox()
            combo.setEditable(True)
            combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            combo.setMaxVisibleItems(VINA_HISTORY_LIMIT)
            combo.setAccessibleName(field.label)
            combo.setAccessibleDescription(
                f"填写{field.label}；下拉列表保留最近 {VINA_HISTORY_LIMIT} 个值。"
            )
            combo.setToolTip(combo.accessibleDescription())
            combo.setStatusTip(combo.toolTip())
            line_edit = combo.lineEdit()
            if line_edit is not None:
                line_edit.setPlaceholderText(field.placeholder)
            label = QLabel(f"{field.label} *")
            label.setBuddy(combo)
            label.setToolTip(combo.toolTip())
            section_layouts[field.section].addRow(label, combo)
            self.fields[field.dest] = combo

        preview_box = QGroupBox("将复制的服务器命令")
        preview_layout = QVBoxLayout(preview_box)
        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setAccessibleName("E2 Vina 命令预览")
        self.preview.setMinimumHeight(245)
        preview_layout.addWidget(self.preview)
        form_layout.addWidget(preview_box)
        form_layout.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(form_body)

        self.problem = QLabel("")
        self.problem.setWordWrap(True)
        self.problem.setVisible(False)
        self.problem.setAccessibleName("Vina 命令字段问题")
        self.status = QLabel("请填写带 * 的全部字段")
        self.status.setAccessibleName("Vina 命令状态")
        self.clear_history_button = QPushButton("清除历史")
        self.clear_history_button.setToolTip("删除所有 Vina 命令字段历史并恢复预设值。")
        self.copy_command_button = QPushButton("复制服务器命令")
        self.copy_command_button.setToolTip(
            "复制命令并保存当前字段；不会启动任何本机或服务器进程（Ctrl+Return）。"
        )
        self.copy_command_button.setAccessibleName("复制 E2 Vina 服务器命令")
        self.copy_shortcut = QShortcut(QKeySequence("Ctrl+Return"), self)
        self.copy_shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
        self.copy_shortcut.activated.connect(self._copy_from_shortcut)

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 8, 0, 0)
        actions_layout.addWidget(self.status)
        actions_layout.addStretch(1)
        actions_layout.addWidget(self.clear_history_button)
        actions_layout.addWidget(self.copy_command_button)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addWidget(summary)
        layout.addWidget(environment_note)
        layout.addWidget(history_note)
        layout.addWidget(scroll, 1)
        layout.addWidget(self.problem)
        layout.addWidget(actions)

        self._restore_fields()
        for dest, combo in self.fields.items():
            combo.editTextChanged.connect(self._refresh_preview)
            combo.activated.connect(
                lambda _index, field_dest=dest: self._save_fields((field_dest,))
            )
            line_edit = combo.lineEdit()
            if line_edit is not None:
                line_edit.editingFinished.connect(
                    lambda field_dest=dest: self._save_fields((field_dest,))
                )
        self.copy_command_button.clicked.connect(self.copy_command)
        self.clear_history_button.clicked.connect(self.clear_history)
        self._refresh_preview()

    def values(self) -> dict[str, str]:
        return {dest: combo.currentText() for dest, combo in self.fields.items()}

    def history_values(self, dest: str) -> tuple[str, ...]:
        combo = self.fields[dest]
        return tuple(combo.itemText(index) for index in range(combo.count()))

    def validation_errors(self) -> dict[str, str]:
        values = self.values()
        errors: dict[str, str] = {}
        for field in VINA_COMMAND_FIELDS:
            raw = values[field.dest]
            if not raw.strip():
                errors[field.dest] = f"请填写{field.label}。"
                continue
            if "\x00" in raw or "\n" in raw or "\r" in raw:
                errors[field.dest] = f"{field.label}不能包含换行或 NUL 字符。"
                continue
            if field.numeric_kind:
                numeric = self._numeric_value(field, raw)
                if numeric is None:
                    errors[field.dest] = (
                        f"{field.label}必须是{'整数' if field.numeric_kind == 'int' else '有限数值'}。"
                    )
                elif field.positive and numeric <= 0:
                    errors[field.dest] = f"{field.label}必须大于 0。"

        for dest in self._path_dests:
            raw = values[dest]
            if raw and raw != raw.strip():
                errors[dest] = (
                    f"{self.field_specs[dest].label}不能以空白开头或结尾。"
                )

        workdir = values["server_workdir"].strip()
        if workdir and not workdir.startswith("/"):
            errors["server_workdir"] = "服务器工作目录必须填写绝对路径。"
        executable = values["vina_executable"].strip()
        if executable and not executable.startswith("/"):
            errors["vina_executable"] = "服务器 Vina 必须填写绝对路径。"
        for dest in ("receptor", "ligand", "pose_output", "log_output"):
            path = values[dest].strip()
            if path.startswith("~") or path.startswith("$"):
                errors[dest] = (
                    f"{self.field_specs[dest].label}请使用相对工作目录路径或服务器绝对路径；"
                    "命令不会展开 ~ 或 shell 变量。"
                )
        if (
            values["pose_output"].strip()
            and values["pose_output"].strip() == values["log_output"].strip()
        ):
            errors["log_output"] = "Vina 日志与姿势输出不能使用同一路径。"
        return errors

    def server_command(self) -> str:
        errors = self.validation_errors()
        if errors:
            raise ValueError(next(iter(errors.values())))
        values = self.values()
        lines = [
            f"cd -- {self._quote_path(values['server_workdir'])} &&",
            f"{shlex.quote(values['vina_executable'])} \\",
        ]
        for dest, option in self._command_options:
            raw = values[dest]
            argument = (
                self._quote_path(raw)
                if dest in self._path_dests
                else shlex.quote(raw.strip())
            )
            lines.append(f"  {option} {argument} \\")
        lines.append(f"  > {self._quote_path(values['log_output'])} 2>&1")
        return "\n".join(lines)

    def copy_command(self) -> None:
        errors = self.validation_errors()
        if errors:
            self._show_problem(next(iter(errors.values())))
            return
        command = self.server_command()
        QApplication.clipboard().setText(command)
        self.save_current_state()
        self.preview.setPlainText(command)
        self.problem.clear()
        self.problem.setVisible(False)
        self.status.setText("已复制；请粘贴到已登录的 E2 shell")

    def save_current_state(self, *, record_history: bool = True) -> None:
        self._save_fields(tuple(self.fields), record_history=record_history)

    def clear_history(self, _checked: bool = False, *, confirm: bool = True) -> None:
        if confirm:
            choice = QMessageBox.question(
                self,
                "清除 Vina 历史",
                "要删除全部服务器路径和科学参数历史，并恢复预设值吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if choice != QMessageBox.StandardButton.Yes:
                return
        self.settings.remove(VINA_SETTINGS_GROUP)
        self.settings.sync()
        for field in VINA_COMMAND_FIELDS:
            combo = self.fields[field.dest]
            blocked = combo.blockSignals(True)
            combo.clear()
            combo.setEditText(field.default)
            combo.blockSignals(blocked)
        self.status.setText("历史已清除；已恢复预设值")
        self._refresh_preview()

    def _copy_from_shortcut(self) -> None:
        if self.copy_command_button.isEnabled():
            self.copy_command_button.click()

    def _refresh_preview(self, _text: str = "") -> None:
        errors = self.validation_errors()
        self.copy_command_button.setEnabled(not errors)
        if errors:
            message = next(iter(errors.values()))
            self.preview.setPlainText(f"# {message}\n# 填写完成后这里会显示可直接粘贴到 E2 的命令。")
            self._show_problem(message)
            self.status.setText("请补全或修正字段")
            return
        self.preview.setPlainText(self.server_command())
        self.problem.clear()
        self.problem.setVisible(False)
        if not self.status.text().startswith("已复制"):
            self.status.setText("命令已就绪；本机不会执行")

    def _restore_fields(self) -> None:
        self.settings.beginGroup(VINA_SETTINGS_GROUP)
        try:
            for field in VINA_COMMAND_FIELDS:
                history = self._coerce_history(
                    self.settings.value(f"history/{field.dest}", [])
                )
                current_key = f"current/{field.dest}"
                current = (
                    str(self.settings.value(current_key, field.default))
                    if self.settings.contains(current_key)
                    else field.default
                )
                combo = self.fields[field.dest]
                combo.addItems(history[:VINA_HISTORY_LIMIT])
                combo.setEditText(current)
        finally:
            self.settings.endGroup()

    def _save_fields(
        self,
        dests: tuple[str, ...],
        *,
        record_history: bool = True,
    ) -> None:
        updated_histories: dict[str, list[str]] = {}
        self.settings.beginGroup(VINA_SETTINGS_GROUP)
        try:
            for dest in dests:
                current = self.fields[dest].currentText()
                self.settings.setValue(f"current/{dest}", current)
                history = self._coerce_history(
                    self.settings.value(f"history/{dest}", [])
                )
                if record_history and current.strip():
                    history = [current, *(item for item in history if item != current)]
                history = history[:VINA_HISTORY_LIMIT]
                self.settings.setValue(f"history/{dest}", history)
                updated_histories[dest] = history
        finally:
            self.settings.endGroup()
        self.settings.sync()
        for dest, history in updated_histories.items():
            combo = self.fields[dest]
            current = combo.currentText()
            blocked = combo.blockSignals(True)
            combo.clear()
            combo.addItems(history)
            combo.setEditText(current)
            combo.blockSignals(blocked)

    @staticmethod
    def _coerce_history(raw: Any) -> list[str]:
        if raw is None:
            return []
        if isinstance(raw, str):
            return [raw] if raw else []
        return [str(item) for item in raw if str(item)]

    @staticmethod
    def _numeric_value(field: VinaCommandField, raw: str) -> float | int | None:
        try:
            if field.numeric_kind == "int":
                return int(raw.strip())
            value = float(raw.strip())
        except ValueError:
            return None
        return value if math.isfinite(value) else None

    @staticmethod
    def _quote_path(value: str) -> str:
        return "'" + value.replace("'", "'\"'\"'") + "'"

    def _show_problem(self, message: str) -> None:
        self.problem.setText(message)
        self.problem.setVisible(True)


class DockingGui(QMainWindow):
    def __init__(
        self,
        source_root: Path | None = None,
        settings: QSettings | None = None,
    ) -> None:
        super().__init__()
        self.source_root = source_root or Path(__file__).resolve().parent
        self.settings = settings
        self.runtime = RuntimeConfig(
            python_executable=discover_cli_python(),
            workdir=self.source_root.parent,
            source_root=self.source_root,
        )
        self.setWindowTitle("Docking 工具台")
        self.resize(1100, 760)
        self.grouped = grouped_tool_specs()
        self.navigation = ToolNavigationTree()
        self.navigation.setHeaderHidden(True)
        self.navigation.setAccessibleName("工具导航")
        self.stack = QStackedWidget()
        self.panels: dict[str, ToolPanel] = {}
        self._panel_indexes: dict[str, int] = {}
        self.vina_command_panel: VinaServerCommandPanel | None = None
        self._active_panel: ToolPanel | None = None
        self._close_after_stop = False

        splitter = QSplitter()
        splitter.addWidget(self.navigation)
        splitter.addWidget(self.stack)
        splitter.setSizes([280, 820])
        main = QWidget()
        main_layout = QVBoxLayout(main)
        main_layout.addWidget(splitter, 1)
        self.setCentralWidget(main)
        self._populate()
        self.navigation.currentItemChanged.connect(self._select_item)
        self.focus_navigation_shortcut = QShortcut(QKeySequence("Ctrl+L"), self)
        self.focus_navigation_shortcut.setContext(Qt.ShortcutContext.WindowShortcut)
        self.focus_navigation_shortcut.activated.connect(self.navigation.setFocus)
        self._select_first_tool()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - Qt API shape
        if self.vina_command_panel is not None:
            self.vina_command_panel.save_current_state()
        panel = self._active_panel
        if panel is not None and panel.runner.is_running():
            choice = QMessageBox.question(
                self,
                "任务仍在运行",
                "当前任务仍在运行。要停止任务并退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if choice != QMessageBox.StandardButton.Yes:
                event.ignore()
                return
            if self._active_panel is panel and panel.runner.is_running():
                self._close_after_stop = True
                panel.stop()
                event.ignore()
                return
        for item in self.panels.values():
            item.cleanup_transient_files()
        event.accept()

    def _populate(self) -> None:
        for group, specs in self.grouped.items():
            is_vina_group = any(spec.group_id == VINA_GROUP_ID for spec in specs)
            visible_specs = tuple(
                spec
                for spec in specs
                if spec.tool_id not in GUI_MERGED_HELPER_TOOL_IDS
            )
            if not visible_specs and not is_vina_group:
                continue
            group_item = QTreeWidgetItem([group])
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.navigation.addTopLevelItem(group_item)
            if is_vina_group:
                command_panel = VinaServerCommandPanel(settings=self.settings)
                self.vina_command_panel = command_panel
                index = self.stack.addWidget(command_panel)
                item = QTreeWidgetItem(["Vina 服务器命令"])
                item.setData(0, Qt.ItemDataRole.UserRole, VINA_COMMAND_NAV_ID)
                group_item.addChild(item)
                self._panel_indexes[VINA_COMMAND_NAV_ID] = index
                group_item.setExpanded(True)
                continue
            for spec in visible_specs:
                item = QTreeWidgetItem([spec.title])
                item.setData(0, Qt.ItemDataRole.UserRole, spec.tool_id)
                group_item.addChild(item)
                panel = ToolPanel(spec, self.runtime)
                panel.run_requested.connect(self._start_panel)
                panel.run_stopped.connect(self._clear_active_panel)
                index = self.stack.addWidget(panel)
                self.panels[spec.tool_id] = panel
                self._panel_indexes[spec.tool_id] = index
            group_item.setExpanded(True)

    def _select_first_tool(self) -> None:
        for group_index in range(self.navigation.topLevelItemCount()):
            group = self.navigation.topLevelItem(group_index)
            if group.childCount():
                self.navigation.setCurrentItem(group.child(0))
                return

    def _select_item(self, current: QTreeWidgetItem | None, _previous: QTreeWidgetItem | None) -> None:
        if current is None:
            return
        tool_id = current.data(0, Qt.ItemDataRole.UserRole)
        if not tool_id:
            return
        self.stack.setCurrentIndex(self._panel_indexes[tool_id])

    def _start_panel(self, panel: ToolPanel, command: ProgramArgs) -> None:
        if self._active_panel is not None:
            panel._discard_pending_review_output()
            if self._active_panel is panel:
                panel._show_problem("当前工具正在运行，请等待或停止后再运行。")
            else:
                panel._show_problem(
                    f"{self._active_panel.spec.title} 正在运行，请等待或停止后再运行。"
                )
            return
        self._active_panel = panel
        for other in self.panels.values():
            other.set_global_busy(other is not panel, panel.spec.title)
        panel.start_approved_run(command)

    def _clear_active_panel(self, panel: ToolPanel) -> None:
        if self._active_panel is panel:
            self._active_panel = None
        for other in self.panels.values():
            other.set_global_busy(False)
        if self._close_after_stop:
            self._close_after_stop = False
            self.close()


def _uses_path_browse(field: ToolField) -> bool:
    return _is_path_field(field)


def _is_path_field(field: ToolField) -> bool:
    return bool(field.presentation.path_kind) or field.presentation.control == "path"


def _contains_path_separator(value: str) -> bool:
    return os.sep in value or bool(os.altsep and os.altsep in value)


def _resolve_executable(value: str, workdir: Path) -> Path | None:
    if not _contains_path_separator(value):
        resolved = shutil.which(value)
        return Path(resolved) if resolved else None
    path = Path(value).expanduser()
    return path if path.is_absolute() else workdir / path


def _browse_mode(field: ToolField) -> str:
    kind = field.presentation.path_kind
    if kind in {"directory", "input_dir", "output_dir"}:
        return "directory"
    if kind in {"output_file", "save"}:
        return "save"
    return "open"


def _is_empty(value: Any) -> bool:
    return value is None or value == "" or value == []


def _friendly_process_error(message: str) -> str:
    mapping = {
        "FailedToStart": "无法启动工具。请检查 Python 或外部程序路径是否存在并可执行。",
        "Crashed": "工具异常退出。请展开技术详情查看原始输出。",
        "Timedout": "工具启动超时。请检查运行环境后重试。",
        "WriteError": "无法向工具发送输入。请检查运行环境后重试。",
        "ReadError": "无法读取工具输出。请检查运行环境后重试。",
    }
    return mapping.get(message, f"无法启动工具：{message}")


def _friendly_process_warning(message: str) -> str:
    mapping = {
        "Crashed": "工具异常退出；正在等待进程结束以恢复界面。",
        "Timedout": "进程操作超时；任务仍受工具台管理。",
        "WriteError": "无法向工具发送数据；任务仍受工具台管理。",
        "ReadError": "无法读取工具输出；任务仍受工具台管理。",
    }
    return mapping.get(message, f"进程报告异常：{message}；任务仍受工具台管理。")


def configure_application_identity() -> None:
    QApplication.setApplicationName("Docking 工具台")
    QApplication.setApplicationDisplayName("Docking 工具台")


def main() -> int:
    configure_application_identity()
    app = QApplication(sys.argv)
    window = DockingGui()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
