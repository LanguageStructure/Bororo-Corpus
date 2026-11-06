"""Guard the intentionally incomplete expanded CorBo working release."""
from __future__ import annotations

import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONLLU = ROOT / "CorBo/Corpus_Files/CorBo.conllu"
REPORT = ROOT / "CorBo_vNext/annotations/latest_conllu_import_report.json"
UD_JSON = ROOT / "docs/data/ud-sentences.json"


class ExpandedCorboWorkTests(unittest.TestCase):
    def test_working_file_matches_its_non_destructive_audit(self):
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        raw = CONLLU.read_bytes()
        lines = raw.decode("utf-8-sig").splitlines()
        sent_ids = [line.partition("=")[2].strip() for line in lines if line.startswith("# sent_id =")]
        malformed = [
            number
            for number, line in enumerate(lines, 1)
            if line and not line.startswith("#") and len(line.split("\t")) != 10
        ]
        self.assertFalse(report["automatic_repairs"])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), report["sha256"])
        self.assertEqual(len(sent_ids), report["sent_id_occurrences"])
        self.assertFalse([key for key, count in Counter(sent_ids).items() if count > 1])
        self.assertEqual(malformed, report["invalid_token_lines"])

    def test_boe_ero_remains_available_for_incremental_annotation(self):
        sentences = json.loads(UD_JSON.read_text(encoding="utf-8"))
        boe = [row for row in sentences if row["sent_id"].startswith("boe_ero_")]
        self.assertEqual(len(boe), 277)
        self.assertEqual(sum(bool(row["tokens"]) for row in boe), 275)
        self.assertIn("boe_ero_02_39", {row["sent_id"] for row in boe})
        self.assertIn("boe_ero_07_51_2", {row["sent_id"] for row in boe})


if __name__ == "__main__":
    unittest.main()
