function show_image(olsh, i)
img = get_image(olsh, i);
image(img*255);
axis image
colormap(gray(256));
