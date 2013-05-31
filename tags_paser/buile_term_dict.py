import pymongo 
import math


# term ==> term_freq ,doc_freq
terms ={}
totalTermCount = 0
def update_terms(t,freq):
    if t in terms:
        terms[t][0] = terms[t][0] + freq
        terms[t][1] = terms[t][1] + 1
    else:
        terms[t]=[freq,1]


conn = pymongo.Connection(host='192.168.4.216', port=19753)
article = conn.tags.article
def load_data(id):
    global totalTermCount,terms
    one = article.find_one({"_id": id, "state_a": 1}, {"title_token": 1,"desc_token":1,"category_token":1})
    if one == None:
        return 
    title_token = one['title_token']+' '+one["desc_token"]+' '+one["category_token"]
    tokens = title_token.split(' ')
    term_freq = {}
    for t in tokens:
        t=t.strip()
        if len(t)==0:
            continue
        totalTermCount += 1

        if t in term_freq:
            term_freq[t]=term_freq[t]+1
        else:
            term_freq[t]=1
    for k,v in term_freq.iteritems():
        update_terms(k,v)

def term_idf_by_doc():
    global totalTermCount,terms
    print totalTermCount
    for k,v in terms.iteritems():
        freqTerm = v[0]
        idf = math.log(((totalTermCount - freqTerm + 0.5) / (freqTerm + 0.5)))
        print k,v,idf

if __name__ == '__main__':
    load_data('169')
    term_idf_by_doc()

