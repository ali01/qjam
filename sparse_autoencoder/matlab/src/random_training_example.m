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
  image_size = size(images,2);
  num_images = size(images,1) / image_size;
  num_samples = image_size / sample_size;

  image_index = randi(num_images);
  sample_row = randi(num_samples);
  sample_col = randi(num_samples);

  start_row = (image_index - 1) * image_size + sample_row;
  start_col = sample_col;

  sample = images(start_row:start_row + sample_size - 1, ...
      sample_col:start_col + sample_size - 1);
  sample = reshape(sample, sample_size * sample_size, 1);
end
