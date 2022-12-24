import json
import pandas as pd

f = open("fullname.json",'r',encoding='gbk')
data = []

for line in f.readlines():
    dic = json.loads(line)
    data.append(dic)

csv_data = pd.read_csv('data.csv',encoding='gbk')

codes = []
names = []
markets = []

for i in range(len(csv_data['code'])):
	codes.append(str(csv_data['code'][i]).zfill(6))
	names.append(csv_data['name'][i])
	markets.append(csv_data['market'][i])


for i in range(len(codes)):
	dic = {}
	dic['code'] = codes[i]
	dic['name'] = names[i]
	dic['location'] = markets[i]
	for line in data:
		if line['code'] == codes[i]:
			dic['fullname'] = line['fullname']

	print(i)
	with open("new.json","a") as f: 
	    str_ = json.dumps(dic, ensure_ascii=False)
	    f.write(str_)
	    f.write('\n')
	    f.close()
