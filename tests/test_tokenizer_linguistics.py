#!/usr/bin/env python3
"""Regression tests for non-destructive ako audit and lexical alignment.

Run: python3 -m unittest discover -s tests -p 'test_tokenizer_linguistics.py'
"""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class AlignmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extract=load("extract_tokenizer_alternations",Path("scripts/extract_tokenizer_alternations.py"))
    def test_mako_paradigm(self):
        for form,prefix in [("imago","i"),("amago","a"),("pamago","pa"),("cemago","ce"),("tamago","ta"),("emago","e"),("tumago","tu")]:
            with self.subTest(form=form):
                p,base,end,status=self.extract.align(form,"mako")
                self.assertEqual((p,base,end,status),(prefix,"mago","","curated_allomorph"))
    def test_mago_alone_is_not_licensed(self):
        self.assertNotEqual(self.extract.align("mago","mako")[3],"curated_allomorph")
    def test_ako_allomorph_is_context_restricted(self):
        self.assertEqual(self.extract.align("inagore","ako"),("i(n)","ago","re","curated_allomorph"))
        self.assertNotEqual(self.extract.align("agore","ako")[3],"curated_allomorph")
    def test_confirmed_nasal_prefix_ako(self):
        cases={"inago":("i(n)","ago","","curated_allomorph"),"inagore":("i(n)","ago","re","curated_allomorph"),"inagokare":("i(n)","ago","kare","curated_allomorph"),"cenagore":("ce(n)","ago","re","curated_allomorph")}
        for form,expected in cases.items():
            with self.subTest(form=form):
                self.assertEqual(self.extract.align(form,"ako"),expected)
    def test_confirmed_ego_allomorph(self):
        self.assertEqual(self.extract.align("egore","ako"),("e","go","re","curated_allomorph"))
        self.assertEqual(self.extract.align("ego","ako"),("e","go","","curated_allomorph"))
    def test_ako_exact_stem(self):
        self.assertEqual(self.extract.align("akore","ako"),("","ako","re","exact_base"))
    def test_personal_marker_paradigm(self):
        cases={
            ("ure","u"):"re",("ire","i"):"re",("are","a"):"re",
            ("ere","e"):"re",("ukare","u"):"ka+re",
            ("ikare","i"):"ka+re",("ekare","e"):"ka+re",
            ("umode","u"):"modu+re",("imode","i"):"modu+re",
            ("amode","a"):"modu+re",
            ("imodukare","i"):"modu+ka+re",
            ("emodukare","e"):"modu+ka+re",
            ("inure","i"):"nu+re",("unure","u"):"nu+re",
            ("iwo","i"):"wo",("uiagu","u"):"iagu",
        }
        for (form,lemma),ending in cases.items():
            with self.subTest(form=form):
                self.assertEqual(self.extract.align(form,lemma),
                                 (lemma,lemma,ending,"curated_allomorph"))
    def test_personal_alignment_not_generalized(self):
        self.assertNotEqual(self.extract.align("ikare","ako")[3],"curated_allomorph")
        self.assertNotEqual(self.extract.align("ureje","u")[3],"curated_allomorph")
    def test_no_suffix_je(self):
        self.assertEqual(self.extract.align("boeje","boe"),("","boeje","","unresolved"))

if __name__=="__main__":unittest.main()
