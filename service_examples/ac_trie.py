#!/usr/bin/python2.7
#-*-coding=utf-8-*-



class Trie:
    """用来存储关键词和进行多模匹配  """
    def __init__(self,filepath=None):
        self.nodetype=0
        self.child={}
        self.fail=None
        self.strout=""
        self.tag=0
        if filepath!=None:
            f=open(filepath)
            for s in f:
                s=s.strip().lower()
                if len(s)>1:
                    self.add(s)
            f.close()

    def add(self,word):
        """ 添加关键词word, word--unicode码 """
        node=self
        for  w in word:
            #print w
            if w not in node.child:
                    node.child[w]=Trie()
            node=node.child[w]
        node.nodetype=1
        node.strout=word
        self.tag=0

    def find(self,word):
        """ 在trie树中搜索关键词, word---unicode码"""
        node=self
        for w in word:
            if w not in node.child:
                return False
            node=node.child[w]
        if node.nodetype==1:
            return True
        else:
            return False

    def getfail(self):
        """计算每个节点的失败跳转节点"""
        if self.tag:
            return
        que=[]
        self.fail=self
        que.append(self)
        while len(que):
            par=que[0]
            del que[0]
            for w,ch in par.child.items():
                while par.fail is not self and (w not in par.fail.child):
                    par=par.fail
                if par.fail is self and ((w not in self.child) or self.child[w] is ch):
                    ch.fail=self
                else:
                    ch.fail=par.fail.child[w]
                que.append(ch)
        self.tag=1
    
    def parse(self,lang):
        """ 对lang进行多模匹配,返回‘(匹配位置,keyword)’的列表，lang---unicode码"""
        if self.tag==0:
            self.getfail()
        result=[]
        node=self
        i=0
        n=len(lang)
        re_skip = re.compile(ur"[a-zA-Z0-9]+")
        while i<n:
            if lang[i] in node.child:
                node=node.child[lang[i]]
                if node.nodetype==1:
                    #主要解决英文字符问题
                    skill_flag = True
                    if re_skip.match(node.strout):
                        if i-len(node.strout) >= 0 and \
                                re_skip.match(lang[i-len(node.strout)]):
                                    skill_flag=False
                        elif i+1 < n and re_skip.match(lang[i+1]) :
                            skill_flag=False

#                    if i-len(node.strout) >= 0 and i+1 < n:
#                        a_ = lang[i-len(node.strout)]
#                        b_ = lang[i+1]
#                        c_ = node.strout
#                        #print a_,b_,lang[i], node.strout
#                        if re_skip.match(c_) and re_skip.match(a_) and re_skip.match(b_) :
#                            skill_flag=False
                    #如果命中结果为英文字符中的一部分则不符合需求
                    if skill_flag:
                        result.append((i-len(node.strout)+1,node.strout))
                i+=1
            else:
                if node is self:
                    i+=1
                else:
                    node=node.fail
        return result   


from urllib import urlopen
import re

if __name__=='__main__':
    t = Trie('./dict/skill.txt')
    print t.find('java')
    url = 'http://ar.newsmth.net/thread-20eb093fe92395-1.html'
    text = urlopen(url).read()
    dr = re.compile(r'<[^>]+>',re.S)
    text = dr.sub('',text)
    #text = 'aa@gmail.com中文java'
    #print text
    result = t.parse(text)
    for r in result:
        print r
