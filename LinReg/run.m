%run function is the main function
%filename is a .csv file to load data of sensors
%prediction_in is a row vector representing the indexes of sensors that should be used for prediction
%prediction_out is a scalar representing the sensor being predicted
function run(filename, prediction_in, prediction_out)
	all_data = csvread(filename);
	%data is loaded into a matrix [start_timestamp end_timestamp eff_val1 eff_val2 .... eff_valn]
	
	N_all = size(all_data, 1);
	perm = randperm(size(all_data, 1))';
	
	N_train = round(0.7 * N_all);
	N_CVS = N_all - N_train;
	
	X_train = all_data(perm(1:N_train), prediction_in + 2);
	y_train = all_data(perm(1:N_train), prediction_out + 2);
	
	X_CVS = all_data(perm(N_train + 1:end), prediction_in + 2);
	y_CVS = all_data(perm(N_train + 1:end), prediction_out + 2);
	
	disp(size(X_train));
	disp(size(y_train));
	disp(N_train);
	disp(size(X_CVS));
	disp(size(y_CVS));
	disp(N_CVS);
	
	disp("machine learning");
	[theta cost] = linear_regression(X_train, y_train, 1);
	
	disp("predicting")
	figure;	hold on;
	plot(X_train, y_train, 'x');
	xlabel("input sensor values");
	ylabel("output sensor values");
	
	printf("Initial cost on training set: %f\n", costFunction(zeros(size(theta)), [ones(N_train, 1) X_train], y_train, 0));
	printf("Initial cost on CVS set: %f\n", costFunction(zeros(size(theta)), [ones(N_CVS, 1) X_CVS], y_CVS, 0));
	
	printf("\nCost on training set: %f\n", costFunction(theta, [ones(N_train, 1) X_train], y_train, 0));
	printf("Cost on CVS set: %f\n", costFunction(theta, [ones(N_CVS, 1) X_CVS], y_CVS, 0));
	
	y_CVS_pred = predict(theta, X_CVS);
	figure; hold on;
	plot(X_CVS, y_CVS, 'xb');
	plot(X_CVS, y_CVS_pred, '.r', 'markersize', 10);
	xlabel(strcat("input sensor values:", mat2str(prediction_in)));
	ylabel(strcat("output sensor values:", num2str(prediction_out)));
	title("Cross validation set");
	image_out = strcat("img_predict_", num2str(prediction_out), "_w_");
	for i=prediction_in
		image_out = strcat(image_out, num2str(i));
	endfor
	image_out = strcat(image_out, ".png");
	print(image_out, "-dpng")
end

%example: run("FL01-all-sensors.csv", [1 3 4], 5)
