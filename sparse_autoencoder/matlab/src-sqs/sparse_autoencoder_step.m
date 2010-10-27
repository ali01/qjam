function p=sparse_autoencoder_step(x, k, p)

%%%%%%% run forward pass
a1 = x;
z2 = p.W1*a1 + p.b1;
a2 = tanh(z2);
z3 = p.W2*a2 + p.b2;
a3 = tanh(z3);

%%%%%%% do one step of stochastic gradient descent using backpropagation
y = a1;
delta3 = -(y-a3) .* (sech(z3).^2);
delta2 = (p.W2' * delta3) .* (sech(z2).^2);

% update params
p.W2 = p.W2 - k.alpha*(delta3*(a2') + k.lambda*p.W2);
p.b2 = p.b2 - k.alpha*delta3;
p.W1 = p.W1 - k.alpha*(delta2*(a1') + k.lambda*p.W1);
p.b1 = p.b1 - k.alpha*delta2;

%%%%%%% modify the params to try to satisfy the expectation constraint
p.rho_hat = 0.99*p.rho_hat + 0.01*a2;
p.b1 = p.b1 - k.alpha*k.beta*(p.rho_hat - k.rho);
