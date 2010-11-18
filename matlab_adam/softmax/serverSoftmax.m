function [w,trainErr,testErr,trainY_res,testY_res,trainY_gt,testY_gt] = serverSoftmax(server, w0, iters, trainXC, trainY, testXC, testY, K, N, L)
  
  w = minFunc(@softmaxLoss, w0, struct('MaxIter',iters, 'MaxFunEvals',round(iters*1.2), 'TolFun', 500), server, trainXC, trainY, K, L);
  theta = [reshape(w, N, K-1), zeros(N,1)];
  
  trainY_local = server.rpc('deal', trainY);
  trainY_local = vertcat(trainY_local{:});
  testY_local = server.rpc('deal', testY);
  testY_local = vertcat(testY_local{:});

  [v1,y1] = server.rpc('@(X,theta) max(X * theta,[],2)', trainXC, theta);
  y1 = vertcat(y1{:});
  
  [v,y] = server.rpc('@(X,theta) max(X * theta,[],2)', testXC, theta);
  y = vertcat(y{:});
  trainErr=sum(y1 ~= trainY_local)/length(y1);
  e1=100*trainErr;

  testErr=sum(y ~= testY_local)/length(y);
  e=100*testErr;
  fprintf(1, 'Training error: %f%% (Acc=%f%%)\nTest error: %f%%  (Acc=%f%%)\n', e1,100-e1,e,100-e);

  %%% returns prob. of class 1 in binary problems...
  v1 = server.rpcvertcat('@(X,theta) 1./(1+exp(-X * theta(:,1)))', trainXC, theta);
  v = server.rpcvertcat('@(X,theta) 1./(1+exp(-X * theta(:,1)))', testXC, theta);

  trainY_gt = trainY_local;
  testY_gt = testY_local;
  trainY_res = v1;
  testY_res = v;
