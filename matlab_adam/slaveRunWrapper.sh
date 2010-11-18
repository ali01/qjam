#!/bin/sh

SERVER=$1
PORT=$2
CWD=$(pwd -P)  #/afs/cs.stanford.edu/u/acoates/stair/deeplearn/trunk/matlabserver
CONTINUE_ON_ERROR=$3
if [[ "$CONTINUE_ON_ERROR" != "" ]]; then
    CF=',1';
fi

trap "echo WOOHOO" SIGINT SIGTERM SIGHUP

ssh gorgon2 "matlab_r2010a -nodesktop -nosplash -r addpath\(\'$CWD\'\),for\ i=1:1e9,x=svd\(randn\(1000,1000\)\)\;,end" & PID=$! ;

sleep 10
kill $PID

#,slaveRun\(\'$SERVER\',$PORT$CF\),quit
