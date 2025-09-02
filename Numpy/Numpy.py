import time 
import numpy as np

start = time.time()
py_list = [i*2 for i in range(1000000)]
print("\n List operation time: ", time.time() - start)

start = time.time()
np_array = np.arange(1000000) * 2
print("\n Numpy operation time: ", time.time() - start)