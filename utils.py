import csv
import unicodecsv as csvu
import random
import unidecode

def decode_csv(csv_file):
    i = 0
    with open('diacritic.csv','r') as fin:
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
        



