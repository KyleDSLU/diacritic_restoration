import numpy as np
import csv
import unicodecsv as csvu
import random
import unidecode

def decode_csv(csv_file):
    i = 0
    with open(csv_file,'rb') as fin:
        reader=csv.reader(fin)
        for row in reader:
            temp=list(row)
            if i==0:
                keys = [s.decode('utf-8') for s in temp]

            if i==1:
                values = [s.decode('utf-8') for s in temp]

            i = i+1

        fin.close()
        return dict(zip(keys,values))

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
        print param
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

def strip_dev(file_name):
    with open(file_name, 'rb') as fin:
        reader = csvu.reader(fin, encoding='utf-8')
        stripped = []
        diacritic_dict = decode_csv('diacritic.csv')
        inv_dict = {v: k for k, v in diacritic_dict.iteritems()}
        for row in reader:
            for i, char in enumerate(row[0]):
                if char in diacritic_dict.values():
                    row[0] = row[0][:i] + unicode(inv_dict[char]) + row[0][i+1:]
            stripped.append(row)
            
        fin.close()
    
    with open('.'+file_name.strip('.csv')+'_stripped.csv', 'w+') as fout:
        writer = csvu.writer(fout, encoding='utf-8')
        for row in stripped:
            writer.writerow(row)

        fout.close()

def create_char_ngram(destination, train, n, n_after=0):
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
    ngram_dict = {} 
    ngram_clist = []
    for j,row in enumerate(csv_data):
        if j%5000 == 0:
            print j,len(csv_data)

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
        if i%100==0: print i, len(ngram_clist)
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
    comp_destination = '.' + destination.split('.')[1] + '_comp.csv'
    print('Writing ngram comp Dictionary to ' + comp_destination)
    with open(comp_destination, 'w+') as fout:
        writer = csvu.DictWriter(fout, comp_dict.keys(), encoding='utf-8')
        writer.writeheader()
        writer.writerow(comp_dict)
        fout.close()

