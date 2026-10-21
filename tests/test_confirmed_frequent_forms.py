import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morph_analyzer_v2 import analyze
class ConfirmedMorphology(unittest.TestCase):
    def test_five_confirmed(self):
        cases={
            "akore":("ako",["ako","re"],True),
            "inagore":("ako",["i","nago","re"],True),
            "egore":("ako",["e","ako","re"],False),
            "cedure":("tu",["ce","du","re"],True),
            "ure":("re",["u","re"],True),
        }
        for form,(lemma,segments,matches) in cases.items():
            with self.subTest(form=form):
                results=analyze(form)["analyses"]
                self.assertTrue(any(a["lemma"]==lemma and a["segments"]==segments
                    and a["status"]=="confirmed" and a["surface_matches"]==matches for a in results))
if __name__=="__main__":unittest.main()
