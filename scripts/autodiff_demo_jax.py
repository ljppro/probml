# -*- coding: utf-8 -*-
"""autodiff_demo_jax.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fOGAmlA4brfHL_5qcUfsQKsy7BCuuTCS
"""

# illustrate automatic differentiation using jax
# https://github.com/google/jax
import superimport

import numpy as np # original numpy
import jax.numpy as jnp
from jax import grad, hessian

np.random.seed(42)
D = 5
w = np.random.randn(D) # jax handles RNG differently

x = np.random.randn(D)
y = 0 # should be 0 or 1

def sigmoid(x): return 0.5 * (jnp.tanh(x / 2.) + 1)

#d/da sigmoid(a) = s(a) * (1-s(a))
deriv_sigmoid = lambda a: sigmoid(a) * (1-sigmoid(a))
deriv_sigmoid_jax = grad(sigmoid)
a0 = 1.5
assert jnp.isclose(deriv_sigmoid(a0), deriv_sigmoid_jax(a0))

# mu(w)=s(w'x), d/dw mu(w) = mu * (1-mu) .* x
def mu(w): return sigmoid(jnp.dot(w,x))
def deriv_mu(w): return mu(w) * (1-mu(w)) * x
deriv_mu_jax =  grad(mu)
assert jnp.allclose(deriv_mu(w), deriv_mu_jax(w))

# NLL(w) = -[y*log(mu) + (1-y)*log(1-mu)]
# d/dw NLL(w) = (mu-y)*x
def nll(w): return -(y*jnp.log(mu(w)) + (1-y)*jnp.log(1-mu(w)))
#def deriv_nll(w): return -(y*(1-mu(w))*x - (1-y)*mu(w)*x)
def deriv_nll(w): return (mu(w)-y)*x
deriv_nll_jax = grad(nll)
assert jnp.allclose(deriv_nll(w), deriv_nll_jax(w))


# Now do it for a batch of data


def predict(weights, inputs):
    return sigmoid(jnp.dot(inputs, weights))

def loss(weights, inputs, targets):
    preds = predict(weights, inputs)
    logprobs = jnp.log(preds) * targets + jnp.log(1 - preds) * (1 - targets)
    return -np.sum(logprobs)

             
N = 3
X = np.random.randn(N, D)
y = np.random.randint(0, 2, N)

from jax import vmap
from functools import partial

preds = vmap(partial(predict, w))(X)  
preds2 = vmap(predict, in_axes=(None, 0))(w, X)
preds3 = [predict(w, x) for x in X]
preds4 = predict(w, X)
assert jnp.allclose(preds, preds2)
assert jnp.allclose(preds, preds3)
assert jnp.allclose(preds, preds4)

grad_fun = grad(loss)
grads = vmap(partial(grad_fun, w))(X,y)
assert grads.shape == (N,D)
grads2 = jnp.dot(np.diag(preds-y), X)
assert jnp.allclose(grads, grads2)

grad_sum = jnp.sum(grads, axis=0)
grad_sum2 = jnp.dot(np.ones((1,N)), grads)
assert jnp.allclose(grad_sum, grad_sum2)

# Now make things go fast
from jax import jit

grad_fun = jit(grad(loss))
grads = vmap(partial(grad_fun, w))(X,y)
assert jnp.allclose(grads, grads2)


# Logistic regression
H1 = hessian(loss)(w, X, y)
mu = predict(w, X)
S = jnp.diag(mu * (1-mu))
H2 = jnp.dot(np.dot(X.T, S), X)
assert jnp.allclose(H1, H2)