from __future__ import print_function

import pymp
import utils_se
ex_array = pymp.shared.array((125,), dtype='uint8')
x = utils_se.n_grams_stat('./data/azj_train_test.csv','utf-8',1,3)
print (x)
shared_list = pymp.shared.list()
shared_list.extend(x)
length = len(shared_list)

with pymp.Parallel(4) as p:
    for index in p.range(0, 100):
        ex_array[index] = p.thread_num
        # The parallel print function takes care of asynchronous output.
        p.print('Yay! {} done!'.format(index),p.thread_num,p.num_threads)

with pymp.Parallel(4) as p:
    for sec_idx in p.xrange(4):
        if sec_idx == 0:
            p.print('Section 0', p.thread_num)
        elif sec_idx == 1:
            p.print('Section 1', p.thread_num)
        elif sec_idx == 2:
            p.print('Section 2', p.thread_num)
        elif sec_idx == 3:
            p.print('Section 3', p.thread_num)

with pymp.Parallel(4) as p:
    for index in p.iterate(shared_list):
        p.print(index, p.thread_num)
