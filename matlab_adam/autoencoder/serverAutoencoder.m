function [weights,b1,b2] = serverAutoencoder(server, patches, k, iterations, displayResults,...
                                             targetact, lambda, weightcost)
  
  if (nargin < 5)
    displayResults = 0;
  end 
  if (nargin < 8)
    display('Using default auto-encoder parameters.');
    targetact = 0.02;
    lambda = 3;
    weightcost = 0.005;
  end
    
  % get patch info
  patchCounts = server.rpc('size', patches, 1);
  inputSize = server.rpc('size', patches, 2);
  inputSize = inputSize{1};

  % set up auto-encoder structure
  netconfig = struct;
  netconfig.inputsize  =  inputSize;
  netconfig.layersizes = { k inputSize };
  plen   = (inputSize+1) * k  + (k+1)*inputSize;
  params = randn(plen, 1)*0.1;

  % set learning parameters
  netconfig.targetact = targetact;
  netconfig.lambda = lambda;
  netconfig.tieweights = true;
  netconfig.weightcost = weightcost;
  
  % set optimization parameters
  options.Method = 'lbfgs';
  options.MaxIter = iterations;
  options.TolFun = 5e2;
  if (displayResults)
    options.outputFcn = @showWeightsHook;
  end
  
  % run backprop
  [optparams, value] = minFunc(@(p,s,c,i,o) s.rpcsum('sigmoidNetLoss',p,c,i,o), ...
                               params, options, server, netconfig, patches, patches);

  stack = params2stack(optparams, netconfig); % unpack result

  weights = stack{1}.w;
  b1 = stack{1}.b;
  b2 = stack{2}.b;
