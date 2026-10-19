"""Regression tests for reviewed, partial, and quarantined paradigms."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from train_tokenizer import load_reviewed_paradigms
from lookup_reviewed_paradigm import load_all_paradigms, lookup_all


class ReviewedParadigmsTest(unittest.TestCase):
    def test_ie_and_ae_segmentations(self):
        reviews = load_reviewed_paradigms()
        self.assertEqual(reviews["ikie"]["segments"], ["ik", "ie"])
        self.assertEqual(reviews["cegie"]["segments"], ["ceg", "ie"])
        self.assertEqual(reviews["eie"]["segments"], ["e", "ie"])
        self.assertEqual(reviews["itae"]["segments"], ["it", "ae"])
        self.assertEqual(reviews["puae"]["segments"], ["pu", "ae"])
        self.assertNotIn("cie", reviews)
        self.assertNotIn("kae", reviews)

    def test_reciprocal_and_variants(self):
        paradigms = load_all_paradigms()
        puae = lookup_all("puae", paradigms)
        self.assertEqual(len(puae), 1)
        self.assertEqual(puae[0]["person"], "RECIP")
        self.assertEqual(lookup_all("cie", paradigms)[0]["person"], "3REFL")
        self.assertEqual(lookup_all("kae", paradigms)[0]["person"], "3SG")
        self.assertTrue(all(p["id"] != "P067" for p in paradigms))

    def test_quarantined_record_is_skipped(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "quarantined_paradigm_reviewed_20261019.json").write_text(
                json.dumps({"id": "QUARANTINED", "review": {"status": "needs_source_verification"}, "forms": []}),
                encoding="utf-8",
            )
            (path / "confirmed_paradigm_reviewed_20261019.json").write_text(
                json.dumps({"id": "CONFIRMED", "review": {
                    "status": "linguist_confirmed_paradigm_membership",
                    "segmentation_status": "partially_confirmed"},
                    "forms": [{"form": "xyz", "segmentation": None}]}),
                encoding="utf-8",
            )
            self.assertEqual([p["id"] for p in load_all_paradigms(path)], ["CONFIRMED"])
            self.assertEqual(load_reviewed_paradigms(path), {})


if __name__ == "__main__":
    unittest.main()
