"""
tests/test_parse_route_extended.py

Round-trip tests for GaussianRouteBuilderDialog.parse_route(): given a route
string, verify the widget state ends up matching what update_preview() would
have produced for that configuration.
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

JOB_TYPES = _constants_mod.JOB_TYPES
DISPERSION_OPTIONS = _constants_mod.DISPERSION_OPTIONS
POP_OPTIONS = _constants_mod.POP_OPTIONS
GRID_OPTIONS = _constants_mod.GRID_OPTIONS
SCF_GUESS_OPTIONS = _constants_mod.SCF_GUESS_OPTIONS
SOLVATION_MODELS = _constants_mod.SOLVATION_MODELS


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
        ["DFT", "Double Hybrid", "Wavefunction (MP2/CC)", "Hartree-Fock", "Semi-Empirical", "All Methods"],
        0,
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
# Round-trip tests
# ---------------------------------------------------------------------------


class TestParseRoutePrintLevel(unittest.TestCase):
    def test_hash_p(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Opt")
        self.assertEqual(dlg.print_level.currentIndex(), 0)

    def test_hash_n(self):
        dlg = _make_dialog()
        dlg.parse_route("#N B3LYP/6-31G(d) Opt")
        self.assertEqual(dlg.print_level.currentIndex(), 1)

    def test_bare_hash(self):
        dlg = _make_dialog()
        dlg.parse_route("# B3LYP/6-31G(d) Opt")
        self.assertEqual(dlg.print_level.currentIndex(), 2)

    def test_hash_t(self):
        dlg = _make_dialog()
        dlg.parse_route("#T B3LYP/6-31G(d) Opt")
        self.assertEqual(dlg.print_level.currentIndex(), 3)


class TestParseRouteMethodBasis(unittest.TestCase):
    def test_method_and_basis_extracted(self):
        dlg = _make_dialog()
        dlg.parse_route("#P wB97XD/6-311+G(d,p) Opt Freq")
        self.assertEqual(dlg.method_name.currentText(), "wB97XD")
        self.assertEqual(dlg.basis_set.currentText(), "6-311+G(d,p)")

    def test_compound_model_chemistry_second_basis(self):
        dlg = _make_dialog()
        dlg.parse_route("#P CCSD(T)/cc-pVTZ//B3LYP/6-31G(d) SP")
        self.assertEqual(dlg.second_basis.text(), "6-31G(d)")


class TestParseRouteJobType(unittest.TestCase):
    def test_opt_freq(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Opt Freq")
        self.assertEqual(dlg.job_type.currentIndex(), 0)

    def test_opt_only(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Opt")
        self.assertEqual(dlg.job_type.currentIndex(), 1)

    def test_freq_only(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Freq")
        self.assertEqual(dlg.job_type.currentIndex(), 2)

    def test_ts(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Opt=(TS,CalcFC,NoEigenTest)")
        self.assertEqual(dlg.job_type.currentIndex(), 4)

    def test_scan(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Opt=ModRedundant")
        self.assertEqual(dlg.job_type.currentIndex(), 5)

    def test_irc(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) IRC=(CalcFC,MaxPoints=20)")
        self.assertEqual(dlg.job_type.currentIndex(), 6)
        self.assertTrue(dlg.irc_calcfc.isChecked())
        self.assertEqual(dlg.irc_maxpoints.value(), 20)

    def test_stable(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Stable")
        self.assertEqual(dlg.job_type.currentIndex(), 7)

    def test_sp(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) SP")
        self.assertEqual(dlg.job_type.currentIndex(), 3)


class TestParseRouteOptFreqOptions(unittest.TestCase):
    def test_opt_options(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Opt=(Tight,CalcFC,MaxCycles=100)")
        self.assertTrue(dlg.opt_tight.isChecked())
        self.assertTrue(dlg.opt_calcfc.isChecked())
        self.assertEqual(dlg.opt_maxcycles.value(), 100)

    def test_freq_options(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Freq=(Raman,VCD)")
        self.assertTrue(dlg.freq_raman.isChecked())
        self.assertTrue(dlg.freq_vcd.isChecked())


class TestParseRouteSolvationDispersion(unittest.TestCase):
    def test_smd_water(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) SCRF=(SMD,Solvent=Water)")
        self.assertEqual(dlg.solv_model.currentText(), "SMD")

    def test_dispersion_gd3bj(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) EmpiricalDispersion=GD3BJ")
        self.assertEqual(dlg.dispersion.currentText(), "GD3BJ")


class TestParseRouteProperties(unittest.TestCase):
    def test_pop_nbo(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Pop=NBO")
        self.assertEqual(dlg.pop_combo.currentText(), "NBO")

    def test_density_current(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Density=Current")
        self.assertTrue(dlg.density_chk.isChecked())

    def test_nosymm(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) NoSymm")
        self.assertEqual(dlg.symmetry_combo.currentIndex(), 2)

    def test_symmetry_loose(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Symmetry=Loose")
        self.assertEqual(dlg.symmetry_combo.currentIndex(), 1)

    def test_grid(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Integral(UltraFine)")
        self.assertEqual(dlg.grid_combo.currentText(), "UltraFine")

    def test_td(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) TD=(NStates=10,Triplets,Root=2)")
        self.assertTrue(dlg.td_enable.isChecked())
        self.assertEqual(dlg.td_nstates.value(), 10)
        self.assertEqual(dlg.td_states_type.currentText(), "Triplets")
        self.assertEqual(dlg.td_root.value(), 2)

    def test_nmr(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) NMR=GIAO")
        self.assertTrue(dlg.nmr_chk.isChecked())

    def test_polar(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Polar")
        self.assertTrue(dlg.polar_chk.isChecked())

    def test_output_wfn(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Output=WFN")
        self.assertEqual(dlg.output_combo.currentText(), "WFN")

    def test_output_wfx(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Output=WFX")
        self.assertEqual(dlg.output_combo.currentText(), "WFX")

    def test_gfinput(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) GFInput")
        self.assertTrue(dlg.gfinput_chk.isChecked())

    def test_scf_xqc_tight(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) SCF=(XQC,Tight)")
        self.assertTrue(dlg.scf_xqc.isChecked())
        self.assertTrue(dlg.scf_tight.isChecked())

    def test_guess_read(self):
        dlg = _make_dialog()
        dlg.parse_route("#P B3LYP/6-31G(d) Guess=Read")
        self.assertEqual(dlg.scf_guess.currentText(), "Read")


class TestParseRouteEdgeCases(unittest.TestCase):
    def test_empty_route_is_noop(self):
        dlg = _make_dialog()
        before_method = dlg.method_name.currentText()
        dlg.parse_route("")
        self.assertEqual(dlg.method_name.currentText(), before_method)

    def test_full_round_trip_via_update_preview(self):
        """parse_route(update_preview()'s own output) should reproduce the same route."""
        dlg = _make_dialog()
        dlg.job_type.setCurrentIndex(1)  # Optimization Only
        dlg.opt_tight.setChecked(True)
        dlg.dispersion.setCurrentText("GD3BJ")
        dlg.update_preview()
        original_route = dlg.get_route()

        dlg2 = _make_dialog()
        dlg2.parse_route(original_route)
        round_tripped = dlg2.get_route()

        self.assertIn("Opt=(Tight)", round_tripped)
        self.assertIn("EmpiricalDispersion=GD3BJ", round_tripped)


if __name__ == "__main__":
    unittest.main()
