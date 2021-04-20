# Author: Meduri Venkata Shivaditya
import math
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import logsumexp
'''
t = Wx + µ + E
the equation above represents the latent variable model which 
relates a d-dimensional data vector t to a corresponding q-dimensional 
latent variables x 
with q < d, for isotropic noise E ∼ N (0, σ2I)
t : latent
x : data
W : latent_to_observation matrix
µ : centres_of_clusters
E : var_of_latent
Initially using Kmeans algorithm parameters are initialized before 
applying the expectation maximization 
algorithm for an estimate of the parameter values
'''


def mixture_ppca_parameter_initialization(data, n_clusters, latent_dim,
                                          n_iterations):
    """
    The k-means algorithm is used to determine the centres. The
	priors are computed from the proportion of examples belonging to each
	cluster. The covariance matrices are calculated as the sample
	covariance of the points associated with (i.e. closest to) the
	corresponding centres. For a mixture of PPCA model, the PPCA
	decomposition is calculated for the points closest to a given centre.
	This initialisation can be used as the starting point for training
	the model using the EM algorithm.
	W : latent_to_observation matrix
    µ/mu : centres_of_clusters
    pi : proportion of data in each cluster
    sigma2 : variance of latent
    covars : The covariance matrices are calculated as the sample
	covariance of the points associated with (i.e. closest to) the
	corresponding centres
    """
    n_datapts, data_dim = data.shape
    # initialization of the centres of clusters
    init_centers = np.random.randint(0, n_datapts, n_clusters)
    # Randomly choose distinct initial centres for the clusters
    while (len(np.unique(init_centers)) != n_clusters):
        init_centers = np.random.randint(0, n_datapts, n_clusters)
    mu = data[init_centers, :]
    distance_square = np.zeros((n_datapts, n_clusters))
    clusters = np.zeros(n_datapts, dtype=np.int32)
    # Running iterations for K means algorithm to assign centres for clusters
    for k in range(n_iterations):
        # assign clusters
        for c in range(n_clusters):
            distance_square[:, c] = np.power(data - mu[c, :], 2).sum(1)
        clusters = np.argmin(distance_square, axis=1)
        # compute distortion
        distmin = distance_square[range(n_datapts), clusters]
        # compute new centers
        for c in range(n_clusters):
            mu[c, :] = data[clusters == c, :].mean(0)
    covars = np.zeros(n_clusters)
    for i in range(n_clusters):
        covars[i] = (np.var(data[clusters == i, 0]) +
                     np.var(data[clusters == i, 1])) / 2
    # parameter initialization
    pi = np.zeros(n_clusters)  # Sum should be equal to 1
    W = np.zeros((n_clusters, data_dim, latent_dim))
    sigma2 = np.zeros(n_clusters)
    for c in range(n_clusters):
        W[c, :, :] = np.random.randn(data_dim, latent_dim)
        pi[c] = (clusters == c).sum() / n_datapts
        sigma2[c] = (distmin[clusters == c]).mean() / data_dim
    return pi, mu, covars, W, sigma2, clusters


def mixture_ppca_expectation_maximization(data, pi, mu, W, simga2, niter):
    '''
       we can find the p(latent|data) with the assumption that data is gaussian
       t : latent
       x : data
       W : latent_to_observation matrix
       µ/mu : centres_of_clusters
       d : data_dimension
       q : latent_dimention
       σ2/ simga2 : variance of latent
       π/pi : cluster proportion
       p(t|x) = (2πσ2)^−d/2 * exp(−1/(2σ2) * ||t − Wx − µ||)
       p(t) = ∫p(t|x)p(x)dx
       Solving for p(t) and then using the result we can find the p(x|t)
       through which we can find
       the log likelihood function which is
       log_likelihood = −N/2 * (d ln(2π) + ln |Σ| + tr(Σ−1S))
       We can develop an iterative EM algorithm for
       optimisation of all of the model parameters µ,W and σ2
       If Rn,i = p(tn, i) is the posterior responsibility of
       mixture i for generating data point tn,given by
       Rn,i = (p(tn|i) * πi) / p(tn)
       Using EM, the parameter estimates are as follows:
       µi = Σ (Rn,i * tn) / Σ Rn,i
       Si = 1/(πi*N) * ΣRn,i*(tn − µi)*(tn − µi)'
       Using Si we can estimate W and σ2
       For more information on EM algorithm for mixture of PPCA
       visit Mixtures of Probabilistic Principal Component Analysers
       by Michael E. Tipping and Christopher M. Bishop:
       page 5-7 of http://www.miketipping.com/papers/met-mppca.pdf
    '''
    n_datapts, data_dim = data.shape
    n_clusters = len(simga2)
    _, latent_dim = W[0].shape
    M = np.zeros((n_clusters, latent_dim, latent_dim))
    Minv = np.zeros((n_clusters, latent_dim, latent_dim))
    Cinv = np.zeros((n_clusters, data_dim, data_dim))
    logR = np.zeros((n_datapts, n_clusters))
    R = np.zeros((n_datapts, n_clusters))
    M[:] = 0.
    Minv[:] = 0.
    Cinv[:] = 0.
    log_likelihood = np.zeros(niter)

    for i in range(niter):
        print('.', end='')
        for c in range(n_clusters):
            # M
            '''
             M = σ2I + WT.W
            '''
            M[c, :, :] = simga2[c] * np.eye(latent_dim) + np.dot(W[c, :, :].T, W[c, :, :])

            Minv[c, :, :] = np.linalg.inv(M[c, :, :])

            # Cinv
            Cinv[c, :, :] = (np.eye(data_dim)
                             - np.dot(np.dot(W[c, :, :], Minv[c, :, :]), W[c, :, :].T)
                             ) / simga2[c]

            # R_ni
            deviation_from_center = data - mu[c, :]
            logR[:, c] = (np.log(pi[c])
                          + 0.5 * np.log(
                        np.linalg.det(
                            np.eye(data_dim) - np.dot(np.dot(W[c, :, :],
                                                             Minv[c, :, :]), W[c, :, :].T)
                        )
                    )
                          - 0.5 * data_dim * np.log(simga2[c])
                          - 0.5 * (deviation_from_center * np.dot(deviation_from_center,
                                                                  Cinv[c, :, :].T)).sum(1)
                          )

        myMax = logR.max(axis=1).reshape((n_datapts, 1))
        log_likelihood[i] = (
                (myMax.ravel() + logsumexp(logR - myMax, axis=1)).sum(axis=0)
                - n_datapts * data_dim * np.log(2 * math.pi) / 2.
        )

        logR = logR - myMax - np.reshape(logsumexp(logR - myMax, axis=1),
                                         (n_datapts, 1))

        myMax = logR.max(axis=0)
        logpi = myMax + logsumexp((logR - myMax), axis=0) - np.log(n_datapts)
        logpi = logpi.T
        pi = np.exp(logpi)
        R = np.exp(logR)
        for c in range(n_clusters):
            mu[c, :] = (R[:, c].reshape((n_datapts, 1)) * data).sum(axis=0) / R[:, c].sum()
            deviation_from_center = data - mu[c, :].reshape((1, data_dim))
            '''
            Si = 1/(πi*N) * ΣRn,i*(tn − µi)*(tn − µi)'
            Si is used to estimate 
            '''
            Si = ((1 / (pi[c] * n_datapts))
                  * np.dot((R[:, c].reshape((n_datapts, 1)) * deviation_from_center).T,
                           np.dot(deviation_from_center, W[c, :, :]))
                  )

            Wnew = np.dot(Si, np.linalg.inv(simga2[c] * np.eye(latent_dim)
                                            + np.dot(np.dot(Minv[c, :, :], W[c, :, :].T), Si)))

            simga2[c] = (1 / data_dim) * (
                    (R[:, c].reshape(n_datapts, 1) * np.power(deviation_from_center, 2)).sum()
                    /
                    (n_datapts * pi[c])
                    -
                    np.trace(np.dot(np.dot(Si, Minv[c, :, :]), Wnew.T))
            )

            W[c, :, :] = Wnew

    return pi, mu, W, simga2, log_likelihood


def generate_data():
    n = 500
    r = np.random.rand(1, n) + 1
    theta = np.random.rand(1, n) * (2 * math.pi)
    x1 = r * np.sin(theta)
    x2 = r * np.cos(theta)
    X = np.vstack((x1, x2))
    return np.transpose(X)


def mixppcademo(data, n_clusters):
    '''
    W : latent to observation matrix
    mu : centres_of_clusters
    covars : variance of the data for each cluster
    pi : proportions of data in each of the cluster
    sigma2 : variance of latent
    L : log likelihood after each iteration
    '''
    plt.plot(data[:, 0], data[:, 1], 'o', c='blue', mfc='none')
    pi, mu, covars, W, sigma2, clusters = mixture_ppca_parameter_initialization(
        data, n_clusters, latent_dim=1, n_iterations=10)
    pi, mu, W, sigma2, L = mixture_ppca_expectation_maximization(data, pi, mu,
                                                                 W, sigma2, 10)
    for i in range(n_clusters):
        v = W[i, :, :]
        start = mu[i].reshape((2, 1)) - (v * np.sqrt(sigma2[i]))
        endpt = mu[i].reshape((2, 1)) + (v * np.sqrt(sigma2[i]))
        linex = [start[0], endpt[0]]
        liney = [start[1], endpt[1]]
        plt.plot(linex, liney, linewidth=3, c='black')
        theta = np.arange(0, 2 * math.pi, 0.02)
        x = np.sqrt(sigma2[i]) * np.cos(theta)
        y = np.sqrt(covars[i]) * np.sin(theta)
        rot_matrix = np.vstack((np.hstack((v[0], -v[1])), np.hstack((v[1], v[0]))))
        ellipse = np.dot(rot_matrix, np.vstack((x, y)))
        ellipse = np.transpose(ellipse)
        ellipse = ellipse + np.dot(np.ones((len(theta), 1)), mu[i, :].reshape((1, 2)))
        plt.plot(ellipse[:, 0], ellipse[:, 1], c='crimson')


def main():
    np.random.seed(61)
    data = generate_data()
    plt.figure(0)
    mixppcademo(data, n_clusters=1)
    plt.savefig("mixppca_k-1.png", dpi=300)
    np.random.seed(7)
    data = generate_data()
    plt.figure(1)
    mixppcademo(data, n_clusters=10)
    plt.savefig("mixppca_k-10.png", dpi=300)
    plt.show()


if __name__ == "__main__":
    main()
