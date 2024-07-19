import os
import pickle
import hashlib

class Cache:
    def __init__(self, cache_dir="__ecroblcache__"):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def get_cache_path(self, code):
        code_hash = hashlib.md5(code.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{code_hash}.cache")

    def load_cache(self, code):
        cache_path = self.get_cache_path(code)
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as cache_file:
                return pickle.load(cache_file)
        return None

    def save_cache(self, code, tree):
        cache_path = self.get_cache_path(code)
        with open(cache_path, 'wb') as cache_file:
            pickle.dump(tree, cache_file)

def main():
    if len(sys.argv) < 2:
        print("Usage: ecrobl <file.ecb>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as file:
        code = file.read()

    cache = Cache()
    tree = cache.load_cache(code)
    if tree is None:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        tree = parser.parse()
        cache.save_cache(code, tree)

    interpreter = Interpreter(tree)
    interpreter.interpret()
