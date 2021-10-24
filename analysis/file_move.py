import Config as conf
import os

path = "target.txt"

if not os.path.exists(conf.FILTED_PAHT) :
    os.mkdir(conf.FILTED_PAHT)


with open(path, 'r') as fp :
    lines = fp.readlines()

    for line in lines :
        line = line.strip('\n&[')
        line = line.replace(']', ' ')
        token = line.split(' ')
        file_name = token[0]
        func_name = token[1]

        file_path = conf.BASE_SET_PATH+"\\%s\\%s.txt" %(file_name, func_name)
        tar_path = "%s-%s" %(file_name, func_name)
        os.system("mv %s %s" %(file_path, tar_path))