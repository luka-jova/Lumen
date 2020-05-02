function [theta, cost] = linear_regression(X, y, lambda)

	m = size(X, 1);
	X = [ones(m, 1) X];
	n = size(X, 2);
	theta_init = zeros(n, 1);

	[cost grad] = costFunction(theta_init, X, y, lambda);
	printf("cost for theta_init is: %f\nGradient: \n", cost);
	disp(grad);
	options = optimset('GradObj', 'on', 'MaxIter', 1000);
	[theta, cost] = fminunc(@(t)(costFunction(t, X, y, lambda)), theta_init, options);

	printf("Found theta:\n");
	disp(theta);
	printf("Provides cost: %f\n", cost);
	
end
