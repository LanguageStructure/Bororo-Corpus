import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morph_analyzer_v2 import analyze
class TestNewConfirmations(unittest.TestCase):
    def test_confirmed(self):
        cases={
            "cenagore":("ako",["ce","nago","re"],True),
            "makore":("mako",["mako","re"],True),
            "cegodure":("kodu",["ce","kodu","re"],False),
        }
        for form,(lemma,segments,surface_matches) in cases.items():
            with self.subTest(form=form):
                self.assertTrue(any(
                    a["status"]=="confirmed" and a["lemma"]==lemma
                    and a["segments"]==segments and a["surface_matches"]==surface_matches
                    for a in analyze(form)["analyses"]
                ))
if __name__=="__main__":unittest.main()
