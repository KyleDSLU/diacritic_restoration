import numpy as np

csv_data = [[u'koik'],[u'pos']]
ngram_clist = [u'ko<*>k',u'p<*>s']
n = 4
n_after = 1
comp_count = np.array(np.zeros(len(ngram_clist)))
for i,comp in enumerate(ngram_clist):
	if i%1000==0: print i, len(ngram_clist)
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
                    		print string_comp, comp, string_comp==comp
                    		if string_comp == comp:
                        		comp_count[i] += 1


