from py2neo import Graph, Node, Relationship

g = Graph('http://localhost:7474', user='neo4j', password='1234')

# n1 = Node("a", name='1')
# n2 = Node("a", name='2')
# n3 = Node("b", name='3')
#
# rel1 = Relationship(n1, "r1", n2)
# rel1_ = Relationship(n2, 'inverse_r1', n1)
#
# rel2 = Relationship(n1, 'r2', n3)
#
# rel3 = Relationship(n2, 'r2', n3)
# rel3_ = Relationship(n3, 'inverse_r2', n2)
#
# g.create(n1)
# g.create(n2)
# g.create(n3)
# g.create(rel1)
# g.create(rel1_)
# g.create(rel2)
# g.create(rel3)
# g.create(rel3_) 613968

rels = g.match()
with open('./data/tuples.txt','w') as file:
    for i in rels:
        e_s = i.start_node['name']
        r = type(i).__name__
        e_t = i.end_node['name']

        if 'inverse' in r:
            g.separate(i)
        else:
            file.write(e_s+'|'+r+'|'+e_t+'\n')