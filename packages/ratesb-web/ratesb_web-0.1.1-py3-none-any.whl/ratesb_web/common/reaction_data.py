from dataclasses import dataclass
import json
import sys
import os
current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(current_dir)
sys.path.append(parent_dir)

from custom_classifier import _CustomClassifier
# from SBMLKinetics.common.simple_sbml import SimpleSBML
# from SBMLKinetics.common.reaction import Reaction
from typing import List, Optional
from results import Results

import os

from typing import List

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

NON_MM_KEYS = [
    ZERO, UNDR1, UNDR2, UNDR3, UNDR_A1, UNDR_A2, UNDR_A3,
    BIDR11, BIDR12, BIDR21, BIDR22, BIDR_A11, BIDR_A12, BIDR_A21, BIDR_A22
]

MM_KEYS = [MM, MM_CAT, AMM, IMM, RMM, RMM_CAT]

UNDR_KEYS = [UNDR1, UNDR2, UNDR3]

UNDR_A_KEYS = [UNDR_A1, UNDR_A2, UNDR_A3]

BIDR_ALL_KEYS = [BIDR11, BIDR12, BIDR21, BIDR22,
                 BIDR_A11, BIDR_A12, BIDR_A21, BIDR_A22]

MM_CAT_KEYS = [MM_CAT, AMM, IMM, RMM_CAT]

UNDR_SBOS = [41, 43, 44, 45, 47, 49, 50, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 140, 141, 142, 143, 144, 145, 146, 163, 166, 333, 560, 561, 562, 563, 564, 430, 270, 458,
             275, 273, 379, 440, 443, 451, 454, 456, 260, 271, 378, 387, 262, 265, 276, 441, 267, 274, 444, 452, 453, 455, 457, 386, 388, 442, 277, 445, 446, 447, 448, 266, 449, 450]

UNDR_A_SBOS = [41, 43, 44, 45, 47, 49, 50, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
               140, 141, 142, 143, 144, 145, 146, 163, 166, 333, 560, 561, 562, 563, 564]

BI_SBOS = [42, 69, 78, 88, 109, 646, 70, 71, 74, 79, 80, 81, 84, 89, 99, 110, 120, 130, 72, 73, 75, 76, 77, 82, 83, 85, 86, 87, 90, 91, 92, 95, 100, 101, 102, 105, 111, 112,
           113, 116, 121, 122, 123, 126, 131, 132, 133, 136, 93, 94, 96, 97, 98, 103, 104, 106, 107, 108, 114, 115, 117, 118, 119, 124, 125, 127, 128, 129, 134, 135, 137, 138, 139]

MM_SBOS = [28, 29, 30, 31, 199]

MM_CAT_SBOS = [28, 29, 30, 31, 199, 430, 270, 458, 275, 273, 379, 440, 443, 451, 454, 456, 260, 271, 378, 387,
               262, 265, 276, 441, 267, 274, 444, 452, 453, 455, 457, 386, 388, 442, 277, 445, 446, 447, 448, 266, 449, 450]

HILL_SBOS = [192, 195, 198]


@dataclass
class ReactionData:
    reaction_id: str
    kinetics: str
    kinetics_sim: str
    reactant_list: List[str]
    product_list: List[str]
    species_in_kinetic_law: List[str]
    parameters_in_kinetic_law: List[str]
    ids_list: List[str]
    sorted_species: List[str]
    boundary_species: List[str]
    parameters_in_kinetic_law_only: List[str]
    compartment_in_kinetic_law: List[str]
    is_reversible: bool
    sbo_term: int
    codes: List[int]
    non_constant_params: List[str]

DEFAULT_CLASSIFIER_PATH = os.path.join(os.path.dirname(__file__), "default_classifier.json")
with open(DEFAULT_CLASSIFIER_PATH, 'r') as file:
    DEFAULT_JSON_STR = file.read()


class AnalyzerData:
    def __init__(self, model_json: str, rate_law_classification_json: Optional[str] = None):
        """
        Initializes the AnalyzerData class.

        Args:
            model_str (str): json representation of the model.
            rate_law_classification_json (str): json representation of the custon classifications.
        """
        reaction_data = json.loads(model_json)
        self.reactions = []
        self.custom_classifier = None
        self.default_classifications = {}
        self.custom_classifications = {}
        self.results = Results()
        
        self.default_classifier = _CustomClassifier(DEFAULT_JSON_STR)

        if rate_law_classification_json:
            self.custom_classifier = _CustomClassifier(rate_law_classification_json)
        
        for reaction in reaction_data:
            reaction_id = reaction['reaction_id']
            kinetics = reaction['kinetics']
            kinetics_sim = reaction['kinetics_sim']
            reactant_list = reaction['reactant_list']
            product_list = reaction['product_list']
            species_in_kinetic_law = reaction['species_in_kinetic_law']
            parameters_in_kinetic_law_only = reaction['parameters_in_kinetic_law_only']
            others_in_kinetic_law = reaction['others_in_kinetic_law']
            ids_list = reaction['ids_list']
            sorted_species = reaction['sorted_species']
            boundary_species = reaction['boundary_species']
            compartment_in_kinetic_law = reaction['compartment_in_kinetic_law']
            is_reversible = reaction['is_reversible']
            sbo_term = reaction['sbo_term']
            const_parameters_in_kinetic_law = reaction['const_parameters_in_kinetic_law']
            codes = []
            non_constant_params = [param for param in parameters_in_kinetic_law_only if param not in const_parameters_in_kinetic_law]
                

            data = ReactionData(
                reaction_id=reaction_id,
                kinetics=kinetics,
                kinetics_sim=kinetics_sim,
                reactant_list=reactant_list,
                product_list=product_list,
                species_in_kinetic_law=species_in_kinetic_law,
                parameters_in_kinetic_law=parameters_in_kinetic_law_only + others_in_kinetic_law,
                ids_list=ids_list,
                sorted_species=sorted_species,
                boundary_species=boundary_species,
                parameters_in_kinetic_law_only=parameters_in_kinetic_law_only,
                compartment_in_kinetic_law=compartment_in_kinetic_law,
                is_reversible=is_reversible,
                sbo_term=sbo_term,
                codes=codes,
                non_constant_params=non_constant_params
            )
            
            self.reactions.append(data)