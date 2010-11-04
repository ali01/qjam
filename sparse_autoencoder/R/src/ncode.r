# algorithm parameters
bt = 5 # one of two learning rates (other is alpha)
rho = -0.996
lambda = 0.002
input_units = 64
hidden_units = 30

# other constants
sample_size = 8 # 8x8 patch of image

status_output_interval = 1e3

out_path = "bases"
out_ext = "dat"

ncode = function(data, alph, iterations=1e4) {
  file_output_interval = iterations / 100

  # - initializing weights matrix and bias values
  # - weights are initializied randomly in the interval [1, 1/sqrt(Q)] where
  #   Q is the fan-in (number of inputs feeding into a node)
  w1_vector = runif(input_units * hidden_units)
  W_1 = matrix(w1_vector, nrow=hidden_units, byrow = TRUE) / sqrt(input_units)

  w2_vector = runif(input_units * hidden_units)
  W_2 =  matrix(w2_vector, nrow=input_units, byrow = TRUE) / sqrt(hidden_units)

  b_1 = rep(0, 30)
  b_2 = rep(0, 64)

  # initializing running rho estimate vector
  rho_est = rep(0, 30)

  for (i in 1:iterations) {
    # -- feedforward pass (computing activations) --
    x = training_example(sample_size, data)

    # hidden layer
    z_2 = W_1 %*% x + b_1
    a_2 = tanh(z_2)

    # output layer
    z_3 = W_2 %*% a_2 + b_2
    a_3 = tanh(z_3)

    # -- computing error and node responsibilities --
    d_3 = -(x - a_3) * (1 - a_3^2)
    d_2 = (t(W_2) %*% d_3) * (1 - a_2^2)

    # -- updating parameters (gradient descent) --
    W_1 = W_1 - alph * (d_2 %*% t(x) + lambda * W_1)
    b_1 = b_1 - alph * d_2

    W_2 = W_2 - alph * (d_3 %*% t(a_2) + lambda * W_2)
    b_2 = b_2 - alph * d_3

    # updating running rho estimate vector
    rho_est = 0.999 * rho_est + 0.001 * a_2

    # updating hidden layer intercept terms based on rho estimate vector
    b_1 = b_1 - alph * bt * (rho_est - rho)

    if (i %% status_output_interval == 0) {
      print(i / iterations)
    }

    if (i %% file_output_interval == 0) {
      write_weights_matrix(W_1, alph, out_ext)
    }
  }
}

training_example = function(sample_size, data) {
  img_size = dim(data)[2]
  num_images = dim(data)[1] / img_size

  img_row = sample(0:(num_images - 1), 1) * img_size
  
  x_row_i = img_row + sample(1:(img_size - sample_size + 1))
  x_col_i = sample(1:(img_size - sample_size + 1))

  x_row_f = x_row_i + sample_size - 1
  x_col_f = x_col_i + sample_size - 1

  sample = data[x_row_i:x_row_f, x_col_i:x_col_f]
  c(sample)
}

write_weights_matrix = function(W, alph, out_ext) {
  file_name = paste("weights1-a(", alph, ").", out_ext, sep="")
  write(W, file.path(out_path, file_name), ncolumns=dim(W)[2])
  print("w");
}

data_matrix = function(file_name) {
  data.matrix(read.table(file_name))
}
