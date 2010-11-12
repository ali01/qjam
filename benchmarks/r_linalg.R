matrix_multiplication <- function(size,n) {
A <- matrix(1:size^2, size, size)
B <- matrix(size^2:1, size, size)
for (i in 1:n) {
    result <- A %*% B
}
}

elementwise_multiplication <- function(size,n) {
A <- matrix(1:size^2, size, size)
B <- matrix(size^2:1, size, size)
for (i in 1:n) {
    result <- A * B
}
}

matrix_transpose <- function(size,n) {
A <- matrix(1:size^2, size, size)
for (i in 1:n) {
    result <- t(A)
}
}

matrix_addition <- function(size,n) {
A <- matrix(1:size^2, size, size)
B <- matrix(size^2:1, size, size)
for (i in 1:n) {
    result <- A + B
}
}


vector_inner_product <- function(size,n) {
a <- 1:size
b <- size:1
for (i in 1:n) {
    result <- a %*% b
}
}




std_sizes <- c(10,50,100,500,1000)
n <- 10000
benchmarks <- c(matrix_multiplication)
benchmark_names = c('matrix_multiplication')

run_benchmark <- function(f,name,sizes,n) {
    for (i in 1:length(sizes)) {
        size = sizes[i]
        cat(paste("R\t",name,"\t",size,"\t"))
        msecs_per<-1000 * (system.time(f(size,n))[3]/n)
        cat(paste(msecs_per,"\n"))
    }
}

run_benchmark(matrix_multiplication,'matrix_multiplication',std_sizes,n)
run_benchmark(elementwise_multiplication,'elementwise_multiplication',3*std_sizes,n)
run_benchmark(matrix_transpose,'matrix_transpose',std_sizes,n)
run_benchmark(matrix_addition,'matrix_addition',std_sizes,n)
run_benchmark(vector_inner_product,'vector_inner_product',50*std_sizes,n)
