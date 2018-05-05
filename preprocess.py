#!/usr/bin/env python 

import numpy as np
import pandas as pd

import utils

import re
import csv
import unicodecsv as csvu
import operator

class diacritic_preprocess():

    def __init__(self, list_string):
        self.list_string = list_string

        self.diacritic_dict = utils.decode_csv('diacritic.csv') 
        self._unigram_d = self._ngram_csv_return('./ref/unigram/unigram.csv')

        self.candidate_char = []
        cursor = 0
        for i,word in enumerate(self.list_string):
            word = word[0]

            for j,char in enumerate(word):
                if char in self.diacritic_dict:
                    char_diacritic = self.diacritic_dict[char] 
                    self.candidate_char.append([char_diacritic, word, i, j])

        # Build list of words and predicting metrics
        self.dict_words = {}
        self.words_index = []
        for char in self.candidate_char:
            if char[1] not in self.dict_words.keys():
                self.dict_words[char[1]] = [0]*len(char[1])
            if char[2] not in self.words_index:
                self.words_index.append(char[2])
                
        tokens = self._tokenize()
        
        # Initial run through of dict_word
        #self.ngram_process(3,1,'./ref/char_gram/trigram/trigram_sym.csv',400,400)
        #self.ngram_process(3,0,'./ref/char_gram/trigram/trigram_2p0f.csv',400,400)
        #self.ngram_process(3,2,'./ref/char_gram/trigram/trigram_0p2f.csv',400,400)
        #self.ngram_process(2,0,'./ref/char_gram/bigram/bigram1p0f.csv',200,200)
        #self.ngram_process(2,1,'./ref/char_gram/bigram/bigram0p1f.csv',200,200)
        #self.ngram_process(1,0,'./ref/char_gram/unigram/unigram.csv',75,75)

        # Determine ambigious diacritics
        # significance_threshold = 50
        # ambig_list = []
        # for char in self.candidate_char:
        #     decision_value = self.dict_words[char[1]][char[3]]
        #     if abs(decision_value) < significance_threshold:
        #         ambig_list.append(char)
        #     elif decision_value > 0:
        #         original_string = self.list_string[char[2]][0]
        #         changed_string = original_string[:char[3]] + char[0] + original_string[char[3]+1:]
        #         self.list_string[char[2]][0] = changed_string
        
        # ambig_word_last = 0 
        # ambig_perm = []
        # for ambig in ambig_list:
        #     ambig_word = ambig[2]
        #     if ambig_word != ambig_word_last:
        #         if ambig_perm:
        #             results = self._unigram_analysis(ambig_perm, './ref/unigram/unigram.csv')
        #             if results[1]>1:
        #                 self.list_string[ambig_word_last][0] = ambig_perm[results[0]]
        #                 #print ('setting value to ' + self.list_string[ambig_word_last][0])
        #         l = self._ambig_perm(ambig[0],[ambig[1]],ambig[3])
        #         ambig_word_last = ambig_word
        #         ambig_perm = l
        #     else:
        #         ambig_perm.extend([ambig[1]])
        #         l = self._ambig_perm(ambig[0],ambig_perm,ambig[3])
        #         ambig_perm.extend(l)
        #         list(set(ambig_perm))
                
            #print self._unigram_analysis(ambig_perm, './ref/char_gram/unigram/unigram.csv')
        #del self.list_string[0]
                

    def _tokenize(self,n):
        tokens = []
        for word in self.words_index:
            token = self.list_string[word] 
            for i in range(1,n):
                index = self.list_string[word-i]
                token.insert(index,0)
                if index = u'<$>':
                    break
            tokens.append(token) 
        return tokens
            
    def _unigram_analysis(self, l, csv_file):
        csv_unigram = self._unigram_d #self._ngram_csv_return(csv_file)
        unique_words = float(len(csv_unigram))
        prob_l = []
        for word in l:
            try:
                prob = (csv_unigram[str(word)]+1)
                #print word,prob
            except:
                prob = 0.001 
                #print type(word),prob

            #print prob,word
            prob_l.append(prob)

        return max(enumerate(prob_l), key=operator.itemgetter(1)) 
        
    def _ngramword_csv_return(self,csv_file):
        with open(csv_file, 'rb') as fin:
            reader = csvu.DictReader(fin, encoding='utf-8')
            for row in reader:
                d = row
            fin.close()
            return d 

    def _ambig_perm(self, character, word_list, index):
        return_list = []
        for word in word_list:
            return_list.append(word)
            word_replace = word[:index] + character + word[index+1:]
            return_list.append(word_replace)

        return list(set(return_list))

        

    def ngram_process(self, n, n_after, ngram_csv, ngram_weight, pred_weight):
        csv_diacritic = self._ngram_csv_return(ngram_csv)
        unique_ngram = len(csv_diacritic)

        csv_comp = self._ngram_csv_return(ngram_csv.split('.csv')[0] + '_comp.csv')

        prec_char = n-1-n_after
        
        # Calculate Probabilities
        for char in self.candidate_char:
            # return dictionary in the form of [raw_ngram, {dict of permutations of ngram}] 
            # for diacritic, non-diacritic, and comp forms of ngram
            ngram_d, ngram_nd, ngram_comp = self._ngram_preprocess(char, n, n_after, prec_char)
            list_d = [ngram_d[0]]
            list_nd = [ngram_nd[0]]

            for perm in ngram_d[1]:
                list_d.append(perm)
            for perm in ngram_nd[1]:
                list_nd.append(perm)

            count_analysis_d, count_analysis_nd = self._ngram_countanalysis(list_d, list_nd, csv_diacritic)

            if count_analysis_d[0] != 0:
                l = [ngram_d[1].keys(),ngram_comp[1].keys()]
                for i,value in enumerate(l[0]): 
                    if value == list_d[count_analysis_d[0]]:
                        d_comp = l[1][i]
                        d_gram = value
                        d_count = csv_diacritic[d_gram]

                        try:
                            d_prob = (csv_diacritic[d_gram]+1)/float(csv_comp[d_comp]+unique_ngram)
                        except:
                            d_prob = 1/(float(unique_ngram))

                        d_predict = ngram_d[1][d_gram]
                        break

            else:
                d_comp = ngram_comp[0]
                d_gram = list_d[count_analysis_d[0]]

                try:
                    d_prob = (csv_diacritic[d_gram]+1)/float(csv_comp[d_comp]+unique_ngram)
                except:
                    d_prob = 1/float(unique_ngram)

                d_predict = None

            if count_analysis_nd[0] != 0:
                l = [ngram_nd[1].keys(),ngram_comp[1].keys()]
                for i,value in enumerate(l[0]):
                    if value == list_nd[count_analysis_nd[0]]:
                        nd_comp = l[1][i] 
                        nd_gram = value
                        nd_count = csv_diacritic[nd_gram]
                        
                        try:
                            nd_prob = (csv_diacritic[nd_gram]+1)/(float(csv_comp[nd_comp]+unique_ngram))
                        except:
                            nd_prob = 1/(float(unique_ngram))

                        nd_predict = ngram_nd[1][nd_gram]
                        break
                        
            else:
                nd_comp = ngram_comp[0]
                nd_gram = list_nd[count_analysis_nd[0]]

                try:
                    nd_prob = (csv_diacritic[nd_gram]+1)/float(csv_comp[nd_comp]+unique_ngram)
                except:
                    nd_prob = 1/float(unique_ngram)

                nd_predict = None

            # Make some decisions here
            if d_prob > nd_prob:
                decision_parameters = [d_prob-nd_prob, d_predict, d_gram]
            elif nd_prob > d_prob:
                decision_parameters = [d_prob-nd_prob, nd_predict, nd_gram]
            else:
                decision_parameters = [0,0]

            # Add probability weight to index of character to be changed
            self.dict_words[char[1]][char[3]] += int(decision_parameters[0]*ngram_weight)
            # Account for prediction data to skew other candidate character
            if decision_parameters[1]:
                for i,value in enumerate(decision_parameters[1]):
                    if value > 0:
                        self.dict_words[char[1]][char[3]+i-n+1+n_after] += int(decision_parameters[0]*pred_weight)

            #print char[1],self.dict_words[char[1]]

            
    def _ngram_countanalysis(self, l_d, l_nd, d_diacritic):
        count_d = []
        count_nd = []
        for i in range(len(l_d)):
            if l_d[i] in d_diacritic.keys():
                count_d.append(d_diacritic[l_d[i]])
            else:
                count_d.append(0)
            if l_nd[i] in d_diacritic.keys():
                count_nd.append(d_diacritic[l_nd[i]])
            else:
                count_nd.append(0)

        return max(enumerate(count_d), key=operator.itemgetter(1)), max(enumerate(count_nd), key=operator.itemgetter(1))


    def _ngram_csv_return(self,csv_file):
        with open(csv_file, 'rb') as fin:
            reader = csvu.DictReader(fin, encoding='utf-8')
            for row in reader:
                d = row
            for key,value in d.iteritems():
                d[key] = int(value)
            fin.close()
            return d 

    def _ngram_preprocess(self, char, n, n_after, prec_char):
        string = char[1]
        ngram_nd = string[char[3]]
        ngram_nd_perm = {}
        ngram_d = char[0]
        ngram_d_perm = {}
        ngram_comp = u'<*>'

        #Get preceding characters
        if (char[3] >= prec_char):
            indexed_char = string[char[3]-prec_char:char[3]]
            ngram_nd = indexed_char + ngram_nd
            ngram_d = indexed_char + ngram_d
            ngram_comp = indexed_char + ngram_comp

        #Get preceding characters if index<available_char
        else:
            indexed_char = string[:char[3]]
            ngram_nd = indexed_char + ngram_nd
            ngram_d = indexed_char + ngram_d
            ngram_comp = indexed_char + ngram_comp

        #Get following characters
        if (char[3]+n_after <= len(string)-1):
            indexed_char = string[char[3]+1:char[3]+n_after+1]
            ngram_nd = ngram_nd + indexed_char
            ngram_d = ngram_d + indexed_char
            ngram_comp = ngram_comp + indexed_char
            
        #Get characters_left<n_after
        else:
            indexed_char = string[char[3]+1:]
            ngram_nd = ngram_nd + indexed_char
            ngram_d = ngram_d + indexed_char
            ngram_comp = ngram_comp + indexed_char

        ngram_comp_perm, comp_index = self._find_comp_permutations(ngram_comp)
        for key,value in ngram_comp_perm.iteritems():
            key_d = self.replace_char_by_listindex(key,char[0],[comp_index,comp_index+2])
            key_nd = self.replace_char_by_listindex(key,string[char[3]],[comp_index,comp_index+2])
            value = self.replace_bool_by_listindex(value,-1,[comp_index,comp_index+2])
            ngram_d_perm[key_d] = value
            ngram_nd_perm[key_nd] = value

        if len(ngram_comp_perm.keys())>0:
            del(ngram_comp_perm[ngram_comp])
            del(ngram_nd_perm[ngram_nd])
            del(ngram_d_perm[ngram_d])

        #print(ngram_d, ngram_d_perm)
        return [ngram_d,ngram_d_perm],[ngram_nd,ngram_nd_perm],[ngram_comp,ngram_comp_perm]

            

    def _find_comp_permutations(self,comp_string):
        perm = {} 
        bool_iter_nd = []
        bool_iter_d = []
        char_index = comp_string.find(u'<*>')

        for i, char in enumerate(comp_string):
            if char in self.diacritic_dict.keys() and (i < char_index or i > char_index+2 or char_index == -1):
                perm_char = self.replace_char_by_index(comp_string, self.diacritic_dict[char], i)
                bool_iter_d = [0]*i + [1] + [0]*(len(comp_string)-i-1)
                bool_iter_nd = [0]*(i+1) + [0]*(len(comp_string)-i-1)
                perm[perm_char] = bool_iter_d
                perm[comp_string] = bool_iter_nd
                sub_perms,null = self._find_comp_permutations(comp_string[i+1:])
                
                for key,value in sub_perms.iteritems():
                    if i == 0:
                        j = 1
                    else:
                        j = i
                    bool_iter_nd = bool_iter_nd[:j] + [0]*(len(comp_string)-len(key)-len(bool_iter_nd[:j])) + value
                    bool_iter_d = bool_iter_d[:j] + [0]*(len(comp_string)-len(key)-len(bool_iter_d[:j])) + value
                    test_nd = comp_string[:i]+char+key
                    if test_nd not in perm.keys(): perm[test_nd] = bool_iter_nd
                    test_d = comp_string[:i]+self.diacritic_dict[char]+key
                    if test_d not in perm.keys(): perm[test_d] = bool_iter_d
                break

        return perm, char_index


    def replace_char_by_index(self, string, replacement, index):
        return string[:index] + replacement + string[index+1:]

    def replace_char_by_listindex(self, string, replacement, listindex):
        return string[:listindex[0]] + replacement + string[listindex[1]+1:]
    
    def replace_bool_by_listindex(self, bool_list, replacement, listindex):
        return bool_list[:listindex[0]] + [replacement] + bool_list[listindex[1]+1:]
        
    def create_series(series_name, values):
        series = pd.Series(dict(zip(self.series_keys,values)))
        series.name = series_name
        return series 


