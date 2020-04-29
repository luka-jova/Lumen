function [J, grad] = costFunction(theta, X, y, lambda)

%COSTFUNCTION Compute the cost function and gradient for linear regression.
	%J is the cost with respect to parameters theta and regularization parameter lambda
	%X has m test examples where every row is one test example

%n = number of features
%m = number of training examples
%theta = [t1; ...; tn] 
%X = [X(1,1) ... X(1,N); ...; X(M, 1) ... X(M, N)]
%y = [y1; ... ; ym]

n = size(X, 2);
m = size(X, 1);

J = sum((X * theta - y) .^ 2) / (2 * m) + lambda / (2 * m) * sum(theta(2:end) .^ 2);
grad = 1 / m * (X' * (X * theta - y) + lambda * [0; theta(2:end)]);

end 
