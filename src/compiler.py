# radon compiler
import radonFileInput
import radonParser
import radonTokenizer
import radonNodes
import radonAssembler





def main():
    source, fileName = radonFileInput.readFiletoStr()

    #preprocess



                                                        #tokenize
    tokens = radonTokenizer.tokenize(source)
    print("Tokenizer Success")
    #[token.print() for token in res]
    #[print(token) for token in tokens]
                                                        #parse
    rootNode = radonParser.parse(tokens, source)
    print("Parser Success")
    #print(rootNode)
    #radonNodes.printTree(rootNode)
                                                        #semantic analysis, link jumps and put type information on operations
    radonNodes.semanticAnalysis(rootNode, source)
    radonNodes.printTree(rootNode)
    print("Semantic Analysis Success\n")
    #print(radonNodes.SymbolTable._symbolTable.__str__())
    #print(rootNode)
                                                        #synthesize (ast to asm)
    asm = radonNodes.toAssembly(rootNode, -1000)     #stack grows downwards, watch out with immediates i hate
    print(asm)


    #assemble
    radonAssembler.assemble(asm.split("\n"), f"{fileName}.schem")
    
    print("Done")




if __name__ == "__main__":
    main()