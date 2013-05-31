import pymongo

conn = pymongo.Connection(host='192.168.4.216', port=19753)

db = conn.pongo
webData = db.webData
webData.insert(
{"_id":"http://www.iteye.com/","state":2,"tags":"java"})
url = "http://blog.csdn.net/zhangchaoyangsun/article/details/8879615"
one = webData.find_one({"_id": url, "state": 2}, {"tags": 1})
print one
print one["tags"]
