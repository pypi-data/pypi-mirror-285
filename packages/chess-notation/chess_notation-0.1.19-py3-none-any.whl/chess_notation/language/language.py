import json
import functools
import os
from typing import Sequence, Literal, get_args
import ramda as R

Language = Literal['CA', 'EN', 'DE', 'RU', 'BG', 'FR', 'RO', 'DK', 'AZ', 'TR', 'PL', 'IS', 'NL', 'HU', 'LV', 'PT']
LANGUAGES: Sequence[Language] = get_args(Language) # type: ignore

@functools.lru_cache(maxsize=1)
def translations():
  folder = os.path.dirname(os.path.abspath(__file__))
  path = os.path.join(folder, 'translations.json')
  with open(path) as f:
    return json.load(f)

@functools.cache
def translator(language: Language) -> dict[int, str]:
  return str.maketrans(translations()[language])

@R.curry
def translate(san: str, language: Language) -> str:
  return san.translate(translator(language))