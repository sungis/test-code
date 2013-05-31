环境准备
========================
setuptools-0.6c11.tar.gz
zeromq-3.1.0-beta.tar.gz
Python 2.7.3
apt-get install mongoDB
apt-get install pip

    pip install pyzmq
    pip install whoosh

程序启动流程
========================
路由机ip    10.0.1.88
路由机      python ppqueue.py
检索机      python ppworker.py ./indexdir/ 10.0.1.88


程序结构
========================
zmq 作为服务接口

worker 从 mongoDB 读取 url 对应的 tags

根据tags 从 Whoosh 索引 的 招聘资料 中 按BM25 排序输出 结果集



客户端        lpclient
服务端队列    ppqueue
服务端工作机  ppworker
mongodb操作   mongodbclient 
索引操作      whoosh_test
结果集高亮    radix_tree
多模匹配      Multi-Pattern-Searching



索引与广告匹配流程
==================

技能抽取:
    多模匹配 加载 技能词库

索引更新:
    添加:职位介绍 ==> 多模匹配抽出 技能关键词 ==> 索引到Whoosh
    删除:根据jobid删除Whoosh对应索引

广告匹配:
    url ==> 抓取html ==> 抽取正文区域 ==> 多模匹配抽取技能关键词 ==>
    排序词频最高技能 ==> 搜索Whoosh索引 ==> 返回结果集


高频词统计:
    分词并统计词条tf-idf并排序


TODO 
==================
包装多模匹配为Whoosh的分词器
集成 206  /home/lihui/py/spider/creamer-read-only 下tagParser.py 过来 正文抽取 

拼装代码 并 部署

lpclient[1,2,3,4,5,6....]
提交请求 url
索引更新 {doc1,doc2,doc3...}

ppqueue(1) + ppqueue(2)
分发任务

ppworker [1,2,3,4,5,6.....]
触发:
    索引更新[增,删]
    广告匹配


发布-订阅模式
==============
  数据更新
  分发到 各个worker机

Query analysis
==============
  

线上部署
==============
pagetags
线下数据重跑tags 生成id对应url 插入线上数据库
线上数据按url排重后抓取分析tag后入库

线上部署程序,接受前端请求


