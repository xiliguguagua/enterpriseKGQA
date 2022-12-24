import pandas as pd


def only_Eng(s):
    for i in s:
        if ord(i) > 0x7f:
            return False
    return True


def ReadPairs(fp, encode_type='utf-8'):
    entity = set()
    relation = set()
    pair = []
    rel_idx = {}
    for data in open(fp, 'r', encoding=encode_type):
        p = data.strip().split(',')
        # print(p)
        # print(p[-3], p[-2], p[-1])
        # input()

        pair.append(p[-3:])
        entity.add(p[-3])
        entity.add(p[-2])
        relation.add(p[-1])

    entity = list(entity)
    relation = list(relation)
    relation.sort()

    for i in range(len(relation)):
        rel_idx[relation[i]] = i

    for p in pair:
        p[2] = rel_idx[p[2]]

    with open('./data/rel_idx.txt', 'w') as file:
        for i in relation:
            file.write(str(rel_idx[i]) + ',' + i + '\n')

    return [entity, relation, pair]


def generate_dict():
    for data in open('./data/entity.csv',encoding='utf-8'):
        d = data.split(',')
        if len(d) != 10:
            print(data)
            continue
        try:
            type = d[1].replace(':', '')
        except:
            print(data)
            print(d)
            print('\n\n')
            continue
        try:
            if type == 'Company':
                with open('./dict/company.txt', 'a', encoding='utf-8') as file:
                    fullname = d[4].split(' ')[0]
                    name = d[-5].split(' ')[0]
                    if len(name) > 0:
                        file.write(name + ' nt\n')  # 机构团体
                    if len(fullname) > 0:
                        file.write(fullname + ' nt\n')  # 机构团体
            # if type == 'Industry':
            #     with open('./dict/industry.txt', 'a', encoding='utf-8') as file:
            #         name = d[-5].split(' ')[0]
            #         file.write(name + ' n\n')  # 名词
            # if type == 'Product':
            #     with open('./dict/product.txt', 'a', encoding='utf-8') as file:
            #         name = d[-5].split(' ')[0]
            #         file.write(name + ' n\n')
            # if type == 'Person':
            #     with open('./dict/person.txt', 'a', encoding='utf-8') as file:
            #         name = d[-5].split(' ')[0]
            #         file.write(name + ' nr\n')  # 人名
        except:
            print(data)
            print(d)
            print('\n\n')

def generate_new_dict():
    with open('./dict/names.txt', 'w', encoding='utf-8') as file:
        for data in open('./data/entity.csv', 'r', encoding='utf-8'):
            d = data.split(',')
            name = d[5]
            fullname = d[4]
            if len(name) > 0:
                file.write(name+'\n')
            if len(fullname) > 0:
                file.write(fullname+'\n')


# ReadPairs('./data/rels.csv')
# generate_dict()
# generate_new_dict()
