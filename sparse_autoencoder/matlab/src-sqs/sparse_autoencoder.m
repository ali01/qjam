function sparse_autoencoder(olsh, niter, alpha)

%%%%%%% constants
k = struct();
k.n_l1 = 64; % input units
k.n_l2 = 30; % hidden units
k.n_l3 = 64; % output units
k.beta = 5;
k.rho = -0.996;
k.lambda = 0.002;
k.alpha = alpha; % TODO: should be in [0.001, 1], needs tweaking
% hardcode for speed?
% k.f = @tanh;
% k.fp = @(num) sech(num).^2;

%%%%%%% params
p = struct();
p.W1 = rand_weight_inits(k.n_l2, k.n_l1, k.n_l1+1); % n_l1 nodes plus bias
p.W2 = rand_weight_inits(k.n_l3, k.n_l2, k.n_l2+1); % n_l2 nodes plus bias
p.b1 = zeros(k.n_l2, 1);
p.b2 = zeros(k.n_l3, 1);
p.rho_hat = k.rho * ones(k.n_l2, 1); % TODO: init with rho?

for i=1:niter,
    x = get_example(olsh);
    p = sparse_autoencoder_step(x, k, p);
    if rem(i-1, 500) == 0
        disp(i-1)
    end
    if rem(i-1, 25000) == 0
        disp('saving p.W1');
        dlmwrite(sprintf('bases/weights-a%.3f-i%d.dat', k.alpha, i-1), p.W1);
    end
end

dlmwrite(sprintf('bases/weights%d-alpha%.3f.dat', niter, k.alpha), p.W1);
%figure, display_network(p.W1');


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% returns n-by-m matrix with elements chosen uniformly at random from
% [0,1/sqrt(q)]
% q=fan-in (#inputs into node)
function W = rand_weight_inits(n, m, q)
a = 0;
b = 1/sqrt(q);
W = a + (b-a).*rand(n,m);