# -*- coding: UTF-8 -*-
import math
import operator  



text = u'四是四十是十十四是十四四十是四十'
text = u'吃葡萄不吐葡萄皮不吃葡萄倒吐葡萄皮吃葡萄不吐葡萄皮不吃葡萄为什么倒吐葡萄皮'
text = ''
file_name = './time.txt'
file_name='shengjing.txt'

#f = open(file_name)
#i = 0
#for l in f:
#    text += l.decode('GBK')
#    i+=1
#    if i>500:break


import pymongo

conn = pymongo.Connection(host='192.168.4.216', port=19753)
article = conn.tags.article
def load_data():
    blog_id_f = open('./data/blog_id.txt')    
    text =''
    i=0
    for id in blog_id_f:
        id =id.strip()
        one = article.find_one({"_id": id}, {"Title": 1,"Description":1,"category":1})        
        text+=one["Title"]+one["Description"]+one["category"]
        i+=1
        if i>500:break
    return text

text = load_data() 

text = ''.join([x for x in text if x.isalpha() or x.isspace()])
terms =[]
cutlist = u" [。，,！……!《》<>\"':：？\?、\|“”‘’；]{}（）{}【】()｛｝（）：？！。，;、~——+％%`:“”＂'‘\n\r"
for i in range(len(text)):
    for j in range(1,6):
        k = i+j
        if (k<len(text)):
            if text[k] !=' ':
                terms.append(text[i:k])

terms = sorted(terms)
term_count = 0
term_freq = {}
term_left = {}
term_right = {}
term_info ={}
for t in terms:
    term_count+=1
    t=t.strip()
    if len(t)==0:
        continue
    if t in term_freq:
        term_freq[t]=term_freq[t]+1
    else:
        term_freq[t]=1
    v = ''
    for c in t:
        if len(v)>0 and len(c.strip())>0:
            if v in term_right:
                term_right[v].append(c)
            else:
                term_right[v]=[c]
        v += c
    v = ''
    for i in range(len(t)):
        c = t[-(i+1)]
        if len(v)>0 and len(c.strip())>0:
            if v in term_left:
                term_left[v].append(c)
            else:
                term_left[v]=[c]
        v=c+v

result_list = {}
result_info = {}
def ngd(t):
    if len(t)>1:
        t1=t[0]
        t2=t[:len(t)]
        s1=0
        s2=0
        if result_info.has_key(t1) and result_info.has_key(t2):
            s1=result_info[t][3]/(result_info[t1][3]*result_info[t2][3])
        t1=t[len(t)-1]
        t2=t[0:len(t)-1]
        if result_info.has_key(t1) and result_info.has_key(t2): 
            s2=result_info[t][3]/(result_info[t1][3]*result_info[t2][3])
        if s1>s2:
            return s2
        else:
            return s1

for k in term_freq.keys():
    tmp = k+"==>"+str(term_freq[k])
    freq = float(term_freq[k])/term_count
    LE=0.0
    RE=0.0
    a=0
    b=0
    c=0

    if k in term_left:
        list_ = term_left[k]
        count_=len(list_)
        dict_ = dict([(x,list_.count(x)) for x in list_])
        a=len(dict_)
        for x in dict_.values():
            LE+= -math.log(float(x)/count_)*(float(x)/count_)

    if k in term_right:
        list_ = term_right[k]
        count_=len(list_)
        dict_ = dict([(x,list_.count(x)) for x in list_])
        b=len(dict_)
        for x in dict_.values():
            RE+= -math.log(float(x)/count_)*(float(x)/count_)

    if k in term_left:
        tmp +=' left:'+",".join(term_left[k])
    if k in term_right:
        tmp +=' right:'+','.join(term_right[k])
#    print tmp,LE,RE,freq
    result_info[k]=[tmp,LE,RE,freq,a,b]

print '=================================='

for k in result_info.keys():
    info = result_info[k]
    info.append(ngd(k))

    if info[1]>0.5 and info[2]>0.5 and info[-1]>250 and info[4]>4 and info[5]>4:
        if len(k)>1:
            result_list[k]=term_freq[k]

sorted_x = sorted(result_list.iteritems(), key=operator.itemgetter(1), reverse=True) 
i = 0
for r in sorted_x:
    p = result_info[r[0]]
    print '%s\t%d\t%f\t%f\t%d\t%d\t%f' %(r[0],r[1],p[1],p[2],p[4],p[5],p[6])
    i += 1
    if i> 300:
        break

#import sys
#
#while(True):
#    print 'input'
#    s = sys.stdin.readline()    
#    s = s.strip().decode('UTF-8')
#    if result_info.has_key(s):
#        p = result_info[r[0]]
#        print p[0],p[1],p[2],p[3]


