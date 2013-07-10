#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
#=============================================================================
#     FileName: matrix.py
#         Desc: 文件转矩阵
#       Author: Sungis
#        Email: mr.sungis@gmail.com
#     HomePage: http://sungis.github.com
#      Version: 0.0.1
#   LastChange: 2013-07-09 12:15:18
#      History:
#=============================================================================
'''
import matplotlib 
matplotlib.use("Agg") 
import pickle 
import math
import jieba.posseg as pseg
#从单词的str到单词的id
termToId = {}
#从单词的id到单词的str
idToTerm = {}
#某一个单词的id对应了多少篇文档
idToDocCount = {}
#某一个分类里面有多少篇文档
classToDocCount = {}
#term 对应 idf
idToIdf = {}

#过滤词条
def filter(w):
    if w.word == None or len(w.word.strip())<=1:
        return False
    if w.flag not in ('x','w','m'):
        return True
    else:
        return False
#文档转为矩阵
def doc2term(path):
    f = open(path,'r')
    rows = [0]
    cols = []
    vals = []
    y = []
    uid = 0    
    for line in f:
        vec = line.split("\t")
        line = vec[0]
        target = int(vec[1])
        y.append(target)
        words = pseg.cut(line)
        doc_term_ids = []
        term_freqs = {}
        for w in words:
            if filter(w):
                term = w.word
                if not termToId.has_key(term):
                    termToId[term] = uid
                    idToTerm[uid] = term
                    uid += 1
                termid = termToId[term]
                doc_term_ids.append(termid)
                if (not term_freqs.has_key(termid)):
                    term_freqs[termid] = 1
                else:
                    term_freqs[termid] += 1
        doc_term_ids = set(doc_term_ids)
        doc_term_ids = list(doc_term_ids)
        doc_term_ids.sort()
        for i in doc_term_ids:
            cols.append(i)
            vals.append(term_freqs[i])
            if(not idToDocCount.has_key(i)):
                idToDocCount[i] = 1
            else:
                idToDocCount[i] += 1

        rows.append(rows[len(rows)-1]+len(doc_term_ids))
        if (not classToDocCount.has_key(target)):
            classToDocCount[target] = 1
        else:
            classToDocCount[target] += 1

    for i in idToTerm.keys():
        idToIdf[i] = math.log(float(len(rows) - 1) /(idToDocCount[i] + 1))

    f.close()
    return rows, cols, vals , y


"""
filter given x,y by blackList
x's row should == y's row
@return newx, newy filtered
"""
def MatrixFilter(idMap,nRow,rows, cols, vals , y):
    #check parameter
    if (nRow <> len(y)):
        print "ERROR!x.nRow should == len(y)"
        return False

    #stores new rows, cols, and vals
    newRows = [0]
    newCols = []
    newVals = []

    for r in range(nRow):
        curRowLen = 0

        #debug
        #print "===new doc==="

        for c in range(rows[r], rows[r + 1]):
            if idMap[cols[c]] >= 0 :
                newCols.append(idMap[cols[c]])
                newVals.append(vals[c])
                curRowLen += 1

        newRows.append(newRows[len(newRows) - 1] + curRowLen)
    return newRows, newCols, newVals, y



"""
create a blackList by given x,y
@rate is a percentage of selected feature
using next formulation:
X^2(t, c) =   N * (AD - CB)^2
            ____________________
            (A+C)(B+D)(A+B)(C+D)
A,B,C,D is doc-count
A:     belong to c,     include t
B: Not belong to c,     include t
C:     belong to c, Not include t
D: Not belong to c, Not include t

B = t's doc-count - A
C = c's doc-count - A
D = N - A - B - C

and score of t can be calculated by next 2 formulations:
X^2(t) = sigma p(ci)X^2(t,ci) (avg)
           i
X^2(t) = max { X^2(t,c) }     (max)
@return true if succeed
"""
def TrainFilter(nRow,nCol,rows, cols, vals , y):
    rate = 0.2
    logPath = './filter.log'
    modelPath = './filter.model'
    method = 'max'
    #check parameter
    if not ((method == "avg") or (method == "max")):
        print "ERROR!method should be avg or max"
        return False

    if (nRow <> len(y)):
        print "ERROR!x.nRow should == len(y)"
        return False

    #using y get set of target
    yy = set(y)
    yy = list(yy)
    yy.sort()

    #create a table stores X^2(t, c)
    #create a table stores A(belong to c, and include t
    chiTable = [[0 for i in range(nCol)] for j in range(yy[len(yy) - 1] + 1)]
    aTable = [[0 for i in range(nCol)] for j in range(yy[len(yy) - 1] + 1)]

    #calculate a-table
    for row in range(nRow):
        for col in range(rows[row], rows[row + 1]):
            aTable[y[row]][cols[col]] += 1

    #calculate chi-table
    n = nRow
    for t in range(nCol):
        for cc in range(len(yy)):
            #get a
            a = aTable[yy[cc]][t]
            #get b
            b = idToDocCount[t] - a
            #get c
            c = classToDocCount[yy[cc]] - a
            #get d
            d = n - a - b -c
            #get X^2(t, c)
            numberator = float(n) * (a*d - c*b) * (a*d - c*b)
            denominator = float(a+c) * (b+d) * (a+b) * (c+d)
            chiTable[yy[cc]][t] = numberator / denominator

    #calculate chi-score of each t
    #chiScore is [score, t's id] ...(n)
    chiScore = [[0 for i in range(2)] for j in range(nCol)]
    if (method == "avg"):
        #calculate prior prob of each c
        priorC = [0 for i in range(yy[len(yy) - 1] + 1)]
        for i in range(len(yy)):
            priorC[yy[i]] = float(classToDocCount[yy[i]]) / n

        #calculate score of each t
        for t in range(nCol):
            chiScore[t][1] = t
            for c in range(len(yy)):
                chiScore[t][0] += priorC[yy[c]] * chiTable[yy[c]][t]
    else:
        #calculate score of each t
        for t in range(nCol):
            chiScore[t][1] = t
            for c in range(len(yy)):
                if (chiScore[t][0] < chiTable[yy[c]][t]):
                    chiScore[t][0] = chiTable[yy[c]][t]

    #sort for chi-score, and make blackList
    chiScore = sorted(chiScore, key = lambda chiType:chiType[0], reverse = True)

    #init idmap
    idMap = [0 for i in range(nCol)]

    #add un-selected feature-id to idmap
    for i in range(int(rate * len(chiScore)), len(chiScore)):
        idMap[chiScore[i][1]] = -1
    offset = 0
    for i in range(nCol):
        if (idMap[i] < 0):
            offset += 1
        else:
            idMap[i] = i - offset
#            newIdToId[i - offset] = i

    #output model information
    if (modelPath <> ""):
        f = open(modelPath, "w")
        modelStr = pickle.dumps([idMap], 1)
        pickle.dump(modelStr, f)
        f.close()

    #output chiSquare info
    if (logPath <> ""):
        f = open(logPath, "w")
        f.write("chiSquare info:\n")
        f.write("=======selected========\n")
        for i in range(len(chiScore)):
            if (i == int(rate * len(chiScore))):
                f.write("========unselected=======\n")
            term = idToTerm[chiScore[i][1]]
            score = chiScore[i][0]
            f.write(term.encode("utf-8") + " " + str(score) + "\n")
        f.close()

    return idMap

def chisquate_filter(rows, cols, vals,y):
    nRow = len(rows) - 1
    maxCol = -1
    for col in cols:
        if (col > maxCol):
            maxCol = col
    nCol = maxCol + 1
    idMap = TrainFilter(nRow,nCol,rows, cols, vals,y)
    return MatrixFilter(idMap,nRow,rows, cols, vals,y)


path = '/home/pongo/gitwork/python-data-mining-platform/trunk/example/data/cluster.200'
#path = '/home/pongo/gitwork/python-data-mining-platform/trunk/example/sogouMini_output'

#rows doc term size
#cols term id
#vals term freq
#y    doc class
rows, cols, vals,y =  doc2term(path)
rows, cols, vals,y = chisquate_filter(rows, cols, vals,y)

import numpy as np
from scipy.cluster.vq import vq, kmeans, whiten,kmeans2

mdata = np.zeros((len(y),len(idToTerm)))
j = 0
d = 0
for i in range(1,len(rows)):
    for k in range(j,rows[i]):
        tid = cols[k]
        freq = vals[k]
        mdata[d][tid] = freq
    j=rows[i]
    d +=1

center = kmeans(mdata,len(set(y)))[0]
result = vq(mdata,center)[0]
dicResult = {}
resultList = result.tolist()
i = 0
for i in range(len(resultList)):
    if dicResult.has_key(resultList[i]):
        dicResult[result[i]].append(i)
    else:
        dicResult[result[i]] = [i]

for v in range(len(dicResult)):
    print '====================='
    for i in dicResult[v]:
        print i,y[i]


#生成图像
from scipy.sparse import *
from scipy import *
import scipy.sparse.linalg
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
import matplotlib.cbook as cbook

a = csr_matrix(mdata)
(u,s,vt) = scipy.sparse.linalg.svds(a, 2)
s = np.diag(s)
colSpaceTrans = np.dot(s, vt).transpose()
b = np.dot(a.todense(),colSpaceTrans)
colors = []
for i in y:
    if (i==7):colors.append('r')
    if (i==2):colors.append('g')
xOffsets = []
yOffsets = [] 
for row in b:
    xOffsets.append(row[0,0]) 
    yOffsets.append(row[0,1]) 
fig = plt.figure()
ax = fig.add_subplot(111)
ax.scatter(xOffsets, yOffsets,c=colors,alpha=0.75)
plt.savefig("1.png")
