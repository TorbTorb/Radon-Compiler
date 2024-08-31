import SchemGenerator as SG  # pip install SchemGenerator
import struct

def floatToBits(f):
    s = struct.pack('>d', f)    #implicit float conversion?
    bits = struct.unpack('>q', s)[0]
    #print(hex(bits))
    #sign, exponent, mantissa
    return (bits & 0x80_00_00_00_00_00_00_00) >> 31, (bits & 0x7f_f0_00_00_00_00_00_00)>> 52, bits & 0x00_0f_ff_ff_ff_ff_ff_ff

def sign(num):
    return -1 if num < 0 else 1

def _convertToBlocks(num, intPos = "stone", intNeg = "dirt", expPos = "oak_planks", expNeg = "cobblestone"):
    colors = ["white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray", "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black"]
    blocks = ["_wool", "_stained_glass", "_terracotta", "_stained_glass_pane", "_carpet", "_concrete", "_concrete_powder", "_glazed_terracotta"]
    out = []
    signNum = sign(num)
    num = abs(num)
    if type(num) == int:
        while num != 0:
            blockType = (num & 0b1110000) >> 4
            color = num & 0b1111

            out.append(colors[color] + blocks[blockType])
            
            num = num>>7

        out.reverse()
        if signNum == -1:
            out.append(intNeg)
        else:
            out.append(intPos)

    elif type(num) == float:
        _, exponent, mantissa = floatToBits(num)
        mantissa += 0x00_10_00_00_00_00_00_00    #leading zero of mantissa
        if exponent == 0:
            mantissa  -= 0x00_10_00_00_00_00_00_00

        exponent -= 1024 + 51
        expSign = sign(exponent)
        exponent = abs(exponent)
        #print(signNum, expSign, exponent, mantissa)
        #first mantissa
        while mantissa != 0:
            blockType = (mantissa & 0b1110000) >> 4
            color = mantissa & 0b1111

            out.append(colors[color] + blocks[blockType])
            
            mantissa = mantissa>>7
            #if mantissa == 0: break

        out.reverse()
        if signNum == -1:
            out.append(intNeg)
        else:
            out.append(intPos)

        #now exponent
        expBlocks = []
        while exponent != 0:
            
            blockType = (exponent & 0b1110000) >> 4
            color = exponent & 0b1111

            expBlocks.append(colors[color] + blocks[blockType])
            
            exponent = exponent>>7
            #if exponent == 0: break

        expBlocks.reverse()
        if expSign == -1:
            expBlocks.append(expNeg)
        else:
            expBlocks.append(expPos)

        out.extend(expBlocks)
        
    else: raise Exception(f"Unsupported type {type(num)} for converting to blocks")

    
    #print(og, out)
    
    return out

def listToSchem(inputList, savePath):

    Schem = SG.Schematic()
    Schem.setBlock((0,0,0), "redstone_block")    #init block
    x = 1
    y = 0
    z = 0
    for index, values in zip(inputList[::2], inputList[1::2]):
        #print(index, values)

        blocks = _convertToBlocks(index - 1, "bedrock", "gold_ore")
        values.append(0)    #hacky >:3 (last value doesnt get converted to blocks so its needed)
        for val in values:
            for block in blocks:
                #print(block)
                Schem.setBlock((x,y,z), block)
                x+=1
                if x > 31:
                    x = 0
                    z += 1
            blocks = _convertToBlocks(val)
        Schem.replace("air", "redstone_block")
        Schem.save(savePath)


#if __name__ == "__main__": main([0, [0, 2, 4, 1, 2, 3, 6, 8, 9, 2, 4, 6, 7, 4,1,7,23,81,72,72,2,5,8,2,6,8,1,6,4,1,7,9,1,7,8,3], -5, [-6, 9, 4]])
