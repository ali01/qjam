function [] = view_images(data)

for i = 1:10
  view_image(image_matrix(i, data, 512));
  pause;
end
