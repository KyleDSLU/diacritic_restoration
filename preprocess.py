#!/usr/bin/env python 

import numpy as np
import pandas as pd

import utils

import re
import nltk
from googletrans import Translator
import csv

class diacritic_preprocess():

    def __init__(self, list_string):
        self.translator = Translator()
        
        self.list_string = list_string
        #self.string = re.findall(r"\w+|[^\w\s]", list_string, re.UNICODE)

        self.diacritic_dict = utils.decode_csv('diacritic.csv') 
        #self.trigram_asprec = utils.decode_csv('./ref/trigram_asym/trigram_asym_prec.csv')
        #self.trigram_asprec_comp = utils.decode_csv('./ref/trigram_asym/trigram_asym_prec_comp.csv')
        #self.trigram_asfol_comp = utils.decode_csv('./ref/trigram_asym/trigram_asym_fol_comp.csv')
        #self.trigram_sym = utils.decode_csv('./ref/trigram_sym/trigram_sym.csv')
        #self.trigram_sym_comp = utils.decode_csv('./ref/trigram_sym/trigram_sym_comp.csv')

        self.candidate_char = []
        cursor = 0
        for i,word in enumerate(self.list_string):
            word = word[0]

            for j,char in enumerate(word):
                if char in self.diacritic_dict:
                    char_diacritic = self.diacritic_dict[char] 
                    self.candidate_char.append([char_diacritic, word, i, j])

        self.series_keys = [row[2] for row in self.candidate_char]
        #self.pd_series = []
        #self.ngram_process(list_string)

    def ngram_process(self, n, n_after, ngram_csv):
        prec_char = n-1-n_after
        for char in self.candidate_char:
            ngram_d, ngram_nd, ngram_comp = self._ngram_preprocess(char, n, n_after, prec_char)
            print ngram_d, ngram_nd, ngram_comp
            

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

        ngram_comp_perm, comp_index = self.find_comp_permutations(ngram_comp)
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

            

    def find_comp_permutations(self,comp_string):
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
                sub_perms,null = self.find_comp_permutations(comp_string[i+1:])
                
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

class ngram_object():
    
    def __init__(self, n, n_after, ngram_d, ngram_nd, ngram_comp, ngram_csv):
        self.ngram_dict = utils.decode_csv(ngram_csv)
        self.ngram_comp_dict = utils.decode_csv('.'+ngram_csv.split('.csv')+'_comp.csv')

        self.ngram_cand = {'Diacritic': ngram_d, 'Non-Diacritic': ngram_nd}
        self.ngram_comp = ngram_comp
        self.n_param = [n, n_after]

        self.diacritic_dict = utils.decode_csv('diacritic.csv') 

        self.ngram_perm = self.find_permutations()

    def find_permutations(self, ngram_list):
        char_index = self.ngram_comp.find(u'<*>')
        for ngram in ngram_list:
            for i, char in enumerate(ngram):
                if i != char_index and char in self.diacritic_dict.keys():
                    print ngram, i, char
                    
             
            

