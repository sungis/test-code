#-*-coding=utf-8-*-
text ='''
诚聘Java高级搜索工程师
诚聘java高级搜索工程师 

        java高级搜索工程师

        全文检索技术是当今互联网应用的基础之一，我们不仅仅需要你了解lucene，了解搜索技术，更需要利用搜索技术实现海量数据的分析和提取，实现千万级用户的行为智能识别和精准定位。你希望在搜索技术领域进行深度的技术钻研和创新吗？你希望通过自己的技术创新驱动整个公司的发展吗？你希望自己实现的搜索产品成为中国互联网的酷应用吗？ 你希望跟随团队的成长和公司的成长，让自己站在更高的职业发展平台和得到更好潜在的个人回报吗？那么这个职位就是为你而准备的！

        地点：北京

        职位描述：

        1、基于全文检索技术开发网站的各类搜索相关的功能

        2、基于全文检索技术开发网站的智能内容分类系统

        3、基于全文检索技术对海量数据进行分析和提取，实现用户行为的智能识别和精准的用户推荐系统

        4、带领搜索和数据挖掘技术团队，打造技术核心竞争力

        ;

        必备条件（必须满足）：

        1、计算机领域的编程基础扎实，具备很强的自学能力

        2、对编程有发自内心的热爱和兴趣，有废寝忘食钻研技术的劲头，爱好程序员这个职业

        3、工作踏踏实实，做事情耐心细致

        4、5年以上java编程经验，3年以上lucene实际开发经验，对全文检索技术有深入的掌握

        5、对海量数据的检索和分析有实践经验，了解推荐引擎和数据挖掘的理论知识

        薪资福利：

        1、公司提供有竞争力的薪资待遇

        2、提供北京市规定的社会保险之外，给员工提供额外的商业医疗保险

        3、月度奖励金+年终奖金

        4、带薪年假、生日礼券、过节费、年度郊游等多项福利制度


        你需要提供的材料：

        1、一份个人简历，重点介绍你掌握什么知识和技术，有过哪些编程相关的实践和项目

        2、提供你编写的lucene实际案例代码，并简要介绍该项目代码的技术实现要点
'''
import re
import json
from actrie import Trie
t=Trie('./skill.txt')
#print t.find('数据挖掘')
#for a in t.parse(text):
#    print a[1]

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
        tags=t.parse(value)
        for a in tags:print a[1]
    break
