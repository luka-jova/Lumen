function runTest(test_filename)
	load(test_filename);
	[theta cost] = linear_regression(X, y, 10^9);
	figure; hold on;
	plot(X(:, 1), y, 'x');
	y_pred = predict(theta, X);
	plot(X(:, 1), y_pred, 'b');
end
