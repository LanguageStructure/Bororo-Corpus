#!/usr/bin/env python3
"""Regression checks for attestation and manually confirmed tokenizer analyses.

Run: python3 -m unittest discover -s tests -p 'test_tokenizer_safeguards.py'
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from train_tokenizer import train


class TokenizerSafeguards(unittest.TestCase):
    def test_unattested_forms_not_generated(self):
        model = train([
            ("ako", "ako", "VERB"),
            ("i", "i", "PRON"),
            ("e", "e", "PRON"),
            ("re", "re", "PART"),
        ])
        for form in ("iakore", "eakore", "tabiapagado", "ibiapagare"):
            self.assertNotIn(form, model["candidates"])

    def test_excluded_forms_not_confirmed_even_if_observed(self):
        model = train([
            ("iakore", "ako", "VERB"),
            ("eakore", "ako", "VERB"),
            ("tabiapagado", "biapaga", "VERB"),
            ("ibiapagare", "biapaga", "VERB"),
        ])
        for form in ("iakore", "eakore", "tabiapagado", "ibiapagare"):
            self.assertNotIn(form, model["candidates"])

    def test_confirmed_analysis_requires_attestation(self):
        model = train([("nure", "nu", "AUX"), ("ire", "i", "AUX")])
        self.assertEqual(model["candidates"]["nure"]["segments"], ["nu", "re"])
        self.assertEqual(model["candidates"]["ire"]["segments"], ["i", "re"])
        self.assertNotIn("iorudukare", model["candidates"])

    def test_aimo_reviewed_boundaries(self):
        expected = {
            "itaimo": ["it", "aimo"],
            "akaimo": ["ak", "aimo"],
            "cedaimo": ["ced", "aimo"],
            "padaimo": ["pad", "aimo"],
            "tagaimo": ["tag", "aimo"],
        }
        rows = [(form, "aimo", "VERB") for form in expected]
        model = train(rows)
        for form, segments in expected.items():
            self.assertEqual(model["candidates"][form]["segments"], segments)
            self.assertEqual(model["candidates"][form]["status"], "linguistically_confirmed")

    def test_aimo_review_does_not_generate_unattested_forms(self):
        model = train([("itaimo", "aimo", "VERB")])
        self.assertIn("itaimo", model["candidates"])
        for form in ("akaimo", "cedaimo", "padaimo", "tagaimo"):
            self.assertNotIn(form, model["candidates"])

    def test_je_not_a_suffix(self):
        model = train([("taje", "ta", "VERB")] * 5 + [("ta", "ta", "VERB")] * 5)
        self.assertNotIn("taje", model["candidates"])


if __name__ == "__main__":
    unittest.main()
