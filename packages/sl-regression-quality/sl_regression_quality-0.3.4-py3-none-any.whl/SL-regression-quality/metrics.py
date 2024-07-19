"""
Assumption calculation:
1) linearity
2) normality
3) homocedasticity
4) independence

"""


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import statsmodels.api as sm
from numpy.linalg import inv
from scipy import stats
import numpy as np

from statsmodels.compat import lzip
import statsmodels.stats.api as sms
from statsmodels.stats.stattools import durbin_watson
from global_constants import GREEN, RED,  RESET

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


class Metrics:
    def __init__(self,data_x,data_y,significance_level,value_dl) -> None:
        self.data_x = data_x
        self.data_y = data_y
        self.alpha = significance_level
        self.value_dl = value_dl

        self.model_RLS = None
        self.standardized_residuals = None
        self.studentized_residuals = None
        self.enable_outlier = False
        self.x_one = None


        #run linear regression:
        self.linear_regression()
#-------------------------------------------------------------------------------
    def linear_regression(self):

        self.x_one = sm.add_constant(self.data_x)
        self.model_RLS=sm.OLS(self.data_y, self.x_one).fit()
        self.model_RLS.summary()
#--------------------------------------------------------------------------
    def linearity(self):
        value_linearity =  self.model_RLS.f_pvalue


        #1) validation:
        if value_linearity < self.alpha:
            print('1.2.1)'+GREEN+'Satisfies linearity'+RESET)
            enable_linearity = True
        else:
            print('1.2.1)'+RED+'Does not satisfies linearity'+RESET)
            enable_linearity = False


        return  enable_linearity
#-------------------------------------------------------------------------------
    def normality(self):


        #main:
        XTr=self.x_one.transpose()
        XM=np.dot(XTr,self.x_one )
        iXM=inv(XM)
        Mxi=np.dot(self.x_one , iXM)
        H=np.dot(Mxi,XTr)
        yPred=np.dot(H,self.data_y)
        Res=self.data_y-yPred
        #perform Shapiro-Wilk Test
        value_normality = stats.shapiro(Res).pvalue

        #1) validation:
        if value_normality > self.alpha:
            print('1.2.2)'+GREEN+ 'Satisfies normality'+RESET)
            enable_normality = True
        else:
            print('1.2.2)'+RED+ 'Does not satisfies normality'+RESET)
            enable_normality = False

        return enable_normality
#----------------------------------------------------------------------------------
    def homocedasticity(self):

        names=['Lagrange multiplier statistic', 'p-value','f-value', 'f p-value']
        test=sms.het_breuschpagan(self.model_RLS.resid, self.model_RLS.model.exog)
        values = lzip(names, test)

        value_homocedasticity = values[1][1]

        #1) validation:
        if value_homocedasticity > self.alpha:
            print('1.2.3)'+GREEN+'Satisfies homoscedasticity'+RESET)
            enable_homocedasticity = True
        else:
            print('1.2.3)'+RED+ 'Does not satisfies homoscedasticity'+RESET)
            enable_homocedasticity = False

        return enable_homocedasticity

#-----------------------------------------------------------------------------------------

    def independence(self):
        value_dL = self.value_dl

        #main:
        value_independence = durbin_watson(self.model_RLS.resid)

        #1) validation:
        if value_independence  > value_dL:
            print('1.2.4)'+GREEN+ 'Satisfies independence '+RESET)
            enable_independence  = True
        else:
            print('1.2.4)'+RED+'Does not satisfies independence '+RESET)
            enable_independence  = False

        return enable_independence

#-----------------------------------------------------------------------------------------
    def run(self):
        print('----'*20)
        #1) linearity:
        enable_line = self.linearity()
        #2) normality:
        if enable_line:
            enable_norm = self.normality()

            if enable_norm:
                enable_homo = self.homocedasticity()

                if enable_homo:
                    enable_inde = self.independence()
                    return enable_inde
                else:
                    return False

            else:
                 return False
        else:
            return False