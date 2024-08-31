from radonTokens import *
from sys import exit
def tokenize(source:str) -> list[Token]:
    #helper? functions
    #get char at pos of index
    def peek(offset:int = 0) -> str:
        if 0 <= index_global + offset and index_global + offset < len(source):
            return source[index_global + offset]
        else:
            #print("exceeded index of source string")
            return ""

    #consume read character
    def consume() -> None:
        global index_global
        index_global += 1

    def expect(char:str) -> None:
        if char == peek():
            consume()
            return
        print(f"Expected character {char} before {peek()} :(")
        error("")
        exit()

    def error(errorStr) -> None:
        lineIndex = source[:index_global].count("\n")
        errorLine = source.split("\n")[lineIndex]

        indexErrorLineStart = source[:index_global].rfind("\n")
        errorIndexinLine = index_global-indexErrorLineStart
        
        print(f"Tokenizer Error: {errorStr} in line {lineIndex}:\n{errorLine}")
        print(f"{' '*(errorIndexinLine-1)}^")
        exit()

    tokenList = []
    global index_global
    index_global = 0

    while index_global < len(source):
        if peek().isspace():
            consume()
            continue
        elif peek() == "/" and peek(1) == "/": #comment
            while not (peek() == "\n" or peek() == "") :
                consume()
            continue
        elif peek().isalpha():  #keywords, names, identifiers
            buffer = ""
            while peek().isalnum() or peek() == "_":
                buffer += peek()
                consume()
            match buffer:       #keyword match case
                case "if":
                    tokenList.append(Token(TokenType.KEYWORD_IF, index_global - len(buffer)))
                case "else":
                    tokenList.append(Token(TokenType.KEYWORD_ELSE, index_global - len(buffer)))
                case "do":
                    tokenList.append(Token(TokenType.KEYWORD_DO, index_global - len(buffer)))
                case "for":
                    tokenList.append(Token(TokenType.KEYWORD_FOR, index_global - len(buffer)))
                case "while":
                    tokenList.append(Token(TokenType.KEYWORD_WHILE, index_global - len(buffer)))
                case "goto":
                    tokenList.append(Token(TokenType.KEYWORD_GOTO, index_global - len(buffer)))
                case "continue":
                    tokenList.append(Token(TokenType.KEYWORD_CONTINUE, index_global - len(buffer)))
                case "break":
                    tokenList.append(Token(TokenType.KEYWORD_BREAK, index_global - len(buffer)))
                case "return":
                    tokenList.append(Token(TokenType.KEYWORD_RETURN, index_global - len(buffer)))
                case "void":
                    tokenList.append(Token(TokenType.SPECIFIER_VOID, index_global - len(buffer)))
                case "int":
                    tokenList.append(Token(TokenType.SPECIFIER_INT, index_global - len(buffer)))
                case "float":
                    tokenList.append(Token(TokenType.SPECIFIER_FLOAT, index_global - len(buffer)))
                #case "string":
                #    tokenList.append(Token(TokenType.SPECIFIER_STRING, index_global - len(buffer)))
                case "char":
                    tokenList.append(Token(TokenType.SPECIFIER_CHAR, index_global - len(buffer)))
                case _: #variable or function name
                    tokenList.append(Token(TokenType.IDENTIFIER, index_global - len(buffer), buffer))
            continue
        elif peek().isnumeric():    #int/float literal
            buffer = ""
            while peek().isnumeric() or peek() == "." or peek() == "_":     #ignore underscore
                buffer += peek()
                consume()
            
            if buffer.count(".") == 1:   #float literal
                tokenList.append(Token(TokenType.LITERAL_FLOAT, index_global - len(buffer), buffer))
            elif buffer.count(".") == 0:       #int literal
                tokenList.append(Token(TokenType.LITERAL_INT, index_global - len(buffer), buffer))
            else:
                error("Invalid Number Literal")
            continue
        elif peek() == "\"":        #string literal
            buffer = ""
            consume()       #dont include qoutes in string

            while not peek() == "\"":
                if index_global > len(source):
                    error("Unterminated string")
                if peek() == "\\":  #next char is escaped
                    match peek(1):
                        case "0": buffer += "\0"
                        case "t": buffer += "\t"
                        case "b": buffer += "\b"
                        case "n": buffer += "\n"
                        case "r": buffer += "\r"
                        case "f": buffer += "\f"
                        case "s": buffer += "\s"
                        case "'": buffer += "\'"
                        case "\"": buffer += "\""
                        case "\\": buffer += "\\"
                        case _:
                            buffer += "\\"
                            consume()
                            continue
                    consume()
                    consume()
                    continue
                buffer += peek()
                consume()

            
            expect("\"") # consume end qoute
            tokenList.append(Token(TokenType.LITERAL_STRING, index_global - len(buffer)-2, buffer))     ###################-2? - 1
            continue
        elif peek() == "\'":        #char literal
            buffer = ""
            consume()       #dont include qoutes in string
            if peek() == "\\":  #char is raw
                match peek(1):
                    case "0": buffer = "\0"
                    case "t": buffer = "\t"
                    case "b": buffer = "\b"
                    case "n": buffer = "\n"
                    case "r": buffer = "\r"
                    case "f": buffer = "\f"
                    case "s": buffer = "\s"
                    case "'": buffer = "\'"
                    case "\"": buffer = "\""
                    case "\\": buffer = "\\"
                    case _:
                        error("Invalid Char litreal with escape character (use '\\\\' if you want to have '\\')")
                consume()
            else:
                buffer = peek()
            consume()
            expect("\'")
            tokenList.append(Token(TokenType.LITERAL_CHAR, index_global - len(buffer) - 2, buffer))         #-2?
            continue
        match peek():   #huge symbol and operator match case
            case "(":
                tokenList.append(Token(TokenType.SYMBOL_PARANTHESIS_OPEN, index_global))
            case ")":
                tokenList.append(Token(TokenType.SYMBOL_PARANTHESIS_CLOSE, index_global))
            case "[":
                tokenList.append(Token(TokenType.SYMBOL_SQUARE_BRACKET_OPEN, index_global))
            case "]":
                tokenList.append(Token(TokenType.SYMBOL_SQUARE_BRACKET_CLOSE, index_global))
            case "{":
                tokenList.append(Token(TokenType.SYMBOL_SQUIGLY_BRACKET_OPEN, index_global))
            case "}":
                tokenList.append(Token(TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE, index_global))
            case ";":
                tokenList.append(Token(TokenType.SYMBOL_SEMICOLON, index_global))
            case ":":
                tokenList.append(Token(TokenType.SYMBOL_COLON, index_global))
            case ",":
                tokenList.append(Token(TokenType.SYMBOL_COMMA, index_global))
            case "+":
                tokenList.append(Token(TokenType.OPERATOR_PLUS, index_global))
            case "-":
                tokenList.append(Token(TokenType.OPERATOR_MINUS, index_global))
            case "*":
                tokenList.append(Token(TokenType.OPERATOR_ASTERISK, index_global))
            case "/":
                tokenList.append(Token(TokenType.OPERATOR_SLASH, index_global))
            case "%":
                tokenList.append(Token(TokenType.OPERATOR_MODULO, index_global))
            case "&":
                if peek(1) == "&":   #logical and
                    tokenList.append(Token(TokenType.OPERATOR_DOUBLE_AMPERSAND, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_AMPERSAND, index_global))
            case "|":
                if peek(1) == "|":   #logical or
                    tokenList.append(Token(TokenType.OPERATOR_DOUBLE_PIPE, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_PIPE, index_global))
            case "!":
                if peek(1) == "=":   # not equals operator (!=)
                    tokenList.append(Token(TokenType.OPERATOR_NOT_EQUAL, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_EXCLAMATION, index_global))

            case "~":
                tokenList.append(Token(TokenType.OPERATOR_TILDE, index_global))
            case "^":
                if peek(1) == "&":   #logical xor
                    tokenList.append(Token(TokenType.OPERATOR_DOUBLE_CIRCUMFLEX, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_CIRCUMFLEX, index_global))
            case "=":
                if peek(1) == "=":   # equals operator (==)
                    tokenList.append(Token(TokenType.OPERATOR_EQUAL, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_ASSIGNMENT, index_global))

                
            case "<":
                if peek(1) == "=":   # lteq operator (<=)
                    tokenList.append(Token(TokenType.OPERATOR_LESS_EQUAL, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_LESS, index_global))
            case ">":
                if peek(1) == "=":   # gteq operator (>=)
                    tokenList.append(Token(TokenType.OPERATOR_GREATER_EQUAL, index_global))
                    consume()
                else:
                    tokenList.append(Token(TokenType.OPERATOR_GREATER, index_global))
            case _:
                if not peek().isspace():    #should be unnecesary
                    error(f"invalid Character: {peek()}")
                    exit()
        consume() #consume char read in match case

    return tokenList