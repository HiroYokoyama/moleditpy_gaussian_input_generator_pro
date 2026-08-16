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
    )
    dlg._populate_search_database = lambda: GaussianRouteBuilderDialog._populate_search_database(dlg)
    dlg._filter_search_table = lambda: GaussianRouteBuilderDialog._filter_search_table(dlg)
    dlg._apply_search_item = lambda kw, cat, btn=None: GaussianRouteBuilderDialog._apply_search_item(dlg, kw, cat, btn)
    dlg._on_search_row_double_clicked = lambda r, c: GaussianRouteBuilderDialog._on_search_row_double_clicked(dlg, r, c)

    dlg._populate_search_database()
    assert len(dlg._search_catalog) > 0

    # Test filtering
    dlg.search_filter_input.text.return_value = "wB97XD"
    dlg.search_category_combo.currentText.return_value = "All Categories"
    dlg._filter_search_table()
    assert dlg.search_table.setRowCount.called

    # Test applying a method
    dlg._apply_search_item("wB97XD", "Methods / Functionals")
    dlg.method_name.setCurrentText.assert_called_with("wB97XD")

    # Test applying a basis set
    dlg._apply_search_item("def2TZVP", "Basis Sets")
    dlg.basis_set.setCurrentText.assert_called_with("def2TZVP")

