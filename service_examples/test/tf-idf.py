#-*-coding=utf-8-*-

import re
import json
from  actrie import Trie
#import jieba

re_jobs= re.compile('{"jobid":.*,"salaryrangecode"')

t = Trie('./skill.txt')

def cut(value):
    #return jieba.cut(value,cut_all=True)
    terms = t.parse(value)
    v = {}
    for i in terms: 
        v[i[0]]=i[1]
    #return v.values()
    g =[]
    for k,v in v.iteritems():
        #g.append('['+v+':'+str(k)+']')
        g.append(v)
    return g

term_freq={}
term_doc_freq={}
f = open('./data/jobs.txt')
numDocs = 0
for i in f:
    m = re_jobs.search(i)
    if m:
        numDocs +=1
        data = m.group()+":0}"
        #print data
        jdata = json.loads(data);
        #print jdata['jobname']
        #print jdata['description']
        value = jdata['jobname'] +' '+ jdata['description']
        seglist=cut(value)
        doc_term_freq={}
        for w in seglist:
            if w in doc_term_freq:
                doc_term_freq[w] = doc_term_freq[w] + 1
            else:
                doc_term_freq[w] = 1
        for k in doc_term_freq.keys():
            if k in term_doc_freq:
                term_doc_freq[k]=term_doc_freq[k]+1
            else:
                term_doc_freq[k]=1
            if k in term_freq:
                term_freq[k]=term_freq[k]+doc_term_freq[k]
            else:
                term_freq[k]=doc_term_freq[k] 


from math import sqrt,log
import operator

term_tfidf={}
for k in term_freq.keys():
    #print k,term_freq[k],term_doc_freq[k],numDocs
    tf = term_freq[k]
    df = 1+ log(numDocs/(term_doc_freq[k]))
    if len(k) >1 :
        term_tfidf[k]=tf*df
sorted_x = sorted(term_tfidf.iteritems(), key=operator.itemgetter(1))
for x in sorted_x:
    print x[0].encode('UTF-8'),x[1],'===>',term_doc_freq[x[0]]
