import timeit, sys

import numpy_linalg

std_sizes = [10,50,100,500,1000]
benchmarks = {
    'matrix_multiplication': std_sizes,
    'elementwise_multiplication': [i*3 for i in std_sizes],
    'matrix_transpose': std_sizes,
    'matrix_addition': std_sizes,
    'vector_inner_product': [i*50 for i in std_sizes],
}

def run_benchmarks(module_name, n=10000, repeat=1):
    for b,args in benchmarks.items():
        for arg in args:
            t = timeit.Timer("%s(%d,number=%d)" % (b, arg, n),
                             "from %s import %s" % (module_name, b))
            print "py\t%s\t%d\t%.3f" % \
                (b, arg, 1000*min(t.repeat(repeat, number=1))/n)


if __name__ == "__main__":
    run_benchmarks('numpy_linalg')
