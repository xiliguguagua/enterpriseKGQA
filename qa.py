from word import word2entity
from search import searcher
w2e = word2entity(['./dict/company.txt',
                   './dict/industry.txt',
                   './dict/product.txt',
                   './dict/person.txt',
                   './dict/relation.txt',
                   './dict/attribute.txt',
                   './dict/type.txt',
                   './dict/reverse_relation.txt'])

searcher = searcher()

while True:
    question = input('> ')

    code = ''
    for i in range(len(question)):
        if question[i].isdigit():
            if question[i:i+6].isdigit():
                code = question[i:i+6]
            else:
                i = i+5

    query_tuple = w2e.getTuple(question, code)

    if len(query_tuple['entity']) <= 0 :
        print('未识别出任何实体')
        continue
    if len(query_tuple['entity']) >= 3 or len(query_tuple['relation']) > 2 :
        print('问题太复杂了')
        continue

    # print(query_tuple)
    searcher.get_answer(query_tuple)

