Input sensor values: list of sensors used to predict the output sensor value
Output sensor value: sensor that is being predicted

x-axis: different values of input sensor values
y-axis: values of output sensor

blue x-es -> real pairs of measurement data... (input_sensor_val, real_output_sensor_val)
red dots -> predicted pairs of measurement data... (input_sensor_val, predicted_output_sensor_val)

For now all the predictions are made for sensors 1-1 (one input sensor predicting one output sensor)
The function is LINEAR approximation found by Linear Regression. It can be extended to polynomial approximation by adding polynomial features (more columns) or n-1 prediction (n input sensors predicting one output sensor).
