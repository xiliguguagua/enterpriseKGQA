import mxnet.initializer

from misc import ReadPairs
from mxnet import gluon, autograd, nd
import mxnet
import random
import numpy as np

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


class TransR(gluon.nn.Block):
    def __init__(self, e_sum, r_sum, e_dim, r_dim, r_types, r_i2t, margin=1):
        super().__init__()
        self.e_sum = e_sum
        self.r_sum = r_sum
        self.e_dim = e_dim
        self.r_dim = r_dim
        self.r_types = r_types
        self.r_i2t = r_i2t  # index to type
        self.margin = margin
        self.e = gluon.nn.Embedding(self.e_sum, e_dim)
        self.r = gluon.nn.Embedding(self.r_sum, r_dim)
        self.M_r = gluon.nn.Embedding(self.r_types, e_dim * r_dim)

    def compute(self, e, M):
        e = e.reshape(-1, 1, self.e_dim)
        M = M.reshape(-1, self.e_dim, self.r_dim)
        res = nd.batch_dot(e, M)
        res = res.reshape(-1, self.r_dim)
        return res

    def fwd(self, real, corrupt):
        h = self.e(real[:, 0])
        t = self.e(real[:, 1])
        r = self.r(real[:, 2])
        r_type = self.r_i2t[real[:, 2]]
        Mr = self.M_r(r_type)

        h_ = self.e(corrupt[:, 0])
        t_ = self.e(corrupt[:, 1])

        M_h = self.compute(h, Mr)
        M_t = self.compute(t, Mr)
        M_h_ = self.compute(h_, Mr)
        M_t_ = self.compute(t_, Mr)

        score_pos = nd.sum((M_h + r - M_t) ** 2, axis=1, keepdims=True) ** 0.5
        score_neg = nd.sum((M_h_ + r - M_t_) ** 2, axis=1, keepdims=True) ** 0.5

        loss = score_pos - score_neg + self.margin
        loss = nd.maximum(0, loss)
        return loss

    def normalize(self):
        for p in self.params:
            p = p.norm(ord=2, asix=1, keepdims=True)

    def calc_dist(self, h_id, r_id, t_id):
        h = self.e(nd.array([h_id]))
        t = self.e(nd.array([t_id]))
        M = self.M_r(nd.array([r_id]))
        r = self.r(nd.array([r_id]))
        h_T = self.compute(h, M)
        t_T = self.compute(t, M)
        return nd.sum((h_T + r - t_T) ** 2, axis=1, keepdims=True) ** 0.5

    def test(self, pair):
        ave = []
        map1 = []
        map10 = []
        map30 = []
        map = []
        has30 = 0
        has60 = 0
        has100 = 0
        s = 0

        for test_pair in pair:
        # for test_pair in random.sample(pair, 10000):
        #     ave = []
            s += 1
            h = self.e(nd.array([test_pair[0]]))
            r = self.r(nd.array([test_pair[2]]))
            r_id = self.r_i2t[nd.array([test_pair[2]])]
            M = self.M_r(r_id)
            h_T = self.compute(h, M)

            # dist = {}
            t = self.e(nd.array([test_pair[1]]))
            t_T = self.compute(t, M)

            dist = nd.sum((h_T + r - t_T) ** 2, axis=1, keepdims=True) ** 0.5
            if dist > 30:
                has30 += 1
                if dist > 60:
                    has60 += 1
                    if dist > 100:
                        has100 += 1

            if s%1000 == 0:
                print(has30/s, ' ', has60/s, ' ', has100/s)
                print('\n\n')
            # #print(dist[test_pair[1]])
            # size = 10000
            # for i in range(size):
            #     t = self.e(nd.array([i]))
            #     t_T = self.compute(t, M)
            #     dist[str(i)] = nd.sum((h_T + r - t_T) ** 2, axis=1, keepdims=True) ** 0.5
            #
            # dist = sorted(dist.items(), key=lambda s: s[1])
            #
            # corr = 0
            # h3 = 0
            # h6 = 0
            # h1 = 0
            # for i in range(size):
            #     p = [test_pair[0], dist[i][0], test_pair[2]]
            #     if p in pair:
            #         corr += 1
            #     #     ave.append(corr/(1+i))
            #     # if i == 1:
            #     #     map1.append(corr/(1+i))
            #     # if i== 10:
            #     #     map10.append(corr/(1+i))
            #     # if i==30:
            #     #     map30.append(corr/(1+i))
            #
            #     if dist[i][1] > 30 and p in pair:
            #         h3 += 1
            #     if dist[i][1] > 60 and p in pair:
            #         h6 += 1
            #     if dist[i][1] > 100 and p in pair:
            #         h1 += 1
            #
            # if corr<=0:
            #     continue
            # #map.append(np.mean(ave))
            # has30.append(h3/corr)
            # has60.append(h6/corr)
            # has100.append(h1/corr)
            #
            # #print(np.mean(map1),' ', np.mean(map10),' ',np.mean(map30),' ',np.mean(map))
            # print(np.mean(has30),' ', np.mean(has60), ' ', np.mean(has100))
            # print('\n\n\n')



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


#entity, relationship, pair = ReadPairs('./data/rels.csv')
# r_i2t = nd.array([0, 1, 2, 6, 6, 6, 6, 6, 3, 4, 6, 6, 6, 6, 6, 6, 6, 5])
# # trsx = TransE(len(entity), len(relationship), 4)
# trsx = TransR(len(entity), len(relationship), e_dim=4, r_dim=2, r_types=6, r_i2t=r_i2t)
# trsx.collect_params().initialize(mxnet.init.Xavier())
#
# print('start training')
# train(trsx, entity, pair, epochs=2, l_r=0.01, batch_size=128)


