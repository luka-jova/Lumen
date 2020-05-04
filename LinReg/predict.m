function y = predict(theta, X)
	m = size(X, 1);
	X = [ones(m, 1) X];
	n = size(X, 2);
	y = X * theta;
end
