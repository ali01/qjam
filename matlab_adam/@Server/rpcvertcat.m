% SERVER.VERTCAT invokes an RPC, then stacks the results on top of each
% other (i.e., along the first dimension).
function varargout = rpcvertcat(server, reqHook, varargin)
  
  argsout = cell(1, nargout);
  [argsout{:}] = server.rpc(reqHook, varargin{:});

  for i=1:length(argsout)
    % concatenate vertically
    argsout{i} = vertcat(argsout{i}{:});
  end
  varargout = argsout;
