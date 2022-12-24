import json

from py2neo import Graph, Relationship, Node
g = Graph('http://localhost:7474', user='neo4j', password='1234')
i=1
for data in open('./data/product_product.json', 'r', encoding='utf-8'):
    if i < 103162:
        i += 1
        continue
    datajson = json.loads(data)
#103162
    fn = datajson['from_entity']
    tn = datajson['to_entity']

    fnode = g.run('match (x:Product{name:\'%s\'}) return x' % fn).data()
    tnode = g.run('match (x:Product{name:\'%s\'}) return x' % tn).data()

    if len(fnode) == 0:
        fnode = Node("Person", name=fn)
        g.create(fnode)
    else:
        fnode = fnode[0]['x']

    if len(tnode) == 0:
        tnode = Node("Person", name=tn)
        g.create(tnode)
    else:
        tnode = tnode[0]['x']

    relname = datajson['rel']
    if relname == '上游材料':
        rel = Relationship(fnode, relname, tnode)
    elif relname == '下游产品':
        rel = Relationship(tnode, '上游材料', fnode)
    elif relname == '产品小类':
        rel = Relationship(tnode, '上游材料', fnode)
    else:
        print(data)
        continue

    g.merge(rel)

