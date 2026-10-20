"""Tests for tokenizer boundary error classification."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tokenizer_error_report import classify, report


class TokenizerErrorTests(unittest.TestCase):
    def test_boundary_types(self):
        self.assertEqual(classify(["ik", "ie"], ["ik", "ie"]), "correct")
        self.assertEqual(classify(["ikie"], ["ik", "ie"]), "oversegmentation")
        self.assertEqual(classify(["ik", "ie"], ["ikie"]), "undersegmentation")
        self.assertEqual(classify(["ik", "ie"], ["i", "kie"]), "mixed_boundary_error")
        self.assertEqual(classify(["i", "k", "ie"], ["ik", "ie"]), "undersegmentation")
        self.assertEqual(classify(["ik", "ie"], None), "unanalysed")

    def test_report(self):
        model = {"candidates": {"ikie": {"segments": ["i", "kie"], "status": "proposed"}}}
        rows = report(model, [{"form": "ikie", "segments": ["ik", "ie"]}])
        self.assertEqual(rows[0]["error_type"], "mixed_boundary_error")
        self.assertEqual(rows[0]["gold_boundaries"], "2")
        self.assertEqual(rows[0]["predicted_boundaries"], "1")


if __name__ == "__main__":
    unittest.main()
