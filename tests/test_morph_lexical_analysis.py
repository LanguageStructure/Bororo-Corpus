#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morph_lexical_analysis import analyze
class TestLexicalSeparation(unittest.TestCase):
    def test_lexical_not_overwritten(self):
        item=analyze("icare")
        self.assertTrue(any(x["lemma"]=="icare" and x["upos"]=="ADV" for x in item["lexical_evidence"]))
        self.assertTrue(any(x["segments"]==["i","ca","re"] for x in item["morphological_segmentations"]))
    def test_ire_lemma_independent(self):
        item=analyze("ire")
        self.assertTrue(any(x["lemma"]=="i" and x["upos"]=="PRON" for x in item["lexical_evidence"]))
        self.assertTrue(any(x["segments"]==["i","re"] for x in item["morphological_segmentations"]))
    def test_no_segmentation_does_not_erase_lexical(self):
        item=analyze("boe")
        self.assertEqual(item["morphological_segmentations"],[])
        self.assertTrue(item["lexical_evidence"])
if __name__=="__main__":unittest.main()
