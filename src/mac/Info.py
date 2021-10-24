class NormInst :
    mnemonic = ""
    operands = list()
    num_operands = 0

    def __init__(self, mnemonic) :
        self.mnemonic = mnemonic
        self.operands = list()
        self.num_operands = 0
        self.len = 0
    
    def get_first_feature(self) :
        return self.mnemonic

    def get_second_feature(self) :
        return self.operands

    def get_third_feature(self) :
        if self.num_operands > 0:
            return self.mnemonic + self.operands[0]
        return None
    
    def get_fourth_feature(self):
        if self.num_operands > 1:
            return self.mnemonic + self.operands[0] + self.operands[1]
        return None

class FunctionInfo :
    # navie_feaure_vector_list is dictionary list
    # Each dictionary for each row contains the navie feature vector per region
    # Where dictionary's key value refers to the feature name and key's value refers the frequency of that feature
    
    name = ""
    len = 0
    features = set()
    navie_features_list = list()
    call_function_list = list()
    

    def __init__(self, name, len) :
        self.navie_features_list = list()
        self.name = name
        self.len = len
        self.features = set()
        self.call_function_list = list()
        

REGGen = {"rax", "eax", "ax", "ah", "al", 
        "rcx", "ecx", "cx", "ch", "cl", 
        "rdx", "edx", "dx", "dh", "dl",
        "rbx", "rbx", "bx", "bh", "bl",
        "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"}

REGSIMD = {'xmm0', 'xmm1', 'xmm2', 'xmm3', 'xmm4', 
        'xmm5', 'xmm6', 'xmm7', 'xmm8', 'xmm9', 
        'xmm10', 'xmm11', 'xmm12', 'xmm13', 'xmm14', 'xmm15',
        'ymm0', 'ymm1', 'ymm2', 'ymm3', 'ymm4', 
        'ymm5', 'ymm6', 'ymm7', 'ymm8', 'ymm9', 
        'ymm10', 'ymm11', 'ymm12', 'ymm13', 'ymm14', 'ymm15'}

REGIdxPtr = {"rsp", "esp", "sp", "spl", 
            "rbp", "ebp", "bp", "bpl", 
            "rsi", "esi", "sl", "sil",
            "rdi", "edi", "dl", "dil"}
            
REGSeg = {"ss:", "cs:", "ds:", "es:", "fs:", "large gs:", "large ss:", "large cs:", "large ds:", "large es:", "large fs:", "large gs:"}
