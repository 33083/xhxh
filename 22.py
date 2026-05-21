import json
# a={'a':'张三','b':'2','c':['python','java']}
# b=json.dumps(a,ensure_ascii=False,indent=2)
# print(b)
# c=json.loads(b)
# print('\n:',c['a'])
# print(':',c['c'])
# d=json.dumps(a,ensure_ascii=False,indent=4)
# print(d)


a={"company": "Alibaba",
"employees": [{"name": "Alice", "position": "Engineer", "salary": 10000},
              {"name": "Bob", "position": "Manager", "salary": 15000}],
"location": "Hangzhou"}
b=json.dumps(a,ensure_ascii=False,indent=2)
c=json.loads(b)
print('\n:',c['company'])
print(':',c['location'])
d=[]
for i in c['employees']:
    print('\n',i['name'],'\n',i['position'])
    d+=i['salary']
print(d/2)
