import logging
import re
from PyQt6 import QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QPushButton,
    QGroupBox,
    QComboBox,
    QCompleter,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QWidget,
    QFormLayout,
    QSizePolicy,
    QScrollArea,
)

from .mixins import Dialog3DPickingMixin

from .constants import (
    ALL_GAUSSIAN_METHODS,
    ALL_GAUSSIAN_BASIS_SETS,
    DFT_METHODS,
    DOUBLE_HYBRID_METHODS,
    WAVEFUNCTION_METHODS,
    HF_METHODS,
    SEMI_EMPIRICAL_METHODS,
    POPLE_BASIS_SETS,
    DUNNING_BASIS_SETS,
    DEF2_BASIS_SETS,
    ECP_BASIS_SETS,
    SOLVATION_MODELS,
    GAUSSIAN_SOLVENTS,
    DISPERSION_OPTIONS,
    JOB_TYPES,
    POP_OPTIONS,
    GRID_OPTIONS,
    SCF_GUESS_OPTIONS,
)


_MODRED_PREFIXES = {1: "X", 2: "B", 3: "A", 4: "D"}
_MODRED_PREFIX_COUNTS = {"X": 1, "B": 2, "A": 3, "D": 4}
_MODRED_LINE_RE = re.compile(
    r"^\s*([XBAD])((?:\s+\d+){1,4})\s+([FS])(?:\s+(\d+)\s+([0-9.eE+-]+))?\s*$",
    re.IGNORECASE,
)


def format_modredundant_line(indices, is_scan=False, steps=10, step_size=0.1):
    """Format a Gaussian ModRedundant line from 1-based atom indices.

    Freeze:  ``B 1 2 F``   Scan: ``B 1 2 S 10 0.10``
    """
    prefix = _MODRED_PREFIXES.get(len(indices))
    if prefix is None:
        raise ValueError(f"ModRedundant needs 1-4 atoms, got {len(indices)}")
    idx_str = " ".join(str(i) for i in indices)
    if is_scan:
        return f"{prefix} {idx_str} S {int(steps)} {float(step_size):.2f}"
    return f"{prefix} {idx_str} F"


def parse_modredundant_line(line):
    """Parse a builder-format ModRedundant line.

    Returns (indices_1based, is_scan, steps, step_size) or None when the
    line is not a constraint line (Gen basis, $NBO, comments, ...).
    """
    m = _MODRED_LINE_RE.match(line)
    if not m:
        return None
    prefix = m.group(1).upper()
    indices = [int(x) for x in m.group(2).split()]
    if _MODRED_PREFIX_COUNTS[prefix] != len(indices):
        return None
    is_scan = m.group(3).upper() == "S"
    if is_scan and not m.group(4):
        return None
    steps = int(m.group(4)) if m.group(4) else 10
    step_size = float(m.group(5)) if m.group(5) else 0.1
    return indices, is_scan, steps, step_size


def _split_route_tokens(route):
    """Split a route line on whitespace, but keep parenthesised groups intact."""
    tokens = []
    buf = ""
    depth = 0
    for ch in route:
        if ch == "(":
            depth += 1
            buf += ch
        elif ch == ")":
            depth = max(0, depth - 1)
            buf += ch
        elif ch.isspace() and depth == 0:
            if buf:
                tokens.append(buf)
                buf = ""
        else:
            buf += ch
    if buf:
        tokens.append(buf)
    return tokens


class GaussianRouteBuilderDialog(Dialog3DPickingMixin, QDialog):
    """Dialog to construct the Gaussian route (#) line."""

    def __init__(self, parent=None, current_route="", mol=None, main_window=None):
        QDialog.__init__(self, parent)
        Dialog3DPickingMixin.__init__(self)
        self.setWindowTitle("Gaussian Route Builder")
        self.resize(750, 650)
        self.setModal(False)
        self.ui_ready = False
        self.current_route = current_route
        self.mol = mol
        self.main_window = main_window
        self.selected_atoms = []
        self.setup_ui()
        self.parse_route(current_route)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def setup_ui(self):
        layout = QVBoxLayout()

        self.tabs = QTabWidget()

        self.tab_method = QWidget()
        self.setup_method_tab()
        self.tabs.addTab(self.tab_method, "Method/Basis")

        self.tab_job = QWidget()
        self.setup_job_tab()
        self.tabs.addTab(self.tab_job, "Job Type")

        self.tab_solvation = QWidget()
        self.setup_solvation_tab()
        self.tabs.addTab(self.tab_solvation, "Solvation/Dispersion")

        self.tab_props = QWidget()
        self.setup_props_tab()
        self.tabs.addTab(self.tab_props, "Properties")

        self.tab_constraints = QWidget()
        self.setup_constraints_tab()
        self.tabs.addTab(self.tab_constraints, "Constraints/Scan")
        self.tabs.currentChanged.connect(self.on_tab_changed)

        layout.addWidget(self.tabs)

        preview_group = QGroupBox("Route Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet(
            "font-weight: bold; color: blue; font-size: 14px;"
        )
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        btn_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_cancel.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.btn_ok = QPushButton("Apply")
        self.btn_ok.clicked.connect(self.accept)
        self.btn_ok.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_ok)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        self.connect_signals()
        self.ui_ready = True
        self.update_ui_state()
        self.update_preview()

    def setup_method_tab(self):
        layout = QFormLayout()

        self.print_level = QComboBox()
        self.print_level.addItems(
            ["Additional Output (#P)", "Standard Output (#)", "Terse Output (#T)"]
        )
        self.print_level.setCurrentIndex(0)
        layout.addRow("Print Level:", self.print_level)

        self.method_type = QComboBox()
        self.method_type.addItems(
            [
                "DFT",
                "Double Hybrid",
                "Wavefunction (MP2/CC)",
                "Hartree-Fock",
                "Semi-Empirical",
                "All Methods",
            ]
        )
        self.method_type.currentIndexChanged.connect(self.update_method_list)
        layout.addRow("Method Type:", self.method_type)

        self.method_name = QComboBox()
        self.method_name.setEditable(True)
        m_completer = QCompleter(ALL_GAUSSIAN_METHODS, self)
        m_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        m_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.method_name.setCompleter(m_completer)
        self.update_method_list()
        layout.addRow("Method:", self.method_name)

        self.basis_set = QComboBox()
        self.basis_set.setEditable(True)
        basis_groups = (
            ["--- Pople ---"]
            + POPLE_BASIS_SETS
            + ["--- Dunning (cc-pV) ---"]
            + DUNNING_BASIS_SETS
            + ["--- Karlsruhe (def2) ---"]
            + DEF2_BASIS_SETS
            + ["--- ECP/Gen ---"]
            + ECP_BASIS_SETS
        )
        self.basis_set.addItems(basis_groups)
        b_completer = QCompleter(ALL_GAUSSIAN_BASIS_SETS, self)
        b_completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        b_completer.setFilterMode(QtCore.Qt.MatchFlag.MatchContains)
        self.basis_set.setCompleter(b_completer)
        self.basis_set.setCurrentText("6-31G(d)")
        layout.addRow("Basis Set:", self.basis_set)

        self.second_basis = QLineEdit()
        self.second_basis.setPlaceholderText(
            "optional second basis for // compound model chemistry"
        )
        layout.addRow("Second Basis (//):", self.second_basis)

        self.tab_method.setLayout(layout)

    def update_method_list(self):
        mtype = self.method_type.currentText()
        current_text = self.method_name.currentText()

        self.method_name.blockSignals(True)
        self.method_name.clear()

        if mtype == "DFT":
            self.method_name.addItems(DFT_METHODS)
        elif mtype == "Double Hybrid":
            self.method_name.addItems(DOUBLE_HYBRID_METHODS)
        elif "Wavefunction" in mtype:
            self.method_name.addItems(WAVEFUNCTION_METHODS)
        elif mtype == "Hartree-Fock":
            self.method_name.addItems(HF_METHODS)
        elif mtype == "Semi-Empirical":
            self.method_name.addItems(SEMI_EMPIRICAL_METHODS)
        else:
            self.method_name.addItems(ALL_GAUSSIAN_METHODS)

        if mtype == "All Methods" and current_text:
            self.method_name.setCurrentText(current_text)
        elif self.method_name.count() > 0:
            self.method_name.setCurrentIndex(0)

        self.method_name.blockSignals(False)
        self.update_ui_state()
        self.update_preview()

    def setup_job_tab(self):
        layout = QVBoxLayout()

        self.job_type = QComboBox()
        self.job_type.addItems(JOB_TYPES)
        layout.addWidget(QLabel("Job Task:"))
        layout.addWidget(self.job_type)
        self.job_type.currentIndexChanged.connect(self.update_ui_state)

        self.opt_group = QGroupBox("Optimization Options")
        opt_layout = QHBoxLayout()
        self.opt_tight = QCheckBox("Tight")
        self.opt_verytight = QCheckBox("VeryTight")
        self.opt_calcfc = QCheckBox("CalcFC")
        self.opt_calcall = QCheckBox("CalcAll")
        self.opt_maxcycles = QSpinBox()
        self.opt_maxcycles.setRange(0, 9999)
        self.opt_maxcycles.setSpecialValueText("(default)")
        self.opt_maxcycles.setPrefix("MaxCycles=")
        opt_layout.addWidget(self.opt_tight)
        opt_layout.addWidget(self.opt_verytight)
        opt_layout.addWidget(self.opt_calcfc)
        opt_layout.addWidget(self.opt_calcall)
        opt_layout.addWidget(self.opt_maxcycles)
        self.opt_group.setLayout(opt_layout)
        layout.addWidget(self.opt_group)

        self.freq_group = QGroupBox("Freq Options")
        freq_layout = QHBoxLayout()
        self.freq_raman = QCheckBox("Raman")
        self.freq_noraman = QCheckBox("NoRaman")
        self.freq_vcd = QCheckBox("VCD")
        self.freq_anharm = QCheckBox("Anharmonic")
        freq_layout.addWidget(self.freq_raman)
        freq_layout.addWidget(self.freq_noraman)
        freq_layout.addWidget(self.freq_vcd)
        freq_layout.addWidget(self.freq_anharm)
        self.freq_group.setLayout(freq_layout)
        layout.addWidget(self.freq_group)

        self.irc_group = QGroupBox("IRC Options")
        irc_layout = QHBoxLayout()
        self.irc_calcfc = QCheckBox("CalcFC")
        self.irc_maxpoints = QSpinBox()
        self.irc_maxpoints.setRange(0, 999)
        self.irc_maxpoints.setSpecialValueText("(default)")
        self.irc_maxpoints.setPrefix("MaxPoints=")
        irc_layout.addWidget(self.irc_calcfc)
        irc_layout.addWidget(self.irc_maxpoints)
        self.irc_group.setLayout(irc_layout)
        layout.addWidget(self.irc_group)

        layout.addStretch()
        self.tab_job.setLayout(layout)

    def setup_solvation_tab(self):
        layout = QFormLayout()

        self.solv_model = QComboBox()
        self.solv_model.addItems(SOLVATION_MODELS)
        self.solv_model.currentIndexChanged.connect(self.update_ui_state)
        layout.addRow("Solvation Model:", self.solv_model)

        self.solvent = QComboBox()
        self.solvent.setEditable(True)
        self.solvent.addItems(GAUSSIAN_SOLVENTS)
        layout.addRow("Solvent:", self.solvent)

        self.dispersion = QComboBox()
        self.dispersion.addItems(DISPERSION_OPTIONS)
        layout.addRow("Dispersion (EmpiricalDispersion):", self.dispersion)

        self.tab_solvation.setLayout(layout)

    def setup_props_tab(self):
        inner = QWidget()
        layout = QFormLayout()

        self.pop_combo = QComboBox()
        self.pop_combo.addItems(POP_OPTIONS)
        layout.addRow("Population Analysis (Pop):", self.pop_combo)

        self.density_chk = QCheckBox("Density=Current")
        layout.addRow(self.density_chk)

        self.symmetry_combo = QComboBox()
        self.symmetry_combo.addItems(["Default", "Loose (Symmetry=Loose)", "None (NoSymm)"])
        layout.addRow("Symmetry:", self.symmetry_combo)

        self.grid_combo = QComboBox()
        self.grid_combo.addItems(GRID_OPTIONS)
        layout.addRow("Integration Grid:", self.grid_combo)

        layout.addRow(QLabel("— TD-DFT —"))
        self.td_enable = QCheckBox("Enable TD")
        layout.addRow(self.td_enable)
        self.td_nstates = QSpinBox()
        self.td_nstates.setRange(1, 500)
        self.td_nstates.setValue(6)
        layout.addRow("NStates:", self.td_nstates)
        self.td_states_type = QComboBox()
        self.td_states_type.addItems(["Default", "Singlets", "Triplets", "50-50"])
        layout.addRow("States:", self.td_states_type)
        self.td_root = QSpinBox()
        self.td_root.setRange(0, 500)
        self.td_root.setSpecialValueText("(default)")
        self.td_root.setPrefix("Root=")
        layout.addRow(self.td_root)

        layout.addRow(QLabel("— NMR / Polarizability —"))
        self.nmr_chk = QCheckBox("NMR (GIAO)")
        layout.addRow(self.nmr_chk)
        self.polar_chk = QCheckBox("Polar")
        layout.addRow(self.polar_chk)

        layout.addRow(QLabel("— Output —"))
        self.output_combo = QComboBox()
        self.output_combo.addItems(["None", "WFN", "WFX"])
        layout.addRow("Output=:", self.output_combo)
        self.gfinput_chk = QCheckBox("GFInput")
        layout.addRow(self.gfinput_chk)

        layout.addRow(QLabel("— SCF —"))
        self.scf_xqc = QCheckBox("XQC")
        layout.addRow(self.scf_xqc)
        self.scf_tight = QCheckBox("Tight")
        layout.addRow(self.scf_tight)
        self.scf_guess = QComboBox()
        self.scf_guess.addItems(SCF_GUESS_OPTIONS)
        layout.addRow("Guess=:", self.scf_guess)

        inner.setLayout(layout)

        scroll = QScrollArea()
        scroll.setWidget(inner)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)
        self.tab_props.setLayout(tab_layout)

    def setup_constraints_tab(self):
        layout = QVBoxLayout()

        info_label = QLabel(
            "Select 1-4 atoms in the 3D view to add ModRedundant constraints "
            "or scans.\n1: Atom (X), 2: Distance (B), 3: Angle (A), 4: Dihedral (D)\n"
            "Lines are appended to Additional Input on Apply and require "
            "Opt=ModRedundant (added automatically)."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.selection_label = QLabel("Selected atoms: None")
        self.selection_label.setStyleSheet("font-weight: bold; color: #D32F2F;")
        layout.addWidget(self.selection_label)

        self.constraint_table = QTableWidget()
        self.constraint_table.setColumnCount(6)
        self.constraint_table.setHorizontalHeaderLabels(
            ["Type", "Atoms (1-based)", "Value", "Scan?", "Steps", "Step Size"]
        )
        self.constraint_table.itemSelectionChanged.connect(
            self.update_selection_display
        )
        self.constraint_table.itemChanged.connect(self.update_preview)
        layout.addWidget(self.constraint_table)

        btn_layout = QHBoxLayout()
        self.btn_add_const = QPushButton("Add Constraint")
        self.btn_add_const.setEnabled(False)
        self.btn_add_const.clicked.connect(self.add_constraint)
        btn_layout.addWidget(self.btn_add_const)

        self.btn_remove_const = QPushButton("Remove Selected")
        self.btn_remove_const.clicked.connect(self.remove_constraint)
        btn_layout.addWidget(self.btn_remove_const)

        self.btn_clear_const = QPushButton("Clear All")
        self.btn_clear_const.clicked.connect(self.clear_all_constraints)
        btn_layout.addWidget(self.btn_clear_const)

        layout.addLayout(btn_layout)
        self.tab_constraints.setLayout(layout)

    # ------------------------------------------------------------------
    # 3D picking (Dialog3DPickingMixin callbacks)
    # ------------------------------------------------------------------

    def on_tab_changed(self, index):
        if self.tabs.currentWidget() == self.tab_constraints:
            self.enable_picking()
        else:
            self.disable_picking()

    def on_atom_picked(self, atom_idx):
        if atom_idx in self.selected_atoms:
            self.selected_atoms.remove(atom_idx)
        else:
            if len(self.selected_atoms) >= 4:
                self.selected_atoms.pop(0)
            self.selected_atoms.append(atom_idx)
        self.update_selection_display()

    def clear_selection(self):
        self.selected_atoms = []
        self.update_selection_display()

    def update_selection_display(self):
        all_to_label = []  # list of (idx, label_text)
        for i, idx in enumerate(self.selected_atoms):
            all_to_label.append((idx, f"P{i + 1}"))

        selected_rows = set(
            index.row() for index in self.constraint_table.selectedIndexes()
        )
        for row in selected_rows:
            idx_item = self.constraint_table.item(row, 1)
            if idx_item:
                try:
                    # Table shows 1-based indices; labels need 0-based
                    row_indices = [int(i) - 1 for i in idx_item.text().split()]
                    for i, idx in enumerate(row_indices):
                        all_to_label.append((idx, f"C{row + 1}:A{i + 1}"))
                except Exception as _e:
                    logging.warning("update_selection_display: %s", _e)

        self.show_atom_labels_for(all_to_label, color="yellow")

        n = len(self.selected_atoms)
        txt = "None"
        can_add = False
        if n > 0:
            indices_txt = ", ".join(str(i + 1) for i in self.selected_atoms)
            types = {1: "Atom", 2: "Distance", 3: "Angle", 4: "Dihedral"}
            txt = f"[{indices_txt}] ({types.get(n, 'Unknown')})"
            can_add = True

        self.selection_label.setText(f"Selected atoms: {txt}")
        self.btn_add_const.setEnabled(can_add)

    def add_constraint(self):
        n = len(self.selected_atoms)
        if n == 0 or not self.mol:
            return
        indices_1based = [i + 1 for i in self.selected_atoms]
        self._insert_constraint_row(indices_1based)
        self.selected_atoms = []
        self.update_selection_display()
        self.update_preview()

    def _insert_constraint_row(
        self, indices_1based, is_scan=False, steps=10, step_size=None
    ):
        """Append a table row for the given 1-based atom indices."""
        n = len(indices_1based)
        c_type = {1: "Atom", 2: "Distance", 3: "Angle", 4: "Dihedral"}.get(n, "")

        val = 0.0
        try:
            from rdkit.Chem import rdMolTransforms

            conf = self.mol.GetConformer()
            zero = [i - 1 for i in indices_1based]
            if n == 2:
                val = rdMolTransforms.GetBondLength(conf, *zero)
            elif n == 3:
                val = rdMolTransforms.GetAngleDeg(conf, *zero)
            elif n == 4:
                val = rdMolTransforms.GetDihedralDeg(conf, *zero)
        except Exception as _e:
            logging.warning("constraint value calc failed: %s", _e)

        row = self.constraint_table.rowCount()
        self.constraint_table.insertRow(row)

        def create_centered_item(text):
            item = QTableWidgetItem(text)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            return item

        self.constraint_table.setItem(row, 0, create_centered_item(c_type))
        idx_str = " ".join(str(i) for i in indices_1based)
        self.constraint_table.setItem(row, 1, create_centered_item(idx_str))
        self.constraint_table.setItem(row, 2, create_centered_item(f"{val:.3f}"))

        chk_scan = QCheckBox()
        chk_scan.setChecked(is_scan)
        chk_widget = QWidget()
        chk_layout = QHBoxLayout(chk_widget)
        chk_layout.addWidget(chk_scan)
        chk_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chk_layout.setContentsMargins(0, 0, 0, 0)
        self.constraint_table.setCellWidget(row, 3, chk_widget)
        chk_scan.stateChanged.connect(self.update_preview)

        self.constraint_table.setItem(row, 4, create_centered_item(str(int(steps))))
        if step_size is None:
            step_size = 0.1 if n == 2 else 10.0  # Å for bonds, degrees otherwise
        self.constraint_table.setItem(
            row, 5, create_centered_item(f"{float(step_size):.2f}")
        )

    def load_modredundant_lines(self, lines):
        """Rebuild the constraint table from tail ModRedundant lines (sync in)."""
        parsed = [
            p for p in (parse_modredundant_line(line) for line in lines) if p
        ]
        self.constraint_table.setRowCount(0)
        for indices, is_scan, steps, step_size in parsed:
            self._insert_constraint_row(indices, is_scan, steps, step_size)
        self.update_preview()

    def remove_constraint(self):
        rows = set(index.row() for index in self.constraint_table.selectedIndexes())
        for row in sorted(rows, reverse=True):
            self.constraint_table.removeRow(row)
        self.update_preview()

    def clear_all_constraints(self):
        self.constraint_table.setRowCount(0)
        self.update_preview()

    def get_modredundant_lines(self):
        """Return the ModRedundant tail lines for all table rows."""
        lines = []
        table = getattr(self, "constraint_table", None)
        if table is None:
            return lines
        for r in range(table.rowCount()):
            idx_item = table.item(r, 1)
            if not idx_item:
                continue
            try:
                indices = [int(i) for i in idx_item.text().split()]
            except ValueError:
                continue

            is_scan = False
            chk_widget = table.cellWidget(r, 3)
            if chk_widget:
                chk_scan = chk_widget.findChild(QCheckBox)
                if chk_scan:
                    is_scan = chk_scan.isChecked()

            steps_item = table.item(r, 4)
            step_item = table.item(r, 5)
            try:
                steps = int(steps_item.text()) if steps_item else 10
                step_size = float(step_item.text()) if step_item else 0.1
            except ValueError:
                steps, step_size = 10, 0.1

            try:
                lines.append(
                    format_modredundant_line(indices, is_scan, steps, step_size)
                )
            except ValueError as _e:
                logging.warning("get_modredundant_lines: %s", _e)
        return lines

    # ------------------------------------------------------------------
    # State save/restore (for reopening the non-modal dialog in sync)
    # ------------------------------------------------------------------

    def store_state(self):
        self._saved_state = {}
        for name, widget in self.__dict__.items():
            if isinstance(widget, QComboBox):
                self._saved_state[name] = widget.currentText()
            elif isinstance(widget, QCheckBox):
                self._saved_state[name] = widget.isChecked()
            elif isinstance(widget, QSpinBox):
                self._saved_state[name] = widget.value()
            elif isinstance(widget, QLineEdit):
                self._saved_state[name] = widget.text()

    def restore_state(self):
        if getattr(self, "_saved_state", None) is None:
            return
        self.ui_ready = False
        for name, val in self._saved_state.items():
            widget = getattr(self, name, None)
            if widget is None:
                continue
            if isinstance(widget, QComboBox):
                widget.setCurrentText(val)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(val)
            elif isinstance(widget, QSpinBox):
                widget.setValue(val)
            elif isinstance(widget, QLineEdit):
                widget.setText(val)
        self.ui_ready = True
        self.update_preview()

    # ------------------------------------------------------------------
    # Signals / UI state
    # ------------------------------------------------------------------

    def connect_signals(self):
        widgets = [
            self.print_level,
            self.method_type,
            self.method_name,
            self.basis_set,
            self.second_basis,
            self.job_type,
            self.opt_tight,
            self.opt_verytight,
            self.opt_calcfc,
            self.opt_calcall,
            self.opt_maxcycles,
            self.freq_raman,
            self.freq_noraman,
            self.freq_vcd,
            self.freq_anharm,
            self.irc_calcfc,
            self.irc_maxpoints,
            self.solv_model,
            self.solvent,
            self.dispersion,
            self.pop_combo,
            self.density_chk,
            self.symmetry_combo,
            self.grid_combo,
            self.td_enable,
            self.td_nstates,
            self.td_states_type,
            self.td_root,
            self.nmr_chk,
            self.polar_chk,
            self.output_combo,
            self.gfinput_chk,
            self.scf_xqc,
            self.scf_tight,
            self.scf_guess,
        ]
        for w in widgets:
            if isinstance(w, QComboBox):
                w.currentIndexChanged.connect(self.update_preview)
                if w.isEditable():
                    w.currentTextChanged.connect(self.update_preview)
            elif isinstance(w, QCheckBox):
                w.toggled.connect(self.update_preview)
            elif isinstance(w, QSpinBox):
                w.valueChanged.connect(self.update_preview)
            elif isinstance(w, QLineEdit):
                w.textChanged.connect(self.update_preview)

    def update_ui_state(self):
        if not getattr(self, "ui_ready", False):
            return

        method_text = self.method_name.currentText().upper()
        is_semi = method_text in [m.upper() for m in SEMI_EMPIRICAL_METHODS]
        self.basis_set.setEnabled(not is_semi)
        self.second_basis.setEnabled(not is_semi)

        job_txt = self.job_type.currentText()
        is_opt = "Opt" in job_txt
        is_freq = "Freq" in job_txt
        is_irc = "IRC" in job_txt
        self.opt_group.setVisible(is_opt)
        self.freq_group.setVisible(is_freq)
        self.irc_group.setVisible(is_irc)

        is_solvated = self.solv_model.currentText() != "None"
        self.solvent.setEnabled(is_solvated)

    # ------------------------------------------------------------------
    # Route construction
    # ------------------------------------------------------------------

    def update_preview(self):
        if not getattr(self, "ui_ready", False):
            return
        self.update_ui_state()

        lvl_map = {0: "#P", 1: "#", 2: "#T"}
        route_parts = [lvl_map.get(self.print_level.currentIndex(), "#P")]

        method = self.method_name.currentText()
        method_upper = method.upper()
        is_semi = method_upper in [m.upper() for m in SEMI_EMPIRICAL_METHODS]

        if is_semi:
            route_parts.append(method)
        else:
            basis = self.basis_set.currentText()
            mb = f"{method}/{basis}" if basis else method
            second = self.second_basis.text().strip()
            if second:
                mb += f"//{method}/{second}"
            route_parts.append(mb)

        # Job type
        job_idx = self.job_type.currentIndex()
        job_txt = self.job_type.currentText()
        opt_opts = []
        if self.opt_tight.isChecked():
            opt_opts.append("Tight")
        if self.opt_verytight.isChecked():
            opt_opts.append("VeryTight")
        if self.opt_calcfc.isChecked():
            opt_opts.append("CalcFC")
        if self.opt_calcall.isChecked():
            opt_opts.append("CalcAll")
        if self.opt_maxcycles.value() > 0:
            opt_opts.append(f"MaxCycles={self.opt_maxcycles.value()}")
        # Constraint rows require Opt=ModRedundant (checked via getattr so
        # this also works when update_preview is bound to test fakes)
        _table = getattr(self, "constraint_table", None)
        if _table is not None:
            try:
                if _table.rowCount() > 0:
                    opt_opts.insert(0, "ModRedundant")
            except Exception as _e:
                logging.warning("constraint table check failed: %s", _e)

        freq_opts = []
        if self.freq_raman.isChecked():
            freq_opts.append("Raman")
        if self.freq_noraman.isChecked():
            freq_opts.append("NoRaman")
        if self.freq_vcd.isChecked():
            freq_opts.append("VCD")
        if self.freq_anharm.isChecked():
            freq_opts.append("Anharmonic")

        def _opt_token(extra=None):
            all_opts = list(opt_opts)
            if extra:
                all_opts = extra + all_opts
            seen = set()
            uniq = []
            for opt in all_opts:
                if opt.upper() not in seen:
                    uniq.append(opt)
                    seen.add(opt.upper())
            if uniq:
                return f"Opt=({', '.join(uniq)})"
            return "Opt"

        def _freq_token():
            if freq_opts:
                return f"Freq=({', '.join(freq_opts)})"
            return "Freq"

        if "Opt Freq" in job_txt:
            route_parts.append(_opt_token())
            route_parts.append(_freq_token())
        elif job_txt.startswith("Optimization Only"):
            route_parts.append(_opt_token())
        elif job_txt.startswith("Frequency Only"):
            route_parts.append(_freq_token())
        elif job_txt.startswith("Single Point"):
            pass
        elif "Opt=TS" in job_txt:
            route_parts.append(_opt_token(["TS", "NoEigenTest"]))
        elif "Scan" in job_txt:
            route_parts.append(_opt_token(["ModRedundant"]))
        elif job_txt == "IRC" or job_txt.startswith("IRC"):
            irc_opts = []
            if self.irc_calcfc.isChecked():
                irc_opts.append("CalcFC")
            if self.irc_maxpoints.value() > 0:
                irc_opts.append(f"MaxPoints={self.irc_maxpoints.value()}")
            if irc_opts:
                route_parts.append(f"IRC=({', '.join(irc_opts)})")
            else:
                route_parts.append("IRC")
        elif "Stable" in job_txt:
            route_parts.append("Stable")

        # Solvation
        solv = self.solv_model.currentText()
        if solv != "None":
            scrf_opts = [solv]
            if solv != "Dipole":
                scrf_opts.append(f"Solvent={self.solvent.currentText()}")
            route_parts.append(f"SCRF=({', '.join(scrf_opts)})")

        # Dispersion
        disp = self.dispersion.currentText()
        if disp != "None":
            route_parts.append(f"EmpiricalDispersion={disp}")

        # Properties
        pop = self.pop_combo.currentText()
        if pop != "None":
            route_parts.append(f"Pop={pop}")
        if self.density_chk.isChecked():
            route_parts.append("Density=Current")

        sym = self.symmetry_combo.currentText()
        if "Loose" in sym:
            route_parts.append("Symmetry=Loose")
        elif "NoSymm" in sym:
            route_parts.append("NoSymm")

        grid = self.grid_combo.currentText()
        if grid != "Default":
            route_parts.append(f"Integral({grid})")

        if self.td_enable.isChecked():
            td_opts = [f"NStates={self.td_nstates.value()}"]
            states = self.td_states_type.currentText()
            if states == "Singlets":
                td_opts.append("Singlets")
            elif states == "Triplets":
                td_opts.append("Triplets")
            elif states == "50-50":
                td_opts.append("50-50")
            if self.td_root.value() > 0:
                td_opts.append(f"Root={self.td_root.value()}")
            route_parts.append(f"TD=({', '.join(td_opts)})")

        if self.nmr_chk.isChecked():
            route_parts.append("NMR=GIAO")
        if self.polar_chk.isChecked():
            route_parts.append("Polar")

        out = self.output_combo.currentText()
        if out != "None":
            route_parts.append(f"Output={out}")
        if self.gfinput_chk.isChecked():
            route_parts.append("GFInput")

        scf_opts = []
        if self.scf_xqc.isChecked():
            scf_opts.append("XQC")
        if self.scf_tight.isChecked():
            scf_opts.append("Tight")
        if scf_opts:
            route_parts.append(f"SCF=({', '.join(scf_opts)})")
        guess = self.scf_guess.currentText()
        if guess != "Default":
            route_parts.append(f"Guess={guess}")

        self.preview_str = " ".join(route_parts)
        self.preview_label.setText(self.preview_str)

    def get_route(self):
        return self.preview_str

    def closeEvent(self, event):
        self.disable_picking()
        super().closeEvent(event)

    def accept(self):
        self.disable_picking()
        super().accept()

    def reject(self):
        self.disable_picking()
        super().reject()

    # ------------------------------------------------------------------
    # Best-effort round-trip parsing of an existing route string
    # ------------------------------------------------------------------

    def parse_route(self, route):
        self.ui_ready = False
        try:
            self._parse_route_impl(route)
        finally:
            self.ui_ready = True
        self.update_ui_state()
        self.update_preview()

    def _parse_route_impl(self, route):
        if not route:
            return
        tokens = _split_route_tokens(route)
        upper_tokens = [t.upper() for t in tokens]

        # Print level
        if "#P" in upper_tokens or any(t.upper().startswith("#P") for t in tokens):
            self.print_level.setCurrentIndex(0)
        elif "#T" in upper_tokens or any(t.upper().startswith("#T") for t in tokens):
            self.print_level.setCurrentIndex(2)
        elif any(t.startswith("#") for t in tokens):
            self.print_level.setCurrentIndex(1)

        # Method/Basis: look for a token containing '/'
        for t in tokens:
            if t.startswith("#") or t.startswith("!"):
                continue
            if "/" in t and not t.upper().startswith(
                ("SCRF", "TD", "OPT", "FREQ", "IRC", "INTEGRAL")
            ):
                mb = t
                second = ""
                if "//" in mb:
                    mb, second_full = mb.split("//", 1)
                    if "/" in second_full:
                        second = second_full.split("/", 1)[1]
                if "/" in mb:
                    method, basis = mb.split("/", 1)
                    self.method_name.setCurrentText(method)
                    self.basis_set.setCurrentText(basis)
                if second:
                    self.second_basis.setText(second)
                break
        else:
            # No basis token found: maybe semi-empirical or bare method
            for t in tokens:
                if t.startswith("#") or t.startswith("!"):
                    continue
                if t.upper() in [m.upper() for m in ALL_GAUSSIAN_METHODS]:
                    self.method_name.setCurrentText(t)
                    break

        route_upper = route.upper()

        # Job type
        has_opt = re.search(r"\bOPT\b", route_upper) is not None
        has_freq = re.search(r"\bFREQ\b", route_upper) is not None
        is_ts = "OPT=(" in route_upper and "TS" in route_upper
        is_scan = "MODREDUNDANT" in route_upper
        is_irc = re.search(r"\bIRC\b", route_upper) is not None
        is_stable = re.search(r"\bSTABLE\b", route_upper) is not None
        is_sp = re.search(r"\bSP\b", route_upper) is not None

        if is_ts:
            self.job_type.setCurrentIndex(4)
        elif is_scan:
            self.job_type.setCurrentIndex(5)
        elif is_irc:
            self.job_type.setCurrentIndex(6)
        elif is_stable:
            self.job_type.setCurrentIndex(7)
        elif has_opt and has_freq:
            self.job_type.setCurrentIndex(0)
        elif has_opt:
            self.job_type.setCurrentIndex(1)
        elif has_freq:
            self.job_type.setCurrentIndex(2)
        elif is_sp:
            self.job_type.setCurrentIndex(3)

        # Opt options
        m_opt = re.search(r"OPT\s*=\s*\(([^)]*)\)", route_upper)
        if m_opt:
            opts = [o.strip() for o in m_opt.group(1).split(",")]
            self.opt_tight.setChecked("TIGHT" in opts)
            self.opt_verytight.setChecked("VERYTIGHT" in opts)
            self.opt_calcfc.setChecked("CALCFC" in opts)
            self.opt_calcall.setChecked("CALCALL" in opts)
            for o in opts:
                mc = re.match(r"MAXCYCLES=(\d+)", o)
                if mc:
                    self.opt_maxcycles.setValue(int(mc.group(1)))

        # Freq options
        m_freq = re.search(r"FREQ\s*=\s*\(([^)]*)\)", route_upper)
        if m_freq:
            opts = [o.strip() for o in m_freq.group(1).split(",")]
            self.freq_raman.setChecked("RAMAN" in opts)
            self.freq_noraman.setChecked("NORAMAN" in opts)
            self.freq_vcd.setChecked("VCD" in opts)
            self.freq_anharm.setChecked("ANHARMONIC" in opts)

        # IRC options
        m_irc = re.search(r"IRC\s*=\s*\(([^)]*)\)", route_upper)
        if m_irc:
            opts = [o.strip() for o in m_irc.group(1).split(",")]
            self.irc_calcfc.setChecked("CALCFC" in opts)
            for o in opts:
                mp = re.match(r"MAXPOINTS=(\d+)", o)
                if mp:
                    self.irc_maxpoints.setValue(int(mp.group(1)))

        # Solvation
        m_scrf = re.search(r"SCRF\s*=\s*\(([^)]*)\)", route_upper)
        if m_scrf:
            opts = [o.strip() for o in m_scrf.group(1).split(",")]
            for model in SOLVATION_MODELS:
                if model != "None" and model.upper() in opts:
                    self.solv_model.setCurrentText(model)
                    break
            for o in opts:
                ms = re.match(r"SOLVENT=(.+)", o)
                if ms:
                    self.solvent.setCurrentText(ms.group(1).title())

        # Dispersion
        m_disp = re.search(r"EMPIRICALDISPERSION\s*=\s*(\w+)", route_upper)
        if m_disp:
            val = m_disp.group(1)
            for opt in DISPERSION_OPTIONS:
                if opt.upper() == val:
                    self.dispersion.setCurrentText(opt)
                    break

        # Pop
        m_pop = re.search(r"POP\s*=\s*(\w+)", route_upper)
        if m_pop:
            val = m_pop.group(1)
            for opt in POP_OPTIONS:
                if opt.upper() == val:
                    self.pop_combo.setCurrentText(opt)
                    break

        if "DENSITY=CURRENT" in route_upper:
            self.density_chk.setChecked(True)

        if "NOSYMM" in route_upper:
            self.symmetry_combo.setCurrentIndex(2)
        elif "SYMMETRY=LOOSE" in route_upper:
            self.symmetry_combo.setCurrentIndex(1)

        for grid in GRID_OPTIONS:
            if grid != "Default" and f"INTEGRAL({grid.upper()})" in route_upper:
                self.grid_combo.setCurrentText(grid)
                break

        m_td = re.search(r"TD\s*=\s*\(([^)]*)\)", route_upper)
        if m_td:
            self.td_enable.setChecked(True)
            opts = [o.strip() for o in m_td.group(1).split(",")]
            for o in opts:
                mn = re.match(r"NSTATES=(\d+)", o)
                if mn:
                    self.td_nstates.setValue(int(mn.group(1)))
                mr = re.match(r"ROOT=(\d+)", o)
                if mr:
                    self.td_root.setValue(int(mr.group(1)))
            if "SINGLETS" in opts:
                self.td_states_type.setCurrentText("Singlets")
            elif "TRIPLETS" in opts:
                self.td_states_type.setCurrentText("Triplets")
            elif "50-50" in opts:
                self.td_states_type.setCurrentText("50-50")

        if "NMR=GIAO" in route_upper or re.search(r"\bNMR\b", route_upper):
            self.nmr_chk.setChecked(True)
        if re.search(r"\bPOLAR\b", route_upper):
            self.polar_chk.setChecked(True)

        if "OUTPUT=WFN" in route_upper:
            self.output_combo.setCurrentText("WFN")
        elif "OUTPUT=WFX" in route_upper:
            self.output_combo.setCurrentText("WFX")
        if "GFINPUT" in route_upper:
            self.gfinput_chk.setChecked(True)

        m_scf = re.search(r"SCF\s*=\s*\(([^)]*)\)", route_upper)
        if m_scf:
            opts = [o.strip() for o in m_scf.group(1).split(",")]
            self.scf_xqc.setChecked("XQC" in opts)
            self.scf_tight.setChecked("TIGHT" in opts)
        elif "SCF=TIGHT" in route_upper:
            self.scf_tight.setChecked(True)
        elif "SCF=XQC" in route_upper:
            self.scf_xqc.setChecked(True)

        m_guess = re.search(r"GUESS\s*=\s*\(?(\w+)", route_upper)
        if m_guess:
            val = m_guess.group(1)
            for opt in SCF_GUESS_OPTIONS:
                if opt.upper() == val:
                    self.scf_guess.setCurrentText(opt)
                    break
