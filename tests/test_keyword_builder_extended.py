"""
tests/test_keyword_builder_extended.py

Additional coverage for GaussianRouteBuilderDialog in keyword_builder.py,
focused on areas not exercised by tests/test_keyword_builder.py,
tests/test_parse_route_extended.py or tests/test_constraints_picking.py:

  - setup_ui() / setup_*_tab() builders + connect_signals() (structural
    coverage: widgets get created and wired)
  - update_method_list() across every method-type category
  - update_ui_state() enable/disable + visibility branches
  - Constraint table plumbing: add_constraint/_insert_constraint_row,
    load_modredundant_lines, remove_constraint, clear_all_constraints,
    get_modredundant_lines findChild-None branch
  - Selection helpers: clear_selection, update_selection_display
  - store_state / restore_state
  - update_preview() branches not covered elsewhere (VeryTight/CalcAll/
    NoRaman, IRC with no sub-options, has_scan_row detection exceptions)
  - parse_route() branches not covered elsewhere (bare semi-empirical
    method fallback, 50-50 TD states, bare SCF=Tight/SCF=XQC)

Same stub technique as test_keyword_builder.py: PyQt6/RDKit are stubbed
(no-op if a real PyQt6 is already on sys.modules, e.g. via conftest.py),
and the dialog's methods are exercised unbound against small stateful fake
widgets or SimpleNamespace fakes -- never by instantiating the real QDialog.
"""

import contextlib
import os
import sys
import types
import importlib.util
import unittest
from unittest.mock import MagicMock

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _install_stubs():
    if "PyQt6" in sys.modules:
        return

    class _Base:
        def __init__(self, *a, **kw):
            pass

    pyqt6 = types.ModuleType("PyQt6")
    qt_widgets = types.ModuleType("PyQt6.QtWidgets")
    qt_core = types.ModuleType("PyQt6.QtCore")
    qt_gui = types.ModuleType("PyQt6.QtGui")

    for name in ["QDialog", "QWidget"]:
        setattr(qt_widgets, name, _Base)
    for name in [
        "QVBoxLayout",
        "QHBoxLayout",
        "QLabel",
        "QLineEdit",
        "QSpinBox",
        "QPushButton",
        "QGroupBox",
        "QComboBox",
        "QCompleter",
        "QTabWidget",
        "QTableWidget",
        "QTableWidgetItem",
        "QCheckBox",
        "QFormLayout",
        "QSizePolicy",
        "QScrollArea",
        "QTextEdit",
        "QMessageBox",
        "QFileDialog",
        "QInputDialog",
    ]:
        setattr(qt_widgets, name, MagicMock)

    qt_core.Qt = MagicMock()
    qt_core.QRegularExpression = MagicMock

    qt_gui.QFont = MagicMock
    qt_gui.QColor = MagicMock
    qt_gui.QPalette = MagicMock
    qt_gui.QKeySequence = MagicMock
    qt_gui.QShortcut = MagicMock

    pyqt6.QtWidgets = qt_widgets
    pyqt6.QtCore = qt_core
    pyqt6.QtGui = qt_gui

    sys.modules.update(
        {
            "PyQt6": pyqt6,
            "PyQt6.QtWidgets": qt_widgets,
            "PyQt6.QtCore": qt_core,
            "PyQt6.QtGui": qt_gui,
            "rdkit": MagicMock(),
            "rdkit.Chem": MagicMock(),
        }
    )


_install_stubs()


def _load_mod(name, relpath, pkg="gaussian_input_generator_pro"):
    full_name = f"{pkg}.{name}"
    if full_name in sys.modules:
        return sys.modules[full_name]
    path = os.path.join(_REPO_ROOT, pkg, relpath)
    spec = importlib.util.spec_from_file_location(full_name, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = pkg
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


_constants_mod = _load_mod("constants", "constants.py")
_kb_mod = _load_mod("keyword_builder", "keyword_builder.py")
GaussianRouteBuilderDialog = _kb_mod.GaussianRouteBuilderDialog

JOB_TYPES = _constants_mod.JOB_TYPES
DISPERSION_OPTIONS = _constants_mod.DISPERSION_OPTIONS
POP_OPTIONS = _constants_mod.POP_OPTIONS
GRID_OPTIONS = _constants_mod.GRID_OPTIONS
SCF_GUESS_OPTIONS = _constants_mod.SCF_GUESS_OPTIONS
SOLVATION_MODELS = _constants_mod.SOLVATION_MODELS
DFT_METHODS = _constants_mod.DFT_METHODS
DOUBLE_HYBRID_METHODS = _constants_mod.DOUBLE_HYBRID_METHODS
WAVEFUNCTION_METHODS = _constants_mod.WAVEFUNCTION_METHODS
HF_METHODS = _constants_mod.HF_METHODS
SEMI_EMPIRICAL_METHODS = _constants_mod.SEMI_EMPIRICAL_METHODS
ALL_GAUSSIAN_METHODS = _constants_mod.ALL_GAUSSIAN_METHODS


@contextlib.contextmanager
def _patch_builder(**kwargs):
    """Temporarily replace module-level names in keyword_builder.py."""
    orig = {}
    for k, v in kwargs.items():
        orig[k] = getattr(_kb_mod, k)
        setattr(_kb_mod, k, v)
    try:
        yield
    finally:
        for k, v in orig.items():
            setattr(_kb_mod, k, v)


@contextlib.contextmanager
def _patch_rdkit_chem():
    """Replace sys.modules["rdkit.Chem"] so the *local*
    `from rdkit.Chem import rdMolTransforms` inside _insert_constraint_row
    resolves to a controllable mock (it is a function-local import, so it
    cannot be patched via _patch_builder)."""
    orig = sys.modules.get("rdkit.Chem")
    fake = MagicMock()
    sys.modules["rdkit.Chem"] = fake
    try:
        yield fake
    finally:
        if orig is not None:
            sys.modules["rdkit.Chem"] = orig


# ---------------------------------------------------------------------------
# Small stateful fake widgets (reused from test_keyword_builder.py)
# ---------------------------------------------------------------------------


class _Combo:
    def __init__(self, items=None, current=0):
        self._items = list(items) if items else [""]
        self._index = current

    def currentText(self):
        if 0 <= self._index < len(self._items):
            return self._items[self._index]
        return ""

    def setCurrentText(self, text):
        if text in self._items:
            self._index = self._items.index(text)
        else:
            self._items.append(text)
            self._index = len(self._items) - 1

    def currentIndex(self):
        return self._index

    def setCurrentIndex(self, i):
        self._index = i

    def count(self):
        return len(self._items)

    def isEnabled(self):
        return True

    def setEnabled(self, v):
        pass

    def blockSignals(self, b):
        pass

    def clear(self):
        self._items = []
        self._index = -1

    def addItems(self, items):
        self._items.extend(items)
        if self._index == -1 and self._items:
            self._index = 0


class _Check:
    def __init__(self, checked=False):
        self._checked = checked

    def isChecked(self):
        return self._checked

    def setChecked(self, v):
        self._checked = v

    def isEnabled(self):
        return True

    def setEnabled(self, v):
        pass


class _Spin:
    def __init__(self, value=0):
        self._value = value

    def value(self):
        return self._value

    def setValue(self, v):
        self._value = v


class _LineEdit:
    def __init__(self, text=""):
        self._text = text

    def text(self):
        return self._text

    def setText(self, t):
        self._text = t


def _make_dialog():
    dlg = types.SimpleNamespace()
    dlg.ui_ready = True
    dlg.preview_str = ""
    dlg.preview_label = MagicMock()

    dlg.print_level = _Combo(
        [
            "Additional Output (#P)",
            "Normal Output (#N)",
            "Normal Output (#)",
            "Terse Output (#T)",
        ],
        2,
    )
    dlg.method_type = _Combo(
        ["DFT", "Double Hybrid", "Wavefunction (MP2/CC)", "Hartree-Fock", "Semi-Empirical", "All Methods"], 0
    )
    dlg.method_name = _Combo(["B3LYP"], 0)
    dlg.basis_set = _Combo(["6-31G(d)"], 0)
    dlg.second_basis = _LineEdit("")

    dlg.job_type = _Combo(JOB_TYPES, 0)
    dlg.opt_tight = _Check(False)
    dlg.opt_verytight = _Check(False)
    dlg.opt_calcfc = _Check(False)
    dlg.opt_calcall = _Check(False)
    dlg.opt_maxcycles = _Spin(0)

    dlg.freq_raman = _Check(False)
    dlg.freq_noraman = _Check(False)
    dlg.freq_vcd = _Check(False)
    dlg.freq_anharm = _Check(False)

    dlg.irc_calcfc = _Check(False)
    dlg.irc_maxpoints = _Spin(0)

    dlg.opt_group = MagicMock()
    dlg.freq_group = MagicMock()
    dlg.irc_group = MagicMock()

    dlg.solv_model = _Combo(SOLVATION_MODELS, 0)
    dlg.solvent = _Combo(["Water"], 0)
    dlg.dispersion = _Combo(DISPERSION_OPTIONS, 0)

    dlg.pop_combo = _Combo(POP_OPTIONS, 0)
    dlg.density_chk = _Check(False)
    dlg.symmetry_combo = _Combo(["Default", "Loose (Symmetry=Loose)", "None (NoSymm)"], 0)
    dlg.grid_combo = _Combo(GRID_OPTIONS, 0)

    dlg.td_method = _Combo(["None", "TD", "TDA"], 0)
    dlg.td_nstates = _Spin(6)
    dlg.td_states_type = _Combo(["Default", "Singlets", "Triplets", "50-50"], 0)
    dlg.td_root = _Spin(0)

    dlg.nmr_chk = _Check(False)
    dlg.polar_chk = _Check(False)
    dlg.output_combo = _Combo(["None", "WFN", "WFX"], 0)
    dlg.gfinput_chk = _Check(False)
    dlg.scf_xqc = _Check(False)
    dlg.scf_tight = _Check(False)
    dlg.scf_guess = _Combo(SCF_GUESS_OPTIONS, 0)

    dlg.update_ui_state = lambda: None
    dlg.update_preview = lambda: GaussianRouteBuilderDialog.update_preview(dlg)
    dlg.get_route = lambda: GaussianRouteBuilderDialog.get_route(dlg)
    dlg.parse_route = lambda route: GaussianRouteBuilderDialog.parse_route(dlg, route)
    dlg._parse_route_impl = lambda route: GaussianRouteBuilderDialog._parse_route_impl(dlg, route)
    dlg.get_modredundant_lines = lambda: GaussianRouteBuilderDialog.get_modredundant_lines(dlg)

    dlg.update_preview()
    return dlg


# ===========================================================================
# 1. setup_ui / setup_*_tab / connect_signals -- structural coverage
# ===========================================================================


class _AutoAttrMeta(type):
    def __getattr__(cls, name):
        return MagicMock()


class _SafeMock(MagicMock, metaclass=_AutoAttrMeta):
    """MagicMock that ignores constructor args (real Qt widgets take a
    text/parent arg positionally, which unittest.mock would otherwise
    interpret as `spec=`, crippling the resulting mock)."""

    def __init__(self, *a, **k):
        super().__init__()


class _ComboMock(_SafeMock):
    pass


class _CheckMock(_SafeMock):
    pass


class _SpinMock(_SafeMock):
    pass


_STRUCTURAL_PATCH = dict(
    QVBoxLayout=_SafeMock,
    QHBoxLayout=_SafeMock,
    QLabel=_SafeMock,
    QLineEdit=_SafeMock,
    QSpinBox=_SpinMock,
    QPushButton=_SafeMock,
    QGroupBox=_SafeMock,
    QComboBox=_ComboMock,
    QCompleter=_SafeMock,
    QTabWidget=_SafeMock,
    QTableWidget=_SafeMock,
    QTableWidgetItem=_SafeMock,
    QCheckBox=_CheckMock,
    QWidget=_SafeMock,
    QFormLayout=_SafeMock,
    QSizePolicy=_SafeMock,
    QScrollArea=_SafeMock,
)


class TestSetupUiStructural(unittest.TestCase):
    """Runs the real widget-builder methods; only checks they complete and
    populate the expected attributes (statement coverage for the GUI
    construction code, otherwise entirely unexercised)."""

    def _new_dialog(self):
        dlg = types.SimpleNamespace()
        dlg.tab_job = MagicMock()
        dlg.tab_method = MagicMock()
        dlg.tab_solvation = MagicMock()
        dlg.tab_tddft = MagicMock()
        dlg.tab_constraints = MagicMock()
        dlg.tab_props = MagicMock()
        dlg.tabs = MagicMock()
        dlg.update_ui_state = MagicMock()
        dlg.update_preview = MagicMock()
        dlg.update_method_list = MagicMock()
        dlg.setup_job_tab = lambda: GaussianRouteBuilderDialog.setup_job_tab(dlg)
        dlg.setup_method_tab = lambda: GaussianRouteBuilderDialog.setup_method_tab(dlg)
        dlg.setup_solvation_tab = (
            lambda: GaussianRouteBuilderDialog.setup_solvation_tab(dlg)
        )
        dlg.setup_tddft_tab = lambda: GaussianRouteBuilderDialog.setup_tddft_tab(dlg)
        dlg.setup_constraints_tab = (
            lambda: GaussianRouteBuilderDialog.setup_constraints_tab(dlg)
        )
        dlg.setup_props_tab = lambda: GaussianRouteBuilderDialog.setup_props_tab(dlg)
        dlg.connect_signals = lambda: GaussianRouteBuilderDialog.connect_signals(dlg)
        dlg.add_constraint = MagicMock()
        dlg.remove_constraint = MagicMock()
        dlg.clear_all_constraints = MagicMock()
        dlg.update_selection_display = MagicMock()
        dlg.on_tab_changed = MagicMock()
        dlg.reject = MagicMock()
        dlg.accept = MagicMock()
        dlg.setLayout = MagicMock()
        return dlg

    def test_setup_method_tab_populates_widgets(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_method_tab(dlg)
        self.assertTrue(hasattr(dlg, "method_type"))
        self.assertTrue(hasattr(dlg, "method_name"))
        self.assertTrue(hasattr(dlg, "basis_set"))
        self.assertTrue(hasattr(dlg, "second_basis"))
        dlg.update_method_list.assert_called()

    def test_setup_job_tab_populates_widgets(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_job_tab(dlg)
        self.assertTrue(hasattr(dlg, "job_type"))
        self.assertTrue(hasattr(dlg, "opt_group"))
        self.assertTrue(hasattr(dlg, "freq_group"))
        self.assertTrue(hasattr(dlg, "irc_group"))
        self.assertTrue(hasattr(dlg, "opt_maxcycles"))
        self.assertTrue(hasattr(dlg, "irc_maxpoints"))

    def test_setup_solvation_tab_populates_widgets(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_solvation_tab(dlg)
        self.assertTrue(hasattr(dlg, "solv_model"))
        self.assertTrue(hasattr(dlg, "solvent"))
        self.assertTrue(hasattr(dlg, "dispersion"))

    def test_setup_props_tab_populates_widgets(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_props_tab(dlg)
        self.assertTrue(hasattr(dlg, "pop_combo"))
        self.assertTrue(hasattr(dlg, "density_chk"))
        self.assertTrue(hasattr(dlg, "symmetry_combo"))
        self.assertTrue(hasattr(dlg, "grid_combo"))
        self.assertTrue(hasattr(dlg, "nmr_chk"))
        self.assertTrue(hasattr(dlg, "polar_chk"))
        self.assertTrue(hasattr(dlg, "output_combo"))
        self.assertTrue(hasattr(dlg, "gfinput_chk"))
        self.assertTrue(hasattr(dlg, "scf_xqc"))
        self.assertTrue(hasattr(dlg, "scf_tight"))
        self.assertTrue(hasattr(dlg, "scf_guess"))

    def test_setup_tddft_tab_populates_widgets(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_tddft_tab(dlg)
        self.assertTrue(hasattr(dlg, "td_method"))
        self.assertTrue(hasattr(dlg, "td_nstates"))
        self.assertTrue(hasattr(dlg, "td_states_type"))
        self.assertTrue(hasattr(dlg, "td_root"))

    def test_setup_constraints_tab_populates_widgets(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_constraints_tab(dlg)
        self.assertTrue(hasattr(dlg, "constraint_table"))
        self.assertTrue(hasattr(dlg, "btn_add_const"))
        self.assertTrue(hasattr(dlg, "btn_remove_const"))
        self.assertTrue(hasattr(dlg, "btn_clear_const"))
        self.assertTrue(hasattr(dlg, "selection_label"))

    def test_setup_ui_full_flow_runs_to_completion(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            for attr in [
                "tab_job",
                "tab_method",
                "tab_solvation",
                "tab_tddft",
                "tab_constraints",
                "tab_props",
                "tabs",
            ]:
                delattr(dlg, attr)
            GaussianRouteBuilderDialog.setup_ui(dlg)
        self.assertTrue(dlg.ui_ready)
        dlg.update_ui_state.assert_called()
        dlg.update_preview.assert_called()

    def test_connect_signals_wires_update_preview(self):
        with _patch_builder(**_STRUCTURAL_PATCH):
            dlg = self._new_dialog()
            GaussianRouteBuilderDialog.setup_method_tab(dlg)
            GaussianRouteBuilderDialog.setup_job_tab(dlg)
            GaussianRouteBuilderDialog.setup_solvation_tab(dlg)
            GaussianRouteBuilderDialog.setup_props_tab(dlg)
            GaussianRouteBuilderDialog.setup_tddft_tab(dlg)
            GaussianRouteBuilderDialog.connect_signals(dlg)

        dlg.job_type.currentIndexChanged.connect.assert_any_call(dlg.update_preview)
        dlg.opt_tight.toggled.connect.assert_any_call(dlg.update_preview)
        dlg.opt_maxcycles.valueChanged.connect.assert_any_call(dlg.update_preview)
        dlg.second_basis.textChanged.connect.assert_any_call(dlg.update_preview)


# ===========================================================================
# 2. update_method_list()
# ===========================================================================


class TestUpdateMethodList(unittest.TestCase):
    def _dlg(self, mtype, current_text=""):
        dlg = types.SimpleNamespace()
        dlg.method_type = _Combo([mtype], 0)
        dlg.method_name = _Combo([current_text] if current_text else [""], 0)
        dlg.update_ui_state = lambda: None
        dlg.update_preview = lambda: None
        return dlg

    def test_dft_populates(self):
        dlg = self._dlg("DFT")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertEqual(dlg.method_name._items, list(DFT_METHODS))

    def test_double_hybrid_populates(self):
        dlg = self._dlg("Double Hybrid")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertEqual(dlg.method_name._items, list(DOUBLE_HYBRID_METHODS))

    def test_wavefunction_populates(self):
        dlg = self._dlg("Wavefunction (MP2/CC)")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertEqual(dlg.method_name._items, list(WAVEFUNCTION_METHODS))

    def test_hartree_fock_populates(self):
        dlg = self._dlg("Hartree-Fock")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertEqual(dlg.method_name._items, list(HF_METHODS))

    def test_semi_empirical_populates(self):
        dlg = self._dlg("Semi-Empirical")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertEqual(dlg.method_name._items, list(SEMI_EMPIRICAL_METHODS))

    def test_all_methods_preserves_current_text(self):
        dlg = self._dlg("All Methods", current_text="PM6")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertEqual(dlg.method_name.currentText(), "PM6")

    def test_all_methods_no_current_text_keeps_default_index(self):
        dlg = self._dlg("All Methods")
        GaussianRouteBuilderDialog.update_method_list(dlg)
        self.assertGreater(dlg.method_name.count(), 0)
        self.assertEqual(dlg.method_name._items, list(ALL_GAUSSIAN_METHODS))


# ===========================================================================
# 3. update_ui_state()
# ===========================================================================


class TestUpdateUiState(unittest.TestCase):
    def _dlg(self, method="B3LYP", job="Optimization + Freq (Opt Freq)", solv="None"):
        dlg = types.SimpleNamespace()
        dlg.ui_ready = True
        dlg.method_name = _Combo([method], 0)
        dlg.basis_set = _Combo(["6-31G(d)"], 0)
        dlg.second_basis = MagicMock()
        dlg.job_type = _Combo([job], 0)
        dlg.opt_group = MagicMock()
        dlg.freq_group = MagicMock()
        dlg.irc_group = MagicMock()
        dlg.solv_model = _Combo([solv], 0)
        dlg.solvent = MagicMock()
        return dlg

    def test_not_ui_ready_is_noop(self):
        dlg = self._dlg()
        dlg.ui_ready = False
        dlg.method_name = None  # would raise if code proceeded
        GaussianRouteBuilderDialog.update_ui_state(dlg)  # must not raise

    def test_semi_empirical_disables_basis(self):
        dlg = self._dlg(method="PM6")
        disabled = {}
        dlg.basis_set.setEnabled = lambda v: disabled.setdefault("basis", v)
        dlg.second_basis.setEnabled = lambda v: disabled.setdefault("second", v)
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        self.assertFalse(disabled["basis"])
        self.assertFalse(disabled["second"])

    def test_dft_enables_basis(self):
        dlg = self._dlg(method="B3LYP")
        enabled = {}
        dlg.basis_set.setEnabled = lambda v: enabled.setdefault("basis", v)
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        self.assertTrue(enabled["basis"])

    def test_opt_freq_job_shows_opt_and_freq(self):
        dlg = self._dlg(job="Optimization + Freq (Opt Freq)")
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        dlg.opt_group.setVisible.assert_called_with(True)
        dlg.freq_group.setVisible.assert_called_with(True)
        dlg.irc_group.setVisible.assert_called_with(False)

    def test_scan_job_treated_as_opt(self):
        dlg = self._dlg(job="Scan (ModRedundant)")
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        dlg.opt_group.setVisible.assert_called_with(True)

    def test_irc_job_shows_irc_group(self):
        dlg = self._dlg(job="IRC")
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        dlg.irc_group.setVisible.assert_called_with(True)

    def test_solvated_enables_solvent(self):
        dlg = self._dlg(solv="SMD")
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        dlg.solvent.setEnabled.assert_called_with(True)

    def test_none_solvation_disables_solvent(self):
        dlg = self._dlg(solv="None")
        GaussianRouteBuilderDialog.update_ui_state(dlg)
        dlg.solvent.setEnabled.assert_called_with(False)


# ===========================================================================
# 4. Constraint table plumbing
# ===========================================================================


class _FakeConstraintItem:
    def __init__(self, text=""):
        self._text = text

    def text(self):
        return self._text

    def setTextAlignment(self, *a, **k):
        pass


class _FakeCheckBoxWidget:
    def __init__(self, checked=False):
        self._checked = checked
        self._callbacks = []

    def isChecked(self):
        return self._checked

    def setChecked(self, v):
        self._checked = bool(v)

    class _Signal:
        def __init__(self, owner):
            self._owner = owner

        def connect(self, fn):
            self._owner._callbacks.append(fn)

    @property
    def stateChanged(self):
        return _FakeCheckBoxWidget._Signal(self)


class _FakeContainerWidget:
    def __init__(self, *a, **k):
        self._child = None

    def findChild(self, cls):
        return self._child


class _FakeHBoxLayout:
    def __init__(self, parent=None):
        self._parent = parent

    def addWidget(self, w):
        if self._parent is not None:
            self._parent._child = w

    def setAlignment(self, *a, **k):
        pass

    def setContentsMargins(self, *a, **k):
        pass


class _FakeQt:
    class AlignmentFlag:
        AlignCenter = 1


class _Idx:
    def __init__(self, row):
        self._row = row

    def row(self):
        return self._row


class _FakeTable:
    def __init__(self):
        self._rows = []
        self.selected_rows = []

    def rowCount(self):
        return len(self._rows)

    def setRowCount(self, n):
        if n == 0:
            self._rows = []
        else:
            self._rows = self._rows[:n]

    def insertRow(self, row):
        self._rows.insert(row, {"items": {}, "widget": None})

    def removeRow(self, row):
        del self._rows[row]

    def setItem(self, row, col, item):
        self._rows[row]["items"][col] = item

    def item(self, row, col):
        return self._rows[row]["items"].get(col)

    def setCellWidget(self, row, col, widget):
        self._rows[row]["widget"] = widget

    def cellWidget(self, row, col):
        return self._rows[row]["widget"]

    def selectedIndexes(self):
        return [_Idx(r) for r in self.selected_rows]


_CONSTRAINT_PATCH = dict(
    QTableWidgetItem=_FakeConstraintItem,
    QCheckBox=_FakeCheckBoxWidget,
    QWidget=_FakeContainerWidget,
    QHBoxLayout=_FakeHBoxLayout,
    Qt=_FakeQt,
)


def _constraints_dialog(mol=None):
    dlg = types.SimpleNamespace()
    dlg.constraint_table = _FakeTable()
    dlg.selected_atoms = []
    dlg.mol = mol
    dlg.selection_label = MagicMock()
    dlg.btn_add_const = MagicMock()
    dlg.show_atom_labels_for = lambda *a, **k: None
    dlg.update_preview = lambda: None
    dlg.update_selection_display = (
        lambda: GaussianRouteBuilderDialog.update_selection_display(dlg)
    )
    dlg._insert_constraint_row = (
        lambda *a, **k: GaussianRouteBuilderDialog._insert_constraint_row(dlg, *a, **k)
    )
    return dlg


class TestConstraintTablePlumbing(unittest.TestCase):
    def test_add_constraint_atom(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem():
            dlg = _constraints_dialog(mol=MagicMock())
            dlg.selected_atoms = [4]
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.rowCount(), 1)
        self.assertEqual(dlg.constraint_table.item(0, 0).text(), "Atom")
        self.assertEqual(dlg.constraint_table.item(0, 1).text(), "5")
        self.assertEqual(dlg.selected_atoms, [])

    def test_add_constraint_distance_uses_bond_length(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem() as fake_chem:
            fake_chem.rdMolTransforms.GetBondLength.return_value = 1.234
            dlg = _constraints_dialog(mol=MagicMock())
            dlg.selected_atoms = [0, 1]
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.item(0, 0).text(), "Distance")
        self.assertEqual(dlg.constraint_table.item(0, 2).text(), "1.234")

    def test_add_constraint_angle_uses_angle_deg(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem() as fake_chem:
            fake_chem.rdMolTransforms.GetAngleDeg.return_value = 109.471
            dlg = _constraints_dialog(mol=MagicMock())
            dlg.selected_atoms = [0, 1, 2]
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.item(0, 0).text(), "Angle")
        self.assertEqual(dlg.constraint_table.item(0, 2).text(), "109.471")

    def test_add_constraint_dihedral_uses_dihedral_deg(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem() as fake_chem:
            fake_chem.rdMolTransforms.GetDihedralDeg.return_value = 180.0
            dlg = _constraints_dialog(mol=MagicMock())
            dlg.selected_atoms = [0, 1, 2, 3]
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.item(0, 0).text(), "Dihedral")
        self.assertEqual(dlg.constraint_table.item(0, 2).text(), "180.000")

    def test_add_constraint_noop_without_mol(self):
        with _patch_builder(**_CONSTRAINT_PATCH):
            dlg = _constraints_dialog(mol=None)
            dlg.selected_atoms = [1, 2]
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.rowCount(), 0)

    def test_add_constraint_noop_without_selection(self):
        with _patch_builder(**_CONSTRAINT_PATCH):
            dlg = _constraints_dialog(mol=MagicMock())
            dlg.selected_atoms = []
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.rowCount(), 0)

    def test_add_constraint_rdkit_failure_falls_back_to_zero(self):
        """rdMolTransforms raising is swallowed; value falls back to 0.0."""
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem() as fake_chem:
            fake_chem.rdMolTransforms.GetBondLength.side_effect = RuntimeError("boom")
            dlg = _constraints_dialog(mol=MagicMock())
            dlg.selected_atoms = [0, 1]
            GaussianRouteBuilderDialog.add_constraint(dlg)
        self.assertEqual(dlg.constraint_table.item(0, 2).text(), "0.000")

    def test_load_modredundant_lines_rebuilds_table(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem():
            dlg = _constraints_dialog(mol=None)
            GaussianRouteBuilderDialog.load_modredundant_lines(
                dlg, ["B 1 2 F", "D 1 2 3 4 S 20 5.00", "not a constraint"]
            )
        self.assertEqual(dlg.constraint_table.rowCount(), 2)
        self.assertEqual(dlg.constraint_table.item(0, 1).text(), "1 2")
        self.assertEqual(dlg.constraint_table.item(1, 1).text(), "1 2 3 4")

    def test_remove_constraint_removes_selected_rows(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem():
            dlg = _constraints_dialog(mol=None)
            GaussianRouteBuilderDialog.load_modredundant_lines(dlg, ["B 1 2 F", "X 3 F"])
            dlg.constraint_table.selected_rows = [0]
            GaussianRouteBuilderDialog.remove_constraint(dlg)
        self.assertEqual(dlg.constraint_table.rowCount(), 1)
        self.assertEqual(dlg.constraint_table.item(0, 1).text(), "3")

    def test_clear_all_constraints_empties_table(self):
        with _patch_builder(**_CONSTRAINT_PATCH), _patch_rdkit_chem():
            dlg = _constraints_dialog(mol=None)
            GaussianRouteBuilderDialog.load_modredundant_lines(dlg, ["B 1 2 F"])
            GaussianRouteBuilderDialog.clear_all_constraints(dlg)
        self.assertEqual(dlg.constraint_table.rowCount(), 0)

    def test_get_modredundant_lines_findchild_none_defaults_to_freeze(self):
        """When the scan checkbox widget can't be found, is_scan stays False."""
        table = _FakeTable()
        table.insertRow(0)
        table.setItem(0, 1, _FakeConstraintItem("1 2"))
        table.setItem(0, 4, _FakeConstraintItem("10"))
        table.setItem(0, 5, _FakeConstraintItem("0.1"))
        table.setCellWidget(0, 3, _FakeContainerWidget())  # findChild -> None
        dlg = types.SimpleNamespace(constraint_table=table)
        lines = GaussianRouteBuilderDialog.get_modredundant_lines(dlg)
        self.assertEqual(lines, ["B 1 2 F"])


# ===========================================================================
# 5. Selection helpers
# ===========================================================================


class TestSelectionHelpers(unittest.TestCase):
    def _dlg(self):
        dlg = types.SimpleNamespace()
        dlg.selected_atoms = []
        dlg.constraint_table = _FakeTable()
        dlg.selection_label = MagicMock()
        dlg.btn_add_const = MagicMock()
        dlg.show_atom_labels_for = lambda *a, **k: None
        return dlg

    def test_clear_selection_empties_list(self):
        dlg = self._dlg()
        dlg.update_selection_display = lambda: None
        dlg.selected_atoms = [1, 2]
        GaussianRouteBuilderDialog.clear_selection(dlg)
        self.assertEqual(dlg.selected_atoms, [])

    def test_update_selection_display_no_atoms(self):
        dlg = self._dlg()
        GaussianRouteBuilderDialog.update_selection_display(dlg)
        dlg.selection_label.setText.assert_called_with("Selected atoms: None")
        dlg.btn_add_const.setEnabled.assert_called_with(False)

    def test_update_selection_display_with_atoms(self):
        dlg = self._dlg()
        dlg.selected_atoms = [2, 5]
        GaussianRouteBuilderDialog.update_selection_display(dlg)
        dlg.btn_add_const.setEnabled.assert_called_with(True)
        (txt,), _kw = dlg.selection_label.setText.call_args
        self.assertIn("3, 6", txt)
        self.assertIn("Distance", txt)

    def test_update_selection_display_includes_selected_table_rows(self):
        dlg = self._dlg()
        dlg.constraint_table.insertRow(0)
        dlg.constraint_table.setItem(0, 1, _FakeConstraintItem("1 2"))
        dlg.constraint_table.selected_rows = [0]
        GaussianRouteBuilderDialog.update_selection_display(dlg)
        # Must not raise; labels get built from the selected row's indices.
        dlg.selection_label.setText.assert_called()

    def test_update_selection_display_bad_row_text_is_swallowed(self):
        """A non-numeric index cell must not raise (caught + logged)."""
        dlg = self._dlg()
        dlg.constraint_table.insertRow(0)
        dlg.constraint_table.setItem(0, 1, _FakeConstraintItem("not numbers"))
        dlg.constraint_table.selected_rows = [0]
        GaussianRouteBuilderDialog.update_selection_display(dlg)  # must not raise


# ===========================================================================
# 6. store_state / restore_state
# ===========================================================================


class TestStoreRestoreState(unittest.TestCase):
    def test_store_and_restore_roundtrip(self):
        with _patch_builder(QComboBox=_Combo, QCheckBox=_Check, QSpinBox=_Spin, QLineEdit=_LineEdit):
            dlg = types.SimpleNamespace()
            dlg.my_combo = _Combo(["A", "B"], 0)
            dlg.my_combo.setCurrentText("B")
            dlg.my_check = _Check(True)
            dlg.my_spin = _Spin(7)
            dlg.my_edit = _LineEdit("hello")

            GaussianRouteBuilderDialog.store_state(dlg)
            self.assertEqual(dlg._saved_state["my_combo"], "B")
            self.assertTrue(dlg._saved_state["my_check"])
            self.assertEqual(dlg._saved_state["my_spin"], 7)
            self.assertEqual(dlg._saved_state["my_edit"], "hello")

            dlg.my_combo.setCurrentText("A")
            dlg.my_check.setChecked(False)
            dlg.my_spin.setValue(0)
            dlg.my_edit.setText("")
            dlg.update_preview = lambda: None

            GaussianRouteBuilderDialog.restore_state(dlg)
        self.assertEqual(dlg.my_combo.currentText(), "B")
        self.assertTrue(dlg.my_check.isChecked())
        self.assertEqual(dlg.my_spin.value(), 7)
        self.assertEqual(dlg.my_edit.text(), "hello")
        self.assertTrue(dlg.ui_ready)

    def test_restore_state_without_prior_save_is_noop(self):
        dlg = types.SimpleNamespace()
        GaussianRouteBuilderDialog.restore_state(dlg)  # must not raise

    def test_restore_state_skips_missing_widgets(self):
        dlg = types.SimpleNamespace()
        dlg._saved_state = {"never_existed": "x"}
        dlg.update_preview = lambda: None
        GaussianRouteBuilderDialog.restore_state(dlg)  # must not raise


# ===========================================================================
# 7. update_preview() -- additional branches
# ===========================================================================


class TestUpdatePreviewExtraBranches(unittest.TestCase):
    def test_verytight_and_calcall_opt_options(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(1)  # Optimization Only
        dlg.opt_verytight.setChecked(True)
        dlg.opt_calcall.setChecked(True)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("VeryTight", route)
        self.assertIn("CalcAll", route)

    def test_noraman_freq_option(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(2)  # Frequency Only
        dlg.freq_noraman.setChecked(True)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("NoRaman", route)

    def test_irc_without_suboptions_is_bare(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(6)  # IRC
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("IRC", route)
        self.assertNotIn("IRC=(", route)

    def test_has_scan_row_detection_swallows_exceptions(self):
        """get_modredundant_lines raising must not blow up update_preview;
        has_scan_row simply falls back to False."""
        dlg = _make_dialog()
        dlg.get_modredundant_lines = lambda: (_ for _ in ()).throw(RuntimeError("boom"))
        dlg.job_type.setCurrentIndex(0)  # Optimization + Freq
        dlg.update_preview()  # must not raise
        route = dlg.get_route()
        self.assertIn("Freq", route)

    def test_force_scan_job_type_swallows_setcurrenttext_exception(self):
        """If job_type.setCurrentText() blows up while forcing the Scan job,
        the exception must be swallowed (logged), not propagated."""

        class _BoomCombo(_Combo):
            def setCurrentText(self, text):
                raise RuntimeError("boom")

        dlg = _make_dialog()
        dlg.job_type = _BoomCombo(JOB_TYPES, 0)  # Optimization + Freq (not Scan)
        dlg.get_modredundant_lines = lambda: ["B 1 2 S 10 0.10"]  # a scan row
        dlg.update_preview()  # must not raise


# ===========================================================================
# 8. parse_route() -- additional branches
# ===========================================================================


class TestParseRouteExtraBranches(unittest.TestCase):
    def test_bare_semi_empirical_method_no_slash(self):
        dlg = _make_dialog()
        dlg.parse_route("#P PM6 Opt")
        self.assertEqual(dlg.method_name.currentText(), "PM6")

    def test_td_states_50_50(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) TD=(NStates=10,50-50)")
        self.assertEqual(dlg.td_states_type.currentText(), "50-50")

    def test_bare_scf_tight(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) SCF=Tight")
        self.assertTrue(dlg.scf_tight.isChecked())

    def test_bare_scf_xqc(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) SCF=XQC")
        self.assertTrue(dlg.scf_xqc.isChecked())


if __name__ == "__main__":
    unittest.main()
