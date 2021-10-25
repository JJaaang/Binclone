from re import L
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

global log_path

global fp
global tmp_path

global log_count
global log_r_count
global log_filted_count
global base_name
global query_name

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

    token = path.split("/")
    folder = token[-2]
    log_path = "%s/%s" %(conf.LOG_PATH, folder)


def make_norm_log(func_name, norm_lines) :

    global log_path

    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    if not os.path.isdir(conf.LOG_PATH) :
        os.mkdir(conf.LOG_PATH)

    if not os.path.isdir(log_path) :
        os.mkdir(log_path)

    log_fp = open('%s/%s' %(log_path, func_name), 'w', encoding='utf8')
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



def init_log_result(single_mode, base, query = None) :

    global fp
    global tmp_path
    global log_count 
    global log_r_count
    global log_filted_count
    global base_name
    global query_name
    
    base_name = base
    query_name = query

    if conf.SINGLE_COMPARE_MODE :
        
        log_count = [0]*11
        log_filted_count = [0]*11
        fp = open(conf.RESULT_PATH+"/[%s]result.txt" %base_name, 'w', encoding='utf8') 
    
    else :
        if conf.MULTIPLE_FAST_MODE :
            log_count = [0]*11
            log_r_count = [0]*11
            fp = open(conf.RESULT_PATH+"/[%sVs%s]F_result.txt" %(base_name, query_name), 'w', encoding='utf8')  

        else :
            log_count = [0]*11            
            fp = open(conf.RESULT_PATH+"/[%sVs%s]result.txt" %(base_name, query_name), 'w', encoding='utf8')  

  
    fp.write('{:#<100}'.format("##### BINCLONE RESULT "))
    fp.write("\n")
    
    fp.write("  * Configuration Information\n")
    
    if conf.SINGLE_COMPARE_MODE :
        fp.write("\tFile Path : %s/%s\n" %(conf.BASE_SET_PATH, base_name))
        
    else :
        fp.write("\tBase File Path : %s/%s\n" %(conf.BASE_SET_PATH, base_name))
        fp.write("\tTarget File Path : %s/%s\n" %(conf.QUERY_SET_PATH, query_name))

    fp.write("\tResult Path : %s\n" %conf.RESULT_PATH)
    fp.write("\tWindow size : %d\n" %conf.WINDOW_SIZE)
    fp.write("\tS_min Value : %.1f\n" %conf.S_MIN)

    if conf.EXCLUDING_LENGTH_DIFFERENCE :
        fp.write("\tWhen the Length difference between the two functions is more than %d times,\n" %conf.LENGTH_DIFFERENCE)
        fp.write("\tthe similarity check is not performed\n")
    
    else :
        fp.write("\n\tThe analysis if performed regardless of length differences between functions\n")

    tmp_path = conf.RESULT_PATH+"/tmp.txt"
    if os.path.isfile(tmp_path) :
        os.system("rm %s" %tmp_path)


def log_file_info(filename, total, filted, isBase) :
    
    global fp

    if conf.MULTIPLE_COMPARE_MODE :
        if isBase :
            fp.write("\n  * Base File Information\n")
        else :
            fp.write("\n  * Target File Information\n")
    else :
        fp.write("\n  * File Information\n")

    fp.write("\tFile name : %s\n" %filename)
    fp.write("\tTotal Number of Functions : %d\n" %total)
    fp.write("\tNumber of analyzed Functions : %d\n" %filted)

def log_tmp_result(name, length, rank) :
        
        global tmp_path
        noFunc = True

        with open(tmp_path, 'a', encoding='utf8') as tmp_fp :
            rank = sorted(rank, key=(lambda x: x['score']), reverse=True)
            st = '--- base function name: %s (LoC : %d) ' %(name,length)
            tmp_fp.write('{:-<65}'.format(st))
            tmp_fp.write("\n")
            for i in range(len(rank)) :
                if rank[i]['score'] < conf.RESULT_SCORE : break
                tmp_fp.write("\t%d. %s (LoC : %d)\n" %(i+1, rank[i]['query_name'], rank[i]['query_len']))
                tmp_fp.write("\t\tScore : %d\n" %(rank[i]['score']))
                tmp_fp.write("\t\tbase start line : %d\n" %rank[i]['base_start'])
                tmp_fp.write("\t\tquery start line : %d\n" %rank[i]['query_start'])
                noFunc = False
        
            if noFunc :
                tmp_fp.write("\tThere is no similar function!\n")
            tmp_fp.write("\n\n")    


def log_processing_count(count_list, min) :

    # [min, 100] score 
    length = 10 - min + 1
    res = [0] * (length)
    tmp_res = [0] * (length)

    #compute num per section
    idx = length - 1
    tmp_res[idx] = count_list[10]
    idx -= 1

    for i in reversed(range(min, 10)) :
        tmp_res[idx] = tmp_res[idx+1] + count_list[i]
        idx -= 1

    #num of comparisons
    total = 0
    for cnt in count_list :
        total += cnt
    
    #exclude num of comparisons(idx = 0)
    for idx in range(0, length) :
        if tmp_res[idx] == 0 :
            per = 0
        else :
            per = float(tmp_res[idx]/total) * 100
        
        res[idx] = "%d (%.2f%%)" %(tmp_res[idx], per)

    res.insert(0, total)
    return res


def log_analysis_result(time, min = 5) :
    global fp
    global tmp_path
    global log_count
    global log_r_count
    global log_filted_count
    global base_name
    global query_name


    fp.write("\n\n")
    fp.write('{:#<100}'.format("##### ANALYASIS RESULT "))

    fp.write("\n")
    fp.write("  * Analysis time : %.2f\n\n" %time)

    fp.write("  * Summary of Results")
    fp.write('\n')
    
    head = ["num of comparisons"]
    for i in range(min, 11) :
        head.append("%d%% ^" %(i*10))
    
    table = list()
    table.append(log_processing_count(log_count, min))
    
    if not query_name == None :
        fp.write("    base : %s, query %s\n" %(base_name, query_name))
    fp.write(tabulate(table, headers = head, tablefmt='pretty'))

    fp.write('\n')
    fp.write("\n")

    if conf.MULTIPLE_COMPARE_MODE and conf.MULTIPLE_FAST_MODE :
        table = list()
        table.append(log_processing_count(log_r_count, min)) 
        fp.write("    base : %s, query %s\n" %(query_name, base_name))
        fp.write(tabulate(table, headers = head, tablefmt='pretty'))

        fp.write('\n')
        fp.write("\n")    

    elif conf.SINGLE_COMPARE_MODE and conf.EXIST_FILTED_FUNCTIONS :
        table = list()
        fp.write("Include filted function\n")
        table.append(log_processing_count(log_filted_count, min))
    

    if os.path.isfile(tmp_path) :
        fp.write("NOTE. Only results with a similarity score of * %d or higher * are output\n" %conf.RESULT_SCORE)
        fp.write("If you want to adjust the score, change the RESULT_SCORE value in the Config.py\n\n")
        with open(tmp_path, 'r', encoding='utf8') as tmp_fp :        
            lines = tmp_fp.readlines()

            for line in lines : 
                fp.write(line)
            
            fp.close()

            os.system("rm %s" %tmp_path)
    
    else :
        fp.close()


def log_score(score, mode = "normal") :
    
    global log_count
    global log_r_count
    global log_filted_count
    
    if mode == "normal" :
        log_list = log_count
    elif mode == "filted" :
        log_list = log_filted_count
    elif mode == "fast" :
        log_list = log_r_count

    if score == 0 :
        log_list[0] += 1
    else :
        log_list[int(score/10)] += 1
 


