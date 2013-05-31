import sys
import operator 
#k = int (sys.argv[1])
f=open('stackoverflow_tag.txt')
x={}
for l in f:               
    s=l[0:l.find(' ')].strip()
    x[s]=len(s)
#    if len(s)<k:
#        print l[0:l.find(' ')]
sorted_x = sorted(x.iteritems(), key=operator.itemgetter(1))
for k in sorted_x:
    print k[0],k[1]

