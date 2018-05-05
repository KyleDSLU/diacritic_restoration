#! /usr/bin python

import unicodecsv as csvu
from preprocess import diacritic_preprocess
import utils
import codecs


class process_diacritic():

    def __init__(self,input_file,output_file):
        with codecs.open(input_file, encoding='utf-8') as fin:
            csv_temp = fin.readlines()
            csv_data = []
            for word in csv_temp:
                index = word.find(',')
                string = word[index+1:].strip()
                string = string.split('"')
                if len(string) > 3:
                    string = u'"'
                elif len(string) == 3:
                    string = string[1]

                csv_data.append([string])

            del csv_data[0]
            fin.close()

        self.input = csv_data

        self.answer = []
        self.add_start_char(u'<$>')
        self.process(output_file)
        #self.write_answer('./answer/4-29-2018_attempt1.csv')
        
    def add_start_char(self,start_char):
        l = []
        l.append([start_char])
        for word in self.input:
            l.append(word)
            if word[0] == '.':
                l.append([start_char])
        self.input = l

    def process(self,csv_file):
        sentence = []
        sentences = []
        sentence_flag = False
        with open(csv_file, 'w+') as fout:
            string = ','.join([u'id', u'token'])+'\r\n'
            fout.write(string.encode('utf-8'))

            j = 1  #Sentence Counter
            for i,word in enumerate(self.input):
                if i%5000 == 0:
                    print ('Building Sentences', i, len(self.input))
                if i > 0:
                    if word[0] == u'<$>' or i == len(self.input)-1:
                        sentence_flag = True
                    else:
                        sentence.append(word)
                else:
                    sentence.append(word)

                if sentence_flag:
                    sentences.append([j,sentence])
                    sentence_flag = False
                    sentence = []
                    sentence = [[u'<$>']]
                    j+=1
            
            length = len(sentences)
            shared_sentences = pymp.shared.list(sentences)
            shared_output_dict = pymp.shared.dict({})

            proc = 7
            with pymp.Parallel(proc) as p:
                i = 0       #index counter
                for index in p.iterate(shared_sentences):
                    if i%5000==0:
                        print('Processing Sentences',i,length/proc,p.num_thread)
                    sentence_num = index[0]
                    sentence = index[1]
                    analysis = diacritic_preprocess(sentence)
                    sentence = ' '.join(word[0] for word in analysis.list_string)
                    shared_output_dict[sentence_num] = sentence 

            j = 1
            for value in shared_output_dict.values():
                if value != u'<$>':
                    string = ','.join([unicode(str(j)), u'\"'+result[0]+u'\"'])+'\r\n'
                    fout.write(string.encode('utf-8'))
                    j += 1

            fout.close()
