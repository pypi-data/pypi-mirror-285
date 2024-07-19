import unittest
import sys
import os
# setting path
current_dir = os.path.dirname(__file__)
parent_dir = os.path.dirname(current_dir)
common_dir = os.path.join(parent_dir, 'ratesb_web', 'common')
sys.path.append(common_dir)

from analyzer import Analyzer


DIR = os.path.dirname(os.path.abspath(__file__))
TEST_MODELS = "test_models"
TRUE_PATH_1 = os.path.join(DIR, TEST_MODELS, "true_0001.json")
FALSE_PATH_1 = os.path.join(DIR, TEST_MODELS, "false_0001.json")
TRUE_PATH_2 = os.path.join(DIR, TEST_MODELS, "true_0002.json")
FALSE_PATH_2 = os.path.join(DIR, TEST_MODELS, "false_0002.json")

TRUE_PATH_1001 = os.path.join(DIR, TEST_MODELS, "true_1001.json")
FALSE_PATH_1001 = os.path.join(DIR, TEST_MODELS, "false_1001.json")
TRUE_PATH_1002 = os.path.join(DIR, TEST_MODELS, "true_1002.json")
FALSE_PATH_1002 = os.path.join(DIR, TEST_MODELS, "false_1002.json")
TRUE_PATH_1003 = os.path.join(DIR, TEST_MODELS, "true_1003.json")
FALSE_PATH_1003 = os.path.join(DIR, TEST_MODELS, "false_1003.json")
TRUE_PATH_1004 = os.path.join(DIR, TEST_MODELS, "true_1004.json")
FALSE_PATH_1004 = os.path.join(DIR, TEST_MODELS, "false_1004.json")
TRUE_PATH_1005 = os.path.join(DIR, TEST_MODELS, "true_1005.json")
FALSE_PATH_1005 = os.path.join(DIR, TEST_MODELS, "false_1005.json")
TRUE_PATH_1006 = os.path.join(DIR, TEST_MODELS, "true_1006.json")
FALSE_PATH_1006 = os.path.join(DIR, TEST_MODELS, "false_1006.json")

TRUE_PATH_1010 = os.path.join(DIR, TEST_MODELS, "true_1010.json")
FALSE_PATH_1010 = os.path.join(DIR, TEST_MODELS, "false_1010.json")

TRUE_PATH_1020 = os.path.join(DIR, TEST_MODELS, "true_1020.json")
FALSE_PATH_1020 = os.path.join(DIR, TEST_MODELS, "false_1020.json")
TRUE_PATH_1021 = os.path.join(DIR, TEST_MODELS, "true_1021.json")
FALSE_PATH_1021 = os.path.join(DIR, TEST_MODELS, "false_1021.json")
TRUE_PATH_1022 = os.path.join(DIR, TEST_MODELS, "true_1022.json")
FALSE_PATH_1022 = os.path.join(DIR, TEST_MODELS, "false_1022.json")

TRUE_PATH_1030 = os.path.join(DIR, TEST_MODELS, "true_1030.json")
FALSE_PATH_1030 = os.path.join(DIR, TEST_MODELS, "false_1030.json")
TRUE_PATH_1031 = os.path.join(DIR, TEST_MODELS, "true_1031.json")
FALSE_PATH_1031 = os.path.join(DIR, TEST_MODELS, "false_1031.json")
TRUE_PATH_1032 = os.path.join(DIR, TEST_MODELS, "true_1032.json")
FALSE_PATH_1032 = os.path.join(DIR, TEST_MODELS, "false_1032.json")
TRUE_PATH_1033 = os.path.join(DIR, TEST_MODELS, "true_1033.json")
FALSE_PATH_1033 = os.path.join(DIR, TEST_MODELS, "false_1033.json")
TRUE_PATH_1034 = os.path.join(DIR, TEST_MODELS, "true_1034.json")
FALSE_PATH_1034 = os.path.join(DIR, TEST_MODELS, "false_1034.json")
TRUE_PATH_1035 = os.path.join(DIR, TEST_MODELS, "true_1035.json")
FALSE_PATH_1035 = os.path.join(DIR, TEST_MODELS, "false_1035.json")
TRUE_PATH_1036 = os.path.join(DIR, TEST_MODELS, "true_1036.json")
FALSE_PATH_1036 = os.path.join(DIR, TEST_MODELS, "false_1036.json")
TRUE_PATH_1037 = os.path.join(DIR, TEST_MODELS, "true_1037.json")
FALSE_PATH_1037 = os.path.join(DIR, TEST_MODELS, "false_1037.json")

TRUE_PATH_1040 = os.path.join(DIR, TEST_MODELS, "true_1040.json")
FALSE_PATH_1040 = os.path.join(DIR, TEST_MODELS, "false_1040.json")
TRUE_PATH_1041 = os.path.join(DIR, TEST_MODELS, "true_1041.json")
FALSE_PATH_1041 = os.path.join(DIR, TEST_MODELS, "false_1041.json")
TRUE_PATH_1042 = os.path.join(DIR, TEST_MODELS, "true_1042.json")
FALSE_PATH_1042 = os.path.join(DIR, TEST_MODELS, "false_1042.json")
TRUE_PATH_1043 = os.path.join(DIR, TEST_MODELS, "true_1043.json")
FALSE_PATH_1043 = os.path.join(DIR, TEST_MODELS, "false_1043.json")
TRUE_PATH_1044 = os.path.join(DIR, TEST_MODELS, "true_1044.json")
FALSE_PATH_1044 = os.path.join(DIR, TEST_MODELS, "false_1044.json")

class TestAnalyzer(unittest.TestCase):

    def setUp(self):
        # self.rate_analyzer = Analyzer("tests/test_models/1.ant", "tests/test_models/rate_laws.json")
        # self.mm_analyzer = Analyzer("tests/test_models/reversible_MM.ant", "tests/test_models/reversible_MM.json")
        # self.analyzer = Analyzer("tests/test_models/1.ant")
        pass

    # def test_get_rate_laws(self):
    #     # Add test logic here. For example:
    #     # self.assertEqual(self.rate_analyzer.get_rate_laws(), expected_result)
    #     pass
    
    def test_check_0001(self):
        with open(TRUE_PATH_1, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1])
        false_case_analyzer.checks([1])
        # self.assertEqual(self.rate_analyzer.classification_cp, [])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), 'No errors or warnings found.')
    
    def test_check_0002(self):
        with open(TRUE_PATH_2, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_2, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([2])
        false_case_analyzer.checks([2])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Error 0002: Expecting reactants in rate law: a\n')
    
    def test_check_1001(self):
        with open(TRUE_PATH_1001, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1001, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1001])
        false_case_analyzer.checks([1001])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1001: Rate law contains only number.\n')

    def test_check_1002(self):
        with open(TRUE_PATH_1002, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1002, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1002])
        false_case_analyzer.checks([1002])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1002: Unrecognized rate law from the standard list.\n')
    
    def test_check_1003(self):
        with open(TRUE_PATH_1003, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1003, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1003])
        false_case_analyzer.checks([1003])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1003: Flux is not increasing as reactant increases.\n_J1:\n  Warning 1003: Flux is not increasing as reactant increases.\n_J2:\n  Warning 1003: Flux is not increasing as reactant increases.\n')
    
    def test_check_1004(self):
        with open(TRUE_PATH_1004, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1004, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1004])
        false_case_analyzer.checks([1004])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1004: Flux is not decreasing as product increases.\n')
    
    def test_check_1005(self):
        with open(TRUE_PATH_1005, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1005, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1005])
        false_case_analyzer.checks([1005])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1005: Expecting boundary species reactant in rate law: a\n')
    
    def test_check_1006(self):
        with open(TRUE_PATH_1006, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1006, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1006])
        false_case_analyzer.checks([1006])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1006: Expecting these parameters to be constants: k1\n')
    
    def test_check_1010(self):
        with open(TRUE_PATH_1010, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1010, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1010])
        false_case_analyzer.checks([1010])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), '_J0:\n  Warning 1010: Irreversible reaction kinetic law contains products: b\n')
    
    def test_check_1020(self):
        with open(TRUE_PATH_1020, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1020, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1020])
        false_case_analyzer.checks([1020])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1020: We recommend that these parameters start with 'k': v1\n_J1:\n  Warning 1020: We recommend that these parameters start with 'k': K1\n_J2:\n  Warning 1020: We recommend that these parameters start with 'k': K1\n_J3:\n  Warning 1020: We recommend that these parameters start with 'k': v1\n")
    
    def test_check_1021(self):
        with open(TRUE_PATH_1021, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1021, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1021])
        false_case_analyzer.checks([1021])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1021: We recommend that these parameters start with 'K': km\n_J1:\n  Warning 1021: We recommend that these parameters start with 'K': km\n_J2:\n  Warning 1021: We recommend that these parameters start with 'K': k3\n")
    
    def test_check_1022(self):
        with open(TRUE_PATH_1022, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1022, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1022])
        false_case_analyzer.checks([1022])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1022: We recommend that these parameters start with 'V': vm\n")
    
    def test_check_1030(self):
        with open(TRUE_PATH_1030, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1030, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1030])
        false_case_analyzer.checks([1030])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1030: Elements of the same type are not ordered alphabetically\n_J1:\n  Warning 1030: Elements of the same type are not ordered alphabetically\n")
    
    def test_check_1031(self):
        with open(TRUE_PATH_1031, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1031, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1031])
        false_case_analyzer.checks([1031])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1031: Formatting convention not followed (compartment before parameters before species)\n_J1:\n  Warning 1031: Formatting convention not followed (compartment before parameters before species)\n")

    def test_check_1032(self):
        with open(TRUE_PATH_1032, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1032, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1032])
        false_case_analyzer.checks([1032])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1032: Denominator not in alphabetical order\n")

    def test_check_1033(self):
        with open(TRUE_PATH_1033, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1033, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1033])
        false_case_analyzer.checks([1033])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1033: Numerator and denominator not in alphabetical order\n")

    def test_check_1034(self):
        with open(TRUE_PATH_1034, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1034, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1034])
        false_case_analyzer.checks([1034])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1034: Numerator convention not followed and denominator not in alphabetical order\n")

    # def test_check_1035(self):
    #     with open(TRUE_PATH_1035, 'r') as file:
    #         true_content = file.read()
    #     with open(FALSE_PATH_1035, 'r') as file:
    #         false_content = file.read()
    #     true_case_analyzer = Analyzer(true_content)
    #     false_case_analyzer = Analyzer(false_content)
    #     true_case_analyzer.checks([1035])
    #     false_case_analyzer.checks([1035])
    #     self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
    #     self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1035: Denominator convention not followed\n")

    # def test_check_1036(self):
    #     true_case_analyzer = Analyzer(TRUE_PATH_1036)
    #     false_case_analyzer = Analyzer(FALSE_PATH_1036)
    #     true_case_analyzer.check(1036)
    #     false_case_analyzer.check(1036)
    #     # self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
    #     self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1036: Numerator not in alphabetical order and denominator convention not followed\n")

    # def test_check_1037(self):
    #     true_case_analyzer = Analyzer(TRUE_PATH_1037)
    #     false_case_analyzer = Analyzer(FALSE_PATH_1037)
    #     true_case_analyzer.check(1037)
    #     false_case_analyzer.check(1037)
    #     self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
    #     self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1037: Numerator and denominator convention not followed\n")

    def test_check_1040(self):
        with open(TRUE_PATH_1040, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1040, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1040])
        false_case_analyzer.checks([1040])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1040: Uni-directional mass action annotation not following recommended SBO terms, we recommend annotations to be subclasses of: SBO_0000430, SBO_0000041\n")

    def test_check_1041(self):
        with open(TRUE_PATH_1041, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1041, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1041])
        false_case_analyzer.checks([1041])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1041: Uni-Directional Mass Action with an Activator annotation not following recommended SBO terms, we recommend annotations to be subclasses of: SBO_0000041\n")

    def test_check_1042(self):
        with open(TRUE_PATH_1042, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1042, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1042])
        false_case_analyzer.checks([1042])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1042: Bi-directional mass action (with an Activator) annotation not following recommended SBO terms, we recommend annotations to be subclasses of: SBO_0000042\n")

    def test_check_1043(self):
        with open(TRUE_PATH_1043, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1043, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1043])
        false_case_analyzer.checks([1043])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1043: Michaelis-Menten kinetics without an explicit enzyme annotation not following recommended SBO terms, we recommend annotations to be subclasses of: SBO_0000028\n")

    def test_check_1044(self):
        with open(TRUE_PATH_1044, 'r') as file:
            true_content = file.read()
        with open(FALSE_PATH_1044, 'r') as file:
            false_content = file.read()
        true_case_analyzer = Analyzer(true_content)
        false_case_analyzer = Analyzer(false_content)
        true_case_analyzer.checks([1044])
        false_case_analyzer.checks([1044])
        self.assertEqual(str(true_case_analyzer.results), 'No errors or warnings found.')
        self.assertEqual(str(false_case_analyzer.results), "_J0:\n  Warning 1044: Michaelis-Menten kinetics with an explicit enzyme annotation not following recommended SBO terms, we recommend annotations to be subclasses of: SBO_0000028, SBO_0000430\n")
    
    # def test_check_except(self):
    #     except_analyzer = Analyzer("tests/test_models/1.ant")
    #     analyzer = Analyzer("tests/test_models/1.ant")
    #     except_analyzer.check_except([1,2])
    #     analyzer.checks([1001, 1002, 1003, 1004, 1005, 1006, 1010, 1020, 1021, 1022, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037, 1040, 1041, 1042, 1043, 1044])
    #     self.assertEqual(str(except_analyzer.results), str(analyzer.results))

if __name__ == "__main__":
    unittest.main()
