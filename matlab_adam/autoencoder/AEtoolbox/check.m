%% Add Paths
addpath minFunc/

%% Run Code!
netconfig = struct;
netconfig.inputsize  =  10;
netconfig.layersizes = { 5 10 };
plen   = computeParamLen(netconfig);
params = randn(plen, 1)*0.1;

netconfig.targetact = 0.035;
netconfig.lambda = 3;
netconfig.tieweights = 0;
netconfig.weightcost = 1e-4;

data = randn(10, 50);

checkgrad('sigmoidNetLoss', params, 1e-4, netconfig, data, data)