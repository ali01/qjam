function showWeightsHook(x,infoStruct,state, server, netconfig, varargin)
  scrsz = get(0,'ScreenSize');
  
  stack = params2stack(x, netconfig); % unpack result
  showCentroids(stack{1}.w, 8);
  set(gcf, 'Position',[1 scrsz(4)/2 scrsz(3)/2 scrsz(4)/2]);
  drawnow;
 