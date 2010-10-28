% returns matrix m containing raw pixel values for image
% assumes img_size is the row count of a single image
% assumes data contains the concatenation of all images
function m = image_matrix(i, data, img_size)
  start_row = (i - 1) * img_size + 1;
  end_row = start_row + img_size - 1;
  m = data(start_row:end_row,:);
end
