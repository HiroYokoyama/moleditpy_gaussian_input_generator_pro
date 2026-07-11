"""
tests/test_constants.py

Keyword-list integrity checks for gaussian_input_generator_pro/constants.py.
Pure Python module -- no Qt/rdkit stubs needed.
"""

import os
import sys
import importlib.util
import unittest

_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def _load_constants():
    path = os.path.join(_REPO_ROOT, "gaussian_input_generator_pro", "constants.py")
    spec = importlib.util.spec_from_file_location(
        "gaussian_input_generator_pro.constants", path
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_c = _load_constants()


class TestMethodLists(unittest.TestCase):
    def test_dft_methods_nonempty(self):
        self.assertGreater(len(_c.DFT_METHODS), 0)

    def test_dft_methods_no_duplicates(self):
        self.assertEqual(len(_c.DFT_METHODS), len(set(_c.DFT_METHODS)))

    def test_expected_dft_members(self):
        for m in ["B3LYP", "wB97XD", "M062X", "PBE1PBE", "CAM-B3LYP", "MN15"]:
            self.assertIn(m, _c.DFT_METHODS)

    def test_wavefunction_methods_nonempty(self):
        self.assertGreater(len(_c.WAVEFUNCTION_METHODS), 0)
        for m in ["MP2", "CCSD", "CCSD(T)"]:
            self.assertIn(m, _c.WAVEFUNCTION_METHODS)

    def test_hf_methods(self):
        self.assertIn("HF", _c.HF_METHODS)
        self.assertIn("UHF", _c.HF_METHODS)

    def test_semi_empirical_methods(self):
        for m in ["AM1", "PM6", "PM7"]:
            self.assertIn(m, _c.SEMI_EMPIRICAL_METHODS)

    def test_all_methods_is_union(self):
        combined = (
            set(_c.DFT_METHODS)
            | set(_c.DOUBLE_HYBRID_METHODS)
            | set(_c.WAVEFUNCTION_METHODS)
            | set(_c.HF_METHODS)
            | set(_c.SEMI_EMPIRICAL_METHODS)
        )
        self.assertEqual(set(_c.ALL_GAUSSIAN_METHODS), combined)

    def test_all_methods_no_duplicates(self):
        self.assertEqual(
            len(_c.ALL_GAUSSIAN_METHODS), len(set(_c.ALL_GAUSSIAN_METHODS))
        )


class TestBasisSets(unittest.TestCase):
    def test_pople_basis_sets_nonempty(self):
        self.assertGreater(len(_c.POPLE_BASIS_SETS), 0)
        self.assertIn("6-31G(d)", _c.POPLE_BASIS_SETS)

    def test_dunning_basis_sets(self):
        self.assertIn("cc-pVDZ", _c.DUNNING_BASIS_SETS)
        self.assertIn("aug-cc-pVTZ", _c.DUNNING_BASIS_SETS)

    def test_def2_basis_sets(self):
        self.assertIn("def2TZVP", _c.DEF2_BASIS_SETS)

    def test_ecp_basis_sets(self):
        for b in ["LanL2DZ", "SDD", "Gen", "GenECP"]:
            self.assertIn(b, _c.ECP_BASIS_SETS)

    def test_all_basis_sets_no_duplicates(self):
        self.assertEqual(
            len(_c.ALL_GAUSSIAN_BASIS_SETS), len(set(_c.ALL_GAUSSIAN_BASIS_SETS))
        )


class TestSolvation(unittest.TestCase):
    def test_solvation_models(self):
        for m in ["None", "PCM", "CPCM", "SMD", "IEFPCM", "Dipole"]:
            self.assertIn(m, _c.SOLVATION_MODELS)

    def test_solvents_nonempty(self):
        self.assertGreater(len(_c.GAUSSIAN_SOLVENTS), 0)
        self.assertIn("Water", _c.GAUSSIAN_SOLVENTS)

    def test_solvents_no_duplicates(self):
        self.assertEqual(
            len(_c.GAUSSIAN_SOLVENTS), len(set(_c.GAUSSIAN_SOLVENTS))
        )

    def test_dispersion_options(self):
        for d in ["None", "GD3", "GD3BJ", "GD2"]:
            self.assertIn(d, _c.DISPERSION_OPTIONS)


class TestJobAndTailData(unittest.TestCase):
    def test_job_types_nonempty(self):
        self.assertGreater(len(_c.JOB_TYPES), 0)

    def test_opt_options(self):
        for o in ["Tight", "VeryTight", "CalcFC", "CalcAll", "ModRedundant"]:
            self.assertIn(o, _c.OPT_OPTIONS)

    def test_freq_options(self):
        for o in ["Raman", "NoRaman", "VCD", "Anharmonic"]:
            self.assertIn(o, _c.FREQ_OPTIONS)

    def test_pop_options(self):
        for o in ["NBO", "NBORead", "Hirshfeld", "MK", "CHelpG", "Reg", "Full"]:
            self.assertIn(o, _c.POP_OPTIONS)

    def test_grid_options(self):
        self.assertIn("UltraFine", _c.GRID_OPTIONS)

    def test_tail_templates_have_expected_keys(self):
        for key in [
            "ModRedundant (Freeze/Scan)",
            "Basis Set (Gen)",
            "Effective Core Potential (GenECP)",
            "NBO Analysis ($NBO)",
            "Link1 (Multiple Jobs)",
            "Connectivity (Geom=Connectivity)",
        ]:
            self.assertIn(key, _c.TAIL_TEMPLATES)

    def test_tail_templates_are_nonempty_strings(self):
        for name, template in _c.TAIL_TEMPLATES.items():
            self.assertIsInstance(template, str, name)
            self.assertGreater(len(template.strip()), 0, name)

    def test_link1_template_contains_marker(self):
        self.assertIn("--Link1--", _c.TAIL_TEMPLATES["Link1 (Multiple Jobs)"])


if __name__ == "__main__":
    unittest.main()
