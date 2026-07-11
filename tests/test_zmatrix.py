"""
tests/test_zmatrix.py

Tests for Z-matrix coordinate output in main_dialog.py:
  - _build_zmatrix_data connectivity/reference selection
  - get_zmatrix_lines() plain and variables formats
  - _get_active_coord_lines() format dispatch + Cartesian fallback
"""

import os
import sys
import types
import importlib.util
import unittest
from types import SimpleNamespace
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
    qt_gui.QSyntaxHighlighter = type(
        "QSyntaxHighlighter", (), {"__init__": lambda s, *a, **k: None}
    )
    qt_gui.QTextCharFormat = MagicMock

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


_md_mod = _load_mod("main_dialog", "main_dialog.py")
GaussianSetupDialogPro = _md_mod.GaussianSetupDialogPro


# ---------------------------------------------------------------------------
# Fake rdkit molecule (linear chain: each atom bonded to the previous one)
# ---------------------------------------------------------------------------


class _FakeAtom:
    def __init__(self, idx, symbol, neighbors):
        self._idx = idx
        self._symbol = symbol
        self._neighbors = neighbors  # list of _FakeAtom, filled later

    def GetIdx(self):
        return self._idx

    def GetSymbol(self):
        return self._symbol

    def HasProp(self, _name):
        return False

    def GetProp(self, _name):
        raise KeyError

    def GetNeighbors(self):
        return self._neighbors


class _FakeMol:
    def __init__(self, symbols):
        self._atoms = [_FakeAtom(i, s, []) for i, s in enumerate(symbols)]
        # linear chain connectivity: i bonded to i-1 and i+1
        for i, atom in enumerate(self._atoms):
            if i > 0:
                atom._neighbors.append(self._atoms[i - 1])
            if i < len(self._atoms) - 1:
                atom._neighbors.append(self._atoms[i + 1])

    def GetAtoms(self):
        return self._atoms

    def GetConformer(self):
        return "conf"


class _FakeRdMolTransforms:
    @staticmethod
    def GetBondLength(conf, i, j):
        return 1.5

    @staticmethod
    def GetAngleDeg(conf, i, j, k):
        return 109.471

    @staticmethod
    def GetDihedralDeg(conf, i, j, k, m):
        return 180.0


def _make_ns(symbols):
    ns = SimpleNamespace()
    ns.mol = _FakeMol(symbols)
    ns._resolve_live_mol = lambda: ns.mol
    ns._build_zmatrix_data = lambda: GaussianSetupDialogPro._build_zmatrix_data(ns)
    ns.get_zmatrix_lines = (
        lambda use_variables=False: GaussianSetupDialogPro.get_zmatrix_lines(
            ns, use_variables
        )
    )
    ns.get_coords_lines = lambda: ["C     0.000000     0.000000     0.000000"]
    ns._get_active_coord_lines = (
        lambda: GaussianSetupDialogPro._get_active_coord_lines(ns)
    )
    return ns


class _FakeCombo:
    def __init__(self, text):
        self._text = text

    def currentText(self):
        return self._text


class TestZMatrixData(unittest.TestCase):
    def setUp(self):
        self._orig = _md_mod.rdMolTransforms
        _md_mod.rdMolTransforms = _FakeRdMolTransforms

    def tearDown(self):
        _md_mod.rdMolTransforms = self._orig

    def test_first_atom_has_no_refs(self):
        data = _make_ns(["C", "O"])._build_zmatrix_data()
        self.assertEqual(data[0]["symbol"], "C")
        self.assertEqual(data[0]["refs"], [])

    def test_reference_counts_grow_then_cap_at_three(self):
        data = _make_ns(["C", "C", "C", "C", "C"])._build_zmatrix_data()
        self.assertEqual([len(r["refs"]) for r in data], [0, 1, 2, 3, 3])

    def test_second_atom_references_first(self):
        data = _make_ns(["C", "O", "H"])._build_zmatrix_data()
        self.assertEqual(data[1]["refs"], [0])
        self.assertAlmostEqual(data[1]["values"][0], 1.5)

    def test_no_molecule_returns_none(self):
        ns = SimpleNamespace(
            _resolve_live_mol=lambda: None,
            _build_zmatrix_data=None,
        )
        self.assertIsNone(GaussianSetupDialogPro._build_zmatrix_data(ns))


class TestZMatrixLines(unittest.TestCase):
    def setUp(self):
        self._orig = _md_mod.rdMolTransforms
        _md_mod.rdMolTransforms = _FakeRdMolTransforms

    def tearDown(self):
        _md_mod.rdMolTransforms = self._orig

    def test_plain_zmatrix_shapes(self):
        lines = _make_ns(["C", "O", "H", "H"]).get_zmatrix_lines()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0].split(), ["C"])
        self.assertEqual(lines[1].split(), ["O", "1", "1.500000"])
        self.assertEqual(
            lines[2].split(), ["H", "2", "1.500000", "1", "109.471000"]
        )
        self.assertEqual(
            lines[3].split(),
            ["H", "3", "1.500000", "2", "109.471000", "1", "180.000000"],
        )

    def test_variables_zmatrix(self):
        lines = _make_ns(["C", "O", "H"]).get_zmatrix_lines(use_variables=True)
        self.assertEqual(lines[0].split(), ["C"])
        self.assertEqual(lines[1].split(), ["O", "1", "B2"])
        self.assertEqual(lines[2].split(), ["H", "2", "B3", "1", "A3"])
        self.assertIn("Variables:", lines)
        var_idx = lines.index("Variables:")
        var_section = lines[var_idx + 1 :]
        self.assertIn(" B2=1.500000", var_section)
        self.assertIn(" B3=1.500000", var_section)
        self.assertIn(" A3=109.471000", var_section)

    def test_empty_molecule_gives_empty_lines(self):
        ns = _make_ns(["C"])
        ns._resolve_live_mol = lambda: None
        ns._build_zmatrix_data = lambda: GaussianSetupDialogPro._build_zmatrix_data(ns)
        self.assertEqual(ns.get_zmatrix_lines(), [])


class TestActiveCoordLines(unittest.TestCase):
    def setUp(self):
        self._orig = _md_mod.rdMolTransforms
        _md_mod.rdMolTransforms = _FakeRdMolTransforms

    def tearDown(self):
        _md_mod.rdMolTransforms = self._orig

    def test_default_is_cartesian_when_combo_missing(self):
        ns = _make_ns(["C", "O"])
        lines = ns._get_active_coord_lines()
        self.assertEqual(lines, ["C     0.000000     0.000000     0.000000"])

    def test_cartesian_selection(self):
        ns = _make_ns(["C", "O"])
        ns.coord_format_combo = _FakeCombo("Cartesian (XYZ)")
        self.assertEqual(
            ns._get_active_coord_lines(),
            ["C     0.000000     0.000000     0.000000"],
        )

    def test_zmatrix_selection(self):
        ns = _make_ns(["C", "O"])
        ns.coord_format_combo = _FakeCombo("Z-Matrix")
        lines = ns._get_active_coord_lines()
        self.assertEqual(lines[1].split(), ["O", "1", "1.500000"])

    def test_zmatrix_variables_selection(self):
        ns = _make_ns(["C", "O"])
        ns.coord_format_combo = _FakeCombo("Z-Matrix (variables)")
        lines = ns._get_active_coord_lines()
        self.assertEqual(lines[1].split(), ["O", "1", "B2"])
        self.assertIn("Variables:", lines)

    def test_fallback_to_cartesian_on_zmatrix_failure(self):
        ns = _make_ns(["C", "O"])
        ns.coord_format_combo = _FakeCombo("Z-Matrix")
        ns.get_zmatrix_lines = lambda use_variables=False: [
            "! Error generating Z-Matrix: boom"
        ]
        lines = ns._get_active_coord_lines()
        self.assertIn("! Z-Matrix generation failed; using Cartesian", lines[0])
        self.assertIn("C     0.000000     0.000000     0.000000", lines)


if __name__ == "__main__":
    unittest.main()
