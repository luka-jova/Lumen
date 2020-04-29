function generateRandomExample(n, m, del, degree, test_filename)
	X = [];
	for i = 1:n
		X = [X linspace(-10, 10, m)'];
	endfor

	theta = rand(n, 1) * 10;
	y = X * theta + (rand(m, 1) * (2 * del) .- del);

	for i=2:degree
		X(:, end+1) = X(:, 1) .^ i;
	endfor

	save(test_filename, "X", "y");

end
