import jieba
import jieba.analyse
import jieba.posseg as posg
# import pyhanlp
import Levenshtein
from py2neo import Graph


class word2entity:
    def __init__(self, dict_list):
        for f in dict_list:
            jieba.load_userdict(f)

        # self.analyzer = pyhanlp.PerceptronLexicalAnalyzer()
        self.word_flag = []
        self.entities = []
        self.relation = []
        self.attribute = []
        self.type = []
        self.query_tuple = {}
        self.g = Graph('http://localhost:7474', user='neo4j', password='1234')
        self.rel_dict = [['上游材料', '上级层游材料商产品'], ['上级行业', '上级游层产行业'], ['主营产品', '生产主营'], '代理董事会秘书', '副经理', '副董事长', '外部监事',
                         '总经理', '所属行业', ['持股', '持股东'], '独立董事', '监事',
                         '监事长', '职工监事', '董事', '董事会秘书', '董事长', '财务总监']
        self.att_dict = [['的名字简称', 'name'], ['的全称名', 'fullname'], ['的公司股票代号码', 'code'], ['的上市日期时间', 'time'], ['的上市交易所地点', 'exchange']]
        self.type_dict = [['公司', 'Company'], ['谁', 'Person'], ['人', 'Person'], ['企业', 'Company'], ['产品', 'Product'], ['商品', 'Product'], ['产业', 'Industry'], ['行业', 'Industry']]

    def getTuple(self, ques, code):
        self.word_flag = []
        self.entities = []
        self.relation = []
        self.attribute = []
        self.type = []
        self.query_tuple = {}
        e = set()

        if len(code) > 0:
            node = self.g.run('match (x{code:\'%s\'}) return x' % code).data()
            if node is None:
                pass
            else:
                node = node[0]['x']['name']
                e.add(node)
                self.entities.append(node)
            ques = ques.replace(code, '')

        self.split(ques)
        #print(self.word_flag)
        self.find_entity(e)

        self.query_tuple['entity'] = self.entities
        self.query_tuple['relation'] = self.relation
        self.query_tuple['type_need'] = self.type
        self.query_tuple['query_attribute'] = self.attribute
        return self.query_tuple

    def split(self, ques):
        # kw = jieba.analyse.extract_tags(ques, topK=10, withWeight=True, allowPOS=('nr', 'nl', 'ng', 'nt', 'nz', 'n'))
        # for item in kw:
        #     print(item)
        # print('\n')
        #
        # kw = jieba.analyse.textrank(ques, topK=20, withWeight=True, allowPOS=('nr', 'nl', 'ng', 'nz', 'nt', 'n'))
        # for item in kw:
        #     print(item)
        # print('\n')

        words = posg.cut(ques)
        self.word_flag = []
        for item in words:
            if item.flag in ['nr', 'nl', 'ng', 'nz', 'nt', 'j']:
                if item.flag == 'j':
                    item.flag = 'nr'
                if item.word == '公司' and item.flag == 'nr':
                    continue
                #print(item.word, item.flag)
                self.word_flag.append([item.word, item.flag])

        if ques[-3:] == '的公司':
            self.word_flag.append([ques[-3:], 'nz'])
        if ques[-2:] == '的人':
            self.word_flag.append([ques[-2:], 'nz'])
        if ques[-3:] == '的产品':
            self.word_flag.append([ques[-3:], 'nz'])
        if ques[-3:] == '的行业':
            self.word_flag.append([ques[-3:], 'nz'])
    #     segs = self.analyzer.analyze(ques)
    #     arr = str(segs).split(" ")
    #     res = self.get_res(arr)
    #     print(res)
    #
    # def get_res(self, arr):
    #     re_list = []
    #     alPOS = ['nr', 'nl', 'ng', 'nz', 'nt', 'n']
    #     for x in arr:
    #         temp = x.split("/")
    #         if temp[1] in alPOS:
    #             re_list.append([temp[0],temp[1]])
    #     return re_list

    def find_entity(self, e):
        error = 0

        for item in self.word_flag:
#######################################################################################################################
            if item[1] == 'nr':  # entity
                sim_max = 0
                best_match = ''
                cover = []
                for name in open('./dict/names.txt', 'r', encoding='utf-8'):
                    name = name.replace('\n','')
                    if item[0] == name:
                        sim = 1
                        sim_max = 1
                        best_match = name
                        break
                    elif item[0] in name:
                        cover.append(name)
                    else:
                        sim = Levenshtein.jaro_winkler(item[0], name)
                        if sim > sim_max:
                            sim_max = sim
                            best_match = name
                        if sim_max > 0.9:
                            break

                min_len = 100
                if sim_max < 1 and len(cover) > 0:
                    sim = 1
                    sim_max = 1
                    for i in cover:
                        if len(i) < min_len:
                            best_match = i
                            min_len = len(i)

                if sim_max < 0.7:
                    error = error | 1  # has unrecognized entity
                else:
                    node1 = self.g.run('match (e{name:\'%s\'}) return e' % best_match).data()
                    node2 = self.g.run('match (e{fullname:\'%s\'}) return e' % best_match).data()
                    if len(node1) > 0:
                        node = node1[0]['e']['name']
                    if len(node2) > 0:
                        node = node2[0]['e']['name']
                    if len(node2) == 0 and len(node1) == 0:
                        error |= 1
                        continue

                    if node not in e:
                        e.add(node)
                        self.entities.append(node)


#######################################################################################################################
            if item[1] == 'nl':  # relation
                sim_max = 0
                best_match = ''
                cover = 0.1

                for name in self.rel_dict:
                    if isinstance(name, str):
                        if '上' in name and '上' not in item[0]:
                            continue
                        sim = Levenshtein.jaro_winkler(item[0], name)
                        cover = 0.1
                        # cover = len(set(item[0]).intersection(name)) / len(item[0])
                    else:
                        if '上' in name[0] and '上' not in item[0]:
                            continue
                        sim = Levenshtein.jaro_winkler(item[0], name[0])
                        cover = len(set(item[0]).intersection(name[1])) / len(item[0])

                        if cover > 0.98:
                            best_match = name[0]
                            break

                    if sim > sim_max:
                        sim_max = sim
                        if isinstance(name, str):
                            best_match = name
                        else:
                            best_match = name[0]

                if sim_max > 0.5 or cover > 0.98:
                    if '上' in best_match:
                        limit = 1
                    else:
                        limit = 0
                    self.relation.append([best_match, max(sim_max, cover), limit])
                else:
                    error = error | 1 << 1  # has unrecognized relation


#######################################################################################################################
            if item[1] == 'ng':  # attribute
                max_cover = 0
                best_match = ''

                for i in self.att_dict:
                    cover = len(set(item[0]).intersection(i[0])) / len(item[0])
                    if cover > 0.98:
                        best_match = i[1]
                        break
                    else:
                        if cover > max_cover:
                            max_cover = cover
                            best_match = i[1]

                self.attribute.append(best_match)


#######################################################################################################################
            if item[1] == 'nz':  # type
                for i in self.type_dict:
                    if i[0] in item[0]:
                        self.type.append(i[1])
                        break


#######################################################################################################################
            if item[1] == 'nt':  # reverse_relation
                item[0] = item[0].replace('下', '上')

                sim_max = 0
                best_match = ''
                cover = 0.1

                for name in self.rel_dict:
                    if isinstance(name, str):
                        sim = Levenshtein.jaro_winkler(item[0], name)
                        cover = 0.1
                    else:
                        sim = Levenshtein.jaro_winkler(item[0], name[0])
                        cover = len(set(item[0]).intersection(name[0])) / len(item[0])

                        if cover > 0.98:
                            best_match = name[0]
                            break

                    if sim > sim_max:
                        sim_max = sim
                        if isinstance(name, str):
                            best_match = name
                        else:
                            best_match = name[0]

                if sim_max > 0.5 or cover > 0.98:
                    self.relation.append([best_match, max(sim_max, cover), -1])
                else:
                    error = error | 1 << 1  # has unrecognized relation
