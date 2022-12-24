from py2neo import Graph,Node,Relationship
graph = Graph('http://localhost:7474',user='neo4j',password='1234')


class neo4j_search():
    def __init__(self):
        self.qword_list = []
        self.sql = ''
        self.answer = []

    def input_tuple(self, query_tuple):
        print(query_tuple)
        query_entity_list = query_tuple['entity']
        query_relation_list = query_tuple['relation']
        type_need = query_tuple['type_need']
        query_attribute = query_tuple['query_attribute']
        # print(query_attribute)

        if len(query_entity_list) == 2 and len(query_relation_list) == 0:
            self.answer = self.search_relation(query_entity_list[0], query_entity_list[1])

        else:
            if len(query_entity_list) == 1 and len(query_relation_list) == 0 and type_need == []:
                self.answer = self.search_attribution(query_entity_list[0])

            elif len(query_entity_list) == 1 and len(query_relation_list) == 0 and type_need != []:
                self.answer = self.bfs(query_entity_list[0],type_need[0])

            elif len(query_entity_list) == 1 and len(query_relation_list) == 1 and type_need != []:
                self.answer = self.inference_bfs(query_entity_list[0], query_relation_list[0], type_need[0])

            elif len(query_entity_list) == 1 and len(query_relation_list) == 2 and type_need != []:
                self.answer = self.inference2_bfs(query_entity_list[0], query_relation_list[0], query_relation_list[1], type_need[0])
            else:
                self.answer = []
            print(self.sql)
            # print(self.answer)
            if self.answer != []:
                if query_attribute == []:
                    for i in range(len(self.answer)):
                        self.answer[i] = self.answer[i]['name']
                else:
                    for i in range(len(self.answer)):
                        self.answer[i] = self.answer[i][query_attribute[0]]
            else:
                self.answer = '无'


    def get_node_data(self, nodes_record):
        data = {"id": str(nodes_record.get('E').identity),
                "label": next(iter(nodes_record.get('E').labels))}
        data.update(nodes_record.get('E')) 
        return data

    def get_relation_data(self, relations_record):
        data = type(relations_record.get('R')).__name__
        return data

    def search_attribution(self, e):
        self.sql = "match(E) where E.name = '{}' return E".format(e)
        entity_list = graph.run(self.sql).data()
        print(entity_list[0])
        if entity_list != []:
            for i in range(len(entity_list)):
                entity_list[i] = self.get_node_data(entity_list[i])
        return entity_list

    def search_tail_entity(self, e, r):
        self.sql = "match(x)-[r:{}]->(E) where x.name = '{}' return E".format(r[0],e)
        entity_list = graph.run(self.sql).data()
        for i in range(len(entity_list)):
            entity_list[i] = self.get_node_data(entity_list[i])
        return entity_list

    def search_head_entity(self, e, r):
        self.sql = "match(E)-[r:{}]->(x) where x.name = '{}' return E".format(r[0],e)
        entity_list = graph.run(self.sql).data()
        for i in range(len(entity_list)):
            entity_list[i] = self.get_node_data(entity_list[i])
        return entity_list

    def search_both_entity(self, e, r):
        total_list = []
        self.sql = "match (x)-[r:{}]->(E) where x.name = '{}' return E".format(r[0],e)
        node_list = graph.run(self.sql).data()
        for i in range(len(node_list)):
            node_list[i] = self.get_node_data(node_list[i])
        for i in range(len(node_list)):
            total_list.append(node_list[i])
        
        self.sql = "match (E)-[r:{}]->(x) where x.name = '{}' return E".format(r[0],e)
        node_list = graph.run(self.sql).data()
        for i in range(len(node_list)):
            node_list[i] = self.get_node_data(node_list[i])
        for i in range(len(node_list)):
            total_list.append(node_list[i])
        return total_list

    def search_relation(self, e1, e2):
        self.sql = "match(x)-[R]->(y) where x.name = '{}' and y.name = '{}' return R".format(e1,e2)
        relation_list = graph.run(self.sql).data()
        for i in range(len(relation_list)):
            relation_list[i] = self.get_relation_data(relation_list[i])
        if relation_list == []:
            self.sql = "match(x)-[R]->(y) where y.name = '{}' and x.name = '{}' return R".format(e1,e2)
            relation_list = graph.run(self.sql).data()
            for i in range(len(relation_list)):
                relation_list[i] = self.get_relation_data(relation_list[i])
        return relation_list
    
    def bfs(self, e, type_need):
        total_list = []
        self.sql = "match (x)-[R]->(E) where x.name = '{}' return E".format(e)
        node_list = graph.run(self.sql).data()
        for i in range(len(node_list)):
            node_list[i] = self.get_node_data(node_list[i])
        for i in range(len(node_list)):
            if node_list[i]['label'] == type_need:
                total_list.append(node_list[i])
        
        self.sql = "match (E)-[R]->(x) where x.name = '{}' return E".format(e)
        node_list = graph.run(self.sql).data()
        for i in range(len(node_list)):
            node_list[i] = self.get_node_data(node_list[i])
        for i in range(len(node_list)):
            if node_list[i]['label'] == type_need:
                total_list.append(node_list[i])
        return total_list

    def inference_bfs(self, e, r, type_need):
        if r[2] == -1:
            entity_list = self.search_head_entity(e, r)
        elif r[2] == 1:
            entity_list = self.search_tail_entity(e, r)
        else:
            entity_list = self.search_both_entity(e, r)
        # print(entity_list)
        if entity_list == []:
            return entity_list

        entity1_list = []
        for i in entity_list:
            if i['label'] == type_need:
                entity1_list.append(i)
        # print(entity1_list)
        if entity1_list != []:
            return entity1_list
        else:
            total_list = []
            for e1 in entity_list:
                bfs_result = self.bfs(e1['name'], type_need)
                for i in bfs_result:
                    total_list.append(i)
            # print(total_list)
            return total_list

    def inference2_bfs(self, e, r1, r2, type_need):
        if r1[2] == -1:
            entity_list = self.search_head_entity(e, r1)
        elif r1[2] == 1:
            entity_list = self.search_tail_entity(e, r1)
        else:
            entity_list = self.search_both_entity(e, r1)
        if entity_list == []:
            return entity_list
        else:
            entity1_list = []
            for e1 in entity_list:
                if r2[2] == -1:
                    search_result = self.search_head_entity(e1['name'], r2)
                elif r2[2] == 1:
                    search_result = self.search_tail_entity(e1['name'], r2)
                else:
                    search_result = self.search_both_entity(e1['name'], r2)
                for e2 in search_result:
                    entity1_list.append(e2)
        if entity1_list == []:
            return entity1_list

        entity2_list = []
        for i in entity1_list:
            if i['label'] == type_need:
                entity2_list.append(i)
        if entity2_list != []:
            return entity2_list
        else:
            total_list = []
            for e2 in entity1_list:
                bfs_result = self.bfs(e2['name'], type_need)
                for i in bfs_result:
                    total_list.append(i)
            return total_list



# Q = neo4j_search()
# Q.search_attribution('中国石油')
# Q.search_head_entity('601857','持股')
# Q.search_tail_entity('601857','所属行业')
# Q.search_relation('601857','750301')
# Q.bfs('中国石化')
# print(Q.answer)
node = Node('c',name='a')
rel = Relationship(node,'1',node)
rel.start_node
