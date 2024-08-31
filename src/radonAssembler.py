import easygui
import copy
import radonListToSchem      #own file
import os.path
import simpleeval       #pip install simpleeval

# Torb 10.3.2024 Assembler for minecraft //g cpu

# basic syntax:
# <opcode> <src1> <src2> <dest>
# use '.' for labels                        ~line 256 for more detail
# use '$' for immediates                    ~line 420
# use '&' and '*' for "pointer" stuff       ~line 263
# use '#' for comments (like python :3)
# 'PC' is predefined
# '._start' is where the program starts executing and required

def strToNum(stringIn):
    if "." in stringIn:
        return float(stringIn)
    return int(stringIn, base = 0)

def assemble(codeRaw:str, savePath:str):
    #print(__file__)
    baseDir = f"{os.path.dirname(__file__)}\\std\\"     #directory for "standard library"
    #instrOrder = [0, 3, 1, 2]       #i c a b       #just reorder everything else tbh so asm is like opcode dest a b

    INSTRUCTIONS = {"POW": {"-1", "Arithmetic"}, "ADD": ("0", "Arithmetic"), "SUB": ("1", "Arithmetic"), "MUL": ("2", "Arithmetic"), "DIV": ("3", "Arithmetic"), 
                    "MOD": ("4", "Arithmetic"), "_GET": ("5", "Pointer"), "CMOVLTZ": ("6", "Conditional"), "CMOVZ": ("7", "Conditional"),
                    "_WAIT": ("8", "Wait"), "_MOVTO": ("9", "Pointer")}     #change _wait to -1 could save a char too (i < 0 instead of i != 8???)
    
    code = []
    for line in codeRaw:     #remove comments and split code and pad
        line = line.split("#")[0]
        line = line.split()
        if line == [] or line[0] == "":
            continue
        line += ["" * (max(0, 4-len(line))+1)]  #padding
        line = line[:-1]    #remove last thing (cause of padding??? idk)
        code.append(line)
    
    #print(code, "\n")

    #header files and offset pass
    
    #       OFFSET
    #adds the offset to the whole program (pc is always -1 and defined stuff doesnt get offset either
    #syntax: @OFFSET <offset>

    #       HEADER FILES
    #just puts the header file at the start
    #syntax: @HEADER <std header(in angled brackets)> / path/to/file
    offset = 0
    codeTemp = copy.deepcopy(code)
    code = []
    for line in codeTemp:
        opcode = line[0]
        if opcode == "@HEADER":
            if line[1][0] == "<" and line[1][-1] == ">":    #standard header
                line[1] = fr"{baseDir}{line[1][1:-1]}.txt"
                #print(f"header: {line[1]}")
            with open(line[1]) as file:
                header = file.readlines()
                for line in header:     #remove comments and split code and pad
                    line = line.split("#")[0]
                    line = line.split()
                    if line == [] or line[0] == "":
                        continue
                    line += ["" * (max(0, 4-len(line))+1)]  #padding
                    line = line[:-1]    #remove last thiing
                    code.append(line)
        elif opcode == "@OFFSET":
            offset = int(line[1])
        else:
            code.append(line)
#
    #print("header pass done")







    #get defined shit

    #       DEFINE
    #defines a constant which you can then use
    #syntax: @DEFINE <name> <value>

    codeTemp = copy.deepcopy(code)
    code = []
    defines = {"PC": f"{-1}"}      #hardcoded pc position
    for line in codeTemp:
        opcode = line[0]
        if opcode == "@DEFINE":
            defines[line[1]] = line[2]
        else:
            code.append(line)

    #print("get define pass done")








    #get macros and remove from code

    #       MACROS
    # macros let you define a macro which gets replaced when you use it
    # recursivly defined macros are allowed
    # syntax: @MACRO <name> <code>
    # arguments for the macro are a,b,c,d,...
    # to get a label relative to the macro use ':<label>' instead of '.<label>'
    # '&<name>' is always relative
    # '*<name>' is always relative  #TODO: better distinction
    # '*_<name>' is always global


    #e.g.
    # @MACRO add2op add a b a
    # add2op 4 5 -> add 4 5 4

    #if you want multi line macros either seperate with ';' or use {}

    #e.g.
    # @MACRO add_mul add a b c; mul a b d
    #or
    # @MACRO add_mul {
    # add a b c
    # mul a b d
    # }
    # for the second variant curly braces have to be the only thing in the line (apart from comments ofc) TODO: better curly brace/; support
    codeTemp = copy.deepcopy(code)
    code = []
    macros = {}
    inBlock = False
    for line in codeTemp:
        opcode = line[0]
        if opcode == "@MACRO":
            if "{" in line[2]:    #macro block
                name = copy.deepcopy(line[1])
                define = []
                inBlock = True
            else:
                definetemp = (" ".join(line[2:])).split(";")
                define = []
                for d in definetemp:
                    define.append(d.split())
                macros[line[1]] = define
                #print(define)
        elif inBlock:
            if "}" in line[0]:  #end macro block
                inBlock = False
                macros[name] = define
            else:
                define.append(line)
        else:
            code.append(line)

    #print("get macros pass done")
    #print(macros)
    #print(codeMacros, "\n")
    #print("e")








    #replace macros in code

    macroCounter = -1       #for naming
    replacedMacro = True    #replaced a macro while going through the code?
    recursionCount = 0
    while replacedMacro and recursionCount < 10:        #10 is arbitrary
        recursionCount += 1
        codeTemp = copy.deepcopy(code)
        code = []
        replacedMacro = False
        for lineIndex, line in enumerate(codeTemp):
            opcode = line[0]

            if macros.get(opcode) == None:
                code.append(line)
                continue
        
            #can replace macro
            replacedMacro = True        #"recursive" macro replacing
            macroCounter += 1
            macro = copy.deepcopy(macros.get(opcode))
            for macroLine in macro:
                for m, macroItem in enumerate(macroLine):

                    if len(macroItem) == 1 and macroItem.isalpha():   #single char
                        
                        macroLine[m] = line[ord(macroItem.lower()) - 96]

                    elif ("$(" == macroItem[0:2] or "(" == macroItem[0]) and ")" == macroItem[-1]:  #expression
                        replacedLine = macroItem[0]
                        for i in range(1, len(macroItem)-1):
                            if not macroItem[i-1].isalpha() and macroItem[i].isalpha() and not macroItem[i+1].isalpha():  #just a single char
                                #print(macroItem[i])
                                replacedLine += line[ord(macroItem[i])-97+1]
                            else:
                                replacedLine += macroItem[i]
                        replacedLine += ")"
                        #for index, arg in enumerate(line[1:]):  #loop trough arguments for the macro and replace
                        #    macroItem = macroItem.replace(chr(index+97), f"({arg})")
                        #val = simpleeval.simple_eval(macroItem.strip("$"))
                        macroLine[m] = replacedLine
                        #if macroItem[0] == "$":
                        #    macroLine[m] = f"${val}"
                        #else:
                        #    macroLine[m] = str(val)

                    elif macroItem[0] == "$" and macroItem[1].isalpha() and len(macroItem)==2:   #immediate char
                        macroLine[m] = f"${line[ord(macroItem[1].lower()) - 96]}"

                    elif macroItem[0] == ":":   #label relative to the macro
                        macroLine[m] = f".__{macroItem[1:]}_MACRO_label_{opcode}_{macroCounter}__"

                    elif macroItem[0] == "&":   #address relateive to the macro
                        nameVal = macroItem[1:].split("=")
                        if len(nameVal) == 1:       #no initvalue provided (just set to 0)
                            name = nameVal[0]
                            val = "0"
                        else:
                            name = nameVal[0]
                            val = nameVal[1]
                        macroLine[m] = f"&__{name}_MACRO_{opcode}_{macroCounter}__={val}"

                    elif macroItem[0] == "*" and macroItem[1] != "_":   #address relateive to the macro and not global (*_ are global addresses)
                        macroLine[m] = f"*__{macroItem[1:]}_MACRO_{opcode}_{macroCounter}__"


                code.append(macroLine)

    
    #print("replace macros pass done")
    #print(codeReplacedMacros)

    #for line in code:
    #    print(line)






    #get label pass and put them into defines dict
    #       LABELS
    # standard label pretty much
    # value is equal to the line number * 4
    # syntax: .<name>
    # jmp .<name>

    #       ADDRESSES/POINTERS(idk)
    # now '&' is where it gets interesting
    # so '&<name>=[initial value]' gives you the exact address of that position
    # which gets initialized with some value

    # for example to use a value of an address as a pointer you need to "derefence" it like this:
    # #address 1 is the pointer and address 2 is where to store the data
    #0 cmovz $0 1 *ptr_deref        #moves the value stored at the address 1 to &ptr_deref(1*4 + 2 = 6)
    #1 cmovz $0 &ptr_deref 2        #moves the value stored at the address the address 6 is pointing to (does that make sense?) to 2

    # other usage (variables)
    # &var1 &var2=(PI/2) &var3=60 &var4=9
    # add *var3 *var4 *var1     #var1 = 60 + 9



    codeTemp = copy.deepcopy(code)
    code = []
    instrPtr = 0
    for lineIndex, line in enumerate(codeTemp):
        opcode = line[0]
        if opcode[0] == ".":
            defines[opcode] = f"${instrPtr*4 + offset}"
        elif opcode == "@REQUIRES" or opcode == "@MEMORY":
            code.append(line)
        else:
            for i, item in enumerate(line): #get addresses
                if item[0] == "&":
                    nameVal = item[1:].split("=")
                    if len(nameVal) == 1:       #no initvalue provided (just set to 0)
                        name = nameVal[0]
                        val = "0"
                    else:
                        name = nameVal[0]
                        val = nameVal[1]
                    defines[f"*{name}"] = f"{instrPtr*4 + i + offset}"
                    line[i] = val
            instrPtr += 1
            code.append(line)

    #print("get labels pass done")





    #       REQUIRES
    # tells the assembler some module requires some constant to be defined
    # syntax: @REQUIRES <name>

    codeTemp = copy.deepcopy(code)
    codeTemp.append(["@REQUIRES", "._start"])
    code = []
    for line in codeTemp:
        opcode = line[0]
        if opcode == "@REQUIRES":
            result = defines.get(line[1])
            if result == None:
                raise Exception(f"'{line[1]}' is required to be defined but it is not defined")
        else:
            code.append(line)

    #print("requires pass done")






    #replace defines and labels and addresses in code
    #now there are @DEFINE, labels and & stuff in the defines dict

    defineList = list(defines.items())
    defineList.sort(key = lambda x: len(x[0]), reverse=True)        #sort the list so we start by replacing the longest strings first
                                                                    #so we dont replace substring that are part of a bigger name
    for lineIndex, line in enumerate(code):
        for i, arg in enumerate(line):
            if (arg[0] == "(" or arg[:2] == "$(") and arg[-1] == ")":   #reaplce defined constants in expression (labels too maybe useful)
                for define in defineList:
                    arg = arg.replace(define[0], define[1].strip("$"))
                    code[lineIndex][i] = arg
            elif arg[0] == "$":
                if defines.get(arg[1:]) != None:
                    code[lineIndex][i] = "$" + defines.get(arg[1:])
            else:
                if defines.get(arg) != None:
                    code[lineIndex][i] = defines.get(arg)

    #print("replace define and label pass done")


 
    #for i, line in enumerate(code): print(f"{i} ({i*4}): {line}")

    #evaluate expressions
    #       EXPRESSIONS
    # expressions will get evaluated at "compile" time and can be really useful
    # they can be used in macros, as the initial value for '&'-stuff, for @DEFINE values(no "recursive" defines tho TODO) and more

    # syntax: ... [$](<expression>) ...

    # for example
    # @DEFINE PI 3.1415926
    # cmovz $0 $(PI/2) 4

    # @DEFINE twentyFive (5**2)
    # #@DEFINE dontDoThisYet (PI*2)     #does not work as of now!!!
    
    # &var1=(PI*2) 0 0 0        #zeroes so its aligned
    
    for lineIndex, line in enumerate(code):
        for i, arg in enumerate(line):
            if (arg[0] == "(" or arg[:2] == "$(") and arg[-1] == ")":   #expression
                val = simpleeval.simple_eval(arg.strip("$"))        #TODO: safety concerns?
                if arg[0] == "$":
                    val = f"${val}"
                code[lineIndex][i] = str(val)

    #print("evaluate epressions pass done")
    #print(codeReplacedMacros, "\n")


    #@memory stuffs

    #       MEMORY
    # sets a specified area of memory (useful for strings)
    # it starts at the address given and goes upwards
    # syntax: @MEMORY <address> [val1] [val2]

    # example:
    # @HEADER <chars>
    # @MEMORY helloWorldStr 'H' 'e' 'l' 'l' 'o' ',' '\s' 'W' 'o' 'r' 'l' 'd' '!' '\0'

    codeTemp = copy.deepcopy(code)
    code = []
    memory = []
    for line in codeTemp:
        opcode = line[0]
        if opcode == "@MEMORY":
            memory.append(int(line[1]))
            memory.append([int(data) for data in line[2:]])
        else:
            code.append(line)

    #print("@MEMORY pass done")






    for i, line in enumerate(code): print(f"{i} ({i*4}): {line}")
    
    
    
    
    #print("lol", code[59])
    #replace immediates

    #       IMMEDIATES
    # well its immediates xd
    # syntax: $<value>

    # example:
    # mul $4 $5 10      #stores 4 * 5 at address 10

    immediates = {}
    for lineIndex, line in enumerate(code):
        for i, arg in enumerate(line):
            if arg[0] == "$":   #immediates
                num = strToNum(arg[1:])
                immAddress = immediates.get(num)
                if immAddress == None:     #not in immediates dict yet
                    immAddress = -len(immediates) - 2 + offset      #offset by 1
                    immediates[num] = immAddress     #directly save the indeces the way we want

                code[lineIndex][i] = str(immAddress)

    #print("immediate pass done")
    #print(codeReplacedMacros, "\n")








    #translate atomic opcodes
    codeTemp = copy.deepcopy(code)
    code = list(immediates.keys())
    code.reverse()
    code.append(0)      #place holder for pc
    for lineIndex, line in enumerate(codeTemp):
        opcode = line[0].upper()
        instr = INSTRUCTIONS.get(opcode)
        if instr == None:
            try:
                instr = str(strToNum(opcode))
            except:
                raise Exception(f"u idiot, line {lineIndex} is 200iq ({line})")
        else:
            instr = instr[0]
        line[0] = instr
        #flippedLine = line[1:]   #a b c i
        #flippedLine.append(instr)

        #print(flippedLine)
        #completely unnecesarry for this assembler just leaving it for future assemblers
        #if instr[1] == "Arithmetic": pass
        #elif instr[1] == "Conditional": pass
        #elif instr[1] == "Query": pass
        if len(line) != 4:
            raise Exception(f"Line '{lineIndex}' ({line}) is not aligning with 4 thingie")
        
        code.append(strToNum(line[0]))      #i      
        code.append(strToNum(line[1]))      #a
        code.append(strToNum(line[2]))      #b
        code.append(strToNum(line[3]))      #c


    #print("final pass done")


    if defines.get("._start") == None:
        raise Exception("._start is missing!")      #probably unreachavble but ill leave it
    pc = int(defines.get("PC"))
    start = int(defines.get("._start").strip("$"))
    startIndex = -len(immediates)-1 + offset

    code[pc - startIndex + offset] = start      #not really necessary but whatevs (why not necessary???)

    listForSchem = [startIndex, code]       #pc, [start],
    listForSchem.extend(memory)

    #print(f"startindex: {startIndex}")
    #print(f"data: {listForSchem}")

    #print(f"pc: {pc}")
    #print(f"start address: {start}")


    radonListToSchem.listToSchem(listForSchem, savePath)
    #print("schematic saved")


def ReadTXT():
    #read the txt input file
    FilePath = easygui.fileopenbox('Select the Assembly .txt file', filetypes = ["*.txt"])

    if FilePath == None:    #no file selected smh
        raise Exception("No File selected")
    #print(FilePath)
    #check if file is .txt
    PathList = FilePath.rsplit('\\',1)          #use os/sys shit TODO
    Name, FileType = PathList[-1].rsplit(".",1)
    if "txt" != FileType:
        raise Exception(f'Selected file has the wrong format: ".{FileType}"')
    with open(FilePath) as file:
        Code = file.readlines()

    return Code, FilePath

if __name__ == "__main__":
    Code, _ = ReadTXT()
    assemble(Code, r"C:\Users\torbe\AppData\Roaming\.minecraft\config\worldedit\schematics\funny.schem")