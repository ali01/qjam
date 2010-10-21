function [] = view_image(m)
  image(m * 255);
  axis off;
  axis image;
  colormap(gray(256));
