import random

from py2neo import Graph
import numpy as np
TYPES = 4
NODETYPES = ['Company', 'Industry', 'Person', 'Product']
RELTYPES = ['上游材料', '上级行业', '主营产品', '代理董事会秘书', '副经理', '副董事长', '外部监事','总经理','所属行业','持股','独立董事','监事','监事长','职工监事','董事','董事会秘书','董事长','财务总监']


class RL_path:
    def __init__(self):
        self.dict = []
        self.paths = {}
        self.path = {}
        self.q = {}
        self.g = Graph('http://localhost:7474', user='neo4j', password='1234')
        self.trys = 0

    def train(self):
        for data in open('./path/train_data.txt', encoding='utf-8'):
            data = data.strip()
            data = data.split(':')
            ans = data[1]
            tup = data[0].split('_')
            entity = tup[0]
            n = self.g.run("match (x) where x.name='{}' return x".format(entity)).data()
            if n is None:
                continue
            e_type = next(iter(n[0].get('x').labels))
            q_type = data[0].replace(entity, e_type)

            if q_type not in self.q:
                self.q[q_type] = {}
                self.paths[q_type] = {}
                for t in NODETYPES:
                    for a in NODETYPES:
                        for r in RELTYPES:
                            self.q[q_type][t+a][r] = 0

            n = self.g.run("match (x) where x.name='{}' return x".format(ans)).data()
            if n is None:
                continue
            t_type = next(iter(n[0].get('x').labels))

            self.trys = 0
            self.interact(entity, e_type, ans, t_type, q_type, [], 0)

        for i in self.paths:
            for j in i:
                print(j)


    def interact(self, cur, cur_type, des, des_type, q_type, p, step):
        if step > 6:
            return
        if self.trys > 1000:
            return
        rd = random.random()
        temp_p = p
        if cur == des:
            link = []
            for i in p:
                link.append(i[0]+'.'+i[1])
            lk = '_'.join(link)
            if lk in self.paths[q_type]:
                self.paths[q_type][lk] += 1/len(lk)
            else:
                self.paths[q_type][lk] = 1/len(lk)

        if rd > 0.5:
            rel = RELTYPES[random.randint(0, len(RELTYPES)-1)]
        else:
            rel = max(self.q[q_type][cur_type+des_type], key = self.q[q_type][cur_type+des_type])

        n = self.g.run("match (x)-[r:{}]->(E) where x.name = '{}' return E".format(rel,cur)).data()
        if len(n) > 0:
            i = random.randint(0, len(n)-1)
            cur = n[i]['E']['name']
            cur_type = next(iter(n[i].get('E').labels))
            temp_p.append([rel, '+'])
            self.interact(cur, cur_type, des, des_type, q_type, temp_p, step+1)

        temp_p = p
        n = self.g.run("match (E)-[r:{}]->(x) where x.name = '{}' return E".format(rel,cur)).data()
        if len(n) > 0:
            i = random.randint(0, len(n)-1)
            cur = n[i]['E']['name']
            cur_type = next(iter(n[i].get('E').labels))
            temp_p.append([rel, '-'])
            self.interact(cur, cur_type, des, des_type, q_type, temp_p, step + 1)

    def search_main(self, qt):
        if len(self.path) == 0:
            for data in open('./path/path_to_use.txt', encoding='utf-8'):
                data = data.strip()
                data = data.split(':')
                q_type = data[0]
                all_path = data[1]
                all_path = all_path.split(';')
                self.path[q_type] = []
                for p in all_path:
                    self.path[q_type].append(p)

        if len(self.path) == 0:
            return False, []

        entity = qt['entity'][0]
        n = self.g.run("match (x) where x.name='{}' return x".format(entity)).data()
        if n is None:
            return False, []
        e_type = next(iter(n[0].get('x').labels))
        cur_type = e_type + '_'
        for rr in qt['relation']:
            if rr[2] == 0:
                cur_type += rr[0]+'.0'
            elif rr[2] == 1:
                cur_type += rr[0]+'.+'
            else:
                cur_type += rr[0]+'.-'

        if len(qt['type_need']) == 1:
            cur_type += '_'+qt['type_need'][0]

        if cur_type not in self.path:
            return False, []

        flag, ans = self.path_go(qt, self.path[cur_type])
        return flag, ans

    def path_go(self, qt, paths):
        flag = True
        cur_node = qt['entity'][0]
        res = []
        ans = []

        for p in paths:
            cur_node = qt['entity'][0]
            rels = p.split('_')

            for r in rels:
                r_name, r_order = r.split('.')
                if r_order == '+':
                    res = self.g.run("match (x)-[r:{}]->(E) where x.name = '{}' return E".format(r_name,cur_node)).data()
                    if len(res) == 0:
                        flag = False
                        break
                    cur_node = res[random.randint(0,len(res)-1)]['E']['name']
                else:
                    res = self.g.run("match (E)-[r:{}]->(x) where x.name = '{}' return E".format(r_name,cur_node)).data()
                    if len(res) == 0:
                        flag = False
                        break
                    cur_node = res[random.randint(0,len(res)-1)]['E']['name']

            if flag and len(res) > 0:
                for s in res:
                    cur_type = next(iter(s.get('E').labels))
                    if len(qt['type_need']) == 0:
                        ans.append(s['E']['name'])
                    elif cur_type == qt['type_need'][0]:
                        ans.append(s['E']['name'])
                return True, ans
            else:
                return flag, ans

