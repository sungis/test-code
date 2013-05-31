import jieba
import jieba.analyse
import pymongo

conn = pymongo.Connection(host='192.168.4.216', port=19753)
article = conn.tags.article

def cut_text(text):
    tokens=jieba.cut(text)
    seg_list = [x for x in tokens]
    count=len(seg_list) 
    return ' '.join(seg_list),count
def load_data(id):
    one = article.find_one({"_id": id, "state_a": 0}, {"Title": 1,"Description":1,"category":1})
    if one == None:        
        return
    title_token,title_count=cut_text(one["Title"])
    desc_token,desc_count=cut_text(one["Description"])
    category_token,category_count=cut_text(one["category"])
    article.update({"_id":id},{"$set":{"state_a":1,
        "title_token":title_token,"title_count":title_count,
        "desc_token":desc_token,"desc_count":desc_count,
        "category_token":category_token,"category_count":category_count
        }})


if __name__ == '__main__':
    blog_id_f = open('./data/blog_id.txt')    
    for id in blog_id_f:
        load_data(id.strip())

#    load_data('169')
#    load_data('170')
