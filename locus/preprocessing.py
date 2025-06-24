"""Preprocessing utilities for the Locus method."""

import re
from dataclasses import dataclass, field
from typing import List, Iterable

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize

JAVA_KEYWORDS = {
    'abstract', 'assert', 'boolean', 'break', 'byte', 'case', 'catch', 'char',
    'class', 'const', 'continue', 'default', 'do', 'double', 'else', 'enum',
    'extends', 'final', 'finally', 'float', 'for', 'goto', 'if', 'implements',
    'import', 'instanceof', 'int', 'interface', 'long', 'native', 'new',
    'package', 'private', 'protected', 'public', 'return', 'short', 'static',
    'strictfp', 'super', 'switch', 'synchronized', 'this', 'throw', 'throws',
    'transient', 'try', 'void', 'volatile', 'while', 'null', 'true', 'false'
}

STOP_WORDS = set(stopwords.words('english'))
STEMMER = PorterStemmer()


@dataclass
class Hunk:
    commit: str
    file_path: str
    diff: str
    nl_tokens: List[str] = field(default_factory=list)
    ce_tokens: List[str] = field(default_factory=list)


def tokenize_nl(text: str) -> List[str]:
    """Tokenize text into normalized NL tokens."""
    tokens = wordpunct_tokenize(text)
    words = []
    for tok in tokens:
        low = tok.lower()
        if low in STOP_WORDS or low in JAVA_KEYWORDS:
            continue
        split = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', tok)
        for part in split or [tok]:
            low_part = part.lower()
            if low_part in STOP_WORDS or low_part in JAVA_KEYWORDS:
                continue
            words.append(STEMMER.stem(low_part))
    return words


def extract_code_entities(text: str, dictionary: Iterable[str]) -> List[str]:
    """Extract code entity tokens present in `dictionary`."""
    candidates = re.findall(r'[A-Za-z_][A-Za-z0-9_\.]*', text)
    return [c for c in candidates if c in dictionary]

