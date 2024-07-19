"""
calculation:

1) Accuracy
2) Range
3) Sensitivity
"""


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from numpy import mean
from numpy import absolute
import numpy as np

#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

class Parameters:

    def __init__(self,data_x,data_y) -> None:
        self.data_x = data_x
        self.data_y = data_y

        self.model_RLS = None
    #-------------------------------------------------------------------------------
    def linear_regression(self):

        self.x_one = sm.add_constant(self.data_x)
        self.model_RLS=sm.OLS(self.data_y, self.x_one).fit()
        self.model_RLS.summary()
    
    #-----------------------------------------------------------------------------------------------
    def accuracy(self):

        #define cross-validation method to use
        cv = KFold(n_splits=10, random_state=1, shuffle=True)

        #build multiple linear regression model
        model = LinearRegression()

        #use k-fold CV to evaluate model
        scores = cross_val_score(model, self.data_x, self.data_y , scoring='neg_root_mean_squared_error',
                                cv=cv, n_jobs=-1)

        value_accuracy = mean(absolute(scores))

        return value_accuracy
    #------------------------------------------------------------------------------------------------

    def dynamic_range(self):
         range_2 = np.max(self.data_y )
         range_1 = np.min(self.data_y)
         dyn_range = np.abs(range_2-range_1)
         return dyn_range
    #------------------------------------------------------------------------------------------------
    def sensitivity(self):
        self.linear_regression()
        sensi = np.abs(self.model_RLS.params[1])
        return sensi
    #------------------------------------------------------------------------------------------------
    def run(self):

        result_accuracy = self.accuracy()
        result_range = self.dynamic_range()
        result_sensitivity = self.sensitivity()

        return result_accuracy, result_range,result_sensitivity 
