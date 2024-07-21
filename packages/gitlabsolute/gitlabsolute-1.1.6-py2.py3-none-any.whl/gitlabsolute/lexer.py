#!/usr/bin/env python3
# pylint: disable=invalid-name
import sys

import ply.lex as plex

tokens = (
    "AND",
    "OR",
    "NOT",
    "EQUAL",
    "TRUE",
    "NOTEQUAL",
    "GT",
    "GTE",
    "KEYWORD",
    "LT",
    "LTE",
    "STRING",
    "LPAREN",
    "RPAREN",
    "FALSE",
    "SEMICOLON",
    "IN",
    "NUMBER",
    "LEN",
    "LBRACKET",
    "RBRACKET",
    "LBRACES",
    "RBRACES",
)

# Order matters
t_SEMICOLON = ";"
t_LPAREN = r"\("
t_RPAREN = r"\)"
t_LBRACKET = r"\["
t_RBRACKET = r"\]"
t_LBRACES = r"\{"
t_RBRACES = r"\}"
t_LT = "<"
t_LTE = "<="
t_GT = ">"
t_GTE = ">="
t_EQUAL = "=="
t_NOTEQUAL = "!="

t_IN = r"[Ii][Nn]"
t_LEN = r"[Ll][Ee][Nn]"

t_TRUE = r"[Tt]rue"
t_FALSE = r"[Ff]alse"
t_KEYWORD = r"[a-z][_a-z]*"
t_NUMBER = r"[0-9][0-9]*"
t_STRING = r"('[^'].*?'|\"[^\"].*?\")"
t_ignore = " \t"


def t_error(t):
    print(f"error: illegal character '{t.value[0]}'", sys.stderr)
    sys.exit(1)


def lex(expression):
    lexer = plex.lex()
    lexer.input(expression)

    # pylint: disable=redefined-outer-name
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break  # No more input
        tokens += [tok]
    # print(tokens, file=sys.stderr)
    return tokens


def lex2python(expression):
    output = ""
    for token in lex(expression):
        if token.type.lower() == "keyword" and token.value.upper() not in tokens:
            output += f'_item["{token.value}"]'
        else:
            output += token.value.lower()
        output += " "
    # print(output, file=sys.stderr)
    if not brackets_are_balanced(output):
        sys.exit("error: Brackets, braces, or parentheses are not balanced")
    return output.strip()


def evaluate(expression, item):
    # pylint: disable=eval-used
    try:
        return eval(expression, {}, {"_item": item, "true": True, "false": False})
    except KeyError as err:
        sys.exit(f"error: Key {err} does not exist")


def brackets_are_balanced(expr):
    stack = []

    for char in expr:
        if char in ["(", "{", "["]:
            stack.append(char)
        elif char in [")", "}", "]"]:
            # If current character is not opening bracket, then it must be closing.
            # So stack cannot be empty at this point.
            if not stack:
                return False

            last_char = stack.pop()
            if last_char == "(" and char != ")":
                return False
            if last_char == "{" and char != "}":
                return False
            if last_char == "[" and char != "]":
                return False

    # If stack is not empty, we didn't consume all opening brackets
    if stack:
        return False
    return True
