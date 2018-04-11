#!/usr/bin/env python 

import numpy as np
import pandas as pd

import utils

import re
import nltk
from googletrans import Translator
import csv

class diacritic_preprocess():

    def __init__(self, string):
        self.translator = Translator()
        self.string = re.findall(r"\w+|[^\w\s]", string, re.UNICODE)
        self.diacritic_dict = utils.decode_csv('diacritic.csv') 

        self.candidate_char = []
        cursor = 0
        for i,word in enumerate(self.string):
            cursor = i*len(word)
            for j,char in enumerate(word):
                if char in self.diacritic_dict:
                    char_diacritic = self.diacritic_dict[char] 
                    self.candidate_char.append([char_diacritic, word, cursor+j, i])

        self.series_keys = [row[2] for row in self.candidate_char]
        self.pd_series = []
        self.pos_process(string)

    def pos_process(self,string):

        
    def create_series(series_name, values):
        return pd.Series(dict(zip(self.series_keys,values)))
