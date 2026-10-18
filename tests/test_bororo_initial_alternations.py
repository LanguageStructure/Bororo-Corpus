#!/usr/bin/env python3
"""Tests for consonant-onset rules (no speculative inflections)."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bororo_initial_alternations import prefixed_stem, find_attested_analysis


class InitialAlternations(unittest.TestCase):
    def test_general_b_w(self):
        for lemma, stem in (("bi", "wi"), ("bia", "wia"), ("bogai", "wogai")):
            self.assertEqual(prefixed_stem(lemma), stem)

    def test_default_correspondences(self):
        for lemma, stem in (("pore", "bore"), ("tore", "dore"),
                            ("kore", "gore"), ("core", "jore")):
            self.assertEqual(prefixed_stem(lemma), stem)

    def test_other_consonants_unchanged(self):
        self.assertEqual(prefixed_stem("mako"), "mako")
        self.assertEqual(prefixed_stem("nure"), "nure")

    def test_surface_and_lemma_required(self):
        self.assertEqual(find_attested_analysis("iwi", "bi")["segments"], ["i", "wi"])
        self.assertEqual(find_attested_analysis("cewogai", "bogai")["segments"], ["ce", "wogai"])
        self.assertIsNone(find_attested_analysis("iwix", "bi"))
        self.assertIsNone(find_attested_analysis("iwi", ""))
        self.assertIsNone(find_attested_analysis("iwi", "bi", exceptions={"bi"}))

    def test_c_j_ipa_notation(self):
        self.assertEqual(find_attested_analysis("ijore", "core")["alternation"], "c>j")


if __name__ == "__main__":
    unittest.main()
