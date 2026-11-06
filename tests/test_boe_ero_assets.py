"""Validation tests for the Boe Ero parallel and annotation assets."""
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_boe_ero_assets import conllu_tokens, read_rows, render_conllu


class BoeEroAssetsTests(unittest.TestCase):
    def test_documentary_counts_and_known_alignment_anomalies(self):
        rows = read_rows()
        self.assertEqual(len(rows), 276)
        self.assertEqual(sum(bool(row["source"].strip()) for row in rows), 275)
        gap = next(row for row in rows if row["id"] == "BOR-CORBO-BOE-02-039")
        self.assertEqual(gap["source"], "")
        self.assertTrue(gap["portuguese"])
        shifted = next(row for row in rows if row["id"] == "BOR-CORBO-BOE-07-050")
        self.assertEqual((shifted["source_number"], shifted["translation_number"]), ("50", "51"))

    def test_conllu_is_standalone_and_preserves_required_comment_order(self):
        rendered, blocks, token_count, skipped = render_conllu(read_rows())
        self.assertEqual(blocks, 275)
        self.assertGreater(token_count, 0)
        self.assertEqual(skipped, ["BOR-CORBO-BOE-02-039"])
        first = rendered.split("\n\n", 1)[0].splitlines()
        self.assertTrue(first[0].startswith("# sent_id = "))
        self.assertTrue(first[1].startswith("# text = "))
        self.assertTrue(first[2].startswith("# text_por = "))
        self.assertTrue(all(len(line.split("\t")) == 10 for line in first if not line.startswith("#")))

    def test_tokenizer_keeps_private_use_glyph_inside_source_word(self):
        tokens = conllu_tokens("Ko\uf087are.")
        self.assertEqual([form for form, _ in tokens], ["Ko\uf087are", "."])
        self.assertEqual(tokens[-1][1], "_")


if __name__ == "__main__":
    unittest.main()
