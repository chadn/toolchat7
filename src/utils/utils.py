
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def dbg_important(msg: str, plain_str: str = ''):
    print_color(bcolors.OKCYAN, msg, plain_str)

def success(msg: str, plain_str: str = ''):
    print_color(bcolors.OKGREEN, msg, plain_str)

def warn(msg: str, plain_str: str = ''):
    print_color(bcolors.WARNING, msg, plain_str)

def error(msg: str, plain_str: str = ''):
    print_color(bcolors.FAIL, msg, plain_str)

def print_color(color: str, message: str, plain_str: str = ''):
    plain_str = f": {plain_str}" if plain_str else ''
    print(f"{color}{message}{bcolors.ENDC}{plain_str}", flush=True)

