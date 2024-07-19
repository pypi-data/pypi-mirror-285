"""
Calls all functions and classes to generate the complete analysis:
1) calculation of assumptions
2) quality of the regression

"""


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from art import text2art

from .outlier_detection import OutlierDetection
from .metrics import Metrics
from .parameters import Parameters
from .resolution import resolution
from .user_messages import parameters_messages
from .global_constants import BLUE,  RESET

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def sl_regression_quality(x,y,alpha,dL,y_extended):
    space_1 = '            '
    space_2 = '                  '
    art_text1 = text2art("SIMPLE    LINEAR") 
    art_text2 = text2art(space_1+"REGRESION")  
    art_text3 = text2art(space_2+"QUALITY")  
   
    print(art_text1)
    print(art_text2)
    print(art_text3)
    #------------------------------------------------------------------------------------
    # 1) part:
    print(BLUE+'===='*20+RESET)
    print(BLUE+'part 1, Assumption calculation: '+RESET)
    print(BLUE+'===='*20+RESET)
    print('part 1.1, outlier identification: ')
    new_x, new_y = OutlierDetection(x,y).run()
    print('----'*20)

    # 2) part:
    print('part 1.2, Verification of: ')
    enable_metrics = Metrics(new_x,new_y,alpha,dL).run()

    # 3) part:
    print(BLUE+'===='*20+RESET)

    if enable_metrics:
        print(BLUE+'part 2, Regression quality: '+RESET)
        print(BLUE+'===='*20+RESET)
        #------------------------------------------
        accuracy,d_range,sensitivity = Parameters(new_x,new_y).run()
        #------------------------------------------
        res_value = resolution(y_extended,alpha)
        #-----------------------------------------
        parameters_messages(accuracy,res_value,sensitivity,d_range)
    else:
        print('Not all metrics were met')