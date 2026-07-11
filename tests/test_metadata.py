"""
tests/test_metadata.py

Tests for gaussian_input_generator_pro/__init__.py:
  - Plugin identity constants
  - get_default_settings() shape and types
  - initialize() registration contract (stub context)
"""

import os
import sys
import types
import importlib.util
import unittest
from unittest.mock import MagicMock

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Qt / heavy-dep stubs (must be installed before any plugin import)
# ---------------------------------------------------------------------------


def _install_stubs():
    pyqt6 = types.ModuleType("PyQt6")
    qt_widgets = types.ModuleType("PyQt6.QtWidgets")
    qt_core = types.ModuleType("PyQt6.QtCore")
    qt_gui = types.ModuleType("PyQt6.QtGui")
    for name in [
        "QDialog",
        "QVBoxLayout",
        "QHBoxLayout",
        "QLabel",
        "QLineEdit",
        "QSpinBox",
        "QPushButton",
        "QGroupBox",
        "QComboBox",
        "QTextEdit",
        "QTabWidget",
        "QCheckBox",
        "QWidget",
        "QFormLayout",
        "QCompleter",
        "QSizePolicy",
        "QMessageBox",
        "QFileDialog",
        "QInputDialog",
        "QApplication",
        "QScrollArea",
    ]:
        setattr(qt_widgets, name, MagicMock)
    for name in ["Qt", "QTimer", "QRegularExpression", "QThread", "QSize"]:
        setattr(qt_core, name, MagicMock)
    for name in [
        "QColor",
        "QFont",
        "QSyntaxHighlighter",
        "QTextCharFormat",
        "QAction",
        "QIcon",
        "QPalette",
        "QKeySequence",
        "QShortcut",
    ]:
        setattr(qt_gui, name, MagicMock)
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
            "pyvista": MagicMock(),
        }
    )


_install_stubs()


def _load_init():
    path = os.path.join(_REPO_ROOT, "gaussian_input_generator_pro", "__init__.py")
    spec = importlib.util.spec_from_file_location("gaussian_input_generator_pro", path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "gaussian_input_generator_pro"
    sys.modules["gaussian_input_generator_pro"] = mod
    spec.loader.exec_module(mod)
    return mod


_init = _load_init()


class TestPluginMetadata(unittest.TestCase):
    def test_plugin_name_present(self):
        self.assertTrue(hasattr(_init, "PLUGIN_NAME"))

    def test_plugin_name_is_string(self):
        self.assertIsInstance(_init.PLUGIN_NAME, str)
        self.assertTrue(len(_init.PLUGIN_NAME) > 0)

    def test_plugin_version_present(self):
        self.assertTrue(hasattr(_init, "PLUGIN_VERSION"))

    def test_plugin_version_semver(self):
        parts = _init.PLUGIN_VERSION.split(".")
        self.assertEqual(len(parts), 3, "Version must be X.Y.Z")
        for p in parts:
            self.assertTrue(p.isdigit(), f"Version part not numeric: {p}")

    def test_plugin_author_present(self):
        self.assertTrue(hasattr(_init, "PLUGIN_AUTHOR"))
        self.assertIsInstance(_init.PLUGIN_AUTHOR, str)

    def test_plugin_description_present(self):
        self.assertTrue(hasattr(_init, "PLUGIN_DESCRIPTION"))

    def test_plugin_supported_version_present(self):
        self.assertTrue(hasattr(_init, "PLUGIN_SUPPORTED_MOLEDITPY_VERSION"))
        ver = _init.PLUGIN_SUPPORTED_MOLEDITPY_VERSION
        self.assertIsInstance(ver, str)
        self.assertGreater(len(ver), 0)


class TestDefaultSettings(unittest.TestCase):
    def setUp(self):
        self.s = _init.get_default_settings()

    def test_returns_dict(self):
        self.assertIsInstance(self.s, dict)

    def test_nproc_key(self):
        self.assertIn("nproc", self.s)
        self.assertIsInstance(self.s["nproc"], int)
        self.assertGreater(self.s["nproc"], 0)

    def test_mem_keys(self):
        self.assertIn("mem_val", self.s)
        self.assertIn("mem_unit", self.s)
        self.assertIn(self.s["mem_unit"], ("GB", "MB", "MW"))

    def test_chk_key(self):
        self.assertIn("chk", self.s)

    def test_route_key(self):
        self.assertIn("route", self.s)
        self.assertIsInstance(self.s["route"], str)
        self.assertTrue(self.s["route"].startswith("#"))

    def test_link1_keys(self):
        self.assertIn("link1_enabled", self.s)
        self.assertIn("link1_route", self.s)
        self.assertIn("link1_title", self.s)
        self.assertIn("link1_geom_src", self.s)

    def test_two_calls_return_independent_dicts(self):
        a = _init.get_default_settings()
        b = _init.get_default_settings()
        a["nproc"] = 999
        self.assertNotEqual(b["nproc"], 999)


class TestInitialize(unittest.TestCase):
    def _make_context(self):
        ctx = MagicMock()
        ctx.get_main_window.return_value = MagicMock()
        return ctx

    def test_initialize_callable(self):
        self.assertTrue(callable(_init.initialize))

    def test_registers_export_action(self):
        ctx = self._make_context()
        _init.initialize(ctx)
        ctx.add_export_action.assert_called_once()
        args = ctx.add_export_action.call_args[0]
        self.assertIsInstance(args[0], str)
        self.assertTrue(callable(args[1]))
        self.assertEqual(args[0], "Gaussian Input...")

    def test_registers_save_handler(self):
        ctx = self._make_context()
        _init.initialize(ctx)
        ctx.register_save_handler.assert_called_once()

    def test_registers_load_handler(self):
        ctx = self._make_context()
        _init.initialize(ctx)
        ctx.register_load_handler.assert_called_once()

    def test_registers_reset_handler(self):
        ctx = self._make_context()
        _init.initialize(ctx)
        ctx.register_document_reset_handler.assert_called_once()

    def test_save_handler_returns_none_before_dialog_opened(self):
        ctx = self._make_context()
        _init._dialog_opened = False
        _init.initialize(ctx)
        save_fn = ctx.register_save_handler.call_args[0][0]
        self.assertIsNone(save_fn())

    def test_save_handler_returns_dict_after_dialog_opened(self):
        ctx = self._make_context()
        _init._dialog_opened = True
        _init.initialize(ctx)
        save_fn = ctx.register_save_handler.call_args[0][0]
        self.assertIsInstance(save_fn(), dict)

    def test_load_handler_updates_settings(self):
        ctx = self._make_context()
        _init._dialog_opened = True
        _init.initialize(ctx)
        load_fn = ctx.register_load_handler.call_args[0][0]
        load_fn({"nproc": 42, "mem_val": 8})
        save_fn = ctx.register_save_handler.call_args[0][0]
        saved = save_fn()
        self.assertEqual(saved["nproc"], 42)
        self.assertEqual(saved["mem_val"], 8)

    def test_load_handler_filters_charge_and_mult(self):
        ctx = self._make_context()
        _init._dialog_opened = True
        _init.initialize(ctx)
        load_fn = ctx.register_load_handler.call_args[0][0]
        load_fn({"nproc": 8, "charge": 1, "mult": 2})
        save_fn = ctx.register_save_handler.call_args[0][0]
        saved = save_fn()
        self.assertNotIn("charge", saved)
        self.assertNotIn("mult", saved)

    def test_reset_handler_restores_defaults(self):
        ctx = self._make_context()
        ctx.get_window.return_value = None  # no dialog open
        _init._dialog_opened = True
        _init.initialize(ctx)
        load_fn = ctx.register_load_handler.call_args[0][0]
        load_fn({"nproc": 99})
        reset_fn = ctx.register_document_reset_handler.call_args[0][0]
        reset_fn()
        save_fn = ctx.register_save_handler.call_args[0][0]
        self.assertIsNone(save_fn())

    def test_reset_deferred_when_dialog_close_is_cancelled(self):
        ctx = self._make_context()
        _init._dialog_opened = True
        _init.initialize(ctx)

        load_fn = ctx.register_load_handler.call_args[0][0]
        load_fn({"nproc": 99})

        dlg = MagicMock()
        dlg.isVisible.return_value = True  # close() was cancelled by the user
        ctx.get_window.return_value = dlg

        reset_fn = ctx.register_document_reset_handler.call_args[0][0]
        reset_fn()

        dlg.close.assert_called_once()
        save_fn = ctx.register_save_handler.call_args[0][0]
        saved = save_fn()
        self.assertIsNotNone(saved)
        self.assertEqual(saved["nproc"], 99)

    def test_reset_proceeds_when_dialog_closes_successfully(self):
        ctx = self._make_context()
        _init._dialog_opened = True
        _init.initialize(ctx)

        load_fn = ctx.register_load_handler.call_args[0][0]
        load_fn({"nproc": 99})

        dlg = MagicMock()
        dlg.isVisible.return_value = False  # close() succeeded
        ctx.get_window.return_value = dlg

        reset_fn = ctx.register_document_reset_handler.call_args[0][0]
        reset_fn()

        dlg.close.assert_called_once()
        save_fn = ctx.register_save_handler.call_args[0][0]
        self.assertIsNone(save_fn())


if __name__ == "__main__":
    unittest.main()
