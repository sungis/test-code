# -*- coding: UTF-8 -*-

from whoosh.analysis import Tokenizer,Token
from whoosh.analysis import RegexTokenizer
from whoosh.index import create_in
from whoosh import index,sorting
from whoosh.qparser import QueryParser
from whoosh.fields import *
from radix_tree import RadixTree
import pymongo
from ac_trie import Trie
import json
import uuid
from cache.lrucache import LRUCache
from hashlib import md5
import config
import logging
LOG_FILENAME="./data/ad_service.log"
logger=logging.getLogger()
handler=logging.FileHandler(LOG_FILENAME)
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

class ADIndex:

    def get_mac_address(self):
        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:]
        return mac

    def __init__(self,indexdir):
        exists = index.exists_in(indexdir)
        if exists :
            self.ix =index.open_dir(indexdir)
        else:
            schema = Schema(title=TEXT(stored=True),
                    id=NUMERIC(unique=True,stored=True),
                    orgid=NUMERIC(stored=True),
                    ishunterjob=NUMERIC(stored=True),
                    tags=KEYWORD(stored=True)
                    )
            self.ix = create_in(indexdir, schema)
        self.mac_address=self.get_mac_address()
        self.conn = pymongo.Connection(config.MONGO_CONN)
        self.tagsParser = Trie(config.SKILL_FILE)
        self.cache = LRUCache(1024)
     
    def add_doc(self,jobs):
        writer = self.ix.writer()
        rep =[] 
        for j in jobs:
            writer.update_document(id=j[0],orgid=j[1],
                    title=j[2],tags=j[3]
                    ,ishunterjob=j[4])
            rep.append('add doc :'+str(j[0]))
        writer.commit()
        return rep

    def del_doc(self,id):
        self.ix.delete_by_term('id',id)
        return ['del doc :'+str(id)+'\r\n']
    def find_by_query(self,q,limit):
        jobs = self.ix.searcher().search(q,limit=limit)
        return jobs
    def find_unique_orgid(self,q,limit):
        facet = sorting.FieldFacet("id", reverse=True)
        jobs = self.ix.searcher().search(q,collapse="orgid",sortedby=facet,limit=limit)
        return jobs
    def find_all(self,limit):
        qp = QueryParser("id", schema=self.ix.schema)
        q = qp.parse(u'*')
        return self.find_by_query(q,limit)
    def find_all_unique_orgid(self,limit):
        qp = QueryParser("id", schema=self.ix.schema)
        q = qp.parse(u'*')
        return self.find_unique_orgid(q,limit)
    def hunter_job(self,limit):
        qp = QueryParser("ishunterjob", schema=self.ix.schema)
        q = qp.parse(u'1')
        return self.find_unique_orgid(q,limit)

    def find(self,query,limit):
        query = query.strip()
        if len(query) == 0:
            query =u'*'
        searcher=self.ix.searcher()
        qp = QueryParser("tags", schema=self.ix.schema)
        q = qp.parse(query)
        return searcher.search(q,limit=limit)
#state 0  插入 链接
#state 1  插入 正文
#state 2  插入 标签
    def search_by_url(self,url,limit):
        pagetags = self.conn.pongo.pagetags
        pageurls = self.conn.pongo.pageurls
        url = unicode(url)
        one = pagetags.find_one({"_id": url}, {"tags": 1})
        if one :
            tags = one["tags"]
            return self.find(tags,limit)
        else:
            pageurls.insert({"_id":url})
            #return ['insert :'+url]
            return None
    def jobs2json(self,jobs):
        rep = {}
        rep["server"] = self.mac_address
        rep["state"] = True
        response = {}
        rep['response'] = response
        if jobs == None:
            response['totalCount']=0
            return rep
        response['totalCount']=len(jobs)
        #response['usedTime']=jobs.runtime
        items=[]
        for j in jobs:
            job={}
            job['jobId'] = j['id'] 
            job['orgid'] = j['orgid']
            job['jobTitle'] = j['title']
            items.append(job) 

        response['items']=items
        return rep
    def search(self,query,limit,hunterjob,uniqueorgid):
        if hunterjob:
            return self.hunter_job(limit)
        elif uniqueorgid:
            return self.find_all_unique_orgid(limit)
        else:
            return self.find(query,limit)

    def cut(self,value):
        value=value.lower().replace('&nbsp','')
        value = value.encode('UTF-8')
        terms = self.tagsParser.parse(value)
        v = {}
        for i in terms:
            v[i[0]]=i[1]
        return v.values()

    def get_cache(self,k):
        if k in self.cache:
            return self.cache[k]
        else:
            return None
    def add_cache(self,k,rep):
        self.cache[k] = rep

    def dispatch_hander(self,worker,frames):
        header = frames[2]
        data = frames[3]
        mkey = ''
        #走缓存出结果
        if header == 'search':
            m = md5()
            m.update(data)
            mkey = m.hexdigest()
            rep = self.get_cache(mkey)
            if rep != None:
                rep = json.dumps(rep)
                msg = [frames[0],frames[1],rep.encode('UTF-8')]
                worker.send_multipart(msg)
                logger.info('search get_cache:'+mkey)
                return 
        #无缓存流程
        jdata = json.loads(data.replace("''","0"),strict=False)
        action = jdata ["action"]
        rep = 'request err :'+data
        if header == 'update' and action == "updateDoc":
            jobs=[]
            for j in jdata['fields']:
                tags = self.cut(j['jobname']+' '+j['description'])
                jobid = j['jobid']
                orgid = j['orgid']
                jobname = unicode(j['jobname'])
                tags = ' '.join(tags).decode('UTF-8')
                ishunterjob=j['ishunterjob']
                jobs.append((jobid,orgid,jobname,tags,ishunterjob))

            rep = self.add_doc(jobs)
        #remove
        #{"action":"removeDoc","name":"job","keyId":"64983"}
        if header == 'remove' and action == "removeDoc":
            keyid = jdata ["keyId"]
            rep =self.del_doc(int(keyid))
        if header == 'search':
            size = jdata['output']["size"]
            if action == 'adv':
                referurl = jdata['q']["referurl"]
                if referurl in self.cache:
                    rep = self.cache[referurl]
                else:
                    rep = self.jobs2json(self.search_by_url(referurl,size))
                    self.cache[referurl] = rep
                logger.info('adv:'+referurl)
            elif action == 'searchJob':
                keyword = ''
                uniqueorgid = False
                hunterjob = False
                if jdata.has_key('filter'):
                    f = jdata['filter']
                    if f.has_key('uniqueKey'):
                        uniqueorgid = True
                    if f.has_key('jobflag'):
                        hunterjob = True
                if jdata.has_key('q') and jdata['q'].has_key('keyword'):
                    keyword = jdata['q']["keyword"]
                rep = self.jobs2json(self.search(keyword,size,hunterjob,uniqueorgid))
                logger.info('searchJob:keyword['+keyword+']')
            elif action == 'all' :#所有职位
                rep = self.jobs2json(self.find_all(size))
                logger.info('search all')
            elif action == 'uniqueorgid': #按orgid排重后的所有职位
                rep = self.jobs2json(self.find_all_unique_orgid(size))
                logger.info('search uniqueorgid')
            elif action == 'hunterjob':#获取最新猎头数据
                rep = self.jobs2json(self.hunter_job(size))
                logger.info('search hunterjob')
            #搜索结果添加缓存
            self.add_cache(mkey,rep)
        rep = json.dumps(rep)
        msg = [frames[0],frames[1],rep.encode('UTF-8')]
        worker.send_multipart(msg)

if __name__ == '__main__' :
    aix = ADIndex('indexdir')
    jobs =[
            (1,u'java搜索',u'java linux lucene'),
            (2,u'ruby开发',u'java linux linux ruby'),
            (3,u'python开发',u'java linux linux python')
          ]
    aix.add_doc(jobs)
    aix.del_doc(2)
    jobs = aix.find(u'java linux',10,False,False)
    print jobs
    for j in jobs:
        print j,j.score
