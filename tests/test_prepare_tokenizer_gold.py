"""Tests for reproducible tokenizer gold sampling."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from prepare_tokenizer_gold import sample


class GoldSamplingTests(unittest.TestCase):
    def test_exclusion_and_reproducibility(self):
        model = {
            "lexicon": {str(i): {"frequency": i + 1} for i in range(20)},
            "candidates": {
                str(i): {"status": "linguistically_confirmed" if i < 5 else "proposed",
                         "segments": [str(i)]}
                for i in range(10)
            },
        }
        first = sample(model, size=12, seed=42, exclude={"1", "15"})
        self.assertEqual(first, sample(model, size=12, seed=42, exclude={"1", "15"}))
        self.assertEqual(len(first), 12)
        self.assertNotIn("1", [row["form"] for row in first])
        self.assertNotIn("15", [row["form"] for row in first])
        self.assertEqual(len({row["form"] for row in first}), 12)
        self.assertTrue(all(row["review_status"] == "pending" for row in first))


if __name__ == "__main__":
    unittest.main()
