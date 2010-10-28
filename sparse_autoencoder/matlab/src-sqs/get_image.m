function img = get_image(olsh, i)
imageSize = 512;
numImages = 10;

img = olsh(1+imageSize*i:imageSize*(i+1), :);

