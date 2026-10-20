"""Regression tests for tokenizer coverage and held-out scoring."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluate_tokenizer import evaluate


class TokenizerEvaluationTests(unittest.TestCase):
    def test_coverage_and_gold(self):
        model = {
            "lexicon": {"ikie": {"frequency": 3}, "abc": {"frequency": 2}, "xyz": {"frequency": 5}},
            "candidates": {
                "ikie": {"segments": ["ik", "ie"], "status": "linguistically_confirmed"},
                "abc": {"segments": ["a", "bc"], "status": "proposed"},
            },
        }
        result = evaluate(model, [{"form": "ikie", "segments": ["ik", "ie"]},
                                  {"form": "abc", "segments": ["ab", "c"]},
                                  {"form": "xyz", "segments": ["xyz"]}])
        self.assertEqual(result["corpus_types"], 3)
        self.assertEqual(result["corpus_tokens"], 10)
        self.assertEqual(result["analysed_types"], 2)
        self.assertEqual(result["analysed_tokens"], 5)
        self.assertEqual(result["confirmed_types"], 1)
        self.assertEqual(result["gold_evaluation"]["correct_exact"], 1)
        self.assertEqual(result["gold_evaluation"]["predicted"], 2)
        self.assertAlmostEqual(result["gold_evaluation"]["exact_match_all"], 1 / 3)

    def test_empty(self):
        result = evaluate({"lexicon": {}, "candidates": {}})
        self.assertIsNone(result["type_coverage"])
        self.assertIsNone(result["gold_evaluation"])


if __name__ == "__main__":
    unittest.main()
