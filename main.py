import re
import sys

REGEX = [
    ("NUMBER", r"[+-]?\d+"),
    ("DECIMAL", r"[+-]?\d+\.\d+"),
    ("STRING", r'"[^"]*"'),
    ("KEYWORD", r"(PRINT|\.|\[|\]|\(|\)|;)"),
    (
        "OPERATOR",
        r"(:-|~|<|>|=|#|\+|-|&|OR|\*|/|AND)",
    ),  # I am not sure how I feel about this
    ("IDENTIFIER", r"\b[a-zA-Z][a-zA-Z0-9]*\b"),
    ("WHITESPACE", r"\s+"),
]


def tokenize(input_text):
    tokens = []
    position = 0
    while position < len(input_text):
        match = None
        for token_type, pattern in REGEX:
            regex = re.compile(pattern)
            match = regex.match(input_text, position)
            if match:
                text = match.group(0)
                if token_type == "WHITESPACE":
                    pass
                else:
                    tokens.append((token_type, text))
                position = match.end(0)
                break
        if not match:
            raise SyntaxError(
                f"Unknown token at position {position}, token {input_text[position]}"
            )
    tokens.append(("EOF", None))
    return tokens


# This would be extremely annoying to keep track of the tokens so its a class, womp womp


# In dreambird we are removing the ability to initalize mutiple instance of a class
# this should not effect how most OOP programmers use classes - DreamBird Docs
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[self.position]

    def get_token(self):
        """Advance to the next token."""
        self.position += 1
        if self.position < len(self.tokens):
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = ("EOF", None)

    def get_token_but_cry_if_not_x(self, token_type, value=None):
        """If Else The function
        This grabs the token_type and comparse it to the token_type and optionally the value
        If it doesnt like it spits it out,
        I did feel like writing this 100 times so here we are
        """
        if self.current_token[0] != token_type or (
            value and self.current_token[1] != value
        ):
            expected = f"{token_type}('{value}')" if value else token_type
            actual = f"{self.current_token[0]}('{self.current_token[1]}')"
            raise SyntaxError(f"Expected {expected}, got {actual}")
        self.get_token()

    def parse(self):
        """Start parsing from the start symbol."""
        self.statement_sequence()
        if self.current_token[0] != "EOF":
            raise SyntaxError("Unexpected token after end of program")
        print("Input program is correct.")

    def statement_sequence(self):
        """StatementSequence → Statement { Statement }"""
        while self.current_token[0] != "EOF":
            self.parse_statement()

    def parse_statement(self):
        """Statement → Assignment | PrintStatement"""
        if self.current_token[0] == "IDENTIFIER":
            self.parse_assignment()
        elif self.current_token[0] == "KEYWORD" and self.current_token[1] == "PRINT":
            self.parse_print()
        else:
            raise SyntaxError(f"Invalid statement starting with {self.current_token}")

    def parse_assignment(self):
        """Assignment → Designator := Expression ."""
        self.parse_designator()
        self.get_token_but_cry_if_not_x("OPERATOR", ":-")
        self.parse_expression()
        self.get_token_but_cry_if_not_x("KEYWORD", ".")

    def parse_print(self):
        """PrintStatement → PRINT ( Expression ) ."""
        self.get_token_but_cry_if_not_x("KEYWORD", "PRINT")
        self.get_token_but_cry_if_not_x("KEYWORD", "(")
        self.parse_expression()
        self.get_token_but_cry_if_not_x("KEYWORD", ")")
        self.get_token_but_cry_if_not_x("KEYWORD", ".")

    def parse_designator(self):
        """Designator → identifier { Selector }"""
        self.get_token_but_cry_if_not_x("IDENTIFIER")
        while self.current_token[1] in ["^", "["]:
            self.parse_selector()

    def parse_selector(self):
        """Selector → ^ identifier | [ Expression ]"""
        if self.current_token[1] == "^":
            self.get_token()
            self.get_token_but_cry_if_not_x("IDENTIFIER")
        elif self.current_token[1] == "[":
            self.get_token()
            self.parse_expression()
            self.get_token_but_cry_if_not_x("KEYWORD", "]")
        else:
            raise SyntaxError(f"Expected '^' or '[', got {self.current_token}")

    def parse_expression(self):
        """Expression → SimpleExpression [ Relation SimpleExpression ]"""
        self.parse_simple_expression()
        if self.current_token[1] in ["<", ">", "=", "#"]:
            self.parse_relation()
            self.parse_simple_expression()

    def parse_relation(self):
        """Relation → < | > | = | #"""
        if self.current_token[1] in ["<", ">", "=", "#"]:
            self.get_token()
        else:
            raise SyntaxError(f"Expected a relation operator, got {self.current_token}")

    def parse_simple_expression(self):
        """SimpleExpression → Term { AddOperator Term }"""
        self.parse_tern()
        while self.current_token[1] in ["+", "-", "OR", "&"]:
            self.parse_add_operator()
            self.parse_tern()

    def parse_add_operator(self):
        """AddOperator → + | - | OR | &"""
        if self.current_token[1] in ["+", "-", "OR", "&"]:
            self.get_token()
        else:
            raise SyntaxError(f"Expected an add operator, got {self.current_token}")

    def parse_tern(self):
        """Term → Factor { MulOperator Factor }"""
        self.parse_factor()
        while self.current_token[1] in ["*", "/", "AND"]:
            self.parse_mul_operator()
            self.parse_factor()

    def parse_mul_operator(self):
        """MulOperator → * | / | AND"""
        if self.current_token[1] in ["*", "/", "AND"]:
            self.get_token()
        else:
            raise SyntaxError(f"Expected a mul operator, got {self.current_token}")

    def parse_factor(self):
        """Factor → integer | decimal | string | identifier | ( Expression ) | ~ Factor"""
        if self.current_token[0] in ["NUMBER", "DECIMAL", "STRING", "IDENTIFIER"]:
            self.get_token()
        elif self.current_token[1] == "(":
            self.get_token()
            self.parse_expression()
            self.get_token_but_cry_if_not_x("KEYWORD", ")")
        elif self.current_token[1] == "~":
            self.get_token()
            self.parse_factor()
        else:
            raise SyntaxError(f"Invalid factor starting with {self.current_token}")


def main():
    input_program = """
x :- 1 .
a [ i ] :- 2 .
w [ 3 ] ^ ch :- "a" .
t ^ key :- s .
p ^ next ^ data :- alpha .
x :- x + y .
y :- x - y .
c :- c + 1 .
PRINT ( c ) .  """
    try:
        tokens = tokenize(input_program)
        parser = Parser(tokens)
        parser.parse()
    except SyntaxError as e:
        print(f"Input program is invalid: {e}")


if __name__ == "__main__":
    main()
