import json

from py2neo import Graph, Node, Relationship
from misc import only_Eng


class EnGraph:
    def __init__(self):
        self.g = Graph('http://localhost:7474', user='neo4j', password='1234')
        self.CompanyFile = './data/company.json'
        self.IndustryFile = './data/industry.json'
        self.ProductFile = './data/product.json'
        self.PersonFile = './data/position.json'
        self.Com2IndFile = './data/company_industry.json'
        self.Com2ProFile = './data/company_product.json'
        self.Ind2IndFile = './data/industry_industry.json'
        self.Pro2ProFile = './data/product_product.json'
        self.ShareholderFile = './data/shareholder.json'

    def create_graph(self):
        self.create_company()
        self.create_industry()
        self.create_product()
        self.create_person()
        self.create_company2industry()
        self.create_company2product()
        self.create_industry2industry()
        self.create_product2product()
        self.create_shareholder()

    def create_company(self):
        i = 1
        for data in open(self.CompanyFile, encoding='gbk'):
            datajson = json.loads(data)
            node = Node("Company", name=datajson['name'], fullname=datajson['fullname'], code=datajson['code'],
                        exchange=datajson['location'], time=datajson['time'])
            self.g.merge(node, "Company", "code")
            if i % 100 == 0:
                print(i, ' a')
            i = i + 1

    def create_industry(self):  # 行业
        i = 1
        for data in open(self.IndustryFile, encoding='utf-8'):
            datajson = json.loads(data)
            node = Node("Industry", name=datajson['name'], code=datajson['code'])
            self.g.merge(node, "Industry", "code")
            if i % 100 == 0:
                print(i, ' b')
            i = i + 1

    def create_product(self):  # 产品
        i = 1
        for data in open(self.ProductFile, encoding='utf-8'):
            datajson = json.loads(data)
            node = Node("Product", name=datajson['name'])
            self.g.merge(node, "Product", "name")
            if i % 100 == 0:
                print(i, ' c')
            i = i + 1

    def create_person(self):  # 人员
        ik = 1
        for data in open(self.PersonFile, encoding='gbk'):
            if ik <= 3500:
                ik = ik + 1
                continue
            datajson = json.loads(data)

            company_code = datajson['code']
            company_node = self.g.nodes.match("Company", code=company_code).first()
            if company_node is None:
                with open("./log.txt", "a") as file:
                    file.write("company not found when adding person:" + str(company_code) + '\n')
                continue
            else:
                for i in datajson['position']:
                    for j in datajson['position'][i]:
                        node = Node("Person", name=j)
                        self.g.merge(node, "Person", "name")

                        rel = Relationship(company_node, i, node)
                        self.g.merge(rel)
                        # rel = Relationship(node, 'inverse' + i, company_node)
                        # self.g.merge(rel)
            print(ik, ' d')
            ik = ik + 1

    def create_company2industry(self):
        i = 1
        for data in open(self.Com2IndFile, encoding='utf-8'):
            datajson = json.loads(data)
            company_node = self.g.nodes.match("Company", code=datajson['company_code'].split('.')[0]).first()
            industry_node = self.g.nodes.match("Industry", code=datajson['industry_code']).first()
            if company_node is None or industry_node is None:
                with open("./log.txt", "a") as file:
                    file.write(
                        "company or industry not found when linking:" + datajson['company_code'].split('.')[0] + ':' +
                        datajson['industry_code'] + '\n')
                continue
            else:
                rel = Relationship(company_node, "所属行业", industry_node)
                self.g.merge(rel)
                # rel = Relationship(industry_node, "inverse所属行业", company_node)
                # self.g.merge(rel)
            if i % 100 == 0:
                print(i, ' e')
            i = i + 1

    def create_company2product(self):
        i = 1
        for data in open(self.Com2ProFile, encoding='utf-8'):
            datajson = json.loads(data)
            company_node = self.g.nodes.match("Company", code=datajson['company_code'].split('.')[0]).first()
            product_node = self.g.nodes.match("Product", name=datajson['product_name']).first()
            if company_node is None:
                with open("./log.txt", "a") as file:
                    file.write(
                        "company not found when linking product:" + datajson['company_code'].split('.')[0] + '\n')
                continue

            else:
                if product_node is None:
                    product_node = Node("Product", name=datajson['product_name'])
                    self.g.create(product_node)

                rel = Relationship(company_node, "主营产品", product_node)
                self.g.merge(rel)
                # rel = Relationship(product_node, "inverse主营产品", company_node)
                # self.g.merge(rel)
            if i % 100 == 0:
                print(i, ' f')
            i = i + 1

    def create_industry2industry(self):
        i = 1
        for data in open(self.Ind2IndFile, encoding='utf-8'):
            datajson = json.loads(data)
            node1 = self.g.nodes.match("Industry", code=datajson['from_code']).first()
            node2 = self.g.nodes.match("Industry", code=datajson['to_code']).first()
            if node1 is None or node2 is None:
                with open("./log.txt", "a") as file:
                    file.write(
                        "industry not found when linking:" + datajson['from_code'] + ':' + datajson['to_code'] + '\n')
                continue
            else:
                rel = Relationship(node1, "上级行业", node2)
                self.g.merge(rel)
                # rel = Relationship(node2, "inverse上级行业", node1)
                # self.g.merge(rel)
            if i % 100 == 0:
                print(i, ' g')
            i = i + 1

    def create_product2product(self):
        i = 1
        for data in open(self.Pro2ProFile, encoding='utf-8'):
            if i <= 81700:
                i = i + 1
                continue
            datajson = json.loads(data)
            node1 = self.g.nodes.match("Product", name=datajson['from_entity']).first()
            node2 = self.g.nodes.match("Product", name=datajson['to_entity']).first()
            if node1 is None:
                node1 = Node("Product", name=datajson['from_entity'])
                self.g.create(node1)
            if node2 is None:
                node2 = Node("Product", name=datajson['to_entity'])
                self.g.create(node2)

            rel = Relationship(node1, "上游材料", node2)
            self.g.merge(rel)
            # rel = Relationship(node2, "inverse上游材料", node1)
            # self.g.merge(rel)

            if i % 100 == 0:
                print(i, ' h')
            i = i + 1

    def create_shareholder(self):
        ik = 1
        for data in open(self.ShareholderFile):
            datajson = json.loads(data)
            company_code = datajson['code']
            company_node = self.g.nodes.match("Company", code=company_code).first()

            if company_node is None:
                with open("./log.txt", "a") as file:
                    file.write("company not found shareholder:" + datajson['code'] + '\n')
                continue

            for i in datajson['shareholder']:
                if len(i) <= 3:  # probably person
                    node = Node("Person", name=i)
                    self.g.merge(node, "Person", "name")
                else:
                    if only_Eng(i):
                        continue
                    else:
                        node = Node("Company", name=i)
                        self.g.merge(node, "Company", 'name')

                rel = Relationship(node, "持股", company_node)
                self.g.merge(rel)
                # rel = Relationship(company_node, "inverse持股", node)
                # self.g.merge(rel)
            if ik % 100 == 0:
                print(ik, ' i')
            ik = ik + 1

    def dump_rels(self):
        ik = 1
        rels = self.g.match()
        with open('./data/tuples.txt', 'w') as file:
            for i in rels:
                e_s = i.start_node['name']
                r = type(i).__name__
                e_t = i.end_node['name']

                file.write(e_s + '|' + r + '|' + e_t + '\n')

                if ik % 1000 == 0:
                    print(ik, ' j')
                ik = ik + 1


# sh = EnGraph()
# sh.dump_rels()
