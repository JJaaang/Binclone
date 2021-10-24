import Config as conf
import os
import re
import pandas as pd
import copy
from tabulate import tabulate

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
    T_list = os.listdir(conf.TARGET_SET_PATH)

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
    tmp_pd.to_csv(conf.FILTED_PATH+"/%s_%s.csv" %(f_list[0].origin, func_info(f_list[0].name, "name")))

global Bin_similar_set
global Similar_set
global Filted_function


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
                Filted_function.update(tmp)
 
        Similar_set.append(tmp)

def analysis() :
    global Result
    global B_list
    global T_list
    global Function_list
    global Filted_function
    global Similar_set

    Filted_function = set()
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
    similar_result = pd.DataFrame(table, columns=B_list)
    similar_result.to_csv(conf.FILTED_PATH+"/result.csv")



if __name__ == "__main__" :
    if not os.path.exists(conf.ANLAYSIS_PATH):
        os.mkdir(conf.ANLAYSIS_PATH)

    if not os.path .exists(conf.FILTED_PATH) :
        os.mkdir(conf.FILTED_PATH)
    
    if not os.path.exists(conf.FILTED_PATH+"/func") :
        os.mkdir(conf.FILTED_PATH+"/func")


    read_result()
    analysis()
    