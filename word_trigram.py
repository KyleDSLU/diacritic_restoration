import math
import re
import csv
from itertools import zip_longest
from datetime import datetime
from collections import Counter

import pymp

def tokenize(input_file, encoding):
    lst =[]
    with open(input_file, 'r', encoding=encoding) as f:
        for sent in f:
            sent = sent.lower()
            sent = re.findall(r'\w+|\.|\<\$\>', sent)
            for word in sent:
                lst.append(word)
    return lst


def ngrams_split(lst, n):
    word_to_ignore = [u'<$>','.']
    ADD_FLAG = False
    lst_out = []
    for i in range(len(lst)-n):
        if lst[i] not in word_to_ignore:
            for j in range(1,n):
                if (lst[i-j+1] in word_to_ignore):
                    stop_ind = j-1
                    break
                else:
                    stop_ind = j

            string = lst[i]
            for j in range(1,stop_ind+1):
                old_string = string
                string = lst[i-j] + ' ' + string
            lst_out.append(string)

    #return [' '.join(lst[i:i+n]) for i in range(len(lst)-n)]
    return lst_out



def three_gram_count(tokens, n_filter, n):
    ngram_count = pymp.shared.list([])
    n_words = len(tokens)
    n_filter = n_filter
    n = n
    d = Counter(ngrams_split(tokens, n))
    lst = [[key,value] for key,value in d.items()]
    length = len(lst)
    shared_token_list = pymp.shared.list(lst)

    lst = ngrams_split(tokens, n-1)
    shared_tokenng_list = pymp.shared.list(lst)

    proc = 7

    with pymp.Parallel(proc) as p:
        i = 0
        for result in p.iterate(shared_token_list):
            if i%1000==0:
                print(i,length/proc,p.thread_num)
            i+=1
            count = result[1]
            ngram = result[0]
            if count >= n_filter:
                splitted_ngram = ngram.split()
                ngram_freq = math.log(count/n_words, 10)
                num = count*n_words
                c2gram = shared_tokenng_list.count(splitted_ngram[0] + " " + splitted_ngram[1])
                product = 1
                for split in splitted_ngram:
                    product *= tokens.count(split)
                mi = math.pow(math.log(num/(product), 10), 2)
                ngram_prob = math.log(count/c2gram, 10)
                ngram_count.append((ngram_freq, mi, ngram_prob, count, ngram))
    return ngram_count



def n_grams_stat(input_file, encoding, n_filter, n):
    tokens = tokenize(input_file, encoding)
    if n == 3:
        return three_gram_count(tokens, n_filter, n)
    return []


if __name__ == "__main__":
    start_time = datetime.now()
    s = n_grams_stat("./data/azj_train.csv",'utf-8', n_filter=5, n=3)
    for a, b, c, d, e in s:
        print(a, b, c, d, e)
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
