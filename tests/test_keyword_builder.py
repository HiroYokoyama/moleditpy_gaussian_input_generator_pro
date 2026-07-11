"""
tests/test_keyword_builder.py

Tests for GaussianRouteBuilderDialog logic in keyword_builder.py.

PyQt6 is stubbed. Rather than instantiating the full Qt dialog (whose
MagicMock-based widgets are not stateful), tests build a lightweight
SimpleNamespace with small stateful fake widgets and bind the real
unbound methods (update_preview / get_route / parse_route) to it --
the same technique used by the sibling ORCA Input Generator Pro suite.
"""

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
_split_route_tokens = _kb_mod._split_route_tokens

JOB_TYPES = _constants_mod.JOB_TYPES
DISPERSION_OPTIONS = _constants_mod.DISPERSION_OPTIONS
POP_OPTIONS = _constants_mod.POP_OPTIONS
GRID_OPTIONS = _constants_mod.GRID_OPTIONS
SCF_GUESS_OPTIONS = _constants_mod.SCF_GUESS_OPTIONS
SOLVATION_MODELS = _constants_mod.SOLVATION_MODELS


# ---------------------------------------------------------------------------
# Small stateful fake widgets (MagicMock is not stateful across calls)
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
    """Return a SimpleNamespace with all widgets update_preview()/parse_route() touch."""
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
        0,
    )
    dlg.method_type = _Combo(["DFT", "Double Hybrid", "Wavefunction (MP2/CC)", "Hartree-Fock", "Semi-Empirical", "All Methods"], 0)
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

    dlg.td_enable = _Check(False)
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

    dlg.update_preview()
    return dlg


# ---------------------------------------------------------------------------
# _split_route_tokens
# ---------------------------------------------------------------------------


class TestSplitRouteTokens(unittest.TestCase):
    def test_simple_split(self):
        self.assertEqual(
            _split_route_tokens("#P B3LYP/6-31G(d) Opt Freq"),
            ["#P", "B3LYP/6-31G(d)", "Opt", "Freq"],
        )

    def test_parens_kept_intact(self):
        tokens = _split_route_tokens("Opt=(Tight, CalcFC) Freq")
        self.assertEqual(tokens, ["Opt=(Tight, CalcFC)", "Freq"])

    def test_nested_parens_no_internal_split(self):
        tokens = _split_route_tokens("SCRF=(SMD, Solvent=Water)")
        self.assertEqual(tokens, ["SCRF=(SMD, Solvent=Water)"])

    def test_empty_string(self):
        self.assertEqual(_split_route_tokens(""), [])


# ---------------------------------------------------------------------------
# update_preview / get_route
# ---------------------------------------------------------------------------


class TestRouteBuilderDefaults(unittest.TestCase):
    def test_default_route_has_print_level_and_slash(self):
        dlg = _make_dialog()
        route = dlg.get_route()
        self.assertTrue(route.startswith("#P"))
        self.assertIn("/", route)

    def test_opt_freq_job(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(0)  # Optimization + Freq
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Opt", route)
        self.assertIn("Freq", route)


class TestRouteBuilderJobTypes(unittest.TestCase):
    def test_single_point_has_no_opt_or_freq(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(3)  # Single Point Energy (SP)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertNotIn("Opt", route)
        self.assertNotIn("Freq", route)

    def test_ts_job_sets_opt_ts_noeigentest(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(4)  # Transition State Opt
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Opt=(TS", route)
        self.assertIn("NoEigenTest", route)

    def test_scan_job_sets_modredundant(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(5)  # Scan (ModRedundant)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("ModRedundant", route)

    def test_irc_job_with_options(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(6)  # IRC
        dlg.irc_calcfc.setChecked(True)
        dlg.irc_maxpoints.setValue(20)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("IRC=(", route)
        self.assertIn("CalcFC", route)
        self.assertIn("MaxPoints=20", route)

    def test_stable_job(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(7)  # Stability Analysis
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Stable", route)

    def test_opt_options_combine_into_opt_token(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(1)  # Optimization Only
        dlg.opt_tight.setChecked(True)
        dlg.opt_calcfc.setChecked(True)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Opt=(", route)
        self.assertIn("Tight", route)
        self.assertIn("CalcFC", route)

    def test_freq_options_combine_into_freq_token(self):
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(2)  # Frequency Only
        dlg.freq_raman.setChecked(True)
        dlg.freq_vcd.setChecked(True)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Freq=(", route)
        self.assertIn("Raman", route)
        self.assertIn("VCD", route)


class TestRouteBuilderSolvationDispersion(unittest.TestCase):
    def test_no_solvation_by_default(self):
        dlg = _make_dialog()
        route = dlg.get_route()
        self.assertNotIn("SCRF", route)

    def test_smd_solvation_adds_scrf(self):
        dlg = _make_dialog()
        dlg.solv_model.setCurrentText("SMD")
        dlg.solvent.setCurrentText("Water")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("SCRF=(SMD", route)
        self.assertIn("Solvent=Water", route)

    def test_dipole_model_has_no_solvent(self):
        dlg = _make_dialog()
        dlg.solv_model.setCurrentText("Dipole")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("SCRF=(Dipole)", route)

    def test_dispersion_default_none(self):
        dlg = _make_dialog()
        route = dlg.get_route()
        self.assertNotIn("EmpiricalDispersion", route)

    def test_dispersion_gd3bj(self):
        dlg = _make_dialog()
        dlg.dispersion.setCurrentText("GD3BJ")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("EmpiricalDispersion=GD3BJ", route)


class TestRouteBuilderProperties(unittest.TestCase):
    def test_pop_nbo(self):
        dlg = _make_dialog()
        dlg.pop_combo.setCurrentText("NBO")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Pop=NBO", route)

    def test_density_current(self):
        dlg = _make_dialog()
        dlg.density_chk.setChecked(True)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Density=Current", route)

    def test_nosymm(self):
        dlg = _make_dialog()
        dlg.symmetry_combo.setCurrentIndex(2)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("NoSymm", route)

    def test_symmetry_loose(self):
        dlg = _make_dialog()
        dlg.symmetry_combo.setCurrentIndex(1)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Symmetry=Loose", route)

    def test_grid_option(self):
        dlg = _make_dialog()
        dlg.grid_combo.setCurrentText("UltraFine")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Integral(UltraFine)", route)

    def test_td_enabled_with_options(self):
        dlg = _make_dialog()
        dlg.td_enable.setChecked(True)
        dlg.td_nstates.setValue(12)
        dlg.td_states_type.setCurrentText("Triplets")
        dlg.td_root.setValue(2)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("TD=(", route)
        self.assertIn("NStates=12", route)
        self.assertIn("Triplets", route)
        self.assertIn("Root=2", route)

    def test_output_wfn(self):
        dlg = _make_dialog()
        dlg.output_combo.setCurrentText("WFN")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Output=WFN", route)

    def test_scf_options(self):
        dlg = _make_dialog()
        dlg.scf_xqc.setChecked(True)
        dlg.scf_tight.setChecked(True)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("SCF=(", route)
        self.assertIn("XQC", route)
        self.assertIn("Tight", route)

    def test_guess_read(self):
        dlg = _make_dialog()
        dlg.scf_guess.setCurrentText("Read")
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("Guess=Read", route)


class TestSemiEmpiricalMethod(unittest.TestCase):
    def test_semi_empirical_has_no_basis_slash(self):
        dlg = _make_dialog()
        dlg.method_name = _Combo(["PM6"], 0)
        dlg.update_preview()
        route = dlg.get_route()
        self.assertIn("PM6", route)
        self.assertNotIn("PM6/", route)


if __name__ == "__main__":
    unittest.main()
