"""Tests for manual gold CSV conversion."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from convert_tokenizer_gold import convert


class ConvertGoldTests(unittest.TestCase):
    def test_approved_and_pending(self):
        rows = [
            {"form": "ikie", "segments": "ik + ie", "review_status": "approved"},
            {"form": "cegie", "segments": "", "review_status": "pending"},
        ]
        gold, pending = convert(rows)
        self.assertEqual(gold, [{"form": "ikie", "segments": ["ik", "ie"]}])
        self.assertEqual(pending, ["cegie"])
        with self.assertRaises(ValueError):
            convert(rows, require_all=True)

    def test_reject_inconsistent_segmentation(self):
        with self.assertRaises(ValueError):
            convert([{"form": "ikie", "segments": "i + ie", "review_status": "approved"}])

    def test_reject_duplicate(self):
        with self.assertRaises(ValueError):
            convert([
                {"form": "ikie", "segments": "ik + ie", "review_status": "approved"},
                {"form": "ikie", "segments": "ik + ie", "review_status": "approved"},
            ])


if __name__ == "__main__":
    unittest.main()
