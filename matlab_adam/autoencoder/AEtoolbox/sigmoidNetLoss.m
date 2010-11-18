function [loss,grad] = sigmoidNetLoss(params, netconfig, data, targets)

%% Generic Deep Network which has weights and biases at each level
data=data';
targets=targets';

if ~isfield(netconfig, 'inputsize')
    netconfig.inputsize = size(data, 1);
end

% Sparsity settings
if isfield(netconfig, 'targetact')
    targetact = netconfig.targetact;
    lambda = netconfig.lambda;
end

% Tie Weights?
if isfield(netconfig, 'tieweights')
    tieweights = netconfig.tieweights;
else
    tieweights = false;
end

% Weight Cost
if isfield(netconfig, 'weightcost')
    weightcost = netconfig.weightcost;
else
    weightcost = 0;
end

% Map the params (a vector into a stack of weights)
depth = numel(netconfig.layersizes);
stack = params2stack(params, netconfig);
gradstack = cell(depth, 1);
nlayers = numel(stack);

if tieweights
    
    % must be a symmetric typoe network
    assert(mod(numel(stack),2) == 0);
    
    % we tie weights in a symmetric fashion
    for l = 1:numel(stack)/2
        stack{nlayers - l + 1}.w = stack{l}.w';
    end
    
end

%% Compute all the gradients!

% Forward Prop
h = cell(nlayers);
for l = 1:nlayers
    if ( l == 1 )
        h{l} = bsxfun(@plus, stack{l}.w * data, stack{l}.b);
    else
        h{l} = bsxfun(@plus, stack{l}.w * h{l-1}, stack{l}.b);
    end
    if (l < nlayers)
        h{l} = sigmoid(h{l});
    end
end

%% Objective Function, just reconstruction
diff = h{nlayers} - targets;
loss = 0.5 * sum(diff(:).^2);

% Error derivatives through the softmax
outderv = diff;

% Back Prop
for l = nlayers:-1:1
    if (l < nlayers)
        outderv = outderv .* h{l} .* (1 - h{l});
    end
    if (l > 1)
        gradstack{l}.w = (outderv * h{l-1}');
    else
        gradstack{l}.w = (outderv * data');
    end
    gradstack{l}.b = sum(outderv, 2);
    outderv = stack{l}.w.' * outderv;
end

% Target Sparsity via Cross-Entropy cost (only at layer1)
if isfield(netconfig, 'targetact')
    
    % targetact lambda
    p = targetact;
    q = mean(h{1},2);
    loss = loss + sum(lambda * size(data, 2) * ( - p * log(q) - (1 - p) * log (1 - q)));
    outderv = lambda * (-p./q + (1-p)./(1-q));
    outderv = repmat(outderv, 1, size(data, 2));
    outderv = outderv .* h{1} .* (1 - h{1});
    gradstack{1}.w = gradstack{1}.w + (outderv * data');
    gradstack{1}.b = gradstack{1}.b + sum(outderv, 2);
    
end


if weightcost > 0
    for l = 1:nlayers
        loss = loss + weightcost * size(data, 2) * 0.5 * sum(stack{l}.w(:).^2);
        gradstack{l}.w = gradstack{l}.w + weightcost * size(data,2) * stack{l}.w;
    end
end

if tieweights
    for l = 1:nlayers/2
        gradstack{l}.w = gradstack{l}.w + gradstack{nlayers - l + 1}.w';
        gradstack{nlayers - l + 1}.w = zeros(size(gradstack{nlayers - l + 1}.w));
    end
end

% Map the gradients back into a single vector
grad = stack2params(gradstack);

end

