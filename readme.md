## 金融知识图谱问答系统

- 通过Python和图数据库Neo4j实现的有关企业知识的问答系统，该问答系统可以根据输入抽取实体与关系，将结果链接到数据库中对象。根据已知信息构造查询四元组，根据四元组与数据库进行交互搜索问题的答案
- 提供有关企业信息，行业信息，企业高管，产品及产品、行业间产业链信息查询等功能
- demo：![image-20220519224604511](https://github.com/xiliguguagua/enterpriseKGQA/blob/main/pic/image-20220519224604511.png)

### 所需环境

- python 3.8
  - py2neo Python与Neo4j交互控件
  - jieba 中文分词与词性分类组件
  - mxnet 深度学习框架
  - Levenshtein 字符串编辑距离库
- Neo4j 4.4.3 图数据库

### 目录结构

```
enterpriseKGQA:.
├─data             源数据文件
├─dict             实体字典
├─model            transX模型参数
├─path             路径缓存文件
├─pic              readme图片
├─爬虫              爬虫
├───build_graph.py  构建图数据库
├───misc.py         杂项(读取三元组，生成实体字典)
├───qa.py           问答主体
├───search.py       查询模块
├───RL_path.py      强化学习路径搜索
├───transX.py       transX训练模块
└───word.py         实体识别、链接模块
```

### 运行方式

- 导入数据至Neo4j

  ```shell
  python build_graph.py
  ```

  共计18万节点和30万条关系，大约需等待4-5小时

  然后需要在Neo4j交互窗口中执行cypher

  ```cypher
  match ()-[r:`上游材料`]-() delete r
  ```

  用于删除所有“上游材料”关系，因为在`build_graph`中对此关系的数据解析有误，之后运行

  ```shell
  python 1.py
  ```

  重新导入正确“上游材料”关系，大约需等待1小时

  数据库构建完成

  ![QQ图片20220507111550](https://github.com/xiliguguagua/enterpriseKGQA/blob/main/pic/QQ%E5%9B%BE%E7%89%8720220507111550.png)

- 进行问答

  运行`qa.py`即可进行问答，过程中需保持数据库在线

  ```
  python qa.py
  ```

  
