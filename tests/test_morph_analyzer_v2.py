#!/usr/bin/env python3
"""Regressão do analisador unificado: python3 -m unittest discover -s tests -p 'test_morph_analyzer_v2.py' -v"""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morph_analyzer_v2 import analyze
class TestUnifiedMorphology(unittest.TestCase):
    def assert_contains(self,word,lemma,segments,status):
        found=analyze(word)["analyses"]
        self.assertTrue(any(x["lemma"]==lemma and x["segments"]==segments and x["status"]==status for x in found),found)
    def test_confirmed(self):
        self.assert_contains("iture","tu",["i","tu","re"],"confirmed")
        self.assert_contains("akodure","kodu",["a","kodu","re"],"confirmed")
    def test_suffix_composition(self):
        self.assert_contains("itumodukare","tu",["i","tu","modu","ka","re"],"hypothesis")
        self.assert_contains("imagomodukare","mako",["i","mago","modu","ka","re"],"hypothesis")
    def test_atomic(self):
        self.assertEqual(analyze("boe")["analyses"],[])
        self.assertEqual(analyze("nowu")["analyses"],[])
    def test_no_duplicate_confirmed(self):
        a=analyze("iture")["analyses"]
        self.assertEqual(sum(x["lemma"]=="tu" and x["segments"]==["i","tu","re"] for x in a),1)
if __name__=="__main__":
    unittest.main()
