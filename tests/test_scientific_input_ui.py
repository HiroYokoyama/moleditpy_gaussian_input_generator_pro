"""Scientific input semantics through real Qt/RDKit dialog operations."""

import sys
from unittest.mock import patch

from . import test_input_loading_ui as loading_tests
from .test_main_dialog_extended import (
    _make_water,
    _real_module,
    _RealDialogTestCase,
    main_dialog_mod,
)


class TestScientificInput(_RealDialogTestCase):
    def setUp(self):
        _RealDialogTestCase.setUp(self)
        modules = {
            name: _real_module(name)
            for name in (
                "PySide6",
                "PySide6.QtCore",
                "PySide6.QtWidgets",
                "rdkit",
                "rdkit.Chem",
            )
        }
        context = patch.dict(sys.modules, modules)
        context.start()
        self.addCleanup(context.stop)
        chemistry = patch.object(modules["rdkit"], "Chem", modules["rdkit.Chem"])
        chemistry.start()
        self.addCleanup(chemistry.stop)

    make_dialog = loading_tests.TestInputLoading.make_dialog

    def test_ghost_import_refresh_keeps_basis_only_atom_and_electron_count(self):
        dialog = self.make_dialog({})
        dialog.restore_input_text(
            "# HF/STO-3G\n\nghost\n\n0 2\nH 0 0 0\nH-Bq 0 0 1\n\n"
        )
        dialog.refresh_input_preview()
        assert "H-Bq" in dialog.preview_text.toPlainText()
        assert main_dialog_mod._electron_count(dialog.mol, 0) == 1

    def test_bohr_import_refresh_preserves_bond_length(self):
        dialog = self.make_dialog({})
        dialog.restore_input_text(
            "# HF/STO-3G Units=Bohr\n\nhydrogen\n\n0 1\nH 0 0 0\nH 0 0 1\n\n"
        )
        dialog.refresh_input_preview()
        from .test_input_parsing import loader

        _, rows, _ = loader.parse_input(dialog.preview_text.toPlainText(), "gaussian")
        assert abs(rows[1][3] - 0.529177210903) < 1e-6

    def test_link1_keeps_job_one_checkpoint_instead_of_reapplying_oldchk(self):
        dialog = self.make_dialog({}, mol=_make_water())
        dialog.oldchk_edit.setText("initial.chk")
        dialog.link1_enable.setChecked(True)
        first, second = dialog.generate_input_content().split("--Link1--")
        assert "%oldchk=initial.chk" in first
        assert "%oldchk" not in second
        assert "Geom=Check" in second

    def test_allcheck_does_not_emit_title_charge_or_coordinates(self):
        dialog = self.make_dialog({}, mol=_make_water())
        dialog.keywords_edit.setPlainText("# HF/Gen Geom=(Connectivity,AllCheck)")
        dialog.comment_edit.setText("DO NOT EMIT THIS TITLE")
        dialog.tail_edit.setPlainText("H O 0\nSTO-3G\n****")
        text = dialog.generate_input_content()
        assert "DO NOT EMIT" not in text and "\n0 1\n" not in text
        assert "\n\nH O 0\nSTO-3G\n****" in text

    def test_link1_allcheck_does_not_emit_title_charge_or_coordinates(self):
        dialog = self.make_dialog({}, mol=_make_water())
        dialog.link1_enable.setChecked(True)
        dialog.link1_route_edit.setPlainText("# HF/STO-3G Geom=AllCheck Output=WFX")
        dialog.link1_title_edit.setText("DO NOT EMIT THIS TITLE")
        text = dialog.generate_input_content().split("--Link1--")[1]
        assert "DO NOT EMIT" not in text and "\n0 1\n" not in text
        assert "-link1.wfx" in text

    def test_checkpoint_source_without_route_flag_emits_geom_check(self):
        dialog = self.make_dialog({}, mol=_make_water())
        dialog.link1_enable.setChecked(True)
        dialog.link1_route_edit.setPlainText("# HF/STO-3G Freq")
        assert "Geom=Check" in dialog.generate_input_content().split("--Link1--")[1]

    def test_builder_preserves_bare_method_default_basis_and_explicit_basis(self):
        builder_class = sys.modules[
            main_dialog_mod.GaussianRouteBuilderDialog.__module__
        ].GaussianRouteBuilderDialog
        for route in ("# HF", "# B3LYP def2SVP Opt"):
            builder = builder_class(None, route)
            self.addCleanup(builder.deleteLater)
            generated = builder.get_route()
            assert "6-31G" not in generated
            if "def2SVP" in route:
                assert "B3LYP/def2SVP" in generated

    def test_ts_does_not_disable_eigenvalue_validation_implicitly(self):
        builder = main_dialog_mod.GaussianRouteBuilderDialog(None, "# HF/STO-3G Opt=TS")
        self.addCleanup(builder.deleteLater)
        assert "NoEigenTest" not in builder.get_route()
        builder.parse_route("# HF/STO-3G Opt=(TS,NoEigenTest)")
        assert "NoEigenTest" in builder.get_route()

    def test_linear_reference_plane_falls_back_without_nan_coordinates(self):
        mol = _make_water()
        from rdkit import Chem

        editable = Chem.RWMol(mol)
        editable.AddAtom(Chem.Atom("H"))
        mol = editable.GetMol()
        conf = Chem.Conformer(4)
        for index in range(4):
            conf.SetAtomPosition(index, (0.0, 0.0, float(index)))
        mol.RemoveAllConformers()
        mol.AddConformer(conf)
        dialog = self.make_dialog({}, mol=mol)
        dialog.coord_format_combo.setCurrentText("Z-Matrix")
        text = dialog.generate_input_content()
        assert "nan" not in text.lower()
        assert "Falling back to XYZ" in text or "using Cartesian" in text
