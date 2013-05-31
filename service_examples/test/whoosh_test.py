#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from whoosh.analysis import Tokenizer,Token
from whoosh.analysis import RegexTokenizer
from radix_tree import RadixTree

import jieba

class ChineseTokenizer(Tokenizer):  
    def __call__(self, value, positions=False, chars=False,  
             keeporiginal=False, removestops=True,  
             start_pos=0, start_char=0, mode='', **kwargs):  
        #assert isinstance(value, text_type), "%r is not unicode" % value  
        t = Token(positions, chars, removestops=removestops, mode=mode,  
            **kwargs)  
        seglist=jieba.cut(value,cut_all=True)  
        for w in seglist:  
            t.original = t.text = w  
            t.boost = 1.0  
            if positions:  
                t.pos=start_pos+value.find(w)  
            if chars:  
                t.startchar=start_char+value.find(w)  
                t.endchar=start_char+value.find(w)+len(w)  
            yield t 

def ChineseAnalyzer():  
    return ChineseTokenizer()

class JiebaTokenizer(Tokenizer):
  def __call__(self, value, positions=False, chars=False, keeporiginal=False,
                removestops=True, start_pos=0, start_char=0, tokenize=True,
                          mode='', **kwargs):
    value=" ".join(jieba.cut_for_search(value))
    reg = RegexTokenizer(r"[^ \t\r\n]+")
    return reg(value,positions,chars,keeporiginal,removestops,start_pos,start_char,mode,**kwargs)

def JiebaAnalyzer(lowercase=False):
  return JiebaTokenizer()

JiebaAnalyzer.__inittypes__ = dict(lowercase=bool)



#from whoosh.analysis import RegexAnalyzer
#rex = RegexAnalyzer(ur"([\u4e00-\u9fa5])|(\w+(\.?\w+)*)")
#terms = [token.text for token in rex(u"hi 中 000 中文测试中文 there 3.141 big-time under_score")]
#for t in terms:print t
#
#wj=JiebaTokenizer()
#terms = [token.text for token in wj(u"hi 中 000 中文测试中文 there 3.141 big-time under_score")]
#for t in terms:print t
#
#



from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer
analyzer = RegexAnalyzer(ur"([\u4e00-\u9fa5])|(\w+(\.?\w+)*)")
analyzer = JiebaAnalyzer()
#analyzer = ChineseAnalyzer()

schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=analyzer))
ix = create_in("indexdir", schema)
writer = ix.writer()
writer.add_document(title=u"First document”, path=u”/a",
    content=u"This is the first document we’ve added!")
writer.add_document(title=u"Second document”, path=u”/b",
    content=u"The second one 你 中文测试中文 is even more interesting!")
writer.commit()
searcher = ix.searcher()

query = u"first"
results = searcher.find("content", query)
print results
print results[0]['content']

#print '===>',results[0].highlights('content')

rt = RadixTree()
rt.insert(query,query)
print rt.high_light(results[0]['content'])

query = u"你"
results = searcher.find("content", u"你")
print results[0]['content']

rt = RadixTree()
rt.insert(query,query)
print rt.high_light(results[0]['content'])

query = u"测试"
results = searcher.find("content", u"测试")
print results[0]['content']

rt = RadixTree()
rt.insert(query,query)
print rt.high_light(results[0]['content'])

