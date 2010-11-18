function stack = params2stack(params, netconfig)

% Map the params (a vector into a stack of weights)
depth = numel(netconfig.layersizes);
stack = cell(depth,1);
lastlayersize = netconfig.inputsize;
curpos = double(1);

for d = 1:depth
    
    if iscell(netconfig.layersizes{d})
        % if you are specifying a cell here, means, separating the input
        % into multiple sections, then you need to specify the section 
        % of the input you will accept as well
        newlastlayersize = 0;
        checksize = 0;
        stack{d} = cell(numel(netconfig.layersizes{d}, 1));
        for c = 1:numel(netconfig.layersizes{d})
            wlen = double(prod(netconfig.layersizes{d}{c}));
            stack{d}{c}.w = reshape(params(curpos:curpos+wlen-1), netconfig.layersizes{d}{c}(2), netconfig.layersizes{d}{c}(1));
            curpos = curpos+wlen;
            blen = double(netconfig.layersizes{d}{c}(2));
            stack{d}{c}.b = reshape(params(curpos:curpos+blen-1), blen, 1);
            curpos = curpos+blen;
            newlastlayersize = newlastlayersize + netconfig.layersizes{d}{c}(2);
            checksize = checksize + netconfig.layersizes{d}{c}(1);
        end
        % sanity check
        assert(checksize == lastlayersize);
        lastlayersize = newlastlayersize;
    else
        stack{d} = struct;
        wlen = double(netconfig.layersizes{d} * lastlayersize);
        stack{d}.w = reshape(params(curpos:curpos+wlen-1), netconfig.layersizes{d}, lastlayersize);
        curpos = curpos+wlen;
        blen = double(netconfig.layersizes{d});
        stack{d}.b = reshape(params(curpos:curpos+blen-1), netconfig.layersizes{d}, 1);
        curpos = curpos+blen;
        lastlayersize = netconfig.layersizes{d};
    end
    
end

end