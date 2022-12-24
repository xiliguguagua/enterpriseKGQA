import json

f = open("old.json",'r',encoding='utf-8')
old_data = []

for line in f.readlines():
    dic = json.loads(line)
    old_data.append(dic)

f = open("new.json",'r',encoding='gbk')
new_data = []

for line in f.readlines():
    dic = json.loads(line)
    new_data.append(dic)

for line in new_data:
	dic = line
	time = 'none'
	for line1 in old_data:
		if line1['code'] == line['code']:
			time = line1['time']

	dic['time'] = time

	
	with open("company.json","a") as f: 
	    str_ = json.dumps(dic, ensure_ascii=False)
	    f.write(str_)
	    f.write('\n')
	    f.close()
