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
    for i in range(len(lst)):
        if lst[i] not in word_to_ignore:
            stop_ind = 0
            for j in range(1,n):
                if (lst[i-j+1] in word_to_ignore):
                    stop_ind = j-1
                    break
                else:
                    stop_ind = j
            string = lst[i]
            for j in range(1,stop_ind+1):
                if lst[i-j] != u'.':
                    string = lst[i-j] + ' ' + string
            lst_out.append(string)

        elif lst[i] == u'<$>':
            string = lst[i]
            lst_out.append(string)

    #return [' '.join(lst[i:i+n]) for i in range(len(lst)-n)]
    return lst_out


def gram_count(tokens, n_filter, n):
    ngram_count = pymp.shared.list([])
    n_words = len(tokens)
    n_filter = n_filter
    n = n
    d = Counter(ngrams_split(tokens, n))
    lst = [[key,value] for key,value in d.items()]
    shared_token_list = pymp.shared.list(lst)
    length_lst = len(lst)

    lst = ngrams_split(tokens, n-1)
    shared_tokenng_list = pymp.shared.list(lst)

    proc = 8
    length = length_lst/(proc-1) 

    with pymp.Parallel(proc) as p:
        i = 0
        for index in p.range(0,length_lst):
            count = shared_token_list[index][1]
            ngram = shared_token_list[index][0]
            if i%1000==0:
                p.print(i,length,index,p.thread_num)
            i+=1
            if count >= n_filter:
                splitted_ngram = ngram.split()
                if splitted_ngram[:-1] and ngram != u' ':
                    ngram_freq = math.log(count/n_words, 10)
                    num = count*n_words
                    #print(splitted_ngram[:-1], splitted_ngram, ngram, len(splitted_ngram), len(ngram), p.thread_num)
                    c2gram = shared_tokenng_list.count(" ".join(splitted_ngram[:-1]))

                    product = 1
                    for split in splitted_ngram:
                        product *= tokens.count(split)

                    mi = math.pow(math.log(num/(product), 10), 2)
                    ngram_prob = math.log(count/c2gram, 10)
                    ngram_count.append((ngram_freq, mi, ngram_prob, count, ngram))

    return ngram_count



def n_grams_stat(input_file, encoding, n_filter, n):
    tokens = tokenize(input_file, encoding)
    if n:
        return gram_count(tokens, n_filter, n)
    return []


if __name__ == "__main__":
    start_time = datetime.now()
    s = n_grams_stat("./data/azj_train.csv",'utf-8', n_filter=2, n=3)
    dictionary = {}
    for result in s:
        dictionary[result[4]] = "{:10.6f}".format(result[2])

    with open("./ref/word_gram/trigram/trigram2p0f.csv", 'wb') as fout:
        string = ','.join(dictionary.keys())+'\r\n'
        print(type(string))
        fout.write(string.encode('utf-8'))
        string = ','.join(dictionary.values())+'\r\n'
        fout.write(string.encode('utf-8'))
        fout.close()
 
    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))
