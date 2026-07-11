"""
tests/test_constraints_picking.py

Tests for the Constraints/Scan (ModRedundant) tab and 3D atom picking:
  - format_modredundant_line() pure formatting
  - Dialog3DPickingMixin integration surface on GaussianRouteBuilderDialog
  - on_atom_picked() selection toggling / 4-atom window
  - get_modredundant_lines() from a fake table
  - GaussianSetupDialogPro._append_modredundant_lines() dedup append
  - Opt=(ModRedundant, ...) injection when constraints exist
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


_kb_mod = _load_mod("keyword_builder", "keyword_builder.py")
_mixins_mod = _load_mod("mixins", "mixins.py")
_md_mod = _load_mod("main_dialog", "main_dialog.py")

format_modredundant_line = _kb_mod.format_modredundant_line
parse_modredundant_line = _kb_mod.parse_modredundant_line
GaussianRouteBuilderDialog = _kb_mod.GaussianRouteBuilderDialog
Dialog3DPickingMixin = _mixins_mod.Dialog3DPickingMixin
GaussianSetupDialogPro = _md_mod.GaussianSetupDialogPro


# ---------------------------------------------------------------------------
# Pure formatting
# ---------------------------------------------------------------------------


class TestFormatModredundantLine(unittest.TestCase):
    def test_freeze_atom(self):
        self.assertEqual(format_modredundant_line([3]), "X 3 F")

    def test_freeze_bond(self):
        self.assertEqual(format_modredundant_line([1, 2]), "B 1 2 F")

    def test_freeze_angle(self):
        self.assertEqual(format_modredundant_line([1, 2, 3]), "A 1 2 3 F")

    def test_freeze_dihedral(self):
        self.assertEqual(format_modredundant_line([1, 2, 3, 4]), "D 1 2 3 4 F")

    def test_scan_bond(self):
        self.assertEqual(
            format_modredundant_line([1, 2], is_scan=True, steps=10, step_size=0.1),
            "B 1 2 S 10 0.10",
        )

    def test_scan_dihedral(self):
        self.assertEqual(
            format_modredundant_line(
                [5, 6, 7, 8], is_scan=True, steps=36, step_size=10.0
            ),
            "D 5 6 7 8 S 36 10.00",
        )

    def test_invalid_atom_counts(self):
        with self.assertRaises(ValueError):
            format_modredundant_line([])
        with self.assertRaises(ValueError):
            format_modredundant_line([1, 2, 3, 4, 5])


class TestParseModredundantLine(unittest.TestCase):
    def test_round_trip_freeze(self):
        for indices in ([3], [1, 2], [1, 2, 3], [1, 2, 3, 4]):
            line = format_modredundant_line(indices)
            self.assertEqual(
                parse_modredundant_line(line), (indices, False, 10, 0.1)
            )

    def test_round_trip_scan(self):
        line = format_modredundant_line([1, 2], is_scan=True, steps=20, step_size=0.05)
        self.assertEqual(parse_modredundant_line(line), ([1, 2], True, 20, 0.05))

    def test_case_insensitive(self):
        self.assertIsNotNone(parse_modredundant_line("b 1 2 f"))

    def test_rejects_non_constraint_lines(self):
        for line in [
            "C H O 0",          # Gen basis atoms line
            "6-31G(d)",
            "****",
            "$NBO",
            "B 1 2",            # missing action
            "B 1 2 3 F",        # wrong index count for B
            "A 1 2 F",          # wrong index count for A
            "B 1 2 S",          # scan without steps
            "",
        ]:
            self.assertIsNone(parse_modredundant_line(line), line)


# ---------------------------------------------------------------------------
# Mixin integration surface
# ---------------------------------------------------------------------------


class TestPickingIntegration(unittest.TestCase):
    def test_builder_inherits_mixin(self):
        self.assertTrue(
            issubclass(GaussianRouteBuilderDialog, Dialog3DPickingMixin)
        )

    def test_mixin_callbacks_defined(self):
        for name in [
            "on_atom_picked",
            "clear_selection",
            "update_selection_display",
            "add_constraint",
            "remove_constraint",
            "clear_all_constraints",
            "get_modredundant_lines",
            "setup_constraints_tab",
            "on_tab_changed",
        ]:
            self.assertTrue(
                hasattr(GaussianRouteBuilderDialog, name), f"missing {name}"
            )

    def test_mixin_provides_picking_api(self):
        for name in [
            "enable_picking",
            "disable_picking",
            "eventFilter",
            "show_atom_labels_for",
            "clear_selection_labels",
        ]:
            self.assertTrue(hasattr(Dialog3DPickingMixin, name), f"missing {name}")

    def test_close_paths_disable_picking(self):
        import inspect

        for name in ["closeEvent", "accept", "reject"]:
            src = inspect.getsource(getattr(GaussianRouteBuilderDialog, name))
            self.assertIn("disable_picking", src, f"{name} must disable picking")


class TestOnAtomPicked(unittest.TestCase):
    def _make(self):
        return SimpleNamespace(
            selected_atoms=[],
            update_selection_display=lambda: None,
            on_atom_picked=None,
        )

    def _pick(self, ns, idx):
        GaussianRouteBuilderDialog.on_atom_picked(ns, idx)

    def test_pick_appends(self):
        ns = self._make()
        self._pick(ns, 0)
        self._pick(ns, 5)
        self.assertEqual(ns.selected_atoms, [0, 5])

    def test_pick_toggles_off(self):
        ns = self._make()
        self._pick(ns, 3)
        self._pick(ns, 3)
        self.assertEqual(ns.selected_atoms, [])

    def test_max_four_atoms_fifo(self):
        ns = self._make()
        for i in range(5):
            self._pick(ns, i)
        self.assertEqual(ns.selected_atoms, [1, 2, 3, 4])


# ---------------------------------------------------------------------------
# get_modredundant_lines with a fake table
# ---------------------------------------------------------------------------


class _FakeItem:
    def __init__(self, text):
        self._text = text

    def text(self):
        return self._text


class _FakeChk:
    def __init__(self, checked):
        self._checked = checked

    def isChecked(self):
        return self._checked


class _FakeChkWidget:
    def __init__(self, checked):
        self._chk = _FakeChk(checked)

    def findChild(self, _cls):
        return self._chk


class _FakeTable:
    """rows: list of dicts {indices, scan, steps, step_size}"""

    def __init__(self, rows):
        self._rows = rows

    def rowCount(self):
        return len(self._rows)

    def item(self, r, c):
        row = self._rows[r]
        if c == 1:
            return _FakeItem(row["indices"])
        if c == 4:
            return _FakeItem(str(row.get("steps", 10)))
        if c == 5:
            return _FakeItem(str(row.get("step_size", 0.1)))
        return None

    def cellWidget(self, r, c):
        if c == 3:
            return _FakeChkWidget(self._rows[r].get("scan", False))
        return None


class TestGetModredundantLines(unittest.TestCase):
    def _lines(self, rows):
        ns = SimpleNamespace(constraint_table=_FakeTable(rows))
        return GaussianRouteBuilderDialog.get_modredundant_lines(ns)

    def test_no_table(self):
        ns = SimpleNamespace()
        self.assertEqual(GaussianRouteBuilderDialog.get_modredundant_lines(ns), [])

    def test_freeze_rows(self):
        lines = self._lines(
            [{"indices": "1 2"}, {"indices": "1 2 3"}, {"indices": "4"}]
        )
        self.assertEqual(lines, ["B 1 2 F", "A 1 2 3 F", "X 4 F"])

    def test_scan_row(self):
        lines = self._lines(
            [{"indices": "1 2", "scan": True, "steps": 20, "step_size": 0.05}]
        )
        self.assertEqual(lines, ["B 1 2 S 20 0.05"])

    def test_bad_indices_skipped(self):
        lines = self._lines([{"indices": "a b"}, {"indices": "1 2"}])
        self.assertEqual(lines, ["B 1 2 F"])

    def test_too_many_indices_skipped(self):
        lines = self._lines([{"indices": "1 2 3 4 5"}, {"indices": "1 2"}])
        self.assertEqual(lines, ["B 1 2 F"])


# ---------------------------------------------------------------------------
# Main dialog: appending to the tail
# ---------------------------------------------------------------------------


class _FakeTailEdit:
    def __init__(self, text=""):
        self._text = text

    def toPlainText(self):
        return self._text

    def setPlainText(self, text):
        self._text = text


class TestSyncModredundantLines(unittest.TestCase):
    """Full two-way sync: the tail's constraint lines mirror the builder table."""

    def _make(self, tail_text, builder_lines):
        builder = SimpleNamespace(get_modredundant_lines=lambda: builder_lines)
        ns = SimpleNamespace(
            builder_dialog=builder, tail_edit=_FakeTailEdit(tail_text)
        )
        ns._split_tail_modredundant = GaussianSetupDialogPro._split_tail_modredundant
        return ns

    def _run(self, ns):
        GaussianSetupDialogPro._sync_modredundant_lines(ns)

    def test_append_to_empty_tail(self):
        ns = self._make("", ["B 1 2 F", "A 1 2 3 F"])
        self._run(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "B 1 2 F\nA 1 2 3 F\n")

    def test_preserves_non_constraint_content(self):
        ns = self._make("$NBO\n$END\n", ["B 1 2 F"])
        self._run(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "$NBO\n$END\nB 1 2 F\n")

    def test_removed_row_disappears_from_tail(self):
        ns = self._make("B 1 2 F\nA 1 2 3 F\n", ["B 1 2 F"])
        self._run(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "B 1 2 F\n")

    def test_cleared_table_removes_all_constraint_lines(self):
        ns = self._make("$NBO\n$END\nB 1 2 F\nD 1 2 3 4 F\n", [])
        self._run(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "$NBO\n$END\n")

    def test_clearing_everything_empties_tail(self):
        ns = self._make("B 1 2 F\n", [])
        self._run(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "")

    def test_edited_scan_replaces_freeze(self):
        ns = self._make("B 1 2 F\n", ["B 1 2 S 10 0.10"])
        self._run(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "B 1 2 S 10 0.10\n")

    def test_unchanged_is_noop(self):
        ns = self._make("keepme\nB 1 2 F\n", ["B 1 2 F"])
        self._run(ns)
        # old == new -> early return, text untouched (order preserved)
        self.assertEqual(ns.tail_edit.toPlainText(), "keepme\nB 1 2 F\n")

    def test_no_builder_is_noop(self):
        ns = SimpleNamespace(builder_dialog=None, tail_edit=_FakeTailEdit("x"))
        GaussianSetupDialogPro._sync_modredundant_lines(ns)
        self.assertEqual(ns.tail_edit.toPlainText(), "x")


class TestSplitTailModredundant(unittest.TestCase):
    def test_split(self):
        others, modred = GaussianSetupDialogPro._split_tail_modredundant(
            "C H O 0\n6-31G(d)\n****\nB 1 2 F\nA 1 2 3 S 5 2.00\n"
        )
        self.assertEqual(modred, ["B 1 2 F", "A 1 2 3 S 5 2.00"])
        self.assertEqual(others, ["C H O 0", "6-31G(d)", "****"])


# ---------------------------------------------------------------------------
# Main dialog: auto-insert of route-implied tail sections ($NBO)
# ---------------------------------------------------------------------------


class TestAutoInsertTailForRoute(unittest.TestCase):
    def _run(self, route, tail_text=""):
        ns = SimpleNamespace(tail_edit=_FakeTailEdit(tail_text))
        GaussianSetupDialogPro._auto_insert_tail_for_route(ns, route)
        return ns.tail_edit.toPlainText()

    def test_nboread_inserts_nbo_section(self):
        tail = self._run("#P B3LYP/6-31G(d) Pop=NBORead Opt")
        self.assertIn("$NBO", tail)
        self.assertIn("$END", tail)

    def test_case_insensitive_route_match(self):
        tail = self._run("#p b3lyp/6-31g(d) pop=nboread")
        self.assertIn("$NBO", tail)

    def test_plain_pop_nbo_does_not_insert(self):
        tail = self._run("#P B3LYP/6-31G(d) Pop=NBO")
        self.assertEqual(tail, "")

    def test_existing_nbo_section_not_duplicated(self):
        existing = "$NBO\n  BNDIDX\n$END\n"
        tail = self._run("#P B3LYP/6-31G(d) Pop=NBORead", existing)
        self.assertEqual(tail, existing)
        self.assertEqual(tail.upper().count("$NBO"), 1)

    def test_existing_tail_content_preserved(self):
        tail = self._run("#P HF/6-31G(d) Pop=NBORead", "B 1 2 F\n")
        self.assertTrue(tail.startswith("B 1 2 F\n"))
        self.assertIn("$NBO", tail)

    def test_route_without_nbo_is_noop(self):
        tail = self._run("#P B3LYP/6-31G(d) Opt Freq", "B 1 2 F\n")
        self.assertEqual(tail, "B 1 2 F\n")


if __name__ == "__main__":
    unittest.main()
