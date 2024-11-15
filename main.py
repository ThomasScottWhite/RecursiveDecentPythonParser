import re
import sys

# I personally would have made each keyword its own regex pattern, but I wanted to follow the language token types
REGEX = [
    ("NUMBER", r"[+-]?\d+"),
    ("DECIMAL", r"[+-]?\d+\.\d+"),
    ("STRING", r'"[^"]*"'),
    ("KEYWORD", r"(PRINT|\.|\[|\]|\(|\)|;)"),
    (
        "OPERATOR",
        r"(:-|~|<|>|=|#|\+|-|&|OR|\*|/|\^|AND)",
    ),
    ("IDENTIFIER", r"\b[a-zA-Z][a-zA-Z0-9]*\b"),
    ("WHITESPACE", r"\s+"),
]


def tokenize(input_text):
    """Turns the input text into a list of tokens"""
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
            position += 1  # This allows characters like {} to be ignored
            continue
    tokens.append(("EOF", None))
    return tokens


position = 0
current_token = None
tokens = []


def init_parser(token_list):
    global tokens, position, current_token
    tokens = token_list
    position = 0
    current_token = tokens[position]


def get_token():
    """Advance to the next token."""
    global position, current_token
    position += 1
    if position < len(tokens):
        current_token = tokens[position]
    else:
        current_token = ("EOF", None)


def get_token_expect(token_type, value=None):
    """ """
    global current_token
    if current_token[0] != token_type or (value and current_token[1] != value):
        expected = f"{token_type}('{value}')" if value else token_type
        actual = f"{current_token[0]}('{current_token[1]}')"
        raise SyntaxError(f"Expected {expected}, got {actual}")
    get_token()


def parse():
    """Start parsing from the start symbol."""
    statement_sequence()
    if current_token[0] != "EOF":
        raise SyntaxError("Unexpected token after end of program")
    print("Input program is correct.")


def statement_sequence():
    """StatementSequence → Statement { Statement }"""
    while current_token[0] != "EOF":
        parse_statement()


def parse_statement():
    """Statement → Assignment | PrintStatement"""
    if current_token[0] == "IDENTIFIER":
        parse_assignment()
    elif current_token[0] == "KEYWORD" and current_token[1] == "PRINT":
        parse_print()
    else:
        raise SyntaxError(f"Invalid statement starting with {current_token}")


def parse_assignment():
    """Assignment → Designator := Expression ."""
    parse_designator()
    get_token_expect("OPERATOR", ":-")
    parse_expression()
    get_token_expect("KEYWORD", ".")


def parse_print():
    """PrintStatement → PRINT ( Expression ) ."""
    get_token_expect("KEYWORD", "PRINT")
    get_token_expect("KEYWORD", "(")
    parse_expression()
    get_token_expect("KEYWORD", ")")
    get_token_expect("KEYWORD", ".")


def parse_designator():
    """Designator → identifier { Selector }"""
    get_token_expect("IDENTIFIER")
    while current_token[1] in ["^", "["]:
        parse_selector()


def parse_selector():
    """Selector → ^ identifier | [ Expression ]"""
    if current_token[1] == "^":
        get_token()
        get_token_expect("IDENTIFIER")
    elif current_token[1] == "[":
        get_token()
        parse_expression()
        get_token_expect("KEYWORD", "]")
    else:
        raise SyntaxError(f"Expected '^' or '[', got {current_token}")


def parse_expression():
    """Expression → SimpleExpression [ Relation SimpleExpression ]"""
    parse_simple_expression()
    if current_token[1] in ["<", ">", "=", "#"]:
        parse_relation()
        parse_simple_expression()


def parse_relation():
    """Relation → < | > | = | #"""
    if current_token[1] in ["<", ">", "=", "#"]:
        get_token()
    else:
        raise SyntaxError(f"Expected a relation operator, got {current_token}")


def parse_simple_expression():
    """SimpleExpression → Term { AddOperator Term }"""
    parse_term()
    while current_token[1] in ["+", "-", "OR", "&", "^"]:
        parse_add_operator()
        parse_term()


def parse_add_operator():
    """AddOperator → + | - | OR | &"""
    if current_token[1] in ["+", "-", "OR", "&"]:
        get_token()
    else:
        raise SyntaxError(f"Expected an add operator, got {current_token}")


def parse_term():
    """Term → Factor { MulOperator Factor }"""
    parse_factor()
    while current_token[1] in ["*", "/", "AND"]:
        parse_mul_operator()
        parse_factor()


def parse_mul_operator():
    """MulOperator → * | / | AND"""
    if current_token[1] in ["*", "/", "AND"]:
        get_token()
    else:
        raise SyntaxError(f"Expected a mul operator, got {current_token}")


def parse_factor():
    """Factor → integer | decimal | string | identifier | ( Expression ) | ~ Factor"""
    if current_token[0] in ["NUMBER", "DECIMAL", "STRING", "IDENTIFIER"]:
        get_token()
    elif current_token[1] == "(":
        get_token()
        parse_expression()
        get_token_expect("KEYWORD", ")")
    elif current_token[1] == "~":
        get_token()
        parse_factor()
    else:
        raise SyntaxError(f"Invalid factor starting with {current_token}")


def main():
    if not sys.stdin.isatty():
        input_program = sys.stdin.read()
    else:
        sys.exit()

    try:
        tokens = tokenize(input_program)
        init_parser(tokens)
        parse()
    except SyntaxError as e:
        print(f"Input program is invalid: {e}")


if __name__ == "__main__":
    main()
