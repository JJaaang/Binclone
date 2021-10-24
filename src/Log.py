import Info as info
import Config as conf
import os

import copy
from tabulate import tabulate

global log_REGGen
global log_REGIdxPtr
global log_REGSIMD
global log_REGSeg
global log_MEM
global log_VAL
global log_ADDR
global log_mnemonic
global log_score

global log_path

global fp
global tmp_path

global log_count
global log_filted_count
global log_single_mode
global log_multiple_mode

def init_norm_log(path) : 
    global log_REGGen
    global log_REGIdxPtr
    global log_REGSIMD
    global log_REGSeg
    global log_MEM
    global log_VAL
    global log_ADDR
    global log_mnemonic

    log_REGGen = set()
    log_REGIdxPtr = set()
    log_REGSIMD = set()
    log_REGSeg = set()
    log_MEM = set()
    log_VAL = set()
    log_ADDR = set()
    log_mnemonic = set()

    global log_path

    token = path.split("\\")
    folder = token[-2]
    log_path = "%s\\%s" %(conf.LOG_PATH, folder)


    

def init_log(path):
    global log_score
    log_score = list()


def make_norm_log(func_name, norm_lines) :

    global log_path

    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    if not os.path.isdir(conf.LOG_PATH) :
        os.mkdir(conf.LOG_PATH)

    if not os.path.isdir(log_path) :
        os.mkdir(log_path)

    log_fp = open('%s\\%s' %(log_path, func_name), 'w')
    log_fp.write("Normalizing\n")
    log_fp.write("function name : %s\n\n" %norm_lines[0])

    for line in norm_lines[1:] :
        log_fp.write("%-11s" %line.mnemonic)
        if line.num_operands > 0 :
            for idx in range(0, line.num_operands) :
                if idx == line.num_operands-1 : 
                    log_fp.write("%s\n" %line.operands[idx])
                else :
                    log_fp.write("%s," %line.operands[idx])
        
        else :
            log_fp.write("\n")


    log_fp.write("\n\n------replacement info------------------------------------------------\n")

    log_fp.write("\tREGGen(%d) : " %len(log_REGGen))
    log_fp.write(", ".join(log_REGGen))
    log_fp.write("\n")
    
    log_fp.write("\tREGIdxPtr(%d) : " %len(log_REGIdxPtr))
    log_fp.write(", ".join(log_REGIdxPtr))
    log_fp.write("\n")
    
    log_fp.write("\tREGSIMD(%d) : " %len(log_REGSIMD))
    log_fp.write(", ".join(log_REGSIMD))
    log_fp.write("\n")
    
    log_fp.write("\tREGSeg(%d) : " %len(log_REGSeg))
    log_fp.write(", ".join(log_REGSeg))
    log_fp.write("\n")
    
    log_fp.write("\tVAL(%d) : " %len(log_VAL))
    log_fp.write(", ".join(log_VAL))
    log_fp.write("\n")

    log_fp.write("\tADDR(%d) : " %len(log_ADDR))
    log_fp.write(", ".join(log_ADDR))
    log_fp.write("\n")

    log_fp.write("\tmnemonic(%d) : " %len(log_mnemonic))
    log_fp.write(", ".join(log_mnemonic))
    log_fp.write("\n")
    log_fp.close()



def init_log_result(single_mode, base, target = False) :

    global fp
    global tmp_path
    global log_count 
    global log_filted_count
    global log_single_mode
    global log_multiple_mode
    
    if single_mode :
        log_single_mode = True
        log_multiple_mode = False
    
    else :
        log_single_mode = False
        log_multiple_mode = True
    
    if log_single_mode :
        log_count = [0]*11
        log_filted_count = [0]*11
        fp = open(conf.RESULT_PATH+"\\[%s]result.txt" %base, 'w')  

    else :
        if conf.MULTIPLE_FAST_MODE :
            log_count = [[0,0],[0,0]]
            fp = open(conf.RESULT_PATH+"\\[%sVs%s]F_result.txt" %(base, target), 'w')  

        else :
            log_count = [[0]*2]
            fp = open(conf.RESULT_PATH+"\\[%sVs%s]result.txt" %(base, target), 'w')  

  
    fp.write('{:#<85}'.format("##### BINCLONE RESULT "))
    fp.write("\n")
    
    fp.write("  * Configuration Information\n")
    
    if log_single_mode :
        fp.write("\tFile Path : %s\%s\n" %(conf.BASE_SET_PATH, base))
        
    else :
        fp.write("\tBase File Path : %s\%s\n" %(conf.BASE_SET_PATH, base))
        fp.write("\tTarget File Path : %s\%s\n" %(conf.TARGET_SET_PATH, target))

    fp.write("\tResult Path : %s\n" %conf.RESULT_PATH)
    fp.write("\tWindow size : %d\n" %conf.WINDOW_SIZE)
    fp.write("\tS_min Value : %.1f\n" %conf.S_MIN)

    if conf.EXCLUDING_LENGTH_DIFFERENCE :
        fp.write("\tWhen the Length difference between the two functions is more than %d times,\n" %conf.LENGTH_DIFFERENCE)
        fp.write("\tthe similarity check is not performed\n")
    
    else :
        fp.write("\n\tThe analxysis if performed regardless of length differences between functions\n")

    tmp_path = conf.RESULT_PATH+"\\tmp.txt"
    if os.path.isfile(tmp_path) :
        os.system("rm %s" %tmp_path)


def log_file_info(filename, total, filted, isBase) :
    
    global fp
    global log_single_mode
    global log_multiple_mode

    if log_multiple_mode :
        if isBase :
            fp.write("\n  * Base File Information\n")
        else :
            fp.write("\n  * Target File Information\n")
    else :
        fp.write("  * File Information\n")

    fp.write("\tFile name : %s\n" %filename)
    fp.write("\tTotal Number of Functions : %d\n" %total)
    fp.write("\tNumber of analyzed Functions : %d\n" %filted)

def log_tmp_result(name, length, rank) :
        
        global tmp_path
        noFunc = True
        with open(tmp_path, 'a') as tmp_fp :
            rank = sorted(rank, key=(lambda x: x['score']), reverse=True)
            st = '--- base function name: %s (LoC : %d) ' %(name,length)
            tmp_fp.write('{:-<65}'.format(st))
            tmp_fp.write("\n")
            for i in range(len(rank)) :
                if rank[i]['score'] < conf.RESULT_SCORE : break
                tmp_fp.write("\t%d. %s (LoC : %d)\n" %(i+1, rank[i]['tar_name'], rank[i]['tar_len']))
                tmp_fp.write("\t\tScore : %d\n" %(rank[i]['score']))
                tmp_fp.write("\t\tbase start line : %d\n" %rank[i]['base_start'])
                tmp_fp.write("\t\ttarget start line : %d\n" %rank[i]['target_start'])
                noFunc = False
        
            if noFunc :
                tmp_fp.write("\tThere is no similar function!\n")
            tmp_fp.write("\n\n")    
        

def log_analysis_result(res1 = list()) :
    global fp
    global tmp_path
    global log_count
    global log_filted_count
    global log_single_mode
    global log_multiple_mode


    fp.write("\n\n")
    fp.write('{:#<85}'.format("##### ANALYASIS RESULT "))
    fp.write("\n  NOTE. Only results with a similarity score of * %d or higher * are output\n" %conf.RESULT_SCORE)
    fp.write("  If you want to adjust the score, change the RESULT_SCORE value in the Config.py\n\n")

    fp.write('{:^40}'.format("Summary of Results"))
    fp.write('\n')
    if log_single_mode :
        head = ["num of comparisons","60% ^", "70% ^", "80% ^", "90% ^", "100%"]
        table = list()

        item = [0]*6
        tmp_item = [0]*6
        tmp_item[5] = log_count[10]
        idx = 4
        total = 0
        for i in reversed(range(6, 10)) :
            tmp_item[idx] =  tmp_item[idx+1] + log_count[i]
            idx -= 1

        for i in range(len(log_count)) :
            total += log_count[i] 
        
        item[0] = total
        for idx in range(1, 6) :
            if tmp_item[idx] == 0 :
                per = 0
            else :
                per = float(tmp_item[idx]/total)*100

            item[idx] = "%d (%.2f)" %(tmp_item[idx], per)

        table.append(copy.deepcopy(item))

        if conf.EXIST_FILTED_FUNCTIONS :
            tmp_item = [0]*6
            tmp_item[5] = log_filted_count[10]
            idx = 4
            for i in reversed(range(6, 10)) :
                tmp_item[idx] =  tmp_item[idx+1] + log_filted_count[i]
                idx -= 1
            item[0] = "include filted func"
            for idx in range(1, 6) :
                if tmp_item[idx] == 0 :
                    per = 0
                else :
                    per = float(tmp_item[idx]/total)*100
                item[idx] = "%d (%.2f)" %(tmp_item[idx], per)
            table.append(copy.deepcopy(item))
        

    else :
        head = ["num of comparisons", "num of detected"]
        table = log_count

    fp.write(tabulate(table, headers = head, tablefmt='pretty'))

    fp.write('\n')
    fp.write("\n")

    if os.path.isfile(tmp_path) :
        with open(tmp_path, 'r') as tmp_fp :        
            lines = tmp_fp.readlines()

            for line in lines : 
                fp.write(line)
            
            fp.close()

            os.system("rm %s" %tmp_path)

def log_score(score, filted = False) :
    if filted :
        if score == 0 :
            log_filted_count[0] += 1
        else :
            log_filted_count[int(score/10)] += 1

    else :
        if score == 0 :
            log_count[0] += 1
        else :
            log_count[int(score/10)] += 1
                

        


