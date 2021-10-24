import Info as info
import Log as log
import os

"""
This file contaits functions to normalize the assembly.
If you want to use the log file, please replace "#log" with "log"
"""


def line_preprocessing(line):
    """
    remove the instruction bytes, comments and spaces
    return preprocessed line
    """
    # Remove instruction bytes
    line  = line.split(" ", 1)[1].strip("\n")

    # Remove comments
    if ";" in line :
        line = line[:line.rindex(";")]

    # Remove spaces at the beginning and at the end of the line
    line = line.strip()

    return line



def branch_check(mnemonic) :
    if mnemonic != "" :
        if mnemonic == "call" : return True
        # jump instructions start with "j"
        elif mnemonic[0] == "j" : return True
    
    return False



def memory_ref_check(operand) :
    """
    This function checks if the operand is memory reference.
    if so return 1, else return 0.
    """
    # Memory references contain "[" and "]"
    if "[" in operand :
        return True
    elif "dword_" in operand :
        return True
    return False



def const_val_check(operand, mnemonic) :
    """
    This function checks if the operand is constant value.
    if so return 1, else return 0.
    """
    if "0" <= operand[0] and operand[0] <= "9" :
        return True

    if "A" <= operand[0] and operand[0] <= "F" :
        if operand[-1] == "h" :
            return True

    return False



def register_check(operand) :
    """
    this function checks if the operand is register.
    (The check is done by referencing asmInfo.py)
    if not, return 0,
    else REGGen : 1/ REGIdxPtr : 2/ REGSIMD : 3/ REGSeg : 4 
    """

    #General register check
    if operand in info.REGGen:
        return 1
    elif operand in info.REGIdxPtr:
        return 2
    elif operand in info.REGSIMD:
        return 3
    elif operand[0:3] in info.REGSeg:
        return 4

def Address_check(operand) :
    """
    This function checks if the oprand is memory address.
    if so return 1, else return 0.
    """
    if "sub_" in operand :
            return True
    elif "loc_" in operand :
        return True
    elif "offset" in operand :
        return True

    return False



def normalize_per_line(line):
    """
    Return normalized instruction information, which is NormInst class.
    """

    line = line_preprocessing(line)
    if not line or "nop" in line : return None
    
    tokens = line.split(' ', 1)
    norm_inst = info.NormInst(tokens[0])
    #log.log_mnemonic.add(tokens[0])

    if len(tokens) > 1 :
        operands = tokens[1].strip().split(', ')
        for operand in operands :

            norm_inst.num_operands += 1 

            # memory reference check
            if memory_ref_check(operand) :
                norm_inst.operands.append("MEM")
                #log.log_MEM.add(operand)
                continue
            
            # const value check
            if const_val_check(operand, norm_inst.mnemonic) :
                norm_inst.operands.append("VAL")
                #log.log_VAL.add(operand)
                continue
            
            # memory address check
            if Address_check(operand) :
                norm_inst.operands.append("ADDR")
                #log.log_ADDR.add(operand)
                continue

            # register check
            reg_check = register_check(operand)
            if reg_check == 1:
                norm_inst.operands.append("REGGen")
                #log.log_REGGen.add(operand)
                continue
            elif reg_check == 2:
                norm_inst.operands.append("REGIdxPtr")
                #log.log_REGIdxPtr.add(operand)
                continue
            elif reg_check == 3:
                norm_inst.operands.append("REGSIMD")
                #log.log_REGSIMD.add(operand)
                continue
            elif reg_check == 4:
                norm_inst.operands.append("REGSeg")
                #log.log_REGSeg.add(operand)
                continue
            
            norm_inst.operands.append(operand)

    return norm_inst



def normalizer(function_path):
    """
    Return Normalized instructions of function in function path.
    Normalized instructions, norm_func, are the form of NormInst class list.
    """
    dump_fp = open(function_path, 'r+', encoding='utf8')
    norm_func = [] 

    log.init_norm_log(function_path)

    file_name = dump_fp.readline().strip("\n")
    norm_func.append(file_name)

    # start normalize per line
    lines = dump_fp.readlines()
    for line in lines :
        norm_inst = normalize_per_line(line)
        if norm_inst != None :
            norm_func.append(norm_inst)

    file_name = os.path.basename(dump_fp.name)        
    log.make_norm_log(file_name, norm_func)
    dump_fp.close()

    return norm_func

"""
if __name__ == "__main__" :

    file_list = os.listdir("ida_log")
    for file in file_list :
        path = 'ida_log/' + file
        normalizer(path)
"""
