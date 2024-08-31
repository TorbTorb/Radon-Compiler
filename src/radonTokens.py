from enum import Enum, auto


#keywords: int float char string void if else for while goto continue break return

class TokenType(Enum):

    EMPTY = auto()
    #literals
    LITERAL_INT = auto()
    LITERAL_FLOAT = auto()
    LITERAL_CHAR = auto()
    LITERAL_STRING = auto()

    #Identifires
    SPECIFIER_VOID = auto()
    SPECIFIER_INT = auto()
    SPECIFIER_FLOAT = auto()
    SPECIFIER_CHAR = auto()
    SPECIFIER_STRING = auto()      #strings still allowed but not as type only for operations
    SPECIFIER_GENERAL = auto()      #for error messages and compund pointer deref cause we cant infer type then #TODO

    #keywords
    KEYWORD_IF = auto()
    KEYWORD_ELSE = auto()
    KEYWORD_DO = auto()
    KEYWORD_FOR = auto()
    KEYWORD_WHILE = auto()
    KEYWORD_GOTO = auto()
    KEYWORD_CONTINUE = auto()
    KEYWORD_BREAK = auto()
    KEYWORD_RETURN = auto()

    #symbols
    SYMBOL_PARANTHESIS_OPEN = auto()
    SYMBOL_PARANTHESIS_CLOSE = auto()
    SYMBOL_SQUARE_BRACKET_OPEN = auto()
    SYMBOL_SQUARE_BRACKET_CLOSE = auto()
    SYMBOL_SQUIGLY_BRACKET_OPEN = auto()
    SYMBOL_SQUIGLY_BRACKET_CLOSE = auto()
    SYMBOL_SEMICOLON = auto()
    SYMBOL_COLON = auto()
    SYMBOL_COMMA = auto()

    #operators
    OPERATOR_PLUS = auto()
    OPERATOR_MINUS = auto()
    OPERATOR_ASTERISK = auto()
    OPERATOR_SLASH = auto()
    OPERATOR_MODULO = auto()
    OPERATOR_AMPERSAND = auto()
    OPERATOR_DOUBLE_AMPERSAND = auto()
    OPERATOR_PIPE = auto()
    OPERATOR_DOUBLE_PIPE = auto()
    OPERATOR_EXCLAMATION = auto()
    OPERATOR_TILDE = auto()
    OPERATOR_CIRCUMFLEX = auto()# ^
    OPERATOR_DOUBLE_CIRCUMFLEX = auto() #^^       #why not lmao
    OPERATOR_LEFTSHIFT = auto()
    OPERATOR_RIGHTSHIFT = auto()        #aithmateic vs logical???

    OPERATOR_ASSIGNMENT = auto() #=
    OPERATOR_EQUAL = auto()
    OPERATOR_NOT_EQUAL = auto()
    OPERATOR_LESS = auto()
    OPERATOR_GREATER = auto()
    OPERATOR_LESS_EQUAL = auto()
    OPERATOR_GREATER_EQUAL = auto()

    #names
    IDENTIFIER = auto()


    def isSpecifier(self, includeVoid:bool = False):
        if includeVoid and self == TokenType.SPECIFIER_VOID:
            return True
        return self in [TokenType.SPECIFIER_CHAR, TokenType.SPECIFIER_FLOAT, TokenType.SPECIFIER_INT]


translationDict:dict[TokenType:str] = {
    TokenType.EMPTY: "<Empty Token> (most likely EoF)",
    TokenType.LITERAL_INT: f"<Int Literal Token>" ,
    TokenType.LITERAL_FLOAT: f"<Float Literal Token>",
    TokenType.LITERAL_CHAR: f"<Char Literal Token>",
    TokenType.LITERAL_STRING: f"<String Literal Token>",        #string literals are still allowed cause of char array init
    TokenType.SPECIFIER_VOID: "void",
    TokenType.SPECIFIER_INT: "int",
    TokenType.SPECIFIER_FLOAT: "float",
    TokenType.SPECIFIER_CHAR: "char",
    TokenType.SPECIFIER_GENERAL: "<Specifier>",
    TokenType.KEYWORD_IF: "if",
    TokenType.KEYWORD_ELSE: "else",
    TokenType.KEYWORD_DO: "do",
    TokenType.KEYWORD_FOR: "for",
    TokenType.KEYWORD_WHILE: "while",
    TokenType.KEYWORD_GOTO: "goto",
    TokenType.KEYWORD_CONTINUE: "continue",
    TokenType.KEYWORD_BREAK: "break",
    TokenType.KEYWORD_RETURN: "return",
    TokenType.SYMBOL_PARANTHESIS_OPEN: "(",
    TokenType.SYMBOL_PARANTHESIS_CLOSE: ")",
    TokenType.SYMBOL_SQUARE_BRACKET_OPEN: "[",
    TokenType.SYMBOL_SQUARE_BRACKET_CLOSE: "]",
    TokenType.SYMBOL_SQUIGLY_BRACKET_OPEN: "{",
    TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE: "}",
    TokenType.SYMBOL_COMMA: ",",
    TokenType.SYMBOL_COLON: ":",
    TokenType.SYMBOL_SEMICOLON: ";",

    TokenType.OPERATOR_PLUS: "+",
    TokenType.OPERATOR_MINUS: "-",
    TokenType.OPERATOR_ASTERISK: "*",
    TokenType.OPERATOR_SLASH: "/",
    TokenType.OPERATOR_MODULO: "%",

    TokenType.OPERATOR_AMPERSAND: "&",
    TokenType.OPERATOR_DOUBLE_AMPERSAND: "&&",
    TokenType.OPERATOR_PIPE: "|",
    TokenType.OPERATOR_DOUBLE_PIPE: "||",
    TokenType.OPERATOR_EXCLAMATION: "!",
    TokenType.OPERATOR_TILDE: "~",
    TokenType.OPERATOR_CIRCUMFLEX: "^",
    TokenType.OPERATOR_DOUBLE_CIRCUMFLEX: "^^",
    TokenType.OPERATOR_LEFTSHIFT: "<<",
    TokenType.OPERATOR_RIGHTSHIFT: ">>",
    TokenType.OPERATOR_ASSIGNMENT: "=",

    TokenType.OPERATOR_EQUAL: "==",
    TokenType.OPERATOR_NOT_EQUAL: "!=",
    TokenType.OPERATOR_LESS: "<",
    TokenType.OPERATOR_GREATER: ">",
    TokenType.OPERATOR_LESS_EQUAL: "<=",
    TokenType.OPERATOR_GREATER_EQUAL: ">=",

    TokenType.IDENTIFIER: "<Identifier Token>",

}


class Token:
    def __init__(self, tokenType:TokenType, sourceIndex:int, value:str|None = None, rightType:TokenType|None = None, leftType:TokenType|None = None):
        self.tokenType:TokenType = tokenType
        self.sourceIndex: int = sourceIndex
        self.value:str|None = value
        self.rightType: TokenType|None = rightType
        self.leftType: TokenType|None = leftType
    def __str__(self):
        return f"Token of type {self.tokenType.name} at Index {self.sourceIndex}{f' with value of: {self.value}' * (self.value != None)}"


