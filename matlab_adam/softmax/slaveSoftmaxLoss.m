% Computes softmax loss and gradient for data in X and labels in y where
% there are K classes.  w is the weight matrix with K-1 columns as a vector.
function [nll, g] = slaveSoftmaxLoss(w, X, y, K, LAMBDA)
  REGULARIZE_INTERCEPT = 0;

  if (nargin < 5)
    LAMBDA = 0;
  end

  [M,N] = size(X);
  theta = reshape(w, N, K-1);
  I=sparse(1:M,y,1,M,K);
  W=[exp(X * theta), ones(M,1)]; % last col is exp(X*0)
  P=bsxfun(@rdivide, W, sum(W,2));
  g=X'*(P - I);

  % L2 regularization
  reg = 0.5 * sum(w.^2);
  d_reg = w;

  if (~REGULARIZE_INTERCEPT)
    intercept_inds = N:N:length(w);
    reg = reg - 0.5 * sum(w(intercept_inds).^2);
    d_reg(intercept_inds) = 0;
  end

  %reg = sum(log(cosh(10 * w))) / 10;
  %d_reg = tanh(10 * w);
  
  g=reshape(g(:,1:K-1), (K-1)*N,1) + LAMBDA * d_reg;
  nll=-full(sum(log(sum(I .* P, 2)))) + LAMBDA * reg;
