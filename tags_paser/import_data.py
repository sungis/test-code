import MySQLdb
import pymongo
#10.0.1.77 mongodb
mdbconn = pymongo.Connection(host='192.168.4.216', port=19753)

cur=None
conn=None

def dbconn():
    global cur
    global conn
    if cur==None:
        conn=MySQLdb.connect(host='192.168.4.228',user='lihui',passwd='lihui123$',port=3306)
        cur=conn.cursor()
        conn.select_db('Blog')
        cur.execute('set names utf8')
def dbclose():
    global cur
    global conn
    if cur!=None:cur.close()
    if conn!=None:conn.close()

def load_data(sql):
        count=cur.execute(sql)
        return cur.fetchall()
        
def load_blog_id():
        sql = 'SELECT ArticleId FROM Article'
        results = load_data(sql)
        for r in results:
            print r[0]


def load_blog():
    blog_id_f = open('./data/blog_id.txt')    
    for id in blog_id_f:
        load_blog(id)

def load_blog(id):
    sql = '''SELECT ArticleId,UserName,Title,Description FROM Article 
            where ArticleId='''+ id

    results = load_data(sql)
    if len(results)>0:
        r=results[0]

        ArticleId = r[0]
        UserName = r[1]
        Title = r[2]
        Description = r[3]

        sql ='''SELECT c.Name FROM ArticleCategory b
        LEFT JOIN  Category AS c ON c.CategoryId=b.CategoryId
        WHERE b.ArticleId='''+id
        results = load_data(sql)
        category = ''
        for r in results:
            if r[0]!=None:
                category +=r[0]+','

        mdbconn.tags.article.insert(
        {"_id":str(ArticleId),
            "UserName":UserName,
            "Title":Title,
            "Description":Description,
            "category":category,
            "state_a":0,
            "state_b":0,
            "state_c":0
            })


if __name__ == '__main__':
    dbconn()
    #load_blog_id()
    load_blog()
    #load_blog('169')
    dbclose()
