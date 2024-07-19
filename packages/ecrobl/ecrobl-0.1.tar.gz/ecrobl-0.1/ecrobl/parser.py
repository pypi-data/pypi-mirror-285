class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def parse(self):
        result = []
        while self.pos < len(self.tokens):
            result.append(self.parse_statement())
        return result

    def parse_statement(self):
        token = self.tokens[self.pos]
        if token[0] == 'VAR':
            return self.parse_variable_declaration()
        elif token[0] == 'FUNCTION':
            return self.parse_function()
        elif token[0] == 'CLASS':
            return self.parse_class()
        elif token[0] == 'SYSTEM':
            return self.parse_system_call()
        elif token[0] == 'IF':
            return self.parse_if_statement()
        elif token[0] == 'FOR':
            return self.parse_for_loop()
        elif token[0] == 'WHILE':
            return self.parse_while_loop()
        elif token[0] == 'IDENT':
            return self.parse_assignment_or_function_call()
        else:
            self.pos += 1

    def parse_variable_declaration(self):
        self.pos += 1
        var_name = self.tokens[self.pos][1]
        self.pos += 2  # Skip '='
        var_value = self.parse_expression()
        return ('VAR_DECL', var_name, var_value)

    def parse_function(self):
        self.pos += 1
        func_name = self.tokens[self.pos][1]
        self.pos += 2  # Skip '('
        parameters = []
        while self.tokens[self.pos][0] != ')':
            parameters.append(self.tokens[self.pos][1])
            self.pos += 1
        self.pos += 1  # Skip ')'
        self.pos += 1  # Skip '{'
        body = []
        while self.tokens[self.pos][0] != '}':
            body.append(self.parse_statement())
        self.pos += 1  # Skip '}'
        return ('FUNC_DEF', func_name, parameters, body)

    def parse_class(self):
        self.pos += 1
        class_name = self.tokens[self.pos][1]
        self.pos += 2  # Skip '('
        self.pos += 1  # Skip '{'
        body = []
        while self.tokens[self.pos][0] != '}':
            body.append(self.parse_statement())
        self.pos += 1  # Skip '}'
        return ('CLASS_DEF', class_name, body)

    def parse_if_statement(self):
        self.pos += 1
        condition = self.parse_expression()
        self.pos += 1  # Skip '{'
        true_block = []
        while self.tokens[self.pos][0] != '}':
            true_block.append(self.parse_statement())
        self.pos += 1  # Skip '}'
        false_block = None
        if self.tokens[self.pos][0] == 'ELSE':
            self.pos += 2  # Skip 'otherwise' and '{'
            false_block = []
            while self.tokens[self.pos][0] != '}':
                false_block.append(self.parse_statement())
            self.pos += 1  # Skip '}'
        return ('IF', condition, true_block, false_block)

    def parse_for_loop(self):
        self.pos += 1
        init = self.parse_assignment()
        self.pos += 1  # Skip ';'
        condition = self.parse_expression()
        self.pos += 1  # Skip ';'
        increment = self.parse_assignment()
        self.pos += 1  # Skip '{'
        body = []
        while self.tokens[self.pos][0] != '}':
            body.append(self.parse_statement())
        self.pos += 1  # Skip '}'
        return ('FOR', init, condition, increment, body)

    def parse_while_loop(self):
        self.pos += 1
        condition = self.parse_expression()
        self.pos += 1  # Skip '{'
        body = []
        while self.tokens[self.pos][0] != '}':
            body.append(self.parse_statement())
        self.pos += 1  # Skip '}'
        return ('WHILE', condition, body)

    def parse_assignment_or_function_call(self):
        var_name = self.tokens[self.pos][1]
        self.pos += 1
        if self.tokens[self.pos][0] == '=':
            self.pos += 1
            value = self.parse_expression()
            return ('ASSIGN', var_name, value)
        elif self.tokens[self.pos][0] == '(':
            self.pos += 1
            args = []
            while self.tokens[self.pos][0] != ')':
                args.append(self.parse_expression())
                self.pos += 1
            self.pos += 1  # Skip ')'
            return ('FUNC_CALL', var_name, args)

    def parse_system_call(self):
        self.pos += 1
        func_name = self.tokens[self.pos][1]
        self.pos += 2  # Skip '('
        args = []
        while self.tokens[self.pos][0] != ')':
            args.append(self.tokens[self.pos][1])
            self.pos += 1
        self.pos += 1  # Skip ')'
        return ('SYSTEM_CALL', func_name, args)

    def parse_expression(self):
        token = self.tokens[self.pos]
        self.pos += 1
        if token[0] == 'NUMBER':
            return ('NUMBER', token[1])
        elif token[0] == 'STRING':
            return ('STRING', token[1])
        elif token[0] == 'IDENT':
            return ('VAR', token[1])
        elif token[0] in {'+', '-', '*', '/'}:
            left = self.parse_expression()
            right = self.parse_expression()
            return ('BIN_OP', token[0], left, right)
