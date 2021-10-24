import Bincore as bin
import Config as conf
import Util as ut
import Log as log

import pandas as pd
import os
import time
import copy
from tqdm import tqdm


#A_function and B_function are "function_info" class
def compute_similarity(base_function, query_function) :

    # "Combined_features" function combines the feature of the base function and the query function
    bin.combine_feature(base_function, query_function)

    # A feature_vector_list is two-demensional list
    # row : region / columne : feature
    base_FV_list = bin.make_feature_vector(base_function)
    query_FV_list = bin.make_feature_vector(query_function)

    bin.compute_median(base_FV_list, query_FV_list)

    # The "make_binary_vector" function conducts filtering and binary vector making.
    base_BV_list = bin.make_binary_vector(base_FV_list)
    query_BV_list = bin.make_binary_vector(query_FV_list)

    # The "compare_region_to_region" function computes the Binary vector similarity
    result_matrix = bin.compare_region_to_region(base_BV_list, query_BV_list)

    # The "clone_merger" function merge the consecutive clones that considered to be similar
    result = bin.clone_merger(result_matrix)

    return result

def binclone_multiple_mode(base, query) :

    start_time = time.time()

    base_path = "%s\\%s" %(conf.BASE_SET_PATH, base)
    query_path  = "%s\\%s" %(conf.QUERY_SET_PATH, query)

    base_list = bin.preprocessing(base_path)
    query_list = bin.preprocessing(query_path)

    num_base = len(base_list)
    num_query = len(query_list)

    # if function size is smaller than the WINDOW SIZE, the similarity check is not performed
    # and append the unchecked list
    unchecked_base_list = list()
    unchecked_query_list = list()

    # the functions in checked list are functions whose size is longer than the window size
    # BinClone performs the similarity check only on the functions in the checked list
    checked_base_list = list()
    checked_query_list = list()

    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    log.init_log_result(False, base, query)

    for base_func in base_list[:] :
        if base_func.len < conf.WINDOW_SIZE :
            unchecked_base_list.append("%s (%d)" %(base_func.name, base_func.len))
            base_list.remove(base_func)
        else :
            checked_base_list.append("%s (%d)" %(base_func.name, base_func.len))

   
    for query_func in query_list[:] :
        if query_func.len < conf.WINDOW_SIZE :
            unchecked_query_list.append("%s (%d)" %(query_func.name, query_func.len))
            query_list.remove(query_func)
        else :
            checked_query_list.append("%s (%d)" %(query_func.name, query_func.len))

    log.log_file_info(base, num_base, len(base_list), True)
    log.log_file_info(query, num_query, len(query_list), False)

    score_result = [[0]*len(query_list) for i in range(len(base_list))]

    for b_idx in tqdm(range(len(base_list)), desc="base", ncols=100) :
        rank = list()
        base_func = base_list[b_idx]
        for t_idx in tqdm(range(len(query_list)), desc="\tquery", ncols=100, leave=False) :
            query_func = query_list[t_idx]

            if conf.EXCLUDING_LENGTH_DIFFERENCE and ut.length_check(base_func.len, query_func.len) : 
                score = 0 
               
            else :
                score = 0
                bin_res = compute_similarity(base_func, query_func)
                if bool(bin_res):
                    
                    score = (int)((bin_res['length']/base_func.len)*100)

                    score_result[b_idx][t_idx] = score
                    
                    bin_res['query_name'] = query_func.name
                    bin_res['query_len'] = query_func.len
                    bin_res['score'] = score
                    rank.append(copy.deepcopy(bin_res))
                    
            log.log_score(score)
        log.log_tmp_result(base_func.name, base_func.len, rank) 

    end_time = time.time() - start_time
    log.log_analysis_result(end_time)  

    score_result = pd.DataFrame(score_result, index=checked_base_list, columns=checked_query_list)
    score_result.to_csv(conf.RESULT_PATH+"\\[%sVS%s]result.csv" %(base, query))

    return end_time


def binclone_multiple_fast_mode(base, query) :

    start_time = time.time()

    base_path = "%s\\%s" %(conf.BASE_SET_PATH, base)
    query_path  = "%s\\%s" %(conf.QUERY_SET_PATH, query)

    base_list = bin.preprocessing(base_path)
    query_list = bin.preprocessing(query_path)

    num_base = len(base_list)
    num_query = len(query_list)

    unchecked_base_list = list()
    unchecked_query_list = list()

    checked_base_list = list()
    checked_query_list = list()

    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    log.init_log_result(False, base, query)

    for base_func in base_list[:] :
        if base_func.len < conf.WINDOW_SIZE :
            unchecked_base_list.append("%s (%d)" %(base_func.name, base_func.len))
            base_list.remove(base_func)
        else :
            checked_base_list.append("%s (%d)" %(base_func.name, base_func.len))

   
    for query_func in query_list[:] :
        if query_func.len < conf.WINDOW_SIZE :
            unchecked_query_list.append("%s (%d)" %(query_func.name, query_func.len))
            query_list.remove(query_func)
        else :
            checked_query_list.append("%s (%d)" %(query_func.name, query_func.len))

    log.log_file_info(base, num_base, len(base_list), True)
    log.log_file_info(query, num_query, len(query_list), False)

    score_result = [["0 (0)"]*len(query_list) for i in range(len(base_list))]

    for b_idx in tqdm(range(len(base_list)), desc="base", ncols=100) :
        base_func = base_list[b_idx]
        for t_idx in tqdm(range(len(query_list)), desc="\tquery", ncols=100, leave=False) :
            query_func = query_list[t_idx]

            if conf.EXCLUDING_LENGTH_DIFFERENCE and ut.length_check(base_func.len, query_func.len) : 
                score = 0
                r_score = 0

            else :
                bin_res = compute_similarity(base_func, query_func)
                score = 0
                r_score = 0

                if bool(bin_res):
                    
                    score = (int)((bin_res['length']/base_func.len)*100)
                    r_score = (int)((bin_res['length']/query_func.len)*100)

                    score_result[b_idx][t_idx] = "%s (%s)"%(score, r_score)

            log.log_score(score)
            log.log_score(r_score, mode = "fast")
             
                   
    end_time = time.time() - start_time
    log.log_analysis_result(end_time)
    score_result = pd.DataFrame(score_result, index=checked_base_list, columns=checked_query_list)
    score_result.to_csv(conf.RESULT_PATH+"\\[%sVS%s]F_result.csv" %(base, query))

    return end_time



def binclone_single_mode(file) :

    start_time = time.time()

    file_path = "%s\\%s" %(conf.BASE_SET_PATH, file)

    func_list = bin.preprocessing(file_path)
    unchecked_func_list = list()
    checked_func_list = list()
    filted_func = list()


    num_func = len(func_list)
    
    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    log.init_log_result(True, file)

    for func in func_list[:] :
        if func.len < conf.WINDOW_SIZE :
            unchecked_func_list.append("%s (%d)" %(func.name, func.len))
            func_list.remove(func)
        else :
            checked_func_list.append("%s (%d)" %(func.name, func.len))

    log.log_file_info(file, num_func, len(base_list), True)

    if conf.EXIST_FILTED_FUNCTIONS :
        filted_func = ut.filted_functions(file)

    score_result = [[0]*len(func_list) for i in range(len(func_list))]
    visit = [[False]*len(func_list) for i in range(len(func_list))]
    backup = dict()

    for idx in tqdm(range(len(func_list)), desc="base", ncols=100) :
        rank = list()
        base_func = func_list[idx]
        for jdx in tqdm(range(len(func_list)), desc="\tquery", leave=False, ncols=100) :
            query_func = func_list[jdx]
            
            if conf.EXCLUDING_LENGTH_DIFFERENCE and ut.length_check(base_func.len, query_func.len) : 
                log.log_score(0)
                continue
            if base_func.name == query_func.name : 
                log.log_score(0)
                continue
            
            if visit[idx][jdx] :
                score = score_result[idx][jdx]
                bin_res = dict()
                if base_func.name in backup :
                    if query_func.name in backup[base_func.name].keys() :
                        bin_res = copy.deepcopy(backup[base_func.name][query_func.name])
                
            else :
                bin_res = compute_similarity(base_func, query_func)
                visit[jdx][idx] = True
                visit[idx][jdx] = True
                score = 0

                if bool(bin_res):
                    score = (int)(( bin_res['length']/base_func.len)*100)
                    r_score = (int)(( bin_res['length']/query_func.len)*100)
                    
                    score_result[idx][jdx] = score
                    score_result[jdx][idx] = r_score

                    tmp = dict()
                    tmp["base_start"] = bin_res["query_start"]
                    tmp["query_start"] = bin_res["base_start"]
                    tmp["length"] = bin_res["length"]
                    if not query_func.name in backup :
                        backup[query_func.name] = dict()
                                  
                    backup[query_func.name][base_func.name] = copy.deepcopy(tmp)
            
            if bool(bin_res) :
                bin_res['query_name'] = query_func.name
                bin_res['query_len'] = query_func.len
                bin_res['score'] = score
                rank.append(copy.deepcopy(bin_res))
           
            log.log_score(score)
            if conf.EXIST_FILTED_FUNCTIONS :
                if (base_func.name in filted_func) or (query_func.name in filted_func) :
                    log.log_score(score, mode = 'filted')

        log.log_tmp_result(base_func.name, base_func.len, rank)
    
    end_time = time.time() - start_time
    log.log_analysis_result(end_time)
    score_result = pd.DataFrame(score_result, index=checked_func_list, columns=checked_func_list)
    score_result.to_csv(conf.RESULT_PATH+"\\[%s]result.csv" %(base))
  
    return end_time




if __name__ == "__main__" :


    total_time = 0

    if conf.MULTIPLE_COMPARE_MODE :
        backup_single_mode = conf.SINGLE_COMPARE_MODE
        backup_exclude_mode = conf.EXCLUDING_LENGTH_DIFFERENCE
        conf.SINGLE_COMPARE_MODE = False
        conf.EXIST_FILTED_FUNCTIONS = False

        base_list = ut.listdir(conf.BASE_SET_PATH)
        query_list = ut.listdir(conf.QUERY_SET_PATH)

        if conf.MULTIPLE_FAST_MODE :
             for base in base_list :
                for query in query_list :
                    if(base == query) :
                        continue
                    print("Similarity check (%s vs %s) ----------------" %(base, query))
                    a_time = binclone_multiple_fast_mode(base, query)
                    print("time : %f\n\n" %a_time)
                    total_time += a_time
        else :
            for base in base_list :
                for query in query_list :
                    if(base == query) :
                        continue
                    print("Similarity check (%s vs %s) ----------------" %(base, query))
                    a_time = binclone_multiple_mode(base, query)
                    print("time : %f\n\n" %a_time)
                    total_time += a_time

        conf.SINGLE_COMPARE_MODE = backup_single_mode
        conf.EXCLUDING_LENGTH_DIFFERENCE = backup_exclude_mode

    if conf.SINGLE_COMPARE_MODE :

        conf.MULTIPLE_COMPARE_MODE = False
        conf.MULTIPLE_FAST_MODE = False

        base_list = ut.listdir(conf.BASE_SET_PATH)
        for base in base_list :

            print("Similarity check (%s) ----------------" %(base))
            a_time = binclone_single_mode(base)
            print("time : %f\n\n" %a_time)
            total_time += a_time


    print("\n\nAnalysis completed successfully\n")
    print("Total analysis time : %.2f\n" %total_time)
