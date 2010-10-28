function sparse_autoencoder_olsh(niter)
load olsh.dat

alphas=[0.001 0.003 0.01 0.03 0.1 0.3 1];
nalphas=size(alphas,2);

for i=1:nalphas,
    disp(alphas(i));
    sparse_autoencoder(olsh, niter, alphas(i));
end