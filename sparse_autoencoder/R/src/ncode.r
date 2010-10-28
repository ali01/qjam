# algorithm parameters
bt = 5 # one of two learning rates (other is alpha)
rho = -0.996
lambda = 0.002
input_units = 64
hidden_units = 30

# other constants
img_size = 512
sample_size = 8 # 8x8 patch of image

status_output_interval = 1e3

out_path = "bases/"
out_ext = "dat"

ncode = function(data, alph, iterations=1e4) {
  file_output_interval = iterations / 100

  # - initializing weights matrix and bias values
  # - weights are initializied randomly in the interval [1, 1/sqrt(Q)] where
  #   Q is the fan-in (number of inputs feeding into a node)
  w1_vector = runif(hidden_units * input_units);
  W1 = matrix(w1_vector, nrow=hidden_units, byrow = TRUE) / sqrt(input_units)

  w2_vector = runif(hidden_units * input_units);
  W2 =  matrix(w2_vector, nrow=input_units, byrow = TRUE) / sqrt(hidden_units)
}
