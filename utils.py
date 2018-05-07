import numpy as np
import csv
import unicodecsv as csvu
import random
import unidecode
import codecs
import wikipedia
import re
import os
from shutil import copyfile
from collections import Counter

wikipedia.set_lang('az')

def decode_csv(csv_file):
    with open(csv_file,'r') as fin:
        lines = fin.readlines()
        for i,row in enumerate(lines):
            s = re.findall(r'\w+|\.|\<\$\>',row)
            if i==0:
                keys = s
            if i==1:
                values = s 

        fin.close()
        return dict(zip(keys,values))

def format_dev_data(dev_data):
    with codecs.open(dev_data, encoding='utf-8') as fin:
        csv_data = fin.readlines()
        csv_data = [word.strip() for word in csv_data]
        fin.close()
            
    dev_data_fmt = dev_data.split('.csv')[0] + '_answer.csv'
    with open(dev_data_fmt, 'w+') as fout:
        string = ','.join([u'id', u'token'])+'\r\n'
        fout.write(string.encode('utf-8'))
        j = 1
        for word in csv_data:
            if word != u'<$>':
                string = ','.join([unicode(str(j)), u'\"'+word+u'\"'])+'\r\n'
                fout.write(string.encode('utf-8'))
                j += 1
        fout.close()

def test_dev(dev_test, dev_ans):
    with open(dev_test, 'rb') as dtest:
        csv_dev_test = []
        reader = csvu.reader(dtest, encoding='utf-8')
        for row in reader:
            csv_dev_test.append(row[1])
        dtest.close()
            
    with open(dev_ans, 'rb') as dans:
        csv_dev_ans = []
        reader = csvu.reader(dans, encoding='utf-8')
        for row in reader:
            csv_dev_ans.append(row[1])
        dans.close()

    num_right = 0
    wrong_answers = []
    for i in range(len(csv_dev_test)):
        if csv_dev_test[i] == csv_dev_ans[i]:
            num_right += 1
        else:
            wrong_answers.append([csv_dev_test[i], csv_dev_ans[i]])

    return num_right/float(len(csv_dev_ans)),wrong_answers


def start_char_addition(file_name, end_char, start_char):
    with open(file_name, 'rb') as fin:
        with open(file_name.split('.')[0]+'_startchar.csv', 'w+') as fout:
            with open(file_name.split('.')[0]+'_startchar_param.csv', 'w+') as paramout:
                reader = csvu.reader(fin,encoding='utf-8')
                writer = csvu.writer(fout,encoding='utf-8')
                writer.writerow([start_char])
                sentences = 0
                words = 0
                for row in reader:
                    writer.writerow(row)
                    words = words+1
                    if row == [end_char]:
                        writer.writerow([start_char])
                        sentences = sentences+1

                par_writer = csv.writer(paramout)
                par_writer.writerow([words,sentences])

                paramout.close()
                fout.close()
                fin.close()

def get_csvparameters(file_name):
    with open(file_name.split('.')[0]+'_param.csv', 'rb') as fin:
        reader = csv.reader(fin)
        param = []
        for row in reader:
            param = [int(element) for element in row]

        keys = ['Words', 'Sentences']
        print (param)
        fin.close()
        return dict(zip(keys, param))

def split_train_dev(file_name, percent, start_char):

    param_dict = get_csvparameters(file_name)
    
    with open(file_name, 'rb') as fin:
        with open(file_name.split('.')[0]+'_train.csv', 'w+') as trainout:
            with open(file_name.split('.')[0]+'_dev.csv', 'w+') as devout:
                reader = csvu.reader(fin,encoding='utf-8')
                trainwriter = csvu.writer(trainout,encoding='utf-8')
                devwriter = csvu.writer(devout,encoding='utf-8')
                csv_data = []
                ind_sentence = []

                for i,row in enumerate(reader):
                    csv_data.append(row)
                    if row == [start_char]:
                        ind_sentence.append(i)

                ind_decision = []
                ind_usedsentences = []
                while(len(ind_decision)<(int(percent*param_dict['Words']))):
                    ind = random.randint(0,param_dict['Sentences']+1)
                    if ind not in ind_usedsentences:
                        ind_usedsentences.append(ind)
                        if ind != param_dict['Sentences']:
                            ind_decision.extend(range(ind_sentence[ind],ind_sentence[ind+1]))
                        else:
                            ind_decision.extend(ind_sentence[ind:])

                print(param_dict['Words'], len(ind_decision))

                ind_decision = sorted(ind_decision)

                dev_data = [csv_data[i] for i in ind_decision]
                print('Development Data Formed')

                for row in dev_data:
                    devwriter.writerow(row)
                print('Development Data Saved')

                train_data = csv_data
                for j in reversed(ind_decision):
                    del train_data[j]
                print('Training Data Formed')

                '''Super ineffecient, TODO: Speed this up'''
                for row in train_data:
                    trainwriter.writerow(row)
                print('Training Data Saved')

                devout.close()
                trainout.close()
                fin.close()
    


def format_answer(file_name, start_char):
    with open(file_name, 'rb') as fin:
        with open(file_name.split('.')[0]+'_fmt.csv', 'w+') as fout:
            reader = csvu.reader(fin, encoding='utf-8')
            writer = csvu.writer(fout, encoding='utf-8', quotechar = "'")

            writer.writerow([u'id',u'token'])
            for i,row in enumerate(reader):
                if row[0] != start_char:
                    writer.writerow([unicode(i),'\"'+row[0]+'\"'])
            fout.close()
            fin.close()

def strip_dev(dev_data):
    with codecs.open(dev_data, encoding='utf-8') as fin:
        csv_data = fin.readlines()
        csv_data = [word.strip() for word in csv_data]
        fin.close()
            
    stripped = []
    diacritic_dict = decode_csv('diacritic.csv')
    inv_dict = {v: k for k, v in diacritic_dict.iteritems()}
    for word in csv_data:
        for i, char in enumerate(word):
            if char in diacritic_dict.values():
                old_word = word
                word = word[:i] + unicode(inv_dict[char]) + word[i+1:]
        stripped.append(word)
        
    dev_data_fmt = dev_data.split('.csv')[0] + '_stripped.csv'
    with open(dev_data_fmt, 'w+') as fout:
        string = ','.join([u'id', u'token'])+'\r\n'
        fout.write(string.encode('utf-8'))
        j = 1
        for word in stripped:
            if word != u'<$>':
                string = ','.join([unicode(str(j)), u'\"'+word+u'\"'])+'\r\n'
                fout.write(string.encode('utf-8'))
                j += 1
        fout.close()

    
def create_word_ngram(destination, train, n, n_after=0):
    with open(train, 'rb') as fin:
        reader = csvu.reader(fin, encoding='utf-8')
        csv_data = []
        for row in reader:
            csv_data.append(row)
        fin.close()
    prec_word = n-1-n_after

    # Finding all trigrams
    ngram_counts = Counter()
    ngram_dict = {}
    ngram_clist = []
    words_to_ignore = [u'<$>', u'', '.']
    for j,row in enumerate(csv_data):
        if j%5000==0:
            print (j,len(csv_data))
        #find sentences
        if row[0] not in words_to_ignore:
            string_row = _create_string_from_middlelist(csv_data,j,row[0],n,n_after)
            if string_row not in ngram_dict.keys():
                ngram_dict[string_row] = 1
                cstring = _create_string_from_middlelist(csv_data,j,u'<*>',n,n_after)
                ngram_clist.append(cstring)
            else:
                ngram_dict[string_row] += 1
    
    # find the amount of times comp words occur
    comp_count = np.zeros(len(ngram_clist), dtype='int')
    for i,comp in enumerate(ngram_clist):
        if i%100==0: print (i, len(ngram_clist))
        comp_list = comp.split(' ')
        for j,row in enumerate(csv_data):
            if row[0] not in words_to_ignore:
                string_row = _create_string_from_middlelist(csv_data,j,u'<*>',n,n_after)
                if string_row == comp:
                    comp_count[i] += 1 

    comp_dict = dict(zip(ngram_clist,list(comp_count)))
    comp_destination = '.' + destination.split('.')[1] + '_comp.csv'

    with open(destination, 'w+') as fout:
        writer = csvu.DictWriter(fout, ngram_dict.keys(), encoding='utf-8')
        writer.writeheader()
        writer.writerow(ngram_dict)
        fout.close()

    with open(comp_destination, 'w+') as fout_comp:
        writer = csvu.DictWriter(fout, comp_dict.keys(), encoding='utf-8')
        writer.writeheader()
        writer.writerow(comp_dict)
        fout.close()

def create_word_unigram(destination, train):
    with open(train, 'rb') as fin:
        reader = csvu.reader(fin, encoding='utf-8')
        csv_data = []
        for row in reader:
            csv_data.append(row)
        fin.close()

    # Finding all unique words 
    ngram_dict = {}
    words_to_ignore = [u'<$>', u'', '.']
    for j,row in enumerate(csv_data):
        if j%5000==0:
            print (j,len(csv_data))

        if row[0] not in words_to_ignore:
            string_row = row[0] 
            if string_row not in ngram_dict.keys():
                ngram_dict[string_row] = 1
            else:
                ngram_dict[string_row] += 1
    
    print('Writing unigram Dictionary to ' + destination)
    with open(destination, 'w+') as fout:
        writer = csvu.DictWriter(fout, ngram_dict.keys(), encoding='utf-8')
        writer.writeheader()
        writer.writerow(ngram_dict)
        fout.close()

def _create_string_from_middlelist(full_list, j, string_to_add, n, n_after):
    prec_word = n-1-n_after
    s = ''
    for i in range(1,prec_word+1):
        word = full_list[j-i][0]
        if word == u'<$>':
            break
        s = word + ' ' + s
    s += string_to_add
    for i in range(1,n_after+1):
        if j+i >= len(full_list):
            break
        word = full_list[j+i][0]
        if word == u'<$>':
            break
        s += ' ' + word 

    return s

def create_char_ngram(destination, train, n, n_after=0):
    d = {} 
    cd = {}
    analyze_ngram(destination, train, n, n_after, d, cd, 'w')

def append_char_ngram(destination, train, n, n_after=0):
    save_file = destination.split('.csv')[0] + '.old'
    copyfile(destination,save_file)
    with open(destination, 'rb') as fin:
        reader = csvu.DictReader(fin, encoding = 'utf-8')
        for row in reader:
            d = dict(row)
        for key,value in d.iteritems():
            d[key] = int(value)
        fin.close()

    cdestination = destination.split('.csv')[0] + '_comp.csv'
    csave_file = cdestination.split('.csv')[0] + '.old'
    copyfile(cdestination,csave_file)
    with open(cdestination, 'rb') as fin:
        reader = csvu.DictReader(fin, encoding = 'utf-8')
        for row in reader:
            cd = dict(row)
        for key,value in cd.iteritems():
            cd[key] = int(value)
        fin.close()

    analyze_ngram(destination, train, n, n_after, d, cd, 'a')

def analyze_ngram(destination, train, n, n_after, dictionary, cdictionary, append_char):
    with open(train, 'rb') as fin:
        reader = csvu.reader(fin, encoding='utf-8')
        csv_data = []
        for row in reader:
            csv_data.append(row)

        fin.close()

    diacritic_dict = decode_csv('diacritic.csv')
    prec_char = n-1-n_after

    '''finding all trigrams'''
    print('Finding all Trigrams')
    ngram_dict = dictionary
    ngram_clist = []
    for j,row in enumerate(csv_data):
        if j%5000 == 0:
            print (j,len(csv_data))

        string_row = row[0]
        parsable_len = len(string_row)-n_after-1
        for i,char in enumerate(string_row):
            if (char in diacritic_dict.keys() or char in diacritic_dict.values()):
                if (i>=prec_char and i<=parsable_len):
                    string_to_add = string_row[i-prec_char:i+1+n_after]
                    string_comp = string_to_add[:prec_char] + u'<*>' + string_to_add[n-n_after:]
                elif (i<prec_char):
                    string_to_add = string_row[:i+1+n_after]
                    string_comp = string_to_add[:i] + u'<*>' + string_to_add[i+1:]
                elif (i>parsable_len):
                    string_to_add = string_row[i-prec_char:]
                    string_comp = string_to_add[:prec_char] + u'<*>' + string_to_add[n-n_after:]

                if string_to_add not in ngram_dict.keys():
                    ngram_dict[string_to_add] = 1
                else:
                    ngram_dict[string_to_add] += 1

                '''Create complementary list with all occurrences of trigram minus char'''
                if string_comp not in ngram_clist:
                   ngram_clist.append(string_comp) 


    print('Writing ngram Dictionary to ' + destination)
    with open(destination, 'w+') as fout:
        writer = csvu.DictWriter(fout, ngram_dict.keys(), encoding='utf-8')
        writer.writeheader()
        writer.writerow(ngram_dict)
        fout.close()
        
    print('Calculating complementary dictionary')
    comp_count = np.zeros(len(ngram_clist), dtype='int')
    for i,comp in enumerate(ngram_clist):
        if i%100==0: 
            print (i, len(ngram_clist))
        if len(comp)-2 < n:
            prec_char = comp.find(u'<*>')
            end_char = len(comp)-2-prec_char
        else:
            prec_char = n-1-n_after
            end_char = n_after+1
        for row in csv_data:
            string_row = row[0]
            if (len(comp) <= len(string_row)+2 and string_row != u'<$>'):
                for j in range(0, len(string_row)-n_after):
                    string_comp = string_row[j:j+prec_char] + u'<*>' + string_row[j+prec_char+1:j+prec_char+end_char]
                    #print string_comp, comp, string_comp==comp
                    if string_comp == comp:
                        comp_count[i] += 1
                        
    comp_dict = dict(zip(ngram_clist,list(comp_count)))
    for key, value in comp_dict.iteritems():
        if key in cdictionary.keys():
            cdictionary[key] += value
        else:
            cdictionary[key] = value

    comp_destination = '.' + destination.split('.')[1] + '_comp.csv'
    print('Writing ngram comp Dictionary to ' + comp_destination)
    with open(comp_destination, 'w+') as fout:
        writer = csvu.DictWriter(fout, cdictionary.keys(), encoding='utf-8')
        writer.writeheader()
        writer.writerow(cdictionary)
        fout.close()

def wikipedia_to_csv(destination, wiki):
    wikipedia.set_lang('az')
    obj = wikipedia.page(wiki)
    line = obj.content
    line = re.sub('[=\n"]', '', line)
    line = re.sub(r'\.(?! )', ' .', line)
    list_line = line.split(' ')

    if os.path.exists(destination):
        append_write = 'a'
        save_file = destination.split('.csv')[0] + '_old.csv'
        copyfile(destination, save_file)
    else:
        append_write = 'w'

    with open(destination, append_write) as fout:
        writer = csvu.writer(fout, encoding = 'utf-8')
        for row in list_line:
            writer.writerow([row])

        fout.close()

