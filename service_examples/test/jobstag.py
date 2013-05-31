from actrie import Trie
import re
import json
import  os
import sys
t=Trie('./skill.txt')

def cut(value):
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

f = open('./data/jobs.txt')
re_jobs= re.compile('{"jobid":.*,"salaryrangecode"')
for i in f:
    m = re_jobs.search(i)
    if m:
        data = m.group()+":0}"
        jdata = json.loads(data);
        value = jdata['jobname'] +' '+ jdata['description']
        #value = jdata['description']
        value=value.lower().replace('&nbsp','')
        value = value.encode('UTF-8')
        seglist=cut(value)
#        if len(seglist) == 0:
        print value 
        print '========================'
        print '|'.join(seglist)    
        ch = sys.stdin.read(1)        
