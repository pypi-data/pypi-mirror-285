class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.system_functions = {
            'Output': self.system_output,
            'CommandInput': self.system_input
        }

    def interpret(self):
        for node in self.tree:
            self.execute(node)

    def execute(self, node):
        if node[0] == 'VAR_DECL':
            self.variables[node[1]] = self.evaluate(node[2])
        elif node[0] == 'FUNC_DEF':
            self.functions[node[1]] = node
        elif node[0] == 'CLASS_DEF':
            self.classes[node[1]] = node
        elif node[0] == 'IF':
            self.execute_if(node)
        elif node[0] == 'FOR':
            self.execute_for(node)
        elif node[0] == 'WHILE':
            self.execute_while(node)
        elif node[0] == 'ASSIGN':
            self.variables[node[1]] = self.evaluate(node[2])
        elif node[0] == 'FUNC_CALL':
            self.execute_function_call(node)
        elif node[0] == 'SYSTEM_CALL':
            self.execute_system_call(node)

    def evaluate(self, node):
        if node[0] == 'NUMBER':
            return node[1]
        elif node[0] == 'STRING':
            return node[1]
        elif node[0] == 'VAR':
            return self.variables[node[1]]
        elif node[0] == 'BIN_OP':
            left = self.evaluate(node[2])
            right = self.evaluate(node[3])
            if node[1] == '+':
                return left + right
            elif node[1] == '-':
                return left - right
            elif node[1] == '*':
                return left * right
            elif node[1] == '/':
                return left / right

    def execute_if(self, node):
        condition = self.evaluate(node[1])
        if condition:
            for stmt in node[2]:
                self.execute(stmt)
        elif node[3]:
            for stmt in node[3]:
                self.execute(stmt)

    def execute_for(self, node):
        self.execute(node[1])
        while self.evaluate(node[2]):
            for stmt in node[4]:
                self.execute(stmt)
            self.execute(node[3])

    def execute_while(self, node):
        while self.evaluate(node[1]):
            for stmt in node[2]:
                self.execute(stmt)

    def execute_function_call(self, node):
        func_name = node[1]
        if func_name in self.functions:
            func = self.functions[func_name]
            params = func[2]
            args = node[2]
            local_vars = self.variables.copy()
            for i in range(len(params)):
                self.variables[params[i]] = self.evaluate(args[i])
            for stmt in func[3]:
                self.execute(stmt)
            self.variables = local_vars

    def execute_system_call(self, node):
        func_name = node[1]
        if func_name in self.system_functions:
            self.system_functions[func_name](node[2])

    def system_output(self, args):
        print(self.evaluate(args[0]))

    def system_input(self, args):
        return input(self.evaluate(args[0]))
