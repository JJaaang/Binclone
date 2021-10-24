import Config as conf

import copy
import os
import sys

sys.setrecursionlimit(100000)

global CM_result_matrix
global CM_visit

def count_LCS(c_idx, r_idx) :
    
    global CM_result_matrix
    global CM_visit

    if r_idx == len(CM_result_matrix) or c_idx == len(CM_result_matrix[0]) :
        return 0

    if CM_result_matrix[r_idx][c_idx] > conf.S_MIN :
        CM_visit[r_idx][c_idx] = 1
        return 1 + count_LCS(c_idx+1, r_idx+1)

    else : return 0


def listdir(path) :

    file_list = os.listdir(path)

    for function in file_list[:] :
        if function[0] == '.' :
            file_list.remove(function)

    return file_list


def length_check(len_A, len_B) :

    if len_A > len_B :
        if len_A > conf.LENGTH_DIFFERENCE * len_B :
            return True
    else :
        if len_B > conf.LENGTH_DIFFERENCE * len_A :
            return True
    
    return False


def filted_functions(file) :

    file_path = conf.FILTED_FUNCTIONS_PATH + "/" + file + ".txt"
    filted_func = list()
    if os.path.isfile(file_path) :
        with open(file_path, 'r') as fp :
            func_list = fp.readlines()
            filted_func = list(map(lambda s : s.strip(), func_list))
    
    return filted_func

