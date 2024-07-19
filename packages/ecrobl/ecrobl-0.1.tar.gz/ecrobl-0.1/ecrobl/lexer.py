import re

class Lexer:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.keywords = {
            'arg': 'VAR',
            'Function': 'FUNCTION',
            'class': 'CLASS',
            'return': 'RETURN',
            'produce': 'RETURN',
            'evaluate': 'IF',
            'otherwise': 'ELSE',
            'iterate': 'FOR',
            'during': 'WHILE',
            'System': 'SYSTEM',
            'Output': 'OUTPUT',
            'CommandInput': 'INPUT'
        }
        self.token_specification = [
            ('NUMBER',    r'\d+(\.\d*)?'),  # Integer or decimal number
            ('IDENT',     r'[A-Za-z_]\w*'),  # Identifiers
            ('OP',        r'[+\-*/%]'),     # Arithmetic operators
            ('STRING',    r'"[^"]*"'),       # String literals
            ('NEWLINE',   r'\n'),            # Line endings
            ('SKIP',      r'[ \t]+'),        # Skip over spaces and tabs
            ('MISMATCH',  r'.'),             # Any other character
        ]

    def tokenize(self):
        code = self.code
        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.token_specification)
        line_num = 1
        line_start = 0
        for mo in re.finditer(token_regex, code):
            kind = mo.lastgroup
            value = mo.group(kind)
            column = mo.start() - line_start
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'IDENT' and value in self.keywords:
                kind = self.keywords[value]
            elif kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise RuntimeError(f'{value!r} unexpected on line {line_num}')
            self.tokens.append((kind, value))
        return self.tokens
