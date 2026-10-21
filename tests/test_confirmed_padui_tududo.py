import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morph_analyzer_v2 import analyze
class TestConfirmedForms(unittest.TestCase):
    def test_padui(self):
        a=analyze("padui")
        self.assertFalse(a["review_required"])
        self.assertTrue(any(x["segments"]==["pa","tu","i"] and x["status"]=="confirmed" and not x["surface_matches"] for x in a["analyses"]))
    def test_tududo(self):
        a=analyze("tududo")
        self.assertFalse(a["review_required"])
        self.assertTrue(any(x["segments"]==["tu","tu","do"] and x["status"]=="confirmed" and not x["surface_matches"] for x in a["analyses"]))
    def test_ituiagu_still_pending(self):
        self.assertTrue(analyze("ituiagu")["review_required"])
if __name__=="__main__":unittest.main()
