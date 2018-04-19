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
            string = char[1]
            ngram_nd = string[char[3]]
            ngram_d = char[0]
            ngram_comp = u'<*>'
            perm = []

            #Grab preceding characters
            if (char[3] >= prec_char):
                indexed_char = string[char[3]-prec_char:char[3]]
                perm = self.find_permutations(indexed_char)
                
                #Account for permutations
                if (len(perm) > 0):
                    perm.remove(indexed_char)
                    ngram_nd_perm = [ind + ngram_nd for ind in perm]
                    ngram_d_perm = [ind + ngram_d for ind in perm]
                    ngram_comp_perm = [ind + ngram_comp for ind in perm]

                ngram_nd = indexed_char + ngram_nd
                ngram_d = indexed_char + ngram_d
                ngram_comp = indexed_char + ngram_comp

            #Grab preceding characters if index > prec_char)
            else:
                indexed_char = string[:char[3]]
                perm = self.find_permutations(indexed_char)

                #Account for permutations
                if (len(perm) > 0):
                    perm.remove(indexed_char)
                    ngram_nd_perm = [ind + ngram_nd for ind in perm]
                    ngram_d_perm = [ind + ngram_d for ind in perm]
                    ngram_comp_perm = [ind + ngram_comp for ind in perm]

                ngram_nd = indexed_char + ngram_nd
                ngram_d = indexed_char + ngram_d
                ngram_comp = indexed_char + ngram_comp


            #Grab following characters
            if (char[3]+n_after <= len(string)-1):
                indexed_char = string[char[3]+1:char[3]+n_after+1]
                perm = self.find_permutations(indexed_char)
                
                #Account for permutations
                if len(perm) > 0:
                    perm.remove(indexed_char)
                    ngram_nd_perm = [ngram_nd + ind for ind in perm]
                    ngram_d_perm = [ngram_d + ind for ind in perm]
                    ngram_comp_perm = [ngram_comp + ind for ind in perm]
                    
                ngram_nd = ngram_nd + indexed_char
                ngram_d = ngram_d + indexed_char
                ngram_comp = ngram_comp + indexed_char

                
            #Grab following characters if index > parsable length
            else:
                indexed_char = string[char[3]+1:]
                perm = self.find_permutations(indexed_char)

                #Account for permutations
                if len(perm) > 0:
                    perm.remove(indexed_char)
                    ngram_nd_perm = [ngram_nd + ind for ind in perm]
                    ngram_d_perm = [ngram_d + ind for ind in perm]
                    ngram_comp_perm = [ngram_comp + ind for ind in perm]

                ngram_nd = ngram_nd + indexed_char
                ngram_d = ngram_d + indexed_char
                ngram_comp = ngram_comp + indexed_char

            print(ngram_d, ngram_d_perm, ngram_nd, ngram_nd_perm, ngram_comp, ngram_comp_perm)

    def find_permutations(self,string):
        perm = []
        for i, char in enumerate(string):
            if char in self.diacritic_dict.keys():
                perm_char = self.replace_char_by_index(string, self.diacritic_dict[char], i)
                perm.append(perm_char)
                perm.append(string)
                sub_perms = self.find_permutations(string[i+1:])
                for sub in sub_perms:
                    perm.append(char + sub)
                    perm.append(self.diacritic_dict[char] + sub)
                break

        return list(set(perm))

    def replace_char_by_index(self, string, replacement, index):
        return string[:index] + replacement + string[index+1:]
        
    def create_series(series_name, values):
        series = pd.Series(dict(zip(self.series_keys,values)))
        series.name = series_name
        return series 

