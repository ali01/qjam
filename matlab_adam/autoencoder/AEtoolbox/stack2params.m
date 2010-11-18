function params = stack2params(stack)

fulllen = double(0);
for d = 1:numel(stack)
    if iscell(stack{d})
        for c = 1:numel(stack{d})
            wlen = double(numel(stack{d}{c}.w));
            blen = double(numel(stack{d}{c}.b));
            fulllen = fulllen + wlen + blen;
        end
    else
        wlen = double(numel(stack{d}.w));
        blen = double(numel(stack{d}.b));
        fulllen = fulllen + wlen + blen;
    end
end

% Map the gradients back into a single vector
if (iscell (stack{1}) && isa (stack{1}{1}.w, 'GPUsingle')) || ...
   (~iscell (stack{1}) && isa (stack{1}.w, 'GPUsingle'))
    params = zeros(fulllen, 1, GPUsingle);
else
    params = zeros(fulllen, 1);
end

curpos = double(1);
for d = 1:numel(stack)
    if iscell(stack{d})
        for c = 1:numel(stack{d})
            wlen = double(numel(stack{d}{c}.w));
            blen = double(numel(stack{d}{c}.b));
            params(curpos:curpos+wlen-1) = stack{d}{c}.w(:);
            curpos = curpos + wlen;
            blen = numel(stack{d}{c}.b);
            params(curpos:curpos+blen-1) = stack{d}{c}.b(:);
            curpos = curpos + blen;
        end
    else
        wlen = double(numel(stack{d}.w));
        params(curpos:curpos+wlen-1) = stack{d}.w(:);
        curpos = curpos + wlen;
        blen = double(numel(stack{d}.b));
        params(curpos:curpos+blen-1) = stack{d}.b(:);
        curpos = curpos + blen;
    end
end

end