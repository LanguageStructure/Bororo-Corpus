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
    def test_ako_is_not_assumed_to_be_ago(self):
        self.assertNotEqual(self.extract.align("inagore","ako")[3],"curated_allomorph")
    def test_ako_exact_stem(self):
        self.assertEqual(self.extract.align("akore","ako"),("","ako","re","exact_base"))
    def test_no_suffix_je(self):
        self.assertEqual(self.extract.align("boeje","boe"),("","boeje","","unresolved"))

if __name__=="__main__":unittest.main()
