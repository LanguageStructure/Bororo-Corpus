import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from morph_analyzer_v2 import analyze
class TestConflictQuarantine(unittest.TestCase):
    def test_conflicting_forms_not_inferred(self):
        for form in ("padui","tududo","ituiagu"):
            with self.subTest(form=form):
                result=analyze(form)
                self.assertTrue(result["review_required"])
                self.assertFalse(any(a["status"]=="hypothesis" for a in result["analyses"]))
    def test_unrelated_forms_still_work(self):
        self.assertFalse(analyze("iture")["review_required"])
        self.assertTrue(any(a["status"]=="confirmed" for a in analyze("iture")["analyses"]))
if __name__=="__main__":unittest.main()
