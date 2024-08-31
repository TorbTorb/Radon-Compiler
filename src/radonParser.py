from radonNodes import *

def parse(tokenList: list[Token], source:str) -> Node:
    global index_global



    def peek(offset:int = 0) -> Token:
        if 0 <= index_global + offset and index_global + offset < len(tokenList):
            return tokenList[index_global + offset]
        else:
            #print("exceeded index of token list")
            return Token(TokenType.EMPTY, len(source)-1)
            exit()

    #consume token
    def consume() -> None:
        global index_global
        index_global += 1
    

    def expect(expectedTokenType:TokenType) -> None:
        if expectedTokenType == peek().tokenType:
            consume()
            return
        print(f"Expected \"{translationDict.get(expectedTokenType)}\" before \"{translationDict.get(peek().tokenType)}\"")
        error()

    def error(errorStr:str = ""):
        index = peek().sourceIndex
        lineIndex = source[:index].count("\n")
        errorLine = source.split("\n")[lineIndex]

        indexErrorLineStart = source[:index].rfind("\n")+1
        errorIndexinLine = index-indexErrorLineStart

        print(f"Error{': ' * (errorStr != '')}{errorStr} in line {lineIndex+1}:\n{errorLine}")
        print(f"{' '*(errorIndexinLine)}^")
        exit()

    def parseRoot(rootNode: NodeStmtSeq) -> Node:
        while peek().tokenType != TokenType.EMPTY:
            rootNode.appendStmt(parseStmt())

    def parseStmtList() -> Node:
        nodes = NodeStmtSeq(peek().sourceIndex)
        while True:
            if peek().tokenType == TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE:
                consume()
                return nodes
            nodes.appendStmt(parseStmt())

    def parseStmt() -> Node:
        if peek().tokenType == TokenType.SYMBOL_SQUIGLY_BRACKET_OPEN:
            #read stmt list
            consume()
            return parseStmtList()

        elif peek().tokenType.isSpecifier(includeVoid=True):    #Declarations (variable and functions orr array or pointer lmao)
            return parseDecl()
        
        elif peek().tokenType == TokenType.IDENTIFIER:            #variable assignment or label or function call
            identifierStr = peek().value
            lineStartIndex = peek().sourceIndex
            
            if peek(1).tokenType == TokenType.SYMBOL_COLON:      #label
                expect(TokenType.IDENTIFIER)
                consume()
                return NodeLabel(lineStartIndex, identifierStr)

            elif peek(1).tokenType == TokenType.SYMBOL_PARANTHESIS_OPEN:     #function call
                funcCallNode = parseFunctionCall()
                expect(TokenType.SYMBOL_SEMICOLON)
                return funcCallNode
                                                                            #variable assignment
            elif peek(1).tokenType == TokenType.SYMBOL_SQUARE_BRACKET_OPEN:        #array indexed
                identifier = parseArrayIndex()
            else:                                                           #just var
                expect(TokenType.IDENTIFIER)
                identifier = NodeIdentifierVariable(lineStartIndex, identifierStr)

            expect(TokenType.OPERATOR_ASSIGNMENT)
            assignVal = parseExpr()
            expect(TokenType.SYMBOL_SEMICOLON)
            return NodeAssign(lineStartIndex, identifier, assignVal)
        
        elif peek().tokenType == TokenType.OPERATOR_ASTERISK:       #pointer deref assignement
            index = peek().sourceIndex
            consume()
            name = parseHighestPrio()       #maybe just peek().name     ???
            expect(TokenType.OPERATOR_ASSIGNMENT)
            val = parseExpr()
            expect(TokenType.SYMBOL_SEMICOLON)

            return NodeAssign(index, NodeDeref(index, name), val)        
        
        elif peek().tokenType == TokenType.KEYWORD_IF:      #if
            index = peek().sourceIndex
            consume()
            expect(TokenType.SYMBOL_PARANTHESIS_OPEN)
            ifCondition = parseExpr()
            expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)
            ifBody = parseStmt()
            if peek().tokenType == TokenType.KEYWORD_ELSE:  #if else
                consume()
                elseBody = parseStmt()
            else:       #only if
                elseBody = NodeEmpty(index)

            return NodeIf(index, ifCondition, ifBody, elseBody)

        elif peek().tokenType == TokenType.KEYWORD_WHILE:   #while
            index = peek().sourceIndex
            consume()
            expect(TokenType.SYMBOL_PARANTHESIS_OPEN)
            whileCondition = parseExpr()
            expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)
            whileBody = parseStmt()
            return NodeWhile(index, whileCondition, whileBody)
        
        elif peek().tokenType == TokenType.KEYWORD_DO:  #do while
            index = peek().sourceIndex
            consume()
            doWhileBody = parseStmt()
            expect(TokenType.KEYWORD_WHILE)
            doWhileCond = parseExpr()
            expect(TokenType.SYMBOL_SEMICOLON)

            return NodeDoWhile(index, doWhileCond, doWhileBody)

        elif peek().tokenType == TokenType.KEYWORD_FOR: #for else
            index = peek().sourceIndex
            consume()
            expect(TokenType.SYMBOL_PARANTHESIS_OPEN)
            
            forInit = parseVarDecl()            #declaration
            expect(TokenType.SYMBOL_SEMICOLON)
            
            forCond = parseExpr()               #condition
            expect(TokenType.SYMBOL_SEMICOLON)
            
            if peek().tokenType != TokenType.SYMBOL_PARANTHESIS_CLOSE:       #no i = i + 1 thingie
                forIncre = parseForIncrement()      #thinsg that gets executed once at end of every loop
            else:
                forIncre = NodeEmpty(index)
            expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)

            forBody = parseStmt()           #body of for loop

            if peek().tokenType == TokenType.KEYWORD_ELSE:  #else
                consume()
                forElseBody = parseStmt()
            else:       #no else
                forElseBody = NodeEmpty(index)


            return NodeFor(index, forInit, forCond, forIncre, forBody, forElseBody)
        
        elif peek().tokenType == TokenType.KEYWORD_GOTO:    #goto
            index = peek().sourceIndex
            consume()
            gotoLabel = peek().value
            expect(TokenType.IDENTIFIER)
            expect(TokenType.SYMBOL_SEMICOLON)
            return NodeGoto(index, gotoLabel)
        
        elif peek().tokenType == TokenType.KEYWORD_CONTINUE:    #continue
            index = peek().sourceIndex
            consume()
            expect(TokenType.SYMBOL_SEMICOLON)
            return NodeContinue(index)

        elif peek().tokenType == TokenType.KEYWORD_BREAK:       #break
            index = peek().sourceIndex
            consume()
            expect(TokenType.SYMBOL_SEMICOLON)
            return NodeBreak(index)
        
        elif peek().tokenType == TokenType.KEYWORD_RETURN:      #return
            index = peek().sourceIndex
            consume()
            if peek().tokenType == TokenType.SYMBOL_SEMICOLON:
                retVal = NodeEmpty(index)
            else:
                retVal = parseExpr()
            expect(TokenType.SYMBOL_SEMICOLON)
            return NodeReturn(index, retVal)
        
        else:
            error(f"Bad Token: {translationDict.get(peek().tokenType)}")


    def parseDecl() -> Node:    #just elif logic for splitting into different types
        if not peek().tokenType.isSpecifier(includeVoid=True):
            error(f"Invalid Specifier: {translationDict.get(peek().tokenType)}")
        

        if peek(1).tokenType == TokenType.OPERATOR_ASTERISK:        #pointer declare
            return parsePointerDecl()
        
        if not peek(1).tokenType == TokenType.IDENTIFIER:
            consume()   #for nicer error
            error(f"Invalid identifier name: {translationDict.get(peek().tokenType)}")
    
        if peek(2).tokenType == TokenType.SYMBOL_PARANTHESIS_OPEN:   #function
            return parseFunDecl()
        
        if peek(2).tokenType == TokenType.SYMBOL_SQUARE_BRACKET_OPEN:   #array
            return parseArrayDecl()
        
        if peek().tokenType == TokenType.SPECIFIER_VOID:        #variable with void specifier not allowed
            error("Variable with \"void\" specifier is not allowed")
        
        varDecl = parseVarDecl()
        expect(TokenType.SYMBOL_SEMICOLON)
        return varDecl   #not function so variable

    def parsePointerDecl() -> Node:
        index = peek().sourceIndex
        if peek().tokenType == TokenType.SPECIFIER_VOID:        #variable with void specifier not allowed
            error("Pointer with \"void\" specifier is not allowed")

        pointerType = peek().tokenType      #its always a specifier we checked before
        consume()

        expect(TokenType.OPERATOR_ASTERISK)
        name = peek().value
        expect(TokenType.IDENTIFIER)
        #no init for pointers (dont make no sense)

        expect(TokenType.SYMBOL_SEMICOLON)

        return NodePointerDeclaration(index, pointerType, name)


    def parseVarDecl() -> Node:
        index = peek().sourceIndex
        varType = peek().tokenType
        if not varType.isSpecifier():
            error(f"Invalid Specifier for Variable {translationDict.get(peek().tokenType)}")      #feels like triple checking but whatevah
        consume()
        varName = peek().value
        expect(TokenType.IDENTIFIER)
        if peek().tokenType == TokenType.OPERATOR_ASSIGNMENT:       #init too
            consume()
            initVal = parseExpr()
        else:                                                       #not init
            initVal = NodeEmpty(index)

        return NodeVarDeclaration(index, varType, varName, initVal)

    def parseArrayDecl() -> Node:       #this thing is a bit scuffed but its fine :>
        #n dimensional arrays #TODO
        index = peek().sourceIndex
        arrayType = peek().tokenType
        if arrayType == TokenType.SPECIFIER_VOID:
            error("array of void is invalid")
        elif not arrayType.isSpecifier():
            expect(TokenType.SPECIFIER_GENERAL)    #for nice error msg
        consume()
        arrayID = peek().value
        expect(TokenType.IDENTIFIER)
        expect(TokenType.SYMBOL_SQUARE_BRACKET_OPEN)

        if peek().tokenType == TokenType.LITERAL_INT:       #manual size
            arraySize = int(peek().value)     #TODO parse const expr for array size
            autoSize = False
            consume()       #checked that its int
        else:
            arraySize = 0
            autoSize = True
        
        expect(TokenType.SYMBOL_SQUARE_BRACKET_CLOSE)
        

        if peek().tokenType == TokenType.OPERATOR_ASSIGNMENT:       #initialized array
            consume()
            initList = parseArrayInit(arrayType)
            if autoSize:        #set automatic size
                arraySize = len(initList)
            else:       #pad with 0s
                if arrayType == TokenType.SPECIFIER_CHAR:
                    initList += [NodeLiteralChar(index, "\0")] * (arraySize - len(initList))
                elif arrayType == TokenType.SPECIFIER_INT:
                    initList += [NodeLiteralInt(index, "0")] * (arraySize - len(initList))
                elif arrayType == TokenType.SPECIFIER_FLOAT:
                    initList += [NodeLiteralFloat(index, "0.0")] * (arraySize - len(initList))

        else:
            if autoSize:       #auto size but not initilazed
                error("Cant have uninitilazed array with automatic size")
            initList = []

        if len(initList) > int(arraySize):      # too many inits wtf
            error("Too many initalizations for array")


        expect(TokenType.SYMBOL_SEMICOLON)
        arrayObj = NodeArrayDeclaration(index, arrayType, arrayID, arraySize, initList)
        print(arrayObj)
        return arrayObj



    def parseArrayInit(arrayType:TokenType) -> list[Node]:        #returns a list of nodes used to init array
        index = peek().sourceIndex
        initList: list[Node] = []
        if arrayType == TokenType.SPECIFIER_CHAR:       #array of chars: speak string
                #either string init or sequence of chars
            if peek().tokenType == TokenType.LITERAL_STRING:      #init with "xyz"
                initString = peek().value
                consume()
                return [NodeLiteralChar(index, char) for char in initString] + [NodeLiteralChar(index, "\0")]     #null terminator
                
            #init with squigly BRackets
            expect(TokenType.SYMBOL_SQUIGLY_BRACKET_OPEN)
            while peek().tokenType != TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE:   #bit scuffed logic tbh
                initList.append(NodeLiteralChar(index, peek().value))
                expect(TokenType.LITERAL_CHAR)

                if peek().tokenType == TokenType.SYMBOL_COMMA:
                    consume()
                else:
                    break
            initList += [NodeLiteralChar(index, "\0")]      #null terminator
        elif arrayType.isSpecifier():

            #init with squigly BRackets
            expect(TokenType.SYMBOL_SQUIGLY_BRACKET_OPEN)
            while peek().tokenType != TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE:   #bit scuffed logic tbh
                initList.append(parseExpr())

                if peek().tokenType == TokenType.SYMBOL_COMMA:
                    consume()
                else:
                    break
        else:
            error(f"Array of type: {arrayType} is not allowed")     #poterntally unreachable

        
        if peek().tokenType != TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE:
            expect(TokenType.SYMBOL_SQUIGLY_BRACKET_CLOSE)      #for error msg
        consume()       #string litreals init returns early
        #dont consume yet for nice error messages but its checked so we can consume without expecting
        return initList



    def parseFunDecl() -> Node:
        #TODO   #allow array and pointers as args
        index = peek().sourceIndex
        returnType = peek().tokenType
        if not returnType.isSpecifier(includeVoid=True):
            error(f"Invalid Specifier for Function: {translationDict.get(peek().tokenType)}")      #feels like triple checking but whatevah
        consume()
        funName = peek().value
        expect(TokenType.IDENTIFIER)
        expect(TokenType.SYMBOL_PARANTHESIS_OPEN)

        if not peek().tokenType == TokenType.SYMBOL_PARANTHESIS_CLOSE:      #non empty arguments list
            funDeclList = parseDeclList()
        else:
            funDeclList = NodeDeclarationList(peek().sourceIndex)

        expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)
        funBody = parseStmt()

        return NodeFunDeclaration(index, returnType, funName, funDeclList, funBody)

    def parseDeclList() -> Node:
        #checking whether decl list is not empty needs to be sepeartely done
        index = peek().sourceIndex
        declList = NodeDeclarationList(index)
        optional = False
        while True:
            if peek(2).tokenType == TokenType.OPERATOR_ASSIGNMENT:
                optional = True     #default value provided, from now on every arg has to be defaulted

            if optional and peek(2).tokenType != TokenType.OPERATOR_ASSIGNMENT:     #non defaulted arg after defaulted arg
                error("Non-default argument follows default argument")


            
            declList.appendDecl(parseVarDecl())     # #TODO just do parse decl here?? potentially remove functions tho xd
            if not peek().tokenType == TokenType.SYMBOL_COMMA:
                return declList
            expect(TokenType.SYMBOL_COMMA)   #consume the comma

    def parseForIncrement() -> Node:
        index = peek().sourceIndex
        name = peek().value
        expect(TokenType.IDENTIFIER)
        expect(TokenType.OPERATOR_ASSIGNMENT)
        expr = parseExpr()
        return NodeAssign(index, NodeIdentifierVariable(index, name), expr)

    def parseArgList() -> Node:
        index = peek().sourceIndex
        #checking whether arg list is not empty needs to be sepeartely done
        argList = NodeExprList(index)
        while True:
            argList.appendExpr(parseExpr())
            if not peek().tokenType == TokenType.SYMBOL_COMMA:
                return argList
            expect(TokenType.SYMBOL_COMMA)   #consume the comma

    def parseFunctionCall() -> Node:
        index = peek().sourceIndex
        name = peek().value
        expect(TokenType.IDENTIFIER)      ##unnecesasy ig whatevs
        expect(TokenType.SYMBOL_PARANTHESIS_OPEN) #same
        if not peek().tokenType == TokenType.SYMBOL_PARANTHESIS_CLOSE:  #non empty arg list
            argList = parseArgList()
        else:
            argList = NodeExprList(peek().sourceIndex)

        expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)
        return NodeFuncCall(index, name, argList)


    def parseArrayIndex() -> Node:
        index = peek().sourceIndex
        nameA = peek().value
        expect(TokenType.IDENTIFIER)
        expect(TokenType.SYMBOL_SQUARE_BRACKET_OPEN)
        indexB = parseExpr()
        expect(TokenType.SYMBOL_SQUARE_BRACKET_CLOSE)
        # a[b] = *(a+b)
        return NodeDeref(index, NodeTwoOp(index, NodeIdentifierVariable(index, nameA), TokenType.OPERATOR_PLUS, indexB))



    #TODO: refactor to use nicer priority system like wtf is this rn
    def parseExpr() -> Node:     #lowest precednce operators (logical statemtn stuff)
        left = parseLowPrio()
        index = peek().sourceIndex
        while True:
            if peek().tokenType == TokenType.OPERATOR_DOUBLE_CIRCUMFLEX:
                consume()
                right = parseLowPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_DOUBLE_CIRCUMFLEX, right)
            elif peek().tokenType == TokenType.OPERATOR_DOUBLE_AMPERSAND:
                consume()
                right = parseLowPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_DOUBLE_AMPERSAND, right)
            elif peek().tokenType == TokenType.OPERATOR_DOUBLE_PIPE:
                consume()
                right = parseLowPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_DOUBLE_PIPE, right)
            else:
                return left

    
    def parseLowPrio() -> Node:       #low precednce operators (comparison operators)
        left = parseMediumPrio()
        index = peek().sourceIndex
        while True:
            if peek().tokenType == TokenType.OPERATOR_EQUAL:
                consume()
                right = parseMediumPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_EQUAL, right)
            elif peek().tokenType == TokenType.OPERATOR_LESS:
                consume()
                right = parseMediumPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_LESS, right)
            elif peek().tokenType == TokenType.OPERATOR_GREATER:
                consume()
                right = parseMediumPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_GREATER, right)
            elif peek().tokenType == TokenType.OPERATOR_LESS_EQUAL:
                consume()
                right = parseMediumPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_LESS_EQUAL, right)
            elif peek().tokenType == TokenType.OPERATOR_GREATER_EQUAL:
                consume()
                right = parseMediumPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_GREATER_EQUAL, right)
            elif peek().tokenType == TokenType.OPERATOR_NOT_EQUAL:
                consume()
                right = parseMediumPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_NOT_EQUAL, right)
            else:
                return left
            
    def parseMediumPrio() -> Node:  #medium precednce operators         (+ - bitwise)
        left = parseHighPrio()
        index = peek().sourceIndex
        while True:
            if peek().tokenType == TokenType.OPERATOR_PLUS:
                consume()
                right = parseHighPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_PLUS, right)
            elif peek().tokenType == TokenType.OPERATOR_MINUS:
                consume()
                right = parseHighPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_MINUS, right)
            elif peek().tokenType == TokenType.OPERATOR_AMPERSAND:
                consume()
                right = parseHighPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_AMPERSAND, right)
            elif peek().tokenType == TokenType.OPERATOR_PIPE:
                consume()
                right = parseHighPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_PIPE, right)
            elif peek().tokenType == TokenType.OPERATOR_CIRCUMFLEX:
                consume()
                right = parseHighPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_CIRCUMFLEX, right)
            
            else:
                return left

    def parseHighPrio() -> Node:     #high precende operators       (* / % & | ^)
        left = parseHighestPrio()
        index = peek().sourceIndex
        while True:
            if peek().tokenType == TokenType.OPERATOR_ASTERISK:
                consume()
                right = parseHighestPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_ASTERISK, right)
            elif peek().tokenType == TokenType.OPERATOR_SLASH:
                consume()
                right = parseHighestPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_SLASH, right)
            elif peek().tokenType == TokenType.OPERATOR_MODULO:
                consume()
                right = parseHighestPrio()
                left = NodeTwoOp(index, left, TokenType.OPERATOR_MODULO, right)
            else:
                return left

    def parseHighestPrio() -> Node:  #highest precedence operators (infix stuff)
        index = peek().sourceIndex
        if peek().tokenType == TokenType.SYMBOL_PARANTHESIS_OPEN:       #expr in para or type cast
            consume()
            if peek().tokenType.isSpecifier():      #type cast
                toType = peek().tokenType
                consume()
                expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)
                arg = parseHighestPrio()
                return NodeTypeCast(index, toType, arg)
            expr = parseExpr()
            expect(TokenType.SYMBOL_PARANTHESIS_CLOSE)
            return expr
        elif peek().tokenType == TokenType.OPERATOR_ASTERISK:       #deref
            consume()
            arg = parseHighestPrio()
            return NodeDeref(index, arg)
        elif peek().tokenType == TokenType.OPERATOR_AMPERSAND:      #address of
            consume()
            arg = parseHighestPrio()
            return NodeAddrOf(index, arg)
        elif peek().tokenType == TokenType.OPERATOR_EXCLAMATION:       #logical not
            consume()
            arg = parseHighestPrio()
            return NodeOneOp(index, TokenType.OPERATOR_EXCLAMATION, arg)
        elif peek().tokenType == TokenType.OPERATOR_TILDE:          #bitwise not
            consume()
            arg = parseHighestPrio()
            return NodeOneOp(index, TokenType.OPERATOR_TILDE, arg)
        elif peek().tokenType == TokenType.OPERATOR_MINUS:          #negateve
            consume()
            arg = parseHighestPrio()
            return NodeOneOp(index, TokenType.OPERATOR_MINUS, arg)
        elif peek().tokenType == TokenType.OPERATOR_PLUS:     #unnecesary plus
            consume()
            arg = parseHighestPrio()
            return arg
        elif peek().tokenType == TokenType.IDENTIFIER:            #ident or funct call orrr array indexing
            name = peek().value
            if peek(1).tokenType == TokenType.SYMBOL_PARANTHESIS_OPEN:       #function
                return parseFunctionCall()
            elif peek(1).tokenType == TokenType.SYMBOL_SQUARE_BRACKET_OPEN:     #array indexing
                return parseArrayIndex()
            else:                                                              #normal var
                consume()
                return NodeIdentifierVariable(index, name)
        elif peek().tokenType == TokenType.LITERAL_INT:     #literal int
            literal = NodeLiteralInt(index, peek().value)
            consume()
            return literal
        elif peek().tokenType == TokenType.LITERAL_FLOAT:     #literal float
            literal = NodeLiteralFloat(index, peek().value)
            consume()
            return literal
        elif peek().tokenType == TokenType.LITERAL_STRING:     #literal string
            literal = NodeLiteralString(index, peek().value)
            consume()
            return literal
        elif peek().tokenType == TokenType.LITERAL_CHAR:     #literal char
            literal = NodeLiteralChar(index, peek().value)
            consume()
            return literal
        
        else:
            error(f"Invalid Expression: {translationDict.get(peek().tokenType)}")




    index_global = 0
    rootNode = NodeStmtSeq(0)
    parseRoot(rootNode)
    return rootNode