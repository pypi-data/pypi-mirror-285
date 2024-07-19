"""
example code for data analysis
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import pandas as pd 
from .main_routine import regression_quality

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


dataset = pd.read_csv('../data/Data_carne_new.csv')
df = pd.read_csv('../data/pruebaResolu.csv')
alpha = 0.05
dL = 1.055

# Total:
x=dataset.iloc[:27,1:2].values
y=dataset.iloc[:27,2:3].values
y_res = df.iloc[:,3:6].values

# does not independence

# x=dataset.iloc[:25,0:1].values
# y=dataset.iloc[:25,2:3].values


#================================================================================

regression_quality(x,y,alpha,dL,y_res)
