import Normalizer as norm
import Info as info
import Config as conf
import Util as ut



global M_median_vector
global M_idx_to_feature


def extract_feature(function) :

    func_info = info.FunctionInfo(function[0], len(function)-1)    # len(function) - 1 : substract the function name line

    # Extract the feature per region in form of dictionary 
    # region_sp : region start porin 
    for region_sp in range(1, len(function) - conf.WINDOW_SIZE  + 1) :
        
        # naive feature vector is an object that stores the name and frequency of a feature in dictionary form.
        navie_features = dict()

        for inst in function[region_sp : region_sp + conf.WINDOW_SIZE] :
            
            feature = inst.get_first_feature()
            if not feature in navie_features :
                navie_features[feature] = 1
            else :
                navie_features[feature] += 1

            operands = inst.get_second_feature()
            for feature in operands :
                if not feature in navie_features :
                    navie_features[feature] = 1
                else :
                    navie_features[feature] += 1

            feature = inst.get_third_feature()
            if feature != None :
                if not feature in navie_features :
                    navie_features[feature] = 1
                else :
                    navie_features[feature] += 1           

            feature = inst.get_fourth_feature()
            if feature != None :
                if not feature in navie_features :
                    navie_features[feature] = 1
                else :
                    navie_features[feature] += 1
        
        
        func_info.navie_features_list.append(navie_features)
        func_info.features |= set(navie_features.keys())
    
    return func_info



def preprocessing(path) :
    """
    This function conducts normalizing and extract feature
    and return list of FuncitonInfo class object 
    """
    
    
    norm_function_list = list()
    func_info_list = list()

    function_list = ut.listdir(path)

    for function in function_list :
        
        function_path = '%s\\%s' %(path, function)
        norm_function = norm.normalizer(function_path)
        func_info = extract_feature(norm_function)

        #add 1005
        name = function.split('.')[0]
        func_info.name = name 


        func_info_list.append(func_info)

    return func_info_list



def combine_feature(base_func, target_func) :
    global M_idx_to_feature
    M_idx_to_feature = list(base_func.features | target_func.features)
    


def make_feature_vector(function):

    # feature_vector_list is two-dementional list
    # row : region / columne : feature
    global M_idx_to_feature

    FV_list = list()


    for navie_features in function.navie_features_list :
        # feature vectors are fixed-length ordered numeric navie_feature vectors.
        FV = [0 for i in range(len(M_idx_to_feature))]
        
        region_features = navie_features.keys()

        for idx in range(len(M_idx_to_feature)) :
            feature = M_idx_to_feature[idx]
            if feature in region_features :
                freqeuncy = navie_features[feature]
            else :
                freqeuncy = 0
            FV[idx] = freqeuncy
        
        FV_list.append(FV)

    return FV_list



def compute_median(base_FV_list, tar_FV_list) :
    
    global M_median_vector


    if not len(base_FV_list[0]) == len(tar_FV_list[0]) :
        print("compute_median functio() - ERROR!!")
        exit()

    feature_num = len(base_FV_list[0])
    M_median_vector = [0]*feature_num
    
    for fidx in range(feature_num) :
        
        frequency_list = [0]*(len(base_FV_list)+len(tar_FV_list))
        lidx = 0
        
        for FV in base_FV_list :
            frequency_list[lidx] = FV[fidx]
            lidx += 1

        for FV2 in tar_FV_list :
            frequency_list[lidx] = FV2[fidx]
            lidx += 1
        
        frequency_list.sort()
        median = frequency_list[(int)(len(frequency_list)/2)]
        M_median_vector[fidx] = median

    


def make_binary_vector(FV_list) :
    
    global M_median_vector

    BV_list = list()

    for FV in FV_list :
        BV = list()
        for f_idx in range(len(M_median_vector)) :
            median = M_median_vector[f_idx]
            if median == 0 : continue
            else :
                if median > FV[f_idx] : 
                    BV.append(0)
                else :
                    BV.append(1)
        BV_list.append(BV)

    return BV_list


def compare_region_to_region(base_BV_list, tar_BV_list) :
    
    base_len = len(base_BV_list)
    tar_len = len(tar_BV_list)
    feature_num = len(base_BV_list[0])

    result_matrix = [[0]*tar_len for i in range(base_len)]
    num_of_feature = len(base_BV_list[0])
    
    for b_idx in range(base_len) :
        for t_idx in range(tar_len) :

            cnt = 0
            
            for idx in range(feature_num) :
                if base_BV_list[b_idx][idx] == tar_BV_list[t_idx][idx] :
                    cnt += 1
            
            if cnt > 0 :
                result_matrix[b_idx][t_idx] = cnt / num_of_feature
            else :
                result_matrix[b_idx][t_idx] = 0

    return result_matrix



def clone_merger(result_matrix) :

    base_len = len(result_matrix)
    tar_len = len(result_matrix[0])
    max_len = 0

    ut.CM_result_matrix = result_matrix
    ut.CM_visit = [[0]*tar_len for i in range(base_len)]

    # The elements of this list are in the form of a dictionary with
    # two starting line numbers and lenth as keys
    result = dict()

    for b_idx in range(base_len) :
        
        # Maximum possible length is less than max_len
        if base_len - max_len < b_idx : break
        
        for t_idx in range(tar_len) :
            
            # Maximum possible length is less than max_len
            if tar_len - max_len < t_idx : break
            if ut.CM_visit[b_idx][t_idx] == 1 : continue
            else :
                ut.CM_visit[b_idx][t_idx] == 1

            if ut.CM_result_matrix[b_idx][t_idx] > conf.S_MIN :
                tmp_len = 1 + ut.count_LCS(t_idx + 1, b_idx + 1)
                if tmp_len > max_len :
                    max_len = tmp_len
                    result["base_start"] = b_idx
                    result["target_start"] = t_idx
                    result["length"] = max_len + conf.WINDOW_SIZE - 1

    return result

