"""
tests/test_highlighter_extended.py

Behavioural tests for GaussianSyntaxHighlighter (highlighter.py).

Unlike test_keyword_builder_extended.py, which stubs PyQt6 so pure-logic
paths run without a GUI toolkit, this file needs the *real* PyQt6:
QSyntaxHighlighter/QRegularExpression behaviour is what is under test, and a
stub cannot tell us whether a pattern flag actually exists or a rule
actually matches. The whole module is skipped when PyQt6 is unavailable
(as it is in the bare-pytest CI job), so it never causes a collection
error there.

Unlike the ORCA sibling's highlighter, GaussianSyntaxHighlighter's
highlightBlock() applies every rule unconditionally to every line (no
per-line "is this a route line?" gating), so the rule coverage here is
mostly independent per-rule checks rather than branch combinations.
"""

import os
import sys
import importlib.util
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))

try:
    from PyQt6.QtGui import QTextDocument
    from PyQt6.QtWidgets import QApplication
except ImportError:  # pragma: no cover - exercised only on PyQt6-less runs
    QApplication = None

if QApplication is None:
    import pytest

    pytest.skip("requires real PyQt6 (host app dep)", allow_module_level=True)


def _load_highlighter():
    full_name = "gaussian_input_generator_pro.highlighter"
    if full_name in sys.modules:
        return sys.modules[full_name]
    path = os.path.join(_REPO_ROOT, "gaussian_input_generator_pro", "highlighter.py")
    spec = importlib.util.spec_from_file_location(full_name, path)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "gaussian_input_generator_pro"
    sys.modules[full_name] = mod
    spec.loader.exec_module(mod)
    return mod


_HL_MOD = _load_highlighter()


class HighlighterTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.mod = _HL_MOD
        cls.Highlighter = cls.mod.GaussianSyntaxHighlighter

    def formats_for(self, text):
        doc = QTextDocument()
        hl = self.Highlighter(doc)
        doc.setPlainText(text)
        hl.rehighlight()
        self._hl = hl
        block = doc.firstBlock()
        return [(r.start, r.length, r.format) for r in block.layout().formats()]

    def assert_highlighted(self, text, msg=None):
        self.assertTrue(
            self.formats_for(text),
            msg or f"expected {text!r} to be highlighted, got nothing",
        )

    def assert_not_highlighted(self, text, msg=None):
        self.assertEqual(
            [], self.formats_for(text), msg or f"expected {text!r} to be left plain"
        )


class TestHighlighterConstruction(HighlighterTestBase):
    def test_constructs_without_error(self):
        doc = QTextDocument()
        hl = self.Highlighter(doc)
        self.assertIsNotNone(hl)

    def test_accepts_none_parent(self):
        self.assertIsNotNone(self.Highlighter(None))

    def test_builds_rule_table(self):
        hl = self.Highlighter(QTextDocument())
        self.assertTrue(hl.rules, "expected a non-empty rule table")
        for pattern, fmt in hl.rules:
            self.assertTrue(pattern.isValid(), f"invalid regex: {pattern.pattern()!r}")
            self.assertIsNotNone(fmt)


class TestLink0Lines(HighlighterTestBase):
    def test_percent_nprocshared_highlighted(self):
        self.assert_highlighted("%nprocshared=4")

    def test_percent_mem_highlighted(self):
        self.assert_highlighted("%mem=4GB")

    def test_percent_chk_highlighted(self):
        self.assert_highlighted("%chk=molecule.chk")

    def test_bare_percent_line(self):
        self.assert_highlighted("%oldchk=old.chk")


class TestRouteLines(HighlighterTestBase):
    def test_hash_route_line_highlighted(self):
        self.assert_highlighted("#P B3LYP/6-31G(d) Opt Freq")

    def test_bare_hash_highlighted(self):
        self.assert_highlighted("# comment style route")

    def test_full_line_covered(self):
        line = "#P B3LYP/6-31G(d) Opt Freq"
        formats = self.formats_for(line)
        covered = max(start + length for start, length, _ in formats)
        self.assertEqual(len(line), covered)


class TestKeywordTokens(HighlighterTestBase):
    """The keyword rule applies on ANY line (no route-line gating), unlike
    the ORCA sibling highlighter."""

    def test_method_keyword_on_plain_line(self):
        self.assert_highlighted("B3LYP")

    def test_pbe1pbe_keyword(self):
        self.assert_highlighted("PBE1PBE")

    def test_job_keyword_opt(self):
        self.assert_highlighted("Opt")

    def test_job_keyword_freq(self):
        self.assert_highlighted("Freq")

    def test_modredundant_keyword(self):
        self.assert_highlighted("ModRedundant")

    def test_scrf_keyword(self):
        self.assert_highlighted("SCRF")

    def test_keyword_case_insensitive(self):
        upper = self.formats_for("B3LYP OPT")
        lower = self.formats_for("b3lyp opt")
        self.assertEqual(
            [(s, l) for s, l, _ in upper],
            [(s, l) for s, l, _ in lower],
            "case-insensitive flag not applied to the keyword rule",
        )


class TestLink1Separator(HighlighterTestBase):
    def test_link1_highlighted(self):
        self.assert_highlighted("--Link1--")

    def test_link1_case_insensitive(self):
        self.assert_highlighted("--LINK1--")

    def test_link1_with_trailing_whitespace(self):
        self.assert_highlighted("--Link1--   ")

    def test_link1_with_leading_text_not_matched_as_separator(self):
        """The ^--Link1--\\s*$ rule requires the whole line; text before it
        must not match that particular rule (still fine if other rules
        happen to match some other substring)."""
        formats = self.formats_for("foo --Link1--")
        # Confirm the Link1 rule itself specifically didn't fire the entire
        # remaining span the way the anchored rule would on its own line.
        self.assertNotEqual(formats, self.formats_for("--Link1--"))


class TestComments(HighlighterTestBase):
    def test_comment_line_highlighted(self):
        self.assert_highlighted("! this is a comment")

    def test_non_comment_not_matched_by_comment_rule(self):
        # A line with no leading '!' should not be highlighted by anything
        # for a coordinate-looking body line.
        self.assert_not_highlighted("  0.000000   0.000000   0.000000")


class TestChargeMultiplicityAndMarkers(HighlighterTestBase):
    def test_charge_multiplicity_line_highlighted(self):
        self.assert_highlighted("0 1")

    def test_negative_charge_multiplicity_line_highlighted(self):
        self.assert_highlighted("-1 2")

    def test_nbo_marker_highlighted(self):
        self.assert_highlighted("$NBO")

    def test_end_marker_highlighted(self):
        self.assert_highlighted("$END")

    def test_stars_marker_highlighted(self):
        self.assert_highlighted("****")

    def test_nbo_marker_case_insensitive(self):
        self.assert_highlighted("$nbo")


class TestPlainLines(HighlighterTestBase):
    def test_empty_line(self):
        self.assert_not_highlighted("")

    def test_whitespace_only_line(self):
        self.assert_not_highlighted("     ")

    def test_generic_atom_coordinate_row_not_highlighted(self):
        self.assert_not_highlighted("C   0.000000   0.000000   0.000000")


class TestHighlightBlockRobustness(HighlighterTestBase):
    def test_full_input_file_does_not_raise(self):
        doc = QTextDocument()
        hl = self.Highlighter(doc)
        doc.setPlainText(
            "%chk=molecule.chk\n"
            "%nprocshared=4\n"
            "%mem=4GB\n"
            "#P B3LYP/6-31G(d) Opt Freq\n"
            "\n"
            "Title\n"
            "\n"
            "0 1\n"
            "C   0.0   0.0   0.0\n"
            "H   1.0   0.0   0.0\n"
            "\n"
            "--Link1--\n"
            "%chk=molecule.chk\n"
            "#P Freq Geom=Check Guess=Read\n"
        )
        hl.rehighlight()
        self.assertEqual(15, doc.blockCount())

    def test_very_long_line(self):
        self.formats_for("#P " + "B3LYP " * 500)


if __name__ == "__main__":
    unittest.main()
