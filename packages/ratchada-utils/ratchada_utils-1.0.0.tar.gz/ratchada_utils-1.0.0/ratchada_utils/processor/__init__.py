# RATCHADA_UTILS: PROCESSOR PACKAGE
#
# COPYRIGHT (C) 2024 RATCHADA UTILS PROJECT
# AUTHOR:   TM-BEST-CHOKULKET
#           TM-ZOON-PATCHARAWIWATPONG
# URL: <https://thinkingmachin.es/>
# LICENSE: see LICENSE for futher info

"""
RATCHADA PROCESSOR PACKAGE:

tokenize_text : preprocesses and tokenizes it accordingly to language.
basic_text_normalizer: class, normalize thai english language.
english_text_normalizer: class, normalize english language numbers.
"""

from .basic import BasicTextNormalizer as BasicTextNormalizer
from .english import EnglishTextNormalizer as EnglishTextNormalizer

from .process import tokenize_text
