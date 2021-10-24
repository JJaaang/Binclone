import sys
from typing import SupportsAbs
import Config as conf
import os
import re
import pandas as pd
import copy
from tabulate import tabulate

sys.path.append("/Users/jjang/Desktop/Binclone/binclone/src/mac/")
import BinClone as bc
import Util as ut
import Bincore as bin


global Result
global B_list
global T_list
global Function_list

class Tar_Info :
    origin = ""
    name = ""
    length = 0
    score = 0
    r_score = 0

    def __init__(self, origin, name, length, score, r_score) :
        self.origin = origin
        self.name = name
        self.length = length
        self.score = 0
        self.r_score = 0

def func_info(line, item) :
    p = re.compile("(?P<name>\w+)\s+[(]+(?P<len>\d+)[)]")
    m = p.match(line)

    return m.group(item)


def read_result() :

    global Result
    global B_list
    global T_list
    global Function_list   
    
    Result = dict()
    Function_list = dict()
    checked = dict()
    
    B_list = os.listdir(conf.BASE_SET_PATH)
    T_list = os.listdir(conf.BASE_SET_PATH)

    for base in B_list[:] :
        if base[0] == '.' :
            B_list.remove(base)
    for tar in T_list[:] :
        if tar[0] == '.' :
            T_list.remove(tar)

    for item in set(B_list + T_list) :
        checked[item] = False
    

    for base in B_list :
        tmp_result_list = dict()
        for tar in T_list :

            if base == tar : continue

            path = conf.RESULT_PATH + "/[%sVs%s]result.csv" %(base, tar)
            res = pd.read_csv(path, index_col=0)
            
            if not checked[base] :
                Function_list[base] = res.index.tolist()
                checked[base] = True
            
            if not checked[tar] :
                Function_list[tar] = res.columns.tolist()
                checked[tar] = True
                
            tmp_result_list[tar] = res

        Result[base] = tmp_result_list

def make_similar_table(f_list) :
    global Result

    length = len(f_list)
    res = [[0]*length for i in range(length)]

    idx = list()

    for item in f_list :
        idx.append("[%s]%s" %(item.origin, item.name))

    for i in range(length) :
        for j in range(length) :
            if i == j :
                res[i][j] = '-'
                continue
            else :
                base = f_list[i]
                tar = f_list[j]
                if base.origin == tar.origin :
                    res[i][j] = '-'
                    continue
                
                else :
                    res[i][j] = Result[base.origin][tar.origin].loc[base.name][tar.name]

    tmp_pd = pd.DataFrame(res, index=idx, columns=idx)
    tmp_pd.to_csv(conf.STEP1_PATH+"/log/%s_%s.csv" %(f_list[0].origin, func_info(f_list[0].name, "name")))

global Bin_similar_set
global Similar_set
global Filted_function
global Similar_result


def duplication_check(checked) :
    global Bin_similar_set
    cnt = checked.count(1)

    # compare the numComparing the number of selected item considering the order
    for ss in Bin_similar_set[:] :
        rm = 0
        for i in range(len(checked)) :
            if checked[i] == ss[i] : rm += 1
        
        # new checked is included in the existing similar set.
        # example : new {a, b} is included in existing {a, b, c}
        if rm == cnt :
            return False

        # the existing similar set is included in the new checked
        # example : existing {a, b} is included in the new {a, b, c}
        elif rm == ss.count(1) :
            Bin_similar_set.remove(ss)
            return True    
    return True


def compute_set(checked, idx, f_list, cnt) :
    
    global Bin_similar_set
    global Result

    if idx == len(f_list) :
        if cnt > 1 and duplication_check(checked) :  
            Bin_similar_set.append(copy.deepcopy(checked))
            return
    
    else :
        #choose
        validity = True
        now = f_list[idx]
        for i in range(0,idx) :
            if checked[i] :
                choosed = f_list[i]

                # origin check
                if now.origin == choosed.origin :
                    validity = False
                    break
                
                # score check
                else :
                    score = Result[now.origin][choosed.origin].loc[now.name][choosed.name]
                    r_score = Result[choosed.origin][now.origin].loc[choosed.name][now.name]    
                    if (score < conf.SCORE or r_score < conf.SCORE) :
                        validity = False
                        break
        
        if validity :
            checked[idx] = 1
            compute_set(checked, idx+1, f_list, cnt+1)
            checked[idx] = 0

        # not choose
        compute_set(checked, idx+1, f_list, cnt)

def compute_similar_set(f_list) :
    global Bin_similar_set
    global Filted_function
    global Similar_set

    Bin_similar_set = list()
    checked = [0] * len(f_list)
    checked[0] = 1
    compute_set(checked, 1, f_list, 1)

    num = len(f_list)
    for ss in Bin_similar_set :
        tmp = list()
        for idx in range(num) :
            if ss[idx] :
                tmp.append(f_list[idx])

        if len(tmp) > 1 :
            for new in tmp :
                new_flag = True
                for ff in Filted_function :
                    if ff.name == new.name and ff.origin == new.origin :
                        new_flag = False
                        break
                if new_flag :
                    Filted_function.append(new)
            Similar_set.append(tmp)

def analysis() :
    global Result
    global B_list
    global T_list
    global Function_list
    global Filted_function
    global Similar_set
    global Similar_result

    Filted_function = list()
    Similar_set = list()

    for base in B_list :
        b_func_list = Function_list[base]
        base_result = dict()

        for bf in b_func_list :
            bf_res = list()
            bf_len = int(func_info(bf, "len"))

            for tar in T_list :
                if tar == base : continue
                
                t_func_list = Function_list[tar]
                for tf in t_func_list :
                    tf_len = int(func_info(tf, "len"))

                    if  bf_len > tf_len :
                        if bf_len >  2 * tf_len : continue
                    
                    else :
                        if tf_len > 2 * bf_len : continue
                
                    score = Result[base][tar].loc[bf][tf]
                    r_score = Result[tar][base].loc[tf][bf]
                    if score >= conf.SCORE and r_score >= conf.SCORE :
                        bf_res.append(Tar_Info(tar, tf, tf_len, score, r_score))
            
            if len(bf_res) > 0 :
                make_similar_table([Tar_Info(base, bf, bf_len, 100, 100)] + bf_res)
                compute_similar_set([Tar_Info(base, bf, bf_len, 100, 100)] + bf_res)

    # print out the Similar_set list
    table = list()
    tmp = list()
    for ss in Similar_set :
        tmp = ['-'] * len(B_list)
        for func in ss :
            idx = B_list.index(func.origin)
            tmp[idx] = func.name
        if not tmp in table :
            table.append(tmp)
    Similar_result = pd.DataFrame(table, columns=B_list)
    Similar_result.to_csv(conf.STEP1_PATH+"/similar_set.csv")


def file_move() :
    global Filted_function

    for func in Filted_function :
        file_name = func.origin
        func_name = func_info(func.name, "name")

        file_path = conf.BASE_SET_PATH+"/%s/%s.txt" %(file_name, func_name)
        tar_path = "%s/filted_functions/%s-%s" %(conf.STEP1_PATH, file_name, func_name)
        os.system("cp %s %s" %(file_path, tar_path))

global Similar_base_list


def binclone_for_analysis() :

    global Similar_base_list

    base_path = conf.STEP1_PATH+"/filted_functions"
    base_list = bin.preprocessing(base_path)
    checked_base_list = list()

    Similar_base_list = list()

    for base_func in base_list[:] :
        if base_func.len < conf.WINDOW_SIZE :
            base_list.remove(base_func)
        else :
            checked_base_list.append(base_func)

    target_list = ut.listdir(conf.TARGET_SET_PATH)
    
    for tar in target_list :
        target_path  = "%s/%s" %(conf.TARGET_SET_PATH, tar)
        target_list = bin.preprocessing(target_path)
        checked_target_list = list()

        for tar_func in target_list[:] :
            if tar_func.len < conf.WINDOW_SIZE :
                target_list.remove(tar_func)
            else :
                checked_target_list.append(tar_func)
        
        score_result = [[0]*len(target_list) for i in range(len(base_list))]

        for b_idx in range(len(base_list)) :

            base_func = base_list[b_idx]

            for t_idx in range(len(target_list)) :

                tar_func = target_list[t_idx]
                bin_res = bc.compute_similarity(base_func, tar_func)

                if len(bin_res) > 0 :

                    score = (int)((bin_res[0]['length']/base_func.len)*100)
                    score_result[b_idx][t_idx] = score
                    if score > 60 :
                        if not base_func.name in Similar_base_list :
                            Similar_base_list.append(base_func)

        score_result = pd.DataFrame(score_result, index=checked_base_list, columns=checked_target_list)
        score_result.to_csv(conf.STEP2_PATH+"/log/[%sVS%s]result.csv" %(base_func.name, tar_func.name))

    return Similar_base_list


def start_step1() :

    if not os.path.exists(conf.STEP1_PATH) :
        os.mkdir(conf.STEP1_PATH)

    if not os.path .exists(conf.STEP1_PATH + "/filted_functions") :
        os.mkdir(conf.STEP1_PATH + "/filted_functions")
    
    if not os.path.exists(conf.STEP1_PATH+"/log") :
        os.mkdir(conf.STEP1_PATH+"/log")

    read_result()
    analysis()
    file_move()


def start_step2():

    global Similar_base_list
    global Similar_result

    if not os.path.exists(conf.STEP2_PATH) :
        os.mkdir(conf.STEP2_PATH)

    if not os.path.exists(conf.STEP2_PATH+"/log") :
        os.mkdir(conf.STEP2_PATH+"/log")   


    # preprocessing
    filted_function_list = bin.preprocessing(conf.STEP1_PATH + "/filted_functions")
    
    norm_names = ut.listdir(conf.TARGET_SET_PATH)
    normals = dict()
    for norm in norm_names :
        normals[norm] = bin.preprocessing("%s/%s" %(conf.TARGET_SET_PATH, norm))


    # for all fileted funcitons
    for filted_func in filted_function_list :
        
        # filted function parsing
        tokens = filted_func.name.split('-')
        origin = tokens[0]
        name = "%s (%d)" %(tokens[1], filted_func.len)

        log = list()

        # compare all normal file 
        for norm in normals :
            for norm_func in normals[norm] :

                if norm_func.len < conf.WINDOW_SIZE :
                    continue

                bin_res = bc.compute_similarity(filted_func, norm_func)
                if len(bin_res) > 0 :
                    score = (int)((bin_res[0]['length']/filted_func.len)*100)
                
                    if score > conf.SCORE :
                        log.append("[%s] %s (%d): %d\n" %(norm, norm_func.name, norm_func.len, score))
        
        # If there is a normal file function similar to the current filted function,
        if len(log) > 0 :
            
            # first write log file
            fp = open(conf.STEP2_PATH+"/log/%s-%s" %(origin, name), 'w')
            for line in log :
                fp.write(line)

            # second remove the set containing the function from Similar result
            idx = Similar_result[Similar_result[origin] == name].index
            Similar_result.drop(idx, inplace=True)

    Similar_result.to_csv(conf.STEP2_PATH+"/similar_set.csv")    
    

if __name__ == "__main__" :
    if not os.path.exists(conf.ANLAYSIS_PATH):
        os.mkdir(conf.ANLAYSIS_PATH)
    
    start_step1()
    start_step2()

