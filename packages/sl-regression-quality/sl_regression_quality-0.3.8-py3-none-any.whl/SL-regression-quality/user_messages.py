from global_constants import CYAN,  RESET, BLUE


def parameters_messages(accuracy,resolution,sensitivity,range):
    
    print(f'2.1) Accuracy value:'+CYAN+ f'{round(accuracy,6)}'+RESET)
    print(f'2.2) Resolution value:' +CYAN+ f'{round(resolution,6)}'+RESET)
    print(f'2.3) Sensitivity value:' +CYAN+ f'{round(sensitivity,6)}'+RESET)
    print(f'2.4) Dynamic range:' +CYAN+ f'{round(range,6)}'+RESET)
    print(BLUE+'===='*20+RESET)