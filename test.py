import csv

i = 0
with open('diacritic.csv','r') as fin:
    reader=csv.reader(fin)
    for row in reader:
        temp=list(row)
        fmt=u'{:<15}'*len(temp)
        print fmt.format(*[s.decode('utf-8') for s in temp])
        if i==0:
            keys = [s.decode('utf-8') for s in temp]

        if i==1:
            values = [s.decode('utf-8') for s in temp]

        i = i+1

    dictionary = dict(zip(keys,values))
    print dictionary
