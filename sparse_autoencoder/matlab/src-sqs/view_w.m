function view_w(f)
W = dlmread(f);
figure, display_network(W',f);

