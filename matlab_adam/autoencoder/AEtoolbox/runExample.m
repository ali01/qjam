%% Add Paths
addpath minFunc/

%% Load Data
load /afs/cs/group/brain/scratch5/vanHateren/whitened_lc_patches.mat
rp = randperm(size(data,2));
data = data(:, rp(1:100000)); % pick 100k examples randomly

%% Run Code
netconfig = struct;
netconfig.inputsize  =  192;
netconfig.layersizes = { 200 netconfig.inputsize }; % Learn 200 bases, set outputsize = inputsize

netconfig.targetact     = 0.035;
netconfig.lambda        = 3;
netconfig.tieweights    = false;
netconfig.weightcost    = 3e-3;

plen   = computeParamLen(netconfig);
params = randn(plen, 1)*0.1;

options.DerivativeCheck = false;
options.Method = 'lbfgs';
options.maxIter = 500;
options.display = 'on';
options.logfile = 'log.txt'; % optional

[optparams, value] = minFunc( @(p) sigmoidNetLoss(p, netconfig, data, data), ...
                              params, options);

%% Visualize
stack = params2stack(optparams, netconfig);
dn(stack{1}.w', 14);
