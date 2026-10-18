#!/usr/bin/env python3
"""Tests for combined Bororo prefix/stem/suffix candidates."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from bororo_combined_morphology import analyze_combined
from train_tokenizer import train


class CombinedMorphologyTests(unittest.TestCase):
    def test_b_w_plus_re(self):
        result = analyze_combined("iwire", "bi")
        self.assertEqual(result["segments"], ["i", "wi", "re"])
        self.assertEqual(result["lemma"], "bi")

    def test_c_j_plus_wo(self):
        self.assertEqual(analyze_combined("ijorewo", "core")["segments"],
                         ["i", "jore", "wo"])

    def test_longest_ending(self):
        self.assertEqual(analyze_combined("iwimodukare", "bi")["segments"],
                         ["i", "wi", "modu", "ka", "re"])

    def test_no_guess_from_unmatched_surface(self):
        self.assertIsNone(analyze_combined("iwix", "bi"))
        self.assertIsNone(analyze_combined("iwi", "bi"))
        self.assertIsNone(analyze_combined("iwire", "bi", exceptions={"bi"}))

    def test_attested_candidate_in_model(self):
        model = train([("iwire", "bi", "NOUN")])
        candidate = model["candidates"]["iwire"]
        self.assertEqual(candidate["segments"], ["i", "wi", "re"])
        self.assertEqual(candidate["status"], "combined_rule_proposal")

    def test_reviewed_overrides_combined_candidate(self):
        model = train([("cedaimo", "taimo", "VERB"),
                       ("cedaimo", "aimo", "NOUN")])
        self.assertEqual(model["candidates"]["cedaimo"]["segments"], ["ced", "aimo"])


if __name__ == "__main__":
    unittest.main()
