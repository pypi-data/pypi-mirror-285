import sys
from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter

def main():
    if len(sys.argv) < 2:
        print("Usage: ecrobl <file.ecb>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as file:
        code = file.read()

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    tree = parser.parse()
    interpreter = Interpreter(tree)
    interpreter.interpret()

if __name__ == "__main__":
    main()
