import unittest
import os

import sys
 
# setting path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
common_dir = os.path.join(parent_dir, 'ratesb_web', 'common')
sys.path.append(common_dir)

# from ratesb_web.common.custom_classifier import _CustomClassifier
from analyzer import Analyzer

DIR = os.path.dirname(os.path.realpath(__file__))
UPPER_DIR = os.path.dirname(DIR)
DEFAULT_CLASSIFIER_PATH = os.path.join(UPPER_DIR, "ratesb_web", "common", "default_classifier.json")

TEST_CLASSIFIER_MODELS = "test_classifier_models"
ZERO_PATH = os.path.join(DIR, TEST_CLASSIFIER_MODELS, "zero.ant")

# DEFAULT_CLASSIFIER = _CustomClassifier(DEFAULT_CLASSIFIER_PATH)

ZERO = "ZERO"
UNDR1 = "UNDR1"
UNDR2 = "UNDR2"
UNDR3 = "UNDR3"
UNDR_A1 = "UNDR-A1"
UNDR_A2 = "UNDR-A2"
UNDR_A3 = "UNDR-A3"
BIDR11 = "BIDR11"
BIDR12 = "BIDR12"
BIDR21 = "BIDR21"
BIDR22 = "BIDR22"
BIDR_A11 = "BIDR-A11"
BIDR_A12 = "BIDR-A12"
BIDR_A21 = "BIDR-A21"
BIDR_A22 = "BIDR-A22"
MM = "MM"
MM_CAT = "MMcat"
AMM = "AMM"
IMM = "IMM"
RMM = "RMM"
RMM_CAT = "RMMcat"
HILL = "Hill"

class TestClassifier(unittest.TestCase):
    def test_raise_file_format_error(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr.json"), 'r') as file:
            content = file.read()
        with self.assertRaises(ValueError):
            Analyzer(content, "classifier.notjson")
    
    def test_json_structure(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr.json"), 'r') as file:
            content = file.read()
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "no_name.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        # assert analyzer.data.custom_classifier is not none
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")
        
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "no_expression.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")
        
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "no_optional_symbols.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")
        
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "no_power_limited_species.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")
    
    def test_expression(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr.json"), 'r') as file:
            content = file.read()
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "invalid_expression.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")
    
    def test_optional_symbols(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr.json"), 'r') as file:
            content = file.read()
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "invalid_optional_symbols.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")
    
    def test_power_limited_species(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr.json"), 'r') as file:
            content = file.read()
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "invalid_power_limited_species.json"), 'r') as file:
            json = file.read()
        analyzer = Analyzer(content, json)
        self.assertTrue(analyzer.data.custom_classifier)
        self.assertTrue(analyzer.data.custom_classifier.warning_message != "")

    def test_false(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "false.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            for k, v in val.items():
                self.assertFalse(v)

    def test_zero(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "zero.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[ZERO])
            # assert all other values are false
            for k, v in val.items():
                if k != ZERO:
                    self.assertFalse(v)
    
    def test_undr(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[UNDR1] or val[UNDR2] or val[UNDR3])
            for k, v in val.items():
                if k != UNDR1 and k != UNDR2 and k != UNDR3:
                    self.assertFalse(v)
    
    def test_undr_a(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "undr_a.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[UNDR_A1] or val[UNDR_A2] or val[UNDR_A3])
            for k, v in val.items():
                if k != UNDR_A1 and k != UNDR_A2 and k != UNDR_A3:
                    self.assertFalse(v)
    
    def test_bidr(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "bidr.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[BIDR11] or val[BIDR12] or val[BIDR21] or val[BIDR22])
            for k, v in val.items():
                if k != BIDR11 and k != BIDR12 and k != BIDR21 and k != BIDR22:
                    self.assertFalse(v)
    
    def test_bidr_a(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "bidr_a.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[BIDR_A11] or val[BIDR_A12] or val[BIDR_A21] or val[BIDR_A22])
            for k, v in val.items():
                if k != BIDR_A11 and k != BIDR_A12 and k != BIDR_A21 and k != BIDR_A22:
                    self.assertFalse(v)
    
    def test_mm(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "mm.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[MM])
            for k, v in val.items():
                if k != MM:
                    self.assertFalse(v)
    
    def test_mmcat(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "mmcat.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[MM_CAT])
            for k, v in val.items():
                if k != MM_CAT:
                    self.assertFalse(v)
    
    def test_amm(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "amm.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[AMM])
            for k, v in val.items():
                if k != AMM:
                    self.assertFalse(v)
    
    def test_imm(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "imm.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[IMM])
            for k, v in val.items():
                if k != IMM:
                    self.assertFalse(v)
    
    def test_rmm(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "rmm.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[RMM])
            for k, v in val.items():
                if k != RMM:
                    self.assertFalse(v)
    
    def test_rmmcat(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "rmmcat.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[RMM_CAT])
            for k, v in val.items():
                if k != RMM_CAT:
                    self.assertFalse(v)
    
    def test_hill(self):
        with open(os.path.join(DIR, TEST_CLASSIFIER_MODELS, "hill.json"), 'r') as file:
            content = file.read()
        analyzer = Analyzer(content)
        analyzer.checks([1002])
        for key, val in analyzer.data.default_classifications.items():
            self.assertTrue(val[HILL])
            for k, v in val.items():
                if k != HILL:
                    self.assertFalse(v)

if __name__ == "__main__":
    unittest.main()