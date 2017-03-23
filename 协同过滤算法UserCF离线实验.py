from numpy import *
import random
import math
from operator import itemgetter  
import time

# 加载数据集文件名，并转化为相应的： dict{key:user , item:dict{key:movie , item:score}} 结构
def loadDataSet(fileName):
    dataSet = {}
    fr = open(fileName)
    for line in fr.readlines():
        curLine = line.strip().split('\t') #curLine[0]:user ID , curLine[1]:movie ID , curLine[2]:score
        #字符串转换为数字
        for i in range(3):
            curLine[i] = int(curLine[i])
        if curLine[0] not in dataSet.keys():
            dataSet[curLine[0]] = {}
        oldDict = dataSet[curLine[0]]
        oldDict[curLine[1]] = curLine[2]
        dataSet[curLine[0]] = oldDict
    #print dataSet
    return dataSet



# 将数据集随机分成训练集合测试集的过程
def SplitData(data, M, k ,seed):
    test = []
    train = []
    random.seed(seed)   # seed  为相同的 随机数种子
    for user, item in data:
        if random.randint(0,M) == k:
            test.append([user, item])
        else:
            train.append([user,item])
    return train, test

# 召回率计算，描述测试集中用户－评分纪录中包含的被推荐物品比例
def Recall(train, test, N):
    hit = 0
    all = 0
    for user in train.keys():
        if user not in test.keys():
            continue
        tu = test[user]
        rank = GetRecommendation(user, N) # 返回给 user 推荐的前 N 项物品
        for item , pui in rank:
            if item in tu:
                hit += 1
        all += len(tu)
    return hit / (all * 1.0)

#  准确率计算，描述最终的推荐列表中有多少比例是发生过的用户－物品评分纪录
def Precision(train, test, N):
    hit = 0
    all = 0
    for user in train.keys():
        if user not in test.keys():
            continue
        tu = test[user]
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            if item in tu:
                hit += 1
        all += N
    return hit / (all * 1.0)

# 覆盖率计算 
def Coverage(train, test, N):
    recommend_items = set()
    all_items = set()
    for user in train.keys():
        for item in train[user].keys():
            all_items.add(item)
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            recommend_items.add(item)
    return len(recommend_items) / (len(all_items) * 1.0)

# 新颖度计算
def Popularity(train, test, N):
    item_popularity = dict()
    for user, items in train.items():
        for item in items.keys():
            if item not in item_popularity:
                item_popularity[item] = 0
            item_popularity[item] += 1
    ret = 0
    n = 0
    for user in train.keys():
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            ret += math.log(1 + item_popularity[item])
            n += 1
    ret /= n * 1.0
    return ret 

# 余弦相似度
"""
def UserSimilarity(train):
    W = dict()
    for u in train.keys():
        for v in train.keys():
            if u == v:
                continue:
            W[u][v] = len(train[u] & train[v])
            W[u][v] /= math.sqrt(len(train[u]) * len(train[v]) * 1.0)
# 时间复杂度为 O｜U｜｜V｜
"""
def UserSimilarity(train):
    # build inverse table for item_users
    item_users = dict() #key 为 物品，值为 user
    #print "item_users = ", item_users
    for u, items in train.items():
        #print "u = ", u ,"items = ",items
        for i in items.keys():
            if i not in item_users:
                item_users[i] = set()
            item_users[i].add(u)
            #print "item_users = ", item_users
    print "————物品－用户倒排表建立完成————"
    #print "item_users[1165] = ", item_users[1165]
    # calculate co-rated items between user
    C = dict()  # 纪录用户对(两用户之间)评价过的物品数
    N = dict() # 纪录用户评价过的物品数
    for i,users in item_users.items():
        if i % 10 == 0:
            print "正在更新第 %d 个物品相关用户的共同评价物品数" % i
        for u in users:
            if u not in N:
                N[u] = 0
            N[u] += 1
            #C[u][v] 为二维数组
            if u not in C:
                C[u] = {}
            for v in users:
                if u == v:
                    continue
                if v not in C[u]:
                    C[u][v] = 0
                """ 
                # 相似度计算
                C[u][v] += 1
                """
                # 改进 相似度计算，引入共同兴趣的热门物品惩罚因子
                C[u][v] += 1 / math.log(1 + len(users))
    #print(C[1])
    # calculate final similarity matrix W 
    W = dict()
    for u, related_users in C.items():
        W[u] = {}
        for v, cuv in related_users.items():
            W[u][v] = cuv / math.sqrt(N[u] * N[v])
            #print "W[u][v] = ",W[u][v]
    #print(W[1])
    print "————用户余弦相似度建立完成———— 用时为 ：%f s"  % (time.clock()-startTime)
    return W

# UserCF 推荐算法 page 47
def Recommend(user, train, W, K): #推荐 K 个用户评分高的 L 个物品
    rank = dict()
    interacted_items = train[user]
    for v, wuv in sorted(W[user].items(), key=itemgetter(1), reverse=True)[0:K]: #从大到小
        for i, rvi in train[v].items():
            if i in interacted_items:
                #we should filter items user interacted before
                continue
            if i not in rank.keys():
                rank[i] = 0
            rank[i] += wuv * rvi
            #print "rvi = " , rvi
    return rank
    #return sorted(rank.iteritems() , key=lambda d:d[1], reverse=True )[0:L]

def GetRecommendation(user, N):
    recommendDist = Recommend(user, trainSet, W, K)
    recommendListTopN = sorted(recommendDist.iteritems() , key=lambda d:d[1], reverse=True )[0:N]
    #print"recommendListTopN = " ,recommendListTopN
    """
    recommendDistTopN = {}
    for topN in recommendListTopN:
        recommendDistTopN[topN[0]] = topN[1]
    print "recommendDistTopN = ", recommendDistTopN
    #返回值 rank 应该是 [(物品，评分),(物品，评分),(物品，评分)……] 的格式
    """
    return recommendListTopN
    
#程序运行时间起点
startTime = time.clock()

global trainSet
trainSet = loadDataSet('/Users/wakemeup/Documents/推荐系统实战/movielens/ml-100k/u1.base')
testSet = loadDataSet('/Users/wakemeup/Documents/推荐系统实战/movielens/ml-100k/u1.test')
global W 
W = UserSimilarity(trainSet)
#print(Recommend(1, trainSet, W, 3))
N = 10 #此时 N＝ 10，代表对每个用户推荐10个物品
global K
for K in [3,5,10,20,40,80,160]:
    recallRate = Recall(trainSet, testSet, N) 
    precisionRate = Precision(trainSet, testSet, N)
    coverageRate = Coverage(trainSet,testSet, N)
    popularity = Popularity(trainSet, testSet, N)
    print "While K = %2d | recall rate : %8f | precision rate : %8f | coverage rate : %8f | popularity : %8f " % (K, recallRate, precisionRate, coverageRate, popularity)





#程序运行时间终点
endTime = time.clock()
print "\n--------program complete : %f s--------" % (endTime-startTime)