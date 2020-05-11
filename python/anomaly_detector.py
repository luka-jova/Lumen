import numpy as np
import pandas as pd #needed for debugging input

#estimateGaussian Estimates parameters of a Gausssian distribution for the dataset X
#input arguments:
	#X - n.o.examples * n.o.features -> dataset
#output:
	#mu - row vector - 1 * n.o. features -> contains mean value for each feature
	#sigma2 - row vector - 1 * n.o. features -> contains variance (std. deviation squared) for each feature
def estimateGaussian(X):
	m, n = X.shape
		
	mu = np.sum(X, 0) / m
	sigma2 = sum((X - mu) ** 2, 0) / m
	
	return mu, sigma2

#estimateMultivariateGaussian - Estimate parameters of a Multivariate Gaussian distribution for the dataset X
#input arguments:
	#X - n.o.examples * n.o.features -> dataset
#output:
	#mu - row vector - 1*n.o.features -> mean value for each feature
	#Sigma2 - n.o.features * n.o.features -> Covariance matrix
def estimateMultivariateGaussian(X):
	m, n = X.shape
	mu = np.sum(X, 0) / m
	Sigma2 = 1/m * X.T @ X
	return mu, Sigma2

#multivariateGaussian - Calculate probability density function for examples in dataset X, 
#given parameters of expected normal distribution
#input:
	#X - n.o.examples * n.o.features
	#mu - row vector - 1*n.o.features
	#if Sigma2 is a row vector -> univariate Gaussian (Probability density function is parallel to axes) <=> Covariance matrix is diagonal
	#if Sigma2 is a matrix -> it is a Covariance matrix (n.o.features * n.o.features)
#output:
	#p - row vector representing probability for the i-th example to be in the Normal Distribution with given parameters 
def multivariateGaussian(X, mu, Sigma2):
	m, n = X.shape
	
	if Sigma2.ndim == 1:
		Sigma2 = np.diag(Sigma2)
	
	p = 1 / np.sqrt((2*np.pi) ** n * np.linalg.det(Sigma2)) * np.exp(np.sum(-0.5 * (X - mu) @ np.linalg.pinv(Sigma2) * (X - mu), 1))
	
	return p

#input:
	#yval - row vector representing 0=standard example, 1=outlier (providing CVS - Cross Validation Set)
	#pval - row vector representing the probability for i-th example in CVS 
		#that it is standard (low probability means it is probably an outlier)
#output:
	#best_eps, best_F1 found eps and F1 price 
def selectThreshold(yval, pval):
	best_eps = 0
	best_F1 = 0
	maxval = np.max(pval)
	minval = np.min(pval)
	for cur_eps in np.linspace(minval, maxval, 1000):
		y_pred = pval < cur_eps
		tp = np.sum(yval & y_pred)
		fp = np.sum(np.invert(yval) & y_pred)
		fn = np.sum(yval & np.invert(y_pred))
		
		prec = tp / (tp + fp)
		rec = tp / (tp + fn)
		F1 = 2 * prec * rec / (prec + rec)
		
		if F1 > best_F1:
			best_F1 = F1
			best_eps = cur_eps
	
	return best_eps, best_F1
	
#OTHER FUNCTIONS


def load_data(filename):
	df = pd.read_csv(filename)
	X = []
	for i in df.index: 
		X.append( [ float(df[ 'X' ][ i ]), float(df[ 'Y' ][ i ]) ] )
	return np.array(X)
	
	
