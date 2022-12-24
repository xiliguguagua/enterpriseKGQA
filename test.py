import json
import random

from mxnet import gluon, nd
import mxnet as mx
from transX import TransR
from misc import ReadPairs
from mxnet import gluon, autograd, nd

class TransE(gluon.nn.Block):
    def __init__(self, e_sum, r_sum, dim, margin=1):
        super().__init__()
        self.e_sum = e_sum
        self.r_sum = r_sum
        self.dim = dim
        self.margin = margin

        self.e = gluon.nn.Embedding(self.e_sum, self.dim)  # generate $sum random vectors with $dim
        self.r = gluon.nn.Embedding(self.r_sum, self.dim)

    def fwd(self, real, corrupt):
        h = self.e(real[:, 0])
        t = self.e(real[:, 1])
        r = self.r(real[:, 2])

        h_ = self.e(corrupt[:, 0])
        t_ = self.e(corrupt[:, 1])

        score_pos = nd.sum((h + r - t) ** 2, axis=1, keepdims=True) ** 0.5
        score_neg = nd.sum((h_ + r - t_) ** 2, axis=1, keepdims=True) ** 0.5

        loss = score_pos - score_neg + self.margin
        loss = nd.maximum(0, loss)
        return loss

    def normalize(self):
        for p in self.params:
            p = p.norm(ord=2, asix=1, keepdims=True)

    def test(self, pair):
        for p in pair:
            min_d = 100
            min_id = -1
            h = self.e(nd.array([p[0]]))
            r = self.r(nd.array([p[2]]))
            for i in range(self.e_sum):
                poss_t = self.e(nd.array([i]))
                dist = nd.sum((h + r - poss_t) ** 2, axis=1)
                if dist < min_d:
                    min_d = dist
                    min_id = i
            print(p, ' ', min_id)

    def printt(self):
        for i in range(self.e_sum):
            print(self.e(nd.array([i])))
        for i in range(self.r_sum):
            print(self.r(nd.array([i])))

class TransRR(gluon.nn.Block):
    def __init__(self, e_sum, r_sum, e_dim, r_dim, t_sum, margin=1):
        super().__init__()
        self.e_sum = e_sum
        self.r_sum = r_sum
        self.e_dim = e_dim
        self.r_dim = r_dim
        self.t_sum = t_sum
        self.margin = margin

        self.e = gluon.nn.Embedding(self.e_sum, self.e_dim)  # generate $sum random vectors with $dim
        self.r = gluon.nn.Embedding(self.r_sum, self.r_dim)

        self.m = gluon.nn.Embedding(self.t_sum, self.e_dim * self.r_dim)

    def test(self):
        x = nd.array([[1, 2, 1], [1, 3, 2]])  # , [3, 3, 2], [4, 3, 3]])
        print('entity emb')
        print(self.e(nd.array([0, 1, 2, 3, 4])))
        print('\nrela emb')
        print(self.r(nd.array([0, 1, 2, 3])))
        print('\nM')
        print(self.m(nd.array([0, 1, 2, 3])))
        print('\n**************************')

        h = self.e(x[:, 0])
        print('\nh\n', h)
        t = self.e(x[:, 1])
        print('\nt\n', t)
        r = self.r(x[:, 2])
        print('\nr\n', r)
        Mr = self.m(x[:, 2])
        print('\nm\n', Mr)
        print('\n**************************')

        e = h.reshape(-1, 1, self.e_dim)
        print('\nreshape h\n', e)
        tMr = Mr.reshape(-1, self.e_dim, self.r_dim)
        print('\ntMr\n', tMr)
        result = nd.batch_dot(e, tMr)
        # print('\nres\n', result)
        result = result.reshape(-1, self.r_dim)
        print('\nres\n', result)

    def save_emb(self):
        self.e.save_params('./savetest.txt')


def train(trsx, entity, pair, epochs, l_r, batch_size):
    trainer = gluon.Trainer(trsx.collect_params(), 'adam', {'learning_rate': l_r})
    for e in range(epochs):
        loss_sum = 0
        for b in range(len(pair) // batch_size):
            S_batch = random.sample(pair, batch_size)
            corrupt_batch = []
            for p in S_batch:
                r = p[2]
                # h_ = p[0]
                # t_ = p[1]
                # seed = random.random()
                # if seed <= 0.5:
                h_ = random.sample(entity, 1)[0]
                # else:
                t_ = random.sample(entity, 1)[0]
                corrupt_batch.append([h_, t_, r])

            with autograd.record():
                loss = trsx.fwd(nd.array(S_batch), nd.array(corrupt_batch))
            loss.backward()
            trainer.step(batch_size)
            trsx.normalize()

            loss_sum += sum(loss).asscalar()

        print(e, ' ', loss_sum / len(pair))

# trsx = TransE(5, 4, 4, 2, 4)
# trsx.collect_params().initialize(mx.init.Xavier())
# trsx.test()
# trsx.save_parameters('./st.txt')
#
# tt = TransE(5, 4, 4, 2, 4)
# tt.load_parameters('./st.txt')
# tt.test()

entity, relationship, pair = ReadPairs('./data/rels.csv')
r_i2t = nd.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
t_test = TransR(len(entity), len(relationship), e_dim=128, r_dim=64, r_types=18, r_i2t=r_i2t, margin=100)
t_test.load_parameters('./model/params1 (1)')
print('load done')
t_test.test(pair)

# entity, relationship, pair = ReadPairs('./test_data/pairs.txt')
# t_test = TransE(len(entity), len(relationship), dim=2)
# t_test.collect_params().initialize(mx.init.Xavier())
# train(t_test, entity, pair, epochs=600, l_r=0.01, batch_size=8)
# t_test.printt()
