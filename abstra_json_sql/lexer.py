from typing import List, Tuple

from .tokens import Token, keywords, operators


def start_with_operator(code: str):
    return any(code.startswith(op) for op in operators)


def extract_operator(code: str):
    if start_with_operator(code):
        op = next(op for op in operators if code.startswith(op))
        code = code[len(op) :]
        return Token("operator", op), code
    else:
        raise Exception(f"Not a valid operator, code: {code}")


def start_with_space(code: str):
    return code[0].isspace()


def extract_space(code: str) -> str:
    if not start_with_space(code):
        raise Exception(f"Not white space, code: {code}")
    result = ""
    for idx, char in enumerate(code):
        if char.isspace():
            result = result + char
        else:
            return code[idx:]
    return ""


def start_with_name(code: str):
    return code[0].isalnum() or code[0] == "_" or code[0] == "."


def extract_name(code: str):
    if not start_with_name(code):
        raise Exception(f"Not a valid name, code: {code}")
    result = ""
    for idx, char in enumerate(code):
        if start_with_name(char):
            result = result + char
        else:
            return Token("name", result), code[idx:]
    return Token("name", code), ""


def start_with_keyword(code: str):
    for keyword in keywords:
        if code.upper().startswith(keyword.upper()):
            # Check if keyword is followed by a non-alphanumeric character
            # This ensures we don't match "IN" in "INventory"
            next_idx = len(keyword)
            if next_idx >= len(code):
                return True
            next_char = code[next_idx]
            if not (next_char.isalnum() or next_char == "_" or next_char == "."):
                return True
    return False


def extract_keyword(code: str):
    for keyword in keywords:
        if code.upper().startswith(keyword.upper()):
            # Check if keyword is followed by a non-alphanumeric character
            next_idx = len(keyword)
            if next_idx >= len(code):
                return Token("keyword", code[: len(keyword)]), code[len(keyword) :]
            next_char = code[next_idx]
            if not (next_char.isalnum() or next_char == "_" or next_char == "."):
                return Token("keyword", code[: len(keyword)]), code[len(keyword) :]


def start_with_quoted_name(code: str):
    return code[0] == '"'


def extract_quoted_name(code: str):
    if not start_with_quoted_name(code):
        raise Exception(f"Not a valid str, code: {code}")

    enumeration = enumerate(code)
    for idx, char in enumeration:
        next_idx = idx + 1
        next_char = code[next_idx] if next_idx < len(code) else None
        if char == '"' and '"' == next_char and idx > 0:
            next(enumeration)
        elif char == '"' and next_char != '"' and idx > 0:
            value = code[1:idx].replace('""', '"')
            return Token("name", value), code[next_idx:]


def start_with_number(code: str):
    if code[0].isnumeric():
        return True


def extract_number(code: str) -> Tuple[Token, str]:
    if not start_with_number(code):
        raise Exception(f"Not a valid number, code: {code}")
    result = ""
    result_type = "int"
    for idx, char in enumerate(code):
        if char.isalnum():
            result = result + char
        elif char == "." and result_type == "int":
            result_type = "float"
        else:
            return Token(result_type, result), code[idx:]
    return Token(result_type, code), ""


def start_with_str(code: str):
    return code[0] == "'"


def extract_str(code: str):
    if not start_with_str(code):
        raise Exception(f"Not a valid str, code: {code}")

    enumeration = enumerate(code)
    for idx, char in enumeration:
        next_idx = idx + 1
        next_char = code[next_idx] if next_idx < len(code) else None
        if char == "'" and "'" == next_char and idx > 0:
            next(enumeration)
        elif char == "'" and next_char != "'" and idx > 0:
            value = code[1:idx].replace("''", "'")
            return Token("str", value), code[next_idx:]


def start_with_wildcard(code: str):
    return code[0] == "*"


def extract_wildcard(code: str):
    if not start_with_wildcard(code):
        raise Exception(f"Not a valid wildcard, code: {code}")
    return Token("wildcard", "*"), code[1:]


def scan(code: str) -> List[Token]:
    result = []
    while len(code) > 0:
        if start_with_wildcard(code):
            token, code = extract_wildcard(code)
            result.append(token)
        elif start_with_number(code):
            token, code = extract_number(code)
            result.append(token)
        elif start_with_keyword(code):
            token, code = extract_keyword(code)
            result.append(token)
        elif start_with_name(code):
            token, code = extract_name(code)
            result.append(token)
        elif start_with_quoted_name(code):
            token, code = extract_quoted_name(code)
            result.append(token)
        elif start_with_operator(code):
            token, code = extract_operator(code)
            result.append(token)
        elif start_with_str(code):
            token, code = extract_str(code)
            result.append(token)
        elif start_with_space(code):
            code = extract_space(code)
        elif code[0] == "(":
            result.append(Token("paren_left", "("))
            code = code[1:]
        elif code[0] == ")":
            result.append(Token("paren_right", ")"))
            code = code[1:]
        elif code[0] == ",":
            result.append(Token("comma", ","))
            code = code[1:]
        else:
            raise Exception(f"Invalid token, code: {code}")
    return result
