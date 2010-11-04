function [ sample ] = random_training_example(images, sample_size)
  % RANDOM_TRAINING_EXAMPLE Grabs a random training example from the input
  % Input arguments:
  %   images: an (num_images * image_size) x image_size matrix
  %           containing the images
  %           (the images are assumed to be square)
  %   sample_size: the desired length of a sample_size along one
  %                dimension
  %                (the samples are assumed to be square)
  % Output:
  %   sample: a sample_size * sample_size vector constructed
  %           in row major order from a random sample_size x
  %           sample_size image patch
  image_size = size(images, 2);
  num_images = size(images, 1) / image_size;

  % Find first row of a random image within the image set.
  image_row = (randi(num_images) - 1) * image_size + 1;

  % Find row and column of random example within the image set.
  sample_row_i = image_row + randi(image_size - sample_size + 1) - 1;
  sample_col_i = randi(image_size - sample_size + 1);

  % End row and column of random example.
  sample_row_f = sample_row_i + sample_size - 1;
  sample_col_f = sample_col_i + sample_size - 1;

  sample = images(sample_row_i:sample_row_f, sample_col_i:sample_col_f);
  sample = reshape(sample, sample_size * sample_size, 1);
end
