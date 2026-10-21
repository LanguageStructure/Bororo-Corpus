#!/usr/bin/env python3
"""Testes de regressão do analisador morfofonológico.

Execute: python3 -m unittest discover -s tests -p 'test_morphophonology.py'
"""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morphophonology import analyze
class TestMorphophonology(unittest.TestCase):
    def assert_analysis(self,word,lemma,parts,status=None):
        candidates=analyze(word)["analyses"]
        self.assertTrue(any(x["lemma"]==lemma and x["morphemes"]==parts
                            and (status is None or x["status"]==status)
                            for x in candidates),(word,candidates))
    def test_confirmed_iture(self):
        self.assert_analysis("iture","tu",["i","tu","re"],"confirmed")
    def test_confirmed_akodure(self):
        self.assert_analysis("akodure","kodu",["a","kodu","re"],"confirmed")
    def test_compositional_tu(self):
        self.assert_analysis("itumodukare","tu",["i","tu","modu","ka","re"],"hypothesis")
    def test_compositional_mako(self):
        self.assert_analysis("imagomodukare","mako",["i","mago","modu","ka","re"],"hypothesis")
    def test_no_spurious_segmentation(self):
        self.assertEqual(analyze("boe")["analyses"],[])
    def test_all_reconstructed(self):
        for word in ("iture","akodure","itumodukare","imagomodukare","boe"):
            for item in analyze(word)["analyses"]:
                if item["surface_reconstruction"]:
                    self.assertEqual("".join(item["morphemes"]),word)
if __name__=="__main__":unittest.main()
