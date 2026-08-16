"""Tests for Route Builder Search Tab in Gaussian Input Generator Pro."""

from __future__ import annotations

import types
from unittest.mock import MagicMock

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
    )
    dlg._populate_search_database = lambda: GaussianRouteBuilderDialog._populate_search_database(dlg)
    dlg._filter_search_table = lambda: GaussianRouteBuilderDialog._filter_search_table(dlg)
    dlg._apply_search_item = lambda kw, cat, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, kw, cat, btn)
    dlg._on_search_row_double_clicked = lambda r, c: GaussianRouteBuilderDialog._on_search_row_double_clicked(dlg, r, c)

    GaussianRouteBuilderDialog.setup_search_tab(dlg)

    assert len(dlg._search_catalog) > 0

    # Test filtering
    dlg.search_filter_input.setText("wB97XD")
    dlg.search_category_combo.setCurrentText("All Categories")
    GaussianRouteBuilderDialog._filter_search_table(dlg)
    assert dlg.search_table.rowCount() > 0

    # Test applying a method
    GaussianRouteBuilderDialog._apply_search_item(dlg, "wB97XD", "Methods / Functionals")
    dlg.method_name.setCurrentText.assert_called_with("wB97XD")

    # Test applying a basis set
    GaussianRouteBuilderDialog._apply_search_item(dlg, "def2TZVP", "Basis Sets")
    dlg.basis_set.setCurrentText.assert_called_with("def2TZVP")
