"class for outlier detection"


#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt 

from global_constants import GREEN, RED,  RESET
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++





class OutlierDetection:

    def __init__(self,data_x,data_y) -> None:
        self.data_x = data_x
        self.data_y = data_y

        self.model_RLS = None
        self.standardized_residuals = None
        self.studentized_residuals = None
        self.enable_outlier = False

    def linear_regression(self):

        x_one = sm.add_constant(self.data_x)
        self.model_RLS=sm.OLS(self.data_y, x_one).fit()
        self.model_RLS.summary()

    def outlier_detection(self):

        #1) linear regression:
        self.linear_regression()

        #2) main:
        estandard =self.model_RLS.get_influence()
        self.standardized_residuals = estandard.resid_studentized_internal


        studentized_resid = self.model_RLS.outlier_test()
        self.studentized_residuals = studentized_resid[:,0]

        #3) validation
        size_data = self.standardized_residuals.shape[0]
        index_outlier = []
        limit_outlier = 3

        for idx_data in range(size_data ):

            if (np.abs(self.standardized_residuals[idx_data]) >= limit_outlier) and (np.abs(self.studentized_residuals[idx_data]) >=limit_outlier):
                index_outlier.append(idx_data)
                self.enable_outlier = True


        if self.enable_outlier:
            print('----'*20)
            print('Contains outlier: ')
            print(f'The following indices'+RED+ f'{index_outlier}'+RESET +'of the data x and y are deleted')

            new_x, new_y = self.elimination_outliers(index_outlier)

            return new_x, new_y
        else:
            print('----'*20)
            print(GREEN+'Does not contain outlier'+RESET)
            return self.data_x, self.data_y





    def elimination_outliers(self,idx_outlier):


        #1) elimination outliers:
        new_data_x = np.delete(self.data_x, idx_outlier, axis=0)
        new_data_y = np.delete(self.data_y, idx_outlier, axis=0)
        return new_data_x, new_data_y

    def run(self):

        x_final, y_final  = self.outlier_detection()

        return x_final, y_final


    def visualization(self):

        #run outlier detection:
        self.outlier_detection()


        #visualization
        plt.scatter(self.data_x,self.standardized_residuals)
        plt.xlabel('x', fontsize=18)
        plt.ylabel('Standardized Residuals', fontsize=18)
        plt.axhline(y=-2, color='black', linestyle='--', linewidth=1)
        plt.axhline(y=2, color='black', linestyle='--', linewidth=1)
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.show()



        plt.scatter(self.data_x,self.studentized_residuals)
        plt.xlabel('x', fontsize=18)
        plt.ylabel('Studentized Residuals', fontsize=18)
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)
        plt.axhline(y=-2, color='black', linestyle='--', linewidth=1)
        plt.axhline(y=2, color='black', linestyle='--', linewidth=1)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.show()