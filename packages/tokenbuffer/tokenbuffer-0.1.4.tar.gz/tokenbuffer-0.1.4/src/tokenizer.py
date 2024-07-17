import re
from dataclasses import dataclass
from typing import List

@dataclass
class Token:
    def __init__(self):
        self.type: str = None
        self.value: str = None
        self.column: int = None


def tokenize(input_string: str, pattern: re.Pattern) -> List[Token]:
    result = []
    input_string = input_string.rstrip('\n')
    matches = pattern.finditer(input_string)
    for match in matches:
        token = Token()
        token.type = match.lastgroup
        token.value = match.group()
        token.column = match.start()
        result.append(token)
    return result