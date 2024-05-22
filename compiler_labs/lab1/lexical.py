import sys
import re
from enum import Enum
import warnings
from rich.logging import RichHandler
import logging

logger = logging.getLogger('rich')
# logger.setLevel(logging.INFO)
# rich_handler = RichHandler()
# logger.addHandler(rich_handler)


class _TOKEN_TYPE(Enum):
    KEYWORD      = 1
    DELIMITER    = 2
    IDENTIFIER   = 3
    NUMBER       = 4
    STRING       = 5
    OPERATOR     = 6
    CHAR         = 7

class Token:
    def __init__(self, type, value) -> None:
        self.type = type
        self.value = value

    """ Customized string representation of the token """
    def __str__(self) -> str:
       match self.type:
            case _TOKEN_TYPE.KEYWORD:
                return f"<{self.value}>"
            case _TOKEN_TYPE.DELIMITER:
                return f"<{self.value}>"
            case _TOKEN_TYPE.IDENTIFIER:
                return f"<id, {self.value}>"
            case _TOKEN_TYPE.NUMBER:
                return f"<num, {self.value}>"
            case _TOKEN_TYPE.STRING:
                return "<str, {}>".format(self.value)
            case _TOKEN_TYPE.OPERATOR:
                return f"<{self.value}>"
            case _TOKEN_TYPE.CHAR:
                return f"<{self.value}>"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, o: object) -> bool:
        return self.type == o.type and self.value == o.value

class LexicalParser:
    """ Lexical parser for C language 
    
    Attributes:
    code (str): the code to be parsed
    tokens (list): list of tokens
    
    Usage:
    parser = LexicalParser(code)
    tokens = parser.parse()
    for token in tokens:
        print(token)

    """
    
    """ Define the keywords, delimiters, operators, etc."""
    _keywords = [
            # data types
            "int", "float", "double", "char", "void",
            # control statements
            "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "return",
            # modifiers
            "const", "static", "extern", "register", "auto", "volatile",
            # storage classes
            "typedef", "struct", "union", "enum",
            # constants
            "true", "false", "NULL",
        ]
    
    """ supported character sets """
    _delimiters = ["(", ")", "{", "}", "[", "]", ";", ",", ".", ":"]
    _single_char_operators = ["+", "-", "*", "/", "%", "=", "!", "&", "|", "^", "~", "<", ">", "?"]
    _double_char_operators = ["++", "--", "==", "!=", "<=", ">=", "&&", "||", "<<", ">>", "->"]

    """ Define the regex patterns for parsing """
    _number_pattern =                   re.compile(r"[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?")
    _string_pattern =                   re.compile(r'"[^"]*[^\n]"')
    _unfinished_string_pattern =        re.compile(r'"[^"]*[\n]')
    _identifier_pattern =               re.compile(r"[a-zA-Z_][a-zA-Z_0-9]*")
    _char_pattern =                     re.compile(r"'.'")
    _unfinished_char_pattern =          re.compile(r"'.[\n]")
    _new_line_pattern =                 re.compile('\n')
    _preprocessor_pattern =             re.compile(r"#.*")
    _comment_pattern =                  re.compile(r"//.*")
    _multi_line_comment_pattern =       re.compile(r"/\*.*?\*/", re.DOTALL)
    
    def __init__(self, code: str) -> None:
        """ Initialize the parser with the code to be parsed
        
        Args:
        code (str): the code to be parsed
        
        """
        self.code = code
        self.tokens = []
        
    def parse(self):
        code = self.code
        
        # Preprocess the code
        # Remove preprocessor and comments in the code
        code = re.sub(self._preprocessor_pattern, "", code)
        code = re.sub(self._comment_pattern, "", code)
        code = re.sub(self._multi_line_comment_pattern, "", code)
        
        lines = code.split("\n")
        for index, line in enumerate(lines):
            # print(f"Line {index}: {line}")
            parser = self.generator(line)
            try:
                tokens = list(parser)
            except SyntaxWarning as e:
                logger.error(f'Error in "{line}" \nError at line {index} index {e.args[2]}: {e.args[0]} {e.args[1]}')
                continue
            self.tokens += tokens
            
        return self.tokens
        
    def generator(self, buffer: str):
        # Scan the code and generate tokens
        i = 0
        n = len(buffer)
        while i < n:
            ch = buffer[i]
            i += 1
            # print(code[i-1:])
            if ch.isspace():
                continue
            if ch in self._delimiters:
                yield Token(_TOKEN_TYPE.DELIMITER, ch)
            elif ch in self._single_char_operators:
                # check if double char operator
                if i < n and ch + buffer[i] in self._double_char_operators:
                    yield Token(_TOKEN_TYPE.OPERATOR, ch + buffer[i])
                    i += 1
                else:
                    yield Token(_TOKEN_TYPE.OPERATOR, ch)
                    
            # Check for string
            elif ch == '"':
                match = re.match(self._string_pattern, buffer[i-1:])
                if match:
                    yield Token(_TOKEN_TYPE.STRING, match.group())
                    i += len(match.group()) - 1
                else:
                    match = re.search('\n', buffer[i-1:])
                    if match:
                        raise SyntaxWarning("Unfinished string", buffer[i-1:match.end()], i)
                        i += match.end() - 1
                    
            # Check for character
            elif ch == "'":
                match = re.match(self._char_pattern, buffer[i-1:])
                if match:
                    yield Token(_TOKEN_TYPE.CHAR, match.group())
                    i += len(match.group()) - 1
                else:
                    match = re.search('\n', buffer[i-1:])
                    if match:
                        raise SyntaxWarning("Unfinished char", buffer[i-1:match.end()], i)
                        i += match.end() - 1
                        
            # Check for number
            elif ch.isdigit():
                match = re.match(self._number_pattern, buffer[i-1:])
                if match:
                    yield Token(_TOKEN_TYPE.NUMBER, match.group())
                    i += len(match.group()) - 1
                    
            # Check for identifier
            elif ch.isalpha() or ch == "_":
                match = re.match(self._identifier_pattern, buffer[i-1:])
                if match:
                    word = match.group()
                    word = word.lower()
                    if word in self._keywords:
                        yield Token(_TOKEN_TYPE.KEYWORD, word)
                    else:
                        yield Token(_TOKEN_TYPE.IDENTIFIER, word)
                    i += len(match.group()) - 1
            else:
                raise SyntaxWarning("Unknown character", ch, i)


if __name__ == "__main__":
    """ Simple test driver 
    Usage:
    python lexical.py < test.c
    
    """
    
    with open("./tmp/input") as f:
        code = f.read()
    parser = LexicalParser(code)
    tokens = parser.parse()
    for token in tokens:
        print(token)