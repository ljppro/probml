import pyprobml_utils as pml

import matplotlib.pyplot as plt 
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import HuberRegressor
import numpy as np
import pandas as pd
from statsmodels.miscmodels.tmodel import TLinearModel
import statsmodels.api as sm

#!pip install statsmodels

"""Dataset according to the matlab code and book"""

np.random.seed(1) 
x = np.random.uniform(low=0.3, high=1.1, size=(10,)) 
x = x.flatten()
x = np.sort(x)

y = (np.random.rand(len(x))-0.5 + 1 + 2*x)
y = y.flatten()
y = np.sort(y)

x = np.append(x, 0.1)
x = np.append(x, 0.5)
x = np.append(x, 0.9)
x = x.reshape(-1, 1)

y = np.append(y, -5)
y = np.append(y, -5)
y = np.append(y, -5)
y = y.reshape(-1, 1)

x_test = np.arange(0, 1.1, 0.1)
x_test = x_test.reshape((len(x_test), 1))

xmax = 1 #np.max(x)
xmin = 0 #np.min(x)
ymax = 4 #np.max(y) 
ymin = -6 #np.min(y)

"""L2"""

reg1 = LinearRegression()

model1 = reg1.fit(x, y)
y_pred1 = model1.predict(x_test)

"""Huber"""

reg2 = HuberRegressor(epsilon = 1.0)

model2 = reg2.fit(x, y)
y_pred2 = model2.predict(x_test)

"""L1"""

def MAE_weights_updation(m, b, X, Y, learning_rate):
    m_deriv = 0
    b_deriv = 0
    N = len(X)
    for i in range(N):
        # Calculate partial derivatives
        m_deriv += - X[i] * (Y[i] - (m*X[i] + b)) / abs(Y[i] - (m*X[i] + b))
        b_deriv += -(Y[i] - (m*X[i] + b)) / abs(Y[i] - (m*X[i] + b))

    # Updating in direction of steepest ascent
    m -= (m_deriv / float(N)) * learning_rate
    b -= (b_deriv / float(N)) * learning_rate

    return m, b

m_new = 1
b_new = 1
learning_rate = 0.1
epochs = 100

for i in range(epochs):
  m_old, b_old = m_new, b_new 
  m_new, b_new = MAE_weights_updation(m_old, b_old, x, y, learning_rate)

y_pred4 = m_new*x_test + b_new

"""Student-t"""

dfx = pd.DataFrame(x, columns = ['x'])
dfy = pd.DataFrame(y, columns = ['y'])
exog = sm.add_constant(dfx['x'])
endog = dfy['y']

tmodel = TLinearModel(endog, exog)
results = tmodel.fit(df=0.6)

dft = pd.DataFrame(x_test, columns = ['test'])

ypred_t = np.dot(dft, results.params[1]) + results.params[0] #results.predict(dft)

plt.xlim(xmin, xmax)
plt.ylim(ymin, ymax)
plt.yticks(np.arange(ymin, ymax, 1.0))
plt.scatter(x, y, color="none", edgecolor="black")
plt.plot(x_test, y_pred1, '-.', color='black') #Least squares
plt.plot(x_test, y_pred2, '--', color='green') #Huber
plt.plot(x_test, ypred_t, color='red')         #student
plt.plot(x_test, y_pred4, '--', color='blue')  #Laplace
plt.legend(["Least squares", "Huber, \u0394 =1", "Student-t, \u03BD =0.6", "Laplace"])
pml.save_fig('Robust.png')
plt.savefig('Robust.png')
plt.show()
