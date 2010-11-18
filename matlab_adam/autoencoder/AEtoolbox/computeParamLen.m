function len = computeParamLen(netconfig)

% Map the params (a vector into a stack of weights)
lastlayersize = netconfig.inputsize;
len = 0;
for d = 1:numel(netconfig.layersizes);
    if iscell(netconfig.layersizes{d})
        newlastlayersize = 0;
        checksize = 0;
        for c = 1:numel(netconfig.layersizes{d})
            len = len + prod(netconfig.layersizes{d}{c});
            len = len + netconfig.layersizes{d}{c}(2);
            checksize = checksize + netconfig.layersizes{d}{c}(1);
            newlastlayersize = newlastlayersize + netconfig.layersizes{d}{c}(2);
        end
        % sanity check
        assert(checksize == lastlayersize);
        lastlayersize = newlastlayersize;
    else
        wlen = netconfig.layersizes{d} * lastlayersize;
        blen = netconfig.layersizes{d};
        lastlayersize = blen;
        len = len + wlen + blen;
    end
    
end

end