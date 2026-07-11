"""
tests/test_main_dialog.py

Tests for pure-logic pieces of GaussianSetupDialogPro (main_dialog.py):
  generate_input_content()
    - Link0 order (%nprocshared, %mem, %oldchk, %chk)
    - blank-line placement (route/blank/title/blank/charge-mult/coords/blank)
    - trailing blank line (Gaussian requires the file to end with one)
    - wfn filename line when Output=WFN/WFX in route
    - --Link1-- section (Checkpoint vs Copy coordinates geometry source)
  _rewrite_chk() -- %chk= rewritten to the saved file's basename
  _auto_suffix() -- suffix priority order

Methods are bound to a lightweight SimpleNamespace with small stateful fake
widgets (MagicMock is not stateful across calls), the same technique used by
test_keyword_builder.py / test_parse_route_extended.py.
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
        "QScrollArea",
        "QGroupBox",
        "QFormLayout",
        "QSpinBox",
        "QPushButton",
        "QLabel",
        "QTextEdit",
        "QLineEdit",
        "QComboBox",
        "QSizePolicy",
        "QMessageBox",
        "QFileDialog",
        "QInputDialog",
        "QCheckBox",
    ]:
        setattr(qt_widgets, name, MagicMock)

    qt_core.Qt = MagicMock()
    qt_core.QRegularExpression = MagicMock

    qt_gui.QFont = MagicMock
    qt_gui.QPalette = MagicMock
    qt_gui.QColor = MagicMock
    qt_gui.QSyntaxHighlighter = type(
        "QSyntaxHighlighter", (), {"__init__": lambda s, *a, **k: None}
    )
    qt_gui.QTextCharFormat = MagicMock
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


_load_mod("constants", "constants.py")

# main_dialog.py imports these two submodules; provide lightweight fakes only
# if a real module (loaded by a sibling test file in the same pytest session)
# isn't already cached in sys.modules -- never clobber a real one, since that
# would break later test modules that expect the real class objects.
if "gaussian_input_generator_pro.highlighter" not in sys.modules:
    _hl_mod = types.ModuleType("gaussian_input_generator_pro.highlighter")
    _hl_mod.GaussianSyntaxHighlighter = MagicMock
    sys.modules["gaussian_input_generator_pro.highlighter"] = _hl_mod

if "gaussian_input_generator_pro.keyword_builder" not in sys.modules:
    _kb_mod = types.ModuleType("gaussian_input_generator_pro.keyword_builder")
    _kb_mod.GaussianRouteBuilderDialog = MagicMock
    sys.modules["gaussian_input_generator_pro.keyword_builder"] = _kb_mod

_init_mod = _load_mod("__init__", "__init__.py")
sys.modules["gaussian_input_generator_pro"] = _init_mod
_md_mod = _load_mod("main_dialog", "main_dialog.py")
GaussianSetupDialogPro = _md_mod.GaussianSetupDialogPro


class _Combo:
    def __init__(self, items=None, current=0):
        self._items = list(items) if items else [""]
        self._index = current

    def currentText(self):
        return self._items[self._index] if 0 <= self._index < len(self._items) else ""

    def setCurrentText(self, text):
        if text in self._items:
            self._index = self._items.index(text)
        else:
            self._items.append(text)
            self._index = len(self._items) - 1


class _Check:
    def __init__(self, checked=False):
        self._checked = checked

    def isChecked(self):
        return self._checked

    def setChecked(self, v):
        self._checked = v


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


class _TextEdit:
    def __init__(self, text=""):
        self._text = text

    def toPlainText(self):
        return self._text

    def setPlainText(self, t):
        self._text = t

    setText = setPlainText


def _make_dialog(
    route="#P B3LYP/6-31G(d) EmpiricalDispersion=GD3BJ Opt Freq",
    coords=None,
    filename=None,
    charge=0,
    mult=1,
):
    dlg = types.SimpleNamespace()
    dlg.filename = filename
    dlg.nproc_spin = _Spin(4)
    dlg.mem_spin = _Spin(4)
    dlg.mem_unit = _Combo(["GB", "MB", "MW"], 0)
    dlg.oldchk_edit = _LineEdit("")
    dlg.chk_edit = _LineEdit("")
    dlg.keywords_edit = _TextEdit(route)
    dlg.comment_edit = _LineEdit("Test Title")
    dlg.charge_spin = _Spin(charge)
    dlg.mult_spin = _Spin(mult)
    dlg.tail_edit = _TextEdit("")
    dlg.link1_enable = _Check(False)
    dlg.link1_route_edit = _TextEdit("#P B3LYP/6-31G(d) Freq Geom=Check Guess=Read")
    dlg.link1_title_edit = _LineEdit("Link1 Title")
    dlg.link1_geom_src = _Combo(
        ["Checkpoint (Geom=Check Guess=Read)", "Copy coordinates"], 0
    )
    dlg.link1_tail_edit = _TextEdit("")

    _coords = coords if coords is not None else ["C     0.000000     0.000000     0.000000"]
    dlg.get_coords_lines = lambda: _coords

    dlg._mem_line = lambda: GaussianSetupDialogPro._mem_line(dlg)
    dlg._wfn_filename_hint = lambda: GaussianSetupDialogPro._wfn_filename_hint(dlg)
    dlg.generate_input_content = lambda: GaussianSetupDialogPro.generate_input_content(dlg)
    dlg._auto_suffix = lambda: GaussianSetupDialogPro._auto_suffix(dlg)

    return dlg


# ---------------------------------------------------------------------------
# generate_input_content structure
# ---------------------------------------------------------------------------


class TestGenerateInputContentStructure(unittest.TestCase):
    def test_link0_order(self):
        dlg = _make_dialog()
        content = dlg.generate_input_content()
        lines = content.splitlines()
        self.assertTrue(lines[0].startswith("%nprocshared="))
        self.assertTrue(lines[1].startswith("%mem="))
        self.assertTrue(lines[2].startswith("%chk="))

    def test_oldchk_appears_before_chk_when_set(self):
        dlg = _make_dialog()
        dlg.oldchk_edit.setText("previous.chk")
        content = dlg.generate_input_content()
        lines = content.splitlines()
        self.assertTrue(lines[2].startswith("%oldchk="))
        self.assertTrue(lines[3].startswith("%chk="))

    def test_chk_auto_generated_when_empty(self):
        dlg = _make_dialog(filename="mymol.xyz")
        content = dlg.generate_input_content()
        self.assertIn("%chk=mymol.chk", content)

    def test_chk_uses_explicit_value(self):
        dlg = _make_dialog()
        dlg.chk_edit.setText("custom")
        content = dlg.generate_input_content()
        self.assertIn("%chk=custom.chk", content)

    def test_route_line_present(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt")
        content = dlg.generate_input_content()
        self.assertIn("#P B3LYP/6-31G(d) Opt", content)

    def test_route_gets_hash_prefix_if_missing(self):
        dlg = _make_dialog(route="B3LYP/6-31G(d) Opt")
        content = dlg.generate_input_content()
        self.assertIn("# B3LYP/6-31G(d) Opt", content)

    def test_blank_line_after_route(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt")
        lines = dlg.generate_input_content().splitlines()
        route_idx = next(i for i, l in enumerate(lines) if l.startswith("#"))
        self.assertEqual(lines[route_idx + 1], "")

    def test_title_line_present(self):
        dlg = _make_dialog()
        dlg.comment_edit.setText("My Title")
        content = dlg.generate_input_content()
        self.assertIn("My Title", content)

    def test_blank_line_after_title(self):
        dlg = _make_dialog()
        dlg.comment_edit.setText("My Title")
        lines = dlg.generate_input_content().splitlines()
        title_idx = lines.index("My Title")
        self.assertEqual(lines[title_idx + 1], "")

    def test_charge_mult_line(self):
        dlg = _make_dialog(charge=1, mult=2)
        content = dlg.generate_input_content()
        self.assertIn("1 2", content.splitlines())

    def test_coordinates_present(self):
        dlg = _make_dialog(coords=["C 0.0 0.0 0.0", "H 1.0 0.0 0.0"])
        content = dlg.generate_input_content()
        self.assertIn("C 0.0 0.0 0.0", content)
        self.assertIn("H 1.0 0.0 0.0", content)

    def test_tail_appended_after_coords(self):
        dlg = _make_dialog(coords=["C 0.0 0.0 0.0"])
        dlg.tail_edit.setPlainText("1 2 F")
        content = dlg.generate_input_content()
        coord_idx = content.index("C 0.0 0.0 0.0")
        tail_idx = content.index("1 2 F")
        self.assertGreater(tail_idx, coord_idx)

    def test_trailing_blank_line(self):
        dlg = _make_dialog()
        content = dlg.generate_input_content()
        self.assertTrue(content.endswith("\n\n"))
        self.assertFalse(content.endswith("\n\n\n"))

    def test_coordinate_error_short_circuits(self):
        dlg = _make_dialog(coords=["# Error: boom"])
        content = dlg.generate_input_content()
        self.assertIn("Error generating coordinates", content)


class TestWfnOutputLine(unittest.TestCase):
    def test_wfn_line_added_when_output_wfn(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Output=WFN", filename="mol.xyz")
        content = dlg.generate_input_content()
        self.assertIn("mol.wfn", content)

    def test_wfx_line_added_when_output_wfx(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Output=WFX", filename="mol.xyz")
        content = dlg.generate_input_content()
        self.assertIn("mol.wfx", content)

    def test_no_wfn_line_by_default(self):
        dlg = _make_dialog()
        content = dlg.generate_input_content()
        self.assertNotIn(".wfn", content)
        self.assertNotIn(".wfx", content)


class TestLink1Section(unittest.TestCase):
    def test_link1_disabled_by_default_no_section(self):
        dlg = _make_dialog()
        content = dlg.generate_input_content()
        self.assertNotIn("--Link1--", content)

    def test_link1_enabled_adds_section(self):
        dlg = _make_dialog()
        dlg.link1_enable.setChecked(True)
        content = dlg.generate_input_content()
        self.assertIn("--Link1--", content)

    def test_link1_checkpoint_mode_has_no_extra_coords(self):
        dlg = _make_dialog(coords=["C 0.0 0.0 0.0"])
        dlg.link1_enable.setChecked(True)
        dlg.link1_geom_src.setCurrentText("Checkpoint (Geom=Check Guess=Read)")
        content = dlg.generate_input_content()
        # Coordinates should appear exactly once (job 1 only)
        self.assertEqual(content.count("C 0.0 0.0 0.0"), 1)

    def test_link1_copy_coordinates_mode_repeats_coords(self):
        dlg = _make_dialog(coords=["C 0.0 0.0 0.0"])
        dlg.link1_enable.setChecked(True)
        dlg.link1_geom_src.setCurrentText("Copy coordinates")
        content = dlg.generate_input_content()
        self.assertEqual(content.count("C 0.0 0.0 0.0"), 2)

    def test_link1_route_and_title_present(self):
        dlg = _make_dialog()
        dlg.link1_enable.setChecked(True)
        dlg.link1_route_edit.setPlainText("#P B3LYP/6-31G(d) Freq Geom=Check Guess=Read")
        dlg.link1_title_edit.setText("Freq Job")
        content = dlg.generate_input_content()
        self.assertIn("#P B3LYP/6-31G(d) Freq Geom=Check Guess=Read", content)
        self.assertIn("Freq Job", content)

    def test_link1_charge_mult_repeated(self):
        dlg = _make_dialog(charge=0, mult=1)
        dlg.link1_enable.setChecked(True)
        content = dlg.generate_input_content()
        self.assertEqual(content.count("0 1"), 2)

    def test_link1_ends_with_single_trailing_blank_line(self):
        dlg = _make_dialog()
        dlg.link1_enable.setChecked(True)
        content = dlg.generate_input_content()
        self.assertTrue(content.endswith("\n\n"))
        self.assertFalse(content.endswith("\n\n\n"))

    def test_link1_chk_carried_over(self):
        dlg = _make_dialog(filename="mol.xyz")
        dlg.link1_enable.setChecked(True)
        content = dlg.generate_input_content()
        chk_lines = [l for l in content.splitlines() if l.startswith("%chk=")]
        self.assertEqual(len(chk_lines), 2)
        self.assertEqual(chk_lines[0], chk_lines[1])


# ---------------------------------------------------------------------------
# _rewrite_chk
# ---------------------------------------------------------------------------


class TestRewriteChk(unittest.TestCase):
    def test_rewrites_existing_chk_line(self):
        content = "%nprocshared=4\n%chk=old.chk\n#P B3LYP/6-31G(d) Opt\n"
        result = GaussianSetupDialogPro._rewrite_chk(content, "saved_name")
        self.assertIn("%chk=saved_name.chk", result)
        self.assertNotIn("old.chk", result)

    def test_only_first_chk_line_rewritten(self):
        content = "%chk=old1.chk\n--Link1--\n%chk=old1.chk\n"
        result = GaussianSetupDialogPro._rewrite_chk(content, "new")
        lines = [l for l in result.splitlines() if l.startswith("%chk=")]
        self.assertEqual(lines[0], "%chk=new.chk")
        self.assertEqual(lines[1], "%chk=old1.chk")

    def test_no_chk_line_leaves_content_unchanged(self):
        content = "#P B3LYP/6-31G(d) Opt\n"
        result = GaussianSetupDialogPro._rewrite_chk(content, "new")
        self.assertEqual(result, content)


# ---------------------------------------------------------------------------
# _auto_suffix
# ---------------------------------------------------------------------------


class TestAutoSuffix(unittest.TestCase):
    def test_ts_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt=(TS,CalcFC,NoEigenTest)")
        self.assertEqual(dlg._auto_suffix(), "-ts")

    def test_irc_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) IRC=(CalcFC)")
        self.assertEqual(dlg._auto_suffix(), "-irc")

    def test_scan_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt=ModRedundant")
        self.assertEqual(dlg._auto_suffix(), "-scan")

    def test_opt_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt")
        self.assertEqual(dlg._auto_suffix(), "-opt")

    def test_freq_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Freq")
        self.assertEqual(dlg._auto_suffix(), "-freq")

    def test_td_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) TD=(NStates=10)")
        self.assertEqual(dlg._auto_suffix(), "-td")

    def test_nmr_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) NMR=GIAO")
        self.assertEqual(dlg._auto_suffix(), "-nmr")

    def test_sp_default_suffix(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d)")
        self.assertEqual(dlg._auto_suffix(), "-sp")

    def test_opt_freq_prefers_opt(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt Freq")
        self.assertEqual(dlg._auto_suffix(), "-opt")

    def test_ts_takes_priority_over_opt(self):
        dlg = _make_dialog(route="#P B3LYP/6-31G(d) Opt=(TS,CalcFC,NoEigenTest) Freq")
        self.assertEqual(dlg._auto_suffix(), "-ts")


if __name__ == "__main__":
    unittest.main()
