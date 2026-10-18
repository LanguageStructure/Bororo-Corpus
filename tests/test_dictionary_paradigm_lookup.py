import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from query_dictionary_paradigms import build_index, query


class DictionaryLookupTests(unittest.TestCase):
    def test_lookup_preserves_provenance_and_does_not_infer_segmentation(self):
        data = {"paradigms": [{
            "id": "P001", "pdf_page": "7", "column": "2",
            "reference_3sg_candidate": "aiado",
            "entries": [{"working_form": "itaiado", "original": "itaiado",
                         "person_candidate": "1SG", "status": "revisao_pendente",
                         "flags": ""}],
        }]}
        hit = query(build_index(data), "itaiado")[0]
        self.assertEqual(hit["paradigm_id"], "P001")
        self.assertEqual(hit["reference_3sg_candidate"], "aiado")
        self.assertIsNone(hit["segmentation"])
        self.assertEqual(hit["review_status"], "unreviewed")

    def test_unknown_form(self):
        self.assertEqual(query(build_index({"paradigms": []}), "missing"), [])


if __name__ == "__main__":
    unittest.main()
