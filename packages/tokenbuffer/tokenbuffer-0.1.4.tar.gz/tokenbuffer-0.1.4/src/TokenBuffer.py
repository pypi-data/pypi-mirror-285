from typing import List, Dict
from tokenizer import tokenize, Token
import re

class TokenBuffer:
    def __init__(self):
        self.column = 0
        self.line = 0
        self.file_index = 0
        self.file_line = 1
        self.file_list = []
        self.lines: List[List[str]] = []
        self.configuration = {
            'skip_white_space': False,
            'skip_EOF': True,
            'skip_EOL': True
        }

    def init_patterns(self, patterns: Dict):
        self.token_pattern_str = '|'.join([f"(?P<{key}>{value})" for key, value in patterns.items()])
        self.token_pattern_str += r'|(?P<WHITE_SPACE>\s+)|(?P<UNKNOWN>.)'
        self.re_pattern = re.compile(self.token_pattern_str)
        if not self.re_pattern:
            raise ValueError("TokenBuffer.init_patterns: Unable to compile provided patterns.")
        
    def load_files(self, files: List[str]):
        if not files:
            raise ValueError("TokenBuffer.load_files: No files provided to load.")
        self.file_list = files
        for file in self.file_list:
            with open(file, 'r') as source:
                lines = source.readlines()
                self.lines.append(lines)

    def add_lines(self, file_name, lines):
        self.file_list.append(file_name)
        self.lines.append(lines)
        
    def config(self, **flags):
        self.configuration.update(flags)

    def tokenize(self):
        if not self.lines:
            raise ValueError("TokenBuffer.tokenize: No lines available to tokenize.")
        self.tokens = []
        for file in self.lines:
            for line in file:
                self.tokens.append(tokenize(line, self.re_pattern))
                self.tokens[-1].append(Token())
                self.tokens[-1][-1].type = 'EOL'
            self.tokens.append([Token()])
            self.tokens[-1][-1].type = 'EOF'

    def get_position(self):
        return None if self.out_of_tokens() else self.file_list[self.file_index], self.file_line, self.column

    def skip_next(self) -> bool:
        conf = self.configuration
        return (
            (conf['skip_white_space'] and self.expect_type('WHITE_SPACE'))
                or (conf['skip_EOF'] and self.expect_type('EOF')
                or (conf['skip_EOL']) and self.expect_type('EOL'))
        )
    
    def peek(self) -> Token:
        while self.line < len(self.tokens) and self.skip_next():
            self.consume()
        
        return (
            None if self.line >= len(self.tokens)
            else self.tokens[self.line][self.column]
        )

    def expect_value(self, expected_sting: str, lower: bool = False):
        return self.tokens[self.line][self.column].value.tolower() == expected_sting.tolower() if lower else self.tokens[self.line][self.column].value == expected_sting

    def expect_type(self, expected_type: str):
        return self.tokens[self.line][self.column].type == expected_type

## Cursor movement
    def consume(self):
        if self.expect_type('EOF'):
            self.consume_line()
            self.file_index += 1
            self.file_line = 1
            return
        if self.line >= len(self.tokens):
            return
        if self.expect_type('EOL'):
            self.consume_line()
            return
        self.column += 1
        if self.column >= len(self.tokens[self.line]):
            self.consume_line()

    def consume_line(self):
        if self.line >= len(self.tokens):
            raise IndexError("TokenBuffer.consume_line: Attempt to consume line beyond end of program.")
        self.line += 1
        self.file_line += 1
        self.column = 0

    def backtrack(self):
        self.column -= 1
        if self.column < 0:
            self.backtrack_line()

        while self.skip_next():
            if self.column == 0 and self.line == 0:
                raise IndexError("TokenBuffer.backtrack: Already at first available token.")
            if self.column < 0:
                self.backtrack_line()
            self.column -= 1

    def backtrack_line(self):
        if self.line == 0:
            raise IndexError("TokenBuffer.backtrack_line: Already at first available line.")
        self.line -=1
        self.file_line -= 1
        if self.file_line < 0:
            self.file_index -= 1
            self.file_line = len(self.line)
        self.column = len(self.tokens[self.line])-1

    def reset(self):
        self.column = 0
        self.line = 0
        self.file_index = 0
        self.file_line = 1

## Predicates
    def at_start(self) -> bool:
        return self.line == 0 and self.column == 0
    
    def out_of_tokens(self) -> bool:
        self.peek()
        return self.line >= len(self.tokens)

   