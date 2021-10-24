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
def compute_similarity(base_function, target_function) :

    # "Combined_features" function combines the feature of the base function and the target function
    bin.combine_feature(base_function, target_function)

    # A feature_vector_list is two-demensional list
    # row : region / columne : feature
    base_FV_list = bin.make_feature_vector(base_function)
    target_FV_list = bin.make_feature_vector(target_function)

    bin.compute_median(base_FV_list, target_FV_list)

    # The "make_binary_vector" function conducts filtering and binary vector making.
    base_BV_list = bin.make_binary_vector(base_FV_list)
    target_BV_list = bin.make_binary_vector(target_FV_list)

    # The "compare_region_to_region" function computes the Binary vector similarity
    result_matrix = bin.compare_region_to_region(base_BV_list, target_BV_list)

    # The "clone_merger" function merge the consecutive clones that considered to be similar
    result = bin.clone_merger(result_matrix)


    return result

def binclone_multiple_mode(base, target) :

    base_path = "%s\\%s" %(conf.BASE_SET_PATH, base)
    target_path  = "%s\\%s" %(conf.TARGET_SET_PATH, target)

    base_list = bin.preprocessing(base_path)
    target_list = bin.preprocessing(target_path)

    num_base = len(base_list)
    num_tar = len(target_list)

    # if function size is smaller than the WINDOW SIZE, the similarity check is not performed
    # and append the unchecked list
    unchecked_base_list = list()
    unchecked_target_list = list()

    # the functions in checked list are functions whose size is longer than the window size
    # BinClone performs the similarity check only on the functions in the checked list
    checked_base_list = list()
    checked_target_list = list()

    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    log.init_log_result(False, base, target)

    for base_func in base_list[:] :
        if base_func.len < conf.WINDOW_SIZE :
            unchecked_base_list.append("%s (%d)" %(base_func.name, base_func.len))
            base_list.remove(base_func)
        else :
            checked_base_list.append("%s (%d)" %(base_func.name, base_func.len))

   
    for tar_func in target_list[:] :
        if tar_func.len < conf.WINDOW_SIZE :
            unchecked_target_list.append("%s (%d)" %(tar_func.name, tar_func.len))
            target_list.remove(tar_func)
        else :
            checked_target_list.append("%s (%d)" %(tar_func.name, tar_func.len))

    log.log_file_info(base, num_base, len(base_list), True)
    log.log_file_info(target, num_tar, len(target_list), False)

    score_result = [[0]*len(target_list) for i in range(len(base_list))]

    log.log_count[0][0] = len(target_list) * len(base_list)
    log.log_count[0][1] = 0

    for b_idx in tqdm(range(len(base_list)), desc="base", ncols=100) :
        rank = list()
        base_func = base_list[b_idx]
        for t_idx in tqdm(range(len(target_list)), desc="\ttarget", ncols=100, leave=False) :
            tar_func = target_list[t_idx]
            if conf.EXCLUDING_LENGTH_DIFFERENCE and ut.length_check(base_func.len, tar_func.len) : continue

            else :
                bin_res = compute_similarity(base_func, tar_func)
                if bool(bin_res):
                    
                    score = (int)((bin_res['length']/base_func.len)*100)

                    score_result[b_idx][t_idx] = score
                    
                    bin_res['tar_name'] = tar_func.name
                    bin_res['tar_len'] = tar_func.len
                    bin_res['score'] = score
                    rank.append(copy.deepcopy(bin_res))
                    
                    if score >= conf.RESULT_SCORE :
                        log.log_count[0][1] += 1

        log.log_tmp_result(base_func.name, base_func.len, rank) 

    log.log_analysis_result()  
    score_result = pd.DataFrame(score_result, index=checked_base_list, columns=checked_target_list)
    score_result.to_csv(conf.RESULT_PATH+"\\[%sVS%s]result.csv" %(base, target))


def binclone_multiple_fast_mode(base, target) :

    base_path = "%s\\%s" %(conf.BASE_SET_PATH, base)
    target_path  = "%s\\%s" %(conf.BASE_SET_PATH, target)

    base_list = bin.preprocessing(base_path)
    target_list = bin.preprocessing(target_path)

    num_base = len(base_list)
    num_tar = len(target_list)

    unchecked_base_list = list()
    unchecked_target_list = list()

    checked_base_list = list()
    checked_target_list = list()

    if not os.path.isdir(conf.RESULT_PATH) :
        os.mkdir(conf.RESULT_PATH)

    log.init_log_result(False, base, target)

    for base_func in base_list[:] :
        if base_func.len < conf.WINDOW_SIZE :
            unchecked_base_list.append("%s (%d)" %(base_func.name, base_func.len))
            base_list.remove(base_func)
        else :
            checked_base_list.append("%s (%d)" %(base_func.name, base_func.len))

   
    for tar_func in target_list[:] :
        if tar_func.len < conf.WINDOW_SIZE :
            unchecked_target_list.append("%s (%d)" %(tar_func.name, tar_func.len))
            target_list.remove(tar_func)
        else :
            checked_target_list.append("%s (%d)" %(tar_func.name, tar_func.len))

    log.log_file_info(base, num_base, len(base_list), True)
    log.log_file_info(target, num_tar, len(target_list), False)

    score_result = [["0 (0)"]*len(target_list) for i in range(len(base_list))]

    log.log_count[0][0] = len(target_list) * len(base_list)
    log.log_count[1][0] = len(target_list) * len(base_list)
    log.log_count[0][1] = 0
    log.log_count[1][1] = 0

    for b_idx in tqdm(range(len(base_list)), desc="base", ncols=100) :
        base_func = base_list[b_idx]
        for t_idx in tqdm(range(len(target_list)), desc="\ttarget", ncols=100, leave=False) :
            tar_func = target_list[t_idx]
            if conf.EXCLUDING_LENGTH_DIFFERENCE and ut.length_check(base_func.len, tar_func.len) : 
                continue

            else :
                bin_res = compute_similarity(base_func, tar_func)
                if bool(bin_res):
                    
                    score = (int)((bin_res['length']/base_func.len)*100)
                    r_score = (int)((bin_res['length']/tar_func.len)*100)

                    score_result[b_idx][t_idx] = "%s (%s)"%(score, r_score)
                    
                    if score >= conf.RESULT_SCORE :
                        log.log_count[0][1] += 1
                    
                    if r_score >= conf.RESULT_SCORE :
                        log.log_count[1][1] += 1

    log.log_analysis_result()  
    score_result = pd.DataFrame(score_result, index=checked_base_list, columns=checked_target_list)
    score_result.to_csv(conf.RESULT_PATH+"\\[%sVS%s]F_result.csv" %(base, target))



def binclone_single_mode(file) :

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
        for jdx in tqdm(range(len(func_list)), desc="\ttarget", leave=False, ncols=100) :
            tar_func = func_list[jdx]
            
            if conf.EXCLUDING_LENGTH_DIFFERENCE and ut.length_check(base_func.len, tar_func.len) : 
                log.log_score(0)
                continue
            if base_func.name == tar_func.name : 
                log.log_score(0)
                continue
            
            if visit[idx][jdx] :
                score = score_result[idx][jdx]
                bin_res = dict()
                if base_func.name in backup :
                    if tar_func.name in backup[base_func.name].keys() :
                        bin_res = copy.deepcopy(backup[base_func.name][tar_func.name])
                
            else :
                bin_res = compute_similarity(base_func, tar_func)
                visit[jdx][idx] = True
                visit[idx][jdx] = True
                score = 0

                if bool(bin_res):
                    score = (int)(( bin_res['length']/base_func.len)*100)
                    r_score = (int)(( bin_res['length']/tar_func.len)*100)
                    
                    score_result[idx][jdx] = score
                    score_result[jdx][idx] = r_score

                    tmp = dict()
                    tmp["base_start"] = bin_res["target_start"]
                    tmp["target_start"] = bin_res["base_start"]
                    tmp["length"] = bin_res["length"]
                    if not tar_func.name in backup :
                        backup[tar_func.name] = dict()
                                  
                    backup[tar_func.name][base_func.name] = copy.deepcopy(tmp)
            
            if bool(bin_res) :
                bin_res['tar_name'] = tar_func.name
                bin_res['tar_len'] = tar_func.len
                bin_res['score'] = score
                rank.append(copy.deepcopy(bin_res))
            log.log_score(score)
            if conf.EXIST_FILTED_FUNCTIONS :
                if (base_func.name in filted_func) or (tar_func.name in filted_func) :
                    log.log_score(score, True)

        log.log_tmp_result(base_func.name, base_func.len, rank)
    
    
    log.log_analysis_result()
    score_result = pd.DataFrame(score_result, index=checked_func_list, columns=checked_func_list)
    score_result.to_csv(conf.RESULT_PATH+"\\[%s]result.csv" %(base))
  





if __name__ == "__main__" :


    if conf.MULTIPLE_COMPARE_MODE :
            

        base_list = ut.listdir(conf.BASE_SET_PATH)
        target_list = ut.listdir(conf.TARGET_SET_PATH)

        if conf.MULTIPLE_FAST_MODE :
            for idx in range(len(base_list)) :
                for jdx in range(idx + 1, len(base_list)) :
                    start_time = time.time()
                    print("Similarity check (%s vs %s) ----------------" %(base_list[idx], base_list[jdx]))
                    binclone_multiple_fast_mode(base_list[idx], base_list[jdx])
                    print("time : %f\n\n" %(time.time() - start_time))                    
        else :
            for base in base_list :
                for target in target_list :
                    if(base == target) :
                        continue
                    start_time = time.time()
                    print("Similarity check (%s vs %s) ----------------" %(base, target))
                    binclone_multiple_mode(base, target)
                    print("time : %f\n\n" %(time.time() - start_time))


    if conf.SINGLE_COMPARE_MODE :

        base_list = ut.listdir(conf.BASE_SET_PATH)
        for base in base_list :

            start_time = time.time()
            print("Similarity check (%s) ----------------" %(base))
            binclone_single_mode(base)
            print("time : %f\n\n" %(time.time() - start_time))

