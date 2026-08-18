"""Tests for Route Builder Search Tab in Gaussian Input Generator Pro."""

from __future__ import annotations

import types
from unittest.mock import MagicMock

import pytest

pytest.importorskip("PyQt6")

from gaussian_input_generator_pro.keyword_builder import GaussianRouteBuilderDialog


def test_gaussian_route_builder_search_tab():
    dlg = types.SimpleNamespace(
        _search_catalog=[],
        tab_search=MagicMock(),
        extra_keywords=MagicMock(),
        preview_label=MagicMock(),
        method_name=MagicMock(),
        basis_set=MagicMock(),
        job_type=MagicMock(),
        dispersion=MagicMock(),
        solv_model=MagicMock(),
        solvent=MagicMock(),
        search_filter_input=MagicMock(),
        search_category_combo=MagicMock(),
        search_table=MagicMock(),
        font=MagicMock(),
        update_preview=MagicMock(),
        _filter_search_table=MagicMock(),
    )
    dlg._populate_search_database = lambda: GaussianRouteBuilderDialog._populate_search_database(dlg)
    dlg._apply_search_item = lambda kw, cat, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, kw, cat, btn)

    dlg._populate_search_database()
    assert len(dlg._search_catalog) > 0

    # Test applying a method
    dlg._apply_search_item("wB97XD", "Methods / Functionals")
    dlg.method_name.setCurrentText.assert_called_with("wB97XD")

    # Test applying a basis set
    dlg._apply_search_item("def2TZVP", "Basis Sets")
    dlg.basis_set.setCurrentText.assert_called_with("def2TZVP")




def test_gaussian_search_keeps_unmapped_keyword():
    dlg = types.SimpleNamespace(_search_extra_keywords=[], update_preview=MagicMock())
    dlg._add_search_keyword = lambda keyword: GaussianRouteBuilderDialog._add_search_keyword(dlg, keyword)
    dlg._apply_search_item = lambda keyword, category, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, keyword, category, btn)

    dlg._apply_search_item("SCF=QC", "Convergence & SCF")

    assert dlg._search_extra_keywords == ["SCF=QC"]


def test_gaussian_search_uses_exact_opt_task():
    dlg = types.SimpleNamespace(job_type=MagicMock(), _search_extra_keywords=[], update_preview=MagicMock())
    dlg._add_search_keyword = lambda keyword: GaussianRouteBuilderDialog._add_search_keyword(dlg, keyword)
    dlg._apply_search_item = lambda keyword, category, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, keyword, category, btn)

    dlg._apply_search_item("Opt", "Job Types")

    dlg.job_type.setCurrentText.assert_called_once_with("Optimization Only (Opt)")


def test_gaussian_search_guess_read_wires_the_combo_not_the_route_text():
    # Guess=Read/Mix have a dedicated scf_guess combo. Regression for a bug
    # where this fell through to the raw-keyword fallback, leaving the combo
    # at "Default" -- so a later manual change to the combo produced two
    # conflicting Guess= directives in the generated route.
    dlg = types.SimpleNamespace(scf_guess=MagicMock(), _search_extra_keywords=[], update_preview=MagicMock())
    dlg.scf_guess.findText.return_value = 0
    dlg._add_search_keyword = lambda keyword: GaussianRouteBuilderDialog._add_search_keyword(dlg, keyword)
    dlg._apply_search_item = lambda keyword, category, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, keyword, category, btn)

    dlg._apply_search_item("Guess=Read", "Convergence & SCF")

    dlg.scf_guess.setCurrentText.assert_called_once_with("Read")
    assert dlg._search_extra_keywords == []


def test_gaussian_search_guess_hcore_has_no_combo_entry_so_falls_back():
    # HCore/Alter are not in SCF_GUESS_OPTIONS at all, so there is nothing to
    # wire them to -- the raw-keyword fallback is correct here.
    dlg = types.SimpleNamespace(_search_extra_keywords=[], update_preview=MagicMock())
    dlg._add_search_keyword = lambda keyword: GaussianRouteBuilderDialog._add_search_keyword(dlg, keyword)
    dlg._apply_search_item = lambda keyword, category, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, keyword, category, btn)

    dlg._apply_search_item("Guess=HCore", "Convergence & SCF")

    assert dlg._search_extra_keywords == ["Guess=HCore"]


def test_gaussian_search_nosymm_wires_the_symmetry_combo():
    # NoSymm has a dedicated symmetry_combo. Regression for the same
    # duplicate-directive risk as Guess= above.
    dlg = types.SimpleNamespace(symmetry_combo=MagicMock(), _search_extra_keywords=[], update_preview=MagicMock())
    dlg._add_search_keyword = lambda keyword: GaussianRouteBuilderDialog._add_search_keyword(dlg, keyword)
    dlg._apply_search_item = lambda keyword, category, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, keyword, category, btn)

    dlg._apply_search_item("NoSymm", "Convergence & SCF")

    dlg.symmetry_combo.setCurrentText.assert_called_once_with("None (NoSymm)")
    assert dlg._search_extra_keywords == []