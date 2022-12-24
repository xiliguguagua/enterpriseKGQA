from py2neo import Graph
from transX import TransR
from misc import ReadPairs
from mxnet import gluon, autograd, nd
from RL_path import RL_path

RELATION_1 = 1
RELATION_n = 2
ENTITY = 3


class searcher():
    def __init__(self):
        self.qt = []
        self.ans = []
        self.g = Graph('http://localhost:7474', user='neo4j', password='1234')
        self.rel_ans = []
        self.rel_order = []
        self.ans_type = 0
        self.fail = False
        self.RL = RL_path()

        entity, relationship, pair = ReadPairs('./data/rels.csv')
        r_i2t = nd.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
        self.transr = TransR(len(entity), len(relationship), e_dim=128, r_dim=64, r_types=18, r_i2t=r_i2t, margin=100)
        self.transr.load_parameters('./model/params1 (1)')
        self.rel2id = {'上游材料':0,'上级行业':1,'主营产品':2,'代理董事会秘书':3,'副经理':4,'副董事长':5,'外部监事':6,'总经理':7,'所属行业':8,'持股':9,'独立董事':10,'监事':11,'监事长':12,'职工监事':13,'董事':14,'董事会秘书':15,'董事长':16,'财务总监':17}

    def get_answer(self, q_t):
        self.qt = q_t
        self.ans = []
        self.ans_type = 1
        self.rel_ans = []
        self.rel_order = []
        self.fail = False

        self.search_main()

        if self.fail:
            print('没有搜索到答案，可能问题太复杂了或者库中缺失相关信息')
            return

        if self.ans_type == ENTITY:
            st = set()
            has_ans = 0
            nodes = self.search_entity(self.ans)
            flag = False
            for n in nodes:
                if len(q_t['query_attribute']) > 0:
                    for a in q_t['query_attribute']:
                        if n[a] is None:
                            continue
                        else:
                            if not flag:
                                print('查到如下信息')
                                flag = True
                            print(n[a])
                            has_ans += 1
                else:
                    if not flag:
                        print('查到如下信息')
                        flag = True
                    if n['name'] not in st:
                        print(n['name'])
                        st.add(n['name'])

            if len(q_t['query_attribute']) > 0 and has_ans == 0:
                print('没有查到指定的信息')
                if len(nodes):
                    print('搜索到相关的实体', end='')
                    for n in nodes:
                        print('，', n['name'], end='')
                    print('')

        if self.ans_type == RELATION_1:
            if self.rel_order[0] == 1:
                if self.rel_ans[0] == '持股':
                    print(' %s%s%s ' % (q_t['entity'][0], self.rel_ans[0], q_t['entity'][1]))
                else:
                    print(' %s的%s是%s ' % (q_t['entity'][0], self.rel_ans[0], q_t['entity'][1]))
            else:
                if self.rel_ans[0] == '持股':
                    print(' %s%s%s ' % (q_t['entity'][1], self.rel_ans[0], q_t['entity'][0]))
                else:
                    print(' %s的%s是%s ' % (q_t['entity'][1], self.rel_ans[0], q_t['entity'][0]))

        if self.ans_type == RELATION_n:
            print('%s和%s的关系为' % (q_t['entity'][0], q_t['entity'][1]), end='')
            e_s = q_t['entity'][0]
            for i in range(len(self.rel_ans)):
                if self.rel_order[i] == -1:
                    if self.rel_ans[i] == '持股':
                        print('，%s%s%s' % (e_s, self.rel_ans[i], self.ans[i]), end='')
                    else:
                        print('，%s的%s是%s' % (e_s, self.rel_ans[i], self.ans[i]), end='')
                else:
                    if self.rel_ans[i] == '持股':
                        print('，%s%s%s, ' % (self.ans[i], self.rel_ans[i], e_s), end='')
                    else:
                        print('，%s的%s是%s, ' % (self.ans[i], self.rel_ans[i], e_s), end='')
                e_s = self.ans[i]
            print('')

    def simple_search(self, e_num, r_num):
        if e_num == 1 and r_num == 1:
            e_name = self.qt['entity'][0]
            r_name = self.qt['relation'][0][0]

            if self.qt['relation'][0][2] == 0:
                n = self.g.run("match(x)-[R:{}]-(y) where x.name = '{}' return y".format(r_name, e_name)).data()
            elif self.qt['relation'][0][2] == 1:
                n = self.g.run("match(x)-[R:{}]->(y) where x.name = '{}' return y".format(r_name, e_name)).data()
            else:
                n = self.g.run("match(y)-[R:{}]->(x) where x.name = '{}' return y".format(r_name, e_name)).data()

            if n is not None:
                for t in n:
                    if len(self.qt['type_need']) > 0:
                        type = next(iter(t.get('y').labels))
                        if type in self.qt['type_need']:
                            self.ans.append(t['y']['name'])
                    else:
                        self.ans.append(t['y']['name'])

        if e_num == 2 and r_num == 0:
            e1 = self.qt['entity'][0]
            e2 = self.qt['entity'][1]

            self.rel_ans, self.rel_order = self.search_relation(e1, e2)

        if len(self.ans) > 0:
            self.ans_type = ENTITY
        elif len(self.rel_ans) > 0:
            self.ans_type = RELATION_1
        else:
            self.fail = True

    def search_main(self):
        e_num = len(self.qt['entity'])
        r_num = len(self.qt['relation'])

        self.simple_search(e_num, r_num)
        if not self.fail:
            return

        if e_num == 1 and r_num == 1:
            flag, ans = self.RL.search_main(self.qt)
            if flag:
                self.ans = ans
                self.fail = False
                self.ans_type = ENTITY
                return

        self.fail = False

        if e_num == 2 and r_num == 0:
            self.rel_ans, self.rel_order = self.search_relation(self.qt['entity'][0], self.qt['entity'][1])
            if len(self.rel_ans) == 0:
                self.ans_type = RELATION_n
                self.bfs(self.qt['entity'][1])
            else:
                self.ans_type = RELATION_1
        else:
            if e_num == 1:
                self.ans_type = ENTITY
                self.bfs()
            else:
                self.ans_type = ENTITY
                temp = self.qt['entity']
                self.qt['entity'] = temp[0: 1]
                self.bfs()
                if len(self.ans) > 0 and not self.fail:
                    return
                else:
                    self.qt['entity'] = temp[1:]
                    self.bfs()


    def search_entity(self, names):
        nodes = []
        for i in names:
            n = self.g.run("match(x) where x.name='{}' return x".format(i)).data()
            for t in n:
                nodes.append(t['x'])
        return nodes

    def search_relation(self, e1, e2, limit=0):
        if limit == 0:
            relation_list = self.g.run(
                "match(x)-[R]->(y) where x.name = '{}' and y.name = '{}' return R".format(e1, e2)).data()
            relation_list += self.g.run(
                "match(x)-[R]->(y) where x.name = '{}' and y.name = '{}' return R".format(e2, e1)).data()
        if limit == 1:
            relation_list = self.g.run(
                "match(x)-[R]->(y) where x.name = '{}' and y.name = '{}' return R".format(e1, e2)).data()
        if limit == -1:
            relation_list = self.g.run(
                "match(x)-[R]->(y) where x.name = '{}' and y.name = '{}' return R".format(e2, e1)).data()

        rel_ans = []
        order = []
        for rel in relation_list:
            rel_ans.append(self.get_rel_data(rel))
            if rel['R'].start_node['name'] == e1:
                order.append(1)
            else:
                order.append(-1)

        return rel_ans, order

    def get_rel_data(self, rel):
        data = type(rel.get('R')).__name__
        return data

    def bfs(self, aim_entity=[]):
        neighbour = []
        neighbour.append(self.qt['entity'][0])
        backtrace = []
        ids = []
        n = self.g.run("match (x) where x.name='{}' return x".format(neighbour[0])).data()
        ids.append(n[0]['x'].identity)
        backtrace.append(0)
        hop, cur, layer_end, end = [0, 0, 0, 0]
        close = False

        while cur <= end:
            if hop > 3:
                self.fail = True
                return

            if len(self.qt['relation']) > 0:  # has relation requirement
                rel, order = self.search_relation(neighbour[backtrace[cur]], neighbour[cur], self.qt['relation'][0][2])
                if len(rel) > 0:
                    for i in rel:
                        if i == self.qt['relation'][0][0]:
                            end, neighbour, backtrace, ids = self.filter_queue(neighbour, backtrace, cur, layer_end, ids)
                            layer_end = end
                            self.qt['relation'] = self.qt['relation'][1:]  # no need to check relation limit any more
                            break
            if len(self.qt['relation']) == 0 and self.ans_type == ENTITY:
                if len(self.qt['type_need']) > 0:
                    c_node = self.g.run("match (E) where E.name = '{}' return E".format(neighbour[cur])).data()
                    if len(c_node) > 0:
                        for i in c_node:
                            type = next(iter(i.get('E').labels))
                            if type == self.qt['type_need'][0]:
                                self.ans.append(neighbour[cur])
                                end = layer_end  # stop when this layer ends
                                close = True  # do not take neighbours any more
                                break
                else:
                    self.ans.append(neighbour[cur])
                    end = layer_end
                    close = True

            if not close:
                near_nodes = self.g.run("match (x)-[R]->(E) where x.name = '{}' return E".format(neighbour[cur])).data()
                near_nodes += self.g.run(
                    "match (E)-[R]->(x) where x.name = '{}' return E".format(neighbour[cur])).data()

                for n in near_nodes:
                    node_name = n['E']['name']
                    node_id = n['E'].identity

                    if len(aim_entity) and aim_entity == node_name:
                        neighbour.append(aim_entity)
                        backtrace.append(cur)
                        self.search_rel_trace(backtrace, neighbour, len(neighbour) - 1)
                        self.ans_type = RELATION_n
                        return

                    if node_name not in neighbour:
                        neighbour.append(node_name)
                        backtrace.append(cur)
                        ids.append(node_id)
                        end += 1

            if cur == layer_end:
                layer_end = end
                hop += 1

            cur = cur + 1

    def filter_queue(self, neighbour, backtrace, cur, layer_end, ids):
        neighbour_copy = neighbour[:cur + 1]
        backtrace_copy = backtrace[:cur + 1]
        ids_copy = ids[:cur+1]
        keep = [0 for i in range(layer_end + 1)]

        for i in range(cur + 1, layer_end + 1):
            e_t = neighbour[i]
            t_id = ids[i]
            h_id = ids[backtrace[i]]
            rel_id = self.rel2id[self.qt['relation'][0][0]]

            d = self.transr.calc_dist(h_id, rel_id, t_id)
            d_n = self.transr.calc_dist(t_id, rel_id, h_id)
            if min(d, d_n) > 30:
                keep[i] = 0
                continue

            rel, order = self.search_relation(neighbour[backtrace[i]], e_t, self.qt['relation'][0][2])

            if len(rel) > 0:
                for r in rel:
                    if r == self.qt['relation'][0][0]:
                        keep[i] = 1

        for i in range(cur + 1, layer_end + 1):
            if keep[i]:
                neighbour_copy.append(neighbour[i])
                backtrace_copy.append(backtrace[i])
                ids_copy.append(ids[i])

        return len(neighbour_copy) - 1, neighbour_copy, backtrace_copy, ids_copy

    def search_rel_trace(self, backtrace, neighbour, cur):
        self.ans = []
        self.rel_ans = []
        self.rel_order = []
        while backtrace[cur] != cur:
            self.ans.append(neighbour[cur])
            pre = backtrace[cur]
            e_t = neighbour[pre]
            rel, order = self.search_relation(neighbour[cur], e_t)
            self.rel_ans.append(rel[0])
            self.rel_order.append(order[0])
            cur = backtrace[cur]
        self.rel_order.reverse()
        self.rel_ans.reverse()
        self.ans.reverse()

    def tst(self, a):
        self.qt = a
        self.bfs()

# test = searcher()
# #test.tst({'entity': ['华特气体'], 'relation': [['持股', 1, 0]], 'type_need': ['Company'], 'query_attribute': []})
# test.tst({'entity': ['华特气体', '特种气体'], 'relation': [], 'type_need': [], 'query_attribute': []})

# test = searcher()
# test.tst({'entity': ['苏泊尔'], 'relation': [['所属行业', 1, 0]], 'type_need': ['Company'], 'query_attribute': []})
