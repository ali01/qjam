#!/usr/bin/env Rscript
source('ncode.r')
data = data_matrix('olsh.dat')
ncode(data, 0.003, 4000000)
