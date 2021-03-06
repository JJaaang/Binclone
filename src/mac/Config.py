ROOT_PATH = "/Users/jjang/Desktop/Binclone"
BASE_SET_PATH = ROOT_PATH +"/IDA_DB/base"
QUERY_SET_PATH = ROOT_PATH +"/IDA_DB/target"
RESULT_PATH = ROOT_PATH +"/tmp_res"
LOG_PATH = RESULT_PATH + "/log"


WINDOW_SIZE = 20
S_MIN = 0.7

# Only output values of RESULT_SCORE or higher
RESULT_SCORE = 60

#When SINGLE_COMPARE_MODE is true, perform similarity analysis between functions within one file
SINGLE_COMPARE_MODE = False

# When MULTIPLE_COMPARE_MODE is true, perform analysis between different files
MULTIPLE_COMPARE_MODE = True

# Available in MULTIPLE_COMPARE_MODE and similarity analysis is performed within the base path
# output score and summary only
MULTIPLE_FAST_MODE = True

# When EXCLUDING_LENGTH_DIFFERENCE is true,
# the anlaysis is skipped if the difference between the two function is LENGTH_DIFFERENCE times
EXCLUDING_LENGTH_DIFFERENCE = False
LENGTH_DIFFERENCE = 2

EXIST_FILTED_FUNCTIONS = False
FILTED_FUNCTIONS_PATH = "/Users/jjang/Desktop/Binclone/filted"

