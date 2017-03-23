# -*- coding: UTF-8 -*-  
from numpy import *
import random
import math
from operator import itemgetter  
import time

def SplitDataFromDeliciousDataSetDeliciousBookmarks():
    fr = open('/Users/wakemeup/Documents/推荐系统实战/DeliciousBookmarks/hetrec2011-delicious-2k/user_taggedbookmarks-timestamps.dat')
    print "    ~~~The whole records count is 43 W ~~ \n"
    trainSet = []; testSet = []
    tmpUser = 0; tmpItem = 0; whetherBecomeTrain = True  # 用于纪录上一行的 UserID 和 ItemID，如果新的一行 User 或 Item 不同，则会随机分配到 TrainSet 或者 TestSet。否则就会与上一行分配结果相同
    for line in fr.readlines()[1:30000]:  # [1:] 是为了去掉开头的 userID	bookmarkID	tagID	timestamp
        curLine = line.strip().split('\t')[0:3]
        for i in range(3):   #字符串转换为数字
            curLine[i] = int(curLine[i])
        #print(curLine)
        if (curLine[0] != tmpUser) or (curLine[1] != tmpItem): #新的一行 User 或 Item 不同
            randomNumber = random.randrange(0,5) #取 0,1,2,3,4
            if randomNumber != 0:
                trainSet.append(curLine)
                whetherBecomeTrain = True
            else:
                testSet.append(curLine)
                whetherBecomeTrain = False
        else:
            if whetherBecomeTrain:
                trainSet.append(curLine)
            else:
                testSet.append(curLine)
        #更新 tmpUser tmpItem
        tmpUser = curLine[0]; tmpItem = curLine[1]
    #print "trainSet = ",trainSet[0:40]
    #print "testSet = ", testSet[0:40]
    print "______split Data From Delicious DataSet:COMPLETE ______"
    return trainSet, testSet #格式为 userID |	bookmarkID	|  tagID






def InitStat(records):
    global user_tags, tag_items, user_items, tag_users, item_users #  ｛Ai:{B1:CountB1,B2:CountB2,B3:CountB3...}｝字典
    user_tags = {}
    tag_items = {}
    user_items = {}
    tag_users = {}
    item_users = {}
    count = 0
    itemsNotRepeated = set()
    tagsNotRepeated = set()
    usersNotRepeated = set()
    for user, item, tag in records:
        if count % 10000 == 0 : print "InitStat :  NO.#",count , "| all : 43 W " ; 
        count += 1
        AddValueToMat(user_tags, user, tag)
        AddValueToMat(tag_items, tag, item)
        AddValueToMat(user_items, user, item)
        AddValueToMat(tag_users, tag, user)
        AddValueToMat(item_users,item, user)
        itemsNotRepeated.add(item)
        usersNotRepeated.add(user)
        tagsNotRepeated.add(tag)
 
    #print len(itemsNotRepeated),len(usersNotRepeated),len(tagsNotRepeated)
    #print "user_tags = \n",user_tags
    #print "tag_items = \n",tag_items
    #print "user_items = \n",user_items
    print "_______InitStat______ :COMPLETE, user_tags,tag_items,user_items, tag_users, item_users has been created"
    print "On the average,each user match %f tags, each tag match %f items, each user match %f items\n" % (count*1.0/len(usersNotRepeated), count*1.0/len(tagsNotRepeated), count*1.0/len(usersNotRepeated) )
   

def InitStatTestSet(records):
    global user_tags_test,tag_items_test,user_items_test  #｛Ai:{B1:CountB1,B2:CountB2,B3:CountB3...}｝字典
    user_tags_test = {}
    tag_items_test = {}
    user_items_test = {}
    for user, item, tag in records:
        AddValueToMat(user_tags_test, user, tag)
        AddValueToMat(tag_items_test, tag, item)
        AddValueToMat(user_items_test, user, item)
    print "_______InitStatTestSet______ :COMPLETE, user_tags_test,tag_items_test,user_items_test has been created"



def AddValueToMat(dict, A, B):   # 对于 A 中每个元素，建立/修改 ｛Ai:{B1:CountB1,B2:CountB2,B3:CountB3...}｝字典  
    if A not in dict.keys():
        dict[A] = {}
    if B not in dict[A].keys():
        dict[A][B] = 0
    dict[A][B] += 1

def Recommend(user):
    recommend_items = {}
    tagged_items = user_items[user].keys() # tagged_items 用户已经在trainSet 标记过的物品
    #print "tagged_items = ",tagged_items
    #print "tagged_items in TestSet = " ,user_items_test[user].keys()
    count = 0
    for tag, wut in user_tags[user].items(): # wut 为 user 对 tag 标注次数 
        for item, wti in tag_items[tag].items(): #wti 为 item 被一个 tag 标注次数
            if item in tagged_items: # dont recommend the item which has been tagger by user
                #print "item = %d is in the user's item in TrainSet" % item
                continue
            #if item in user_items_test[user].keys():
                #print "item = %d is in the user's item in testSet!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" % item
            if item not in recommend_items.keys():
                recommend_items[item] = 0

            #计算 user 对 item 兴趣的传统方法 累加：n(u,b)*n(b,i)
            recommend_items[item] += wut * wti

            # 改进 TF-IDF
                # 分子为惩罚因子， len(tag_users[tag],keys()) 代表了标签 tag 被多少用户使用过
            #recommend_items[item] += wut * wti / math.log(1 + len(tag_users[tag],keys())) 

            # 改进 TF-IDF
                # 分子为惩罚因子， len(tag_users[tag],keys()) 代表了标签 tag 被多少用户使用过, len(item_users[item].keys()) 代表了物品 item 被多少用户标记过
            #recommend_items[item] += wut * wti / (math.log(1 + len(tag_users[tag],keys())) * math.log(1 + len(item_users[item].keys())))
            count += 1
            #print "tag = %d, item = %d, recommend_items[%d] += %d * %d" % (tag,item,item,wut,wti)
    print "recommend cal count = ",count
    return recommend_items

def GetRecommendation(user, N):
    recommendItems = Recommend(user)
    recommendItemsListTopN = sorted(recommendItems.iteritems(), key=lambda d:d[1], reverse = True)[0:N]
    return recommendItemsListTopN #返回格式为list。 即 [(item,grade),(item,grade)....]



# 召回率计算，描述测试集中用户－评分纪录中包含的被推荐物品比例
def Recall(train, test, N):  # trainSet 格式为 userID |	bookmarkID	|  tagID
    hit = all = 0
    train_users = set(line[0] for line in train)  
    print "\n  *********the number of train_users is %d *********\n" % len(train_users)
    test_users = set(line[0] for line in test)  
    #print "train_users = ",train_users
    count = 0; tmpTimePast = time.clock()
    for user in train_users:
        if user not in test_users:
            continue
        #tu = set(line[1] for line in test if line[0] == user)   #tu 代码 user 在 test集中评分(标签)过的物品
        tu = user_items_test[user].keys()
        #print "----------------------------------------------------------------------------------------------------------"
        #print "----------------------------------------------------------------------------------------------------------"
        #print "user = ",user
        #print "tu = ",tu
        rank = GetRecommendation(user, N) # 返回给 user 推荐的前 N 项物品 ,
        #print "rank = ", rank 
        for item , pui in rank:
            if item in tu:
                hit += 1
        all += len(tu)
        #print "hit = ",hit,"all = ",all
        tmpTimeNow = time.clock()
        print "calculate recall rate : NO.",count, "occupy time :", tmpTimeNow-tmpTimePast ," s" # 一遍循环用时
        tmpTimePast = tmpTimeNow
        count += 1
    return hit / (all * 1.0)

#  准确率计算，描述最终的推荐列表中有多少比例是发生过的用户－物品评分纪录
def Precision(train, test, N):
    hit = all = 0
    train_users = set(line[0] for line in train)  
    test_users = set(line[0] for line in test)  
    #print "train_users = ",train_users
    count = 0
    for user in train_users:
        print "calculate precision rate : NO.",count
        count += 1
        if user not in test_users:
            continue
        # tu = set(line[1] for line in test if line[0] == user)   #tu 代码 user 在 test集中评分(标签)过的物品
        tu = user_items_test[user].keys()
        rank = GetRecommendation(user, N) # 返回给 user 推荐的前 N 项物品 ,
        for item , pui in rank:
            if item in tu:
                hit += 1
        all += N
    return hit / (all * 1.0)
        
# 覆盖率计算  推荐系统能够推荐出来的物品占总物品集合的比例
def Coverage(train, test, N):
    recommend_items = set()
    all_items = set()
    train_users = set(line[0] for line in train) 
    for user in train_users:
        for item in user_items[user].keys():
            all_items.add(item)    # 这里必须用元组 set() 不用列表 list() 因为不能计算重复的项
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            recommend_items.add(item)
    return len(recommend_items) / (len(all_items) * 1.0)

# 新颖度/流行度计算 这里用推荐列表中物品的平均流行度度量推荐结果的新颖度
def Popularity(train, test, N):
    item_popularity = dict()
    train_users = set(line[0] for line in train) 
    #item_popularity[item]  纪录物品配用户标记的次数
    for user,item,tag in train:
        if item not in item_popularity:  
            item_popularity[item] = 0
        item_popularity[item] += 1
    ret = 0
    n = 0
    for user in train_users:
        rank = GetRecommendation(user, N)
        for item, pui in rank:
            ret += math.log(1 + item_popularity[item])
            n += 1
    ret /= n * 1.0
    return ret 

def SplitDataFromDeliciousDataSetCityULike():
    fr = open('/Users/wakemeup/Documents/推荐系统实战/DeliciousBookmarks/hetrec2011-delicious-2k/user_taggedbookmarks-timestamps.dat')
    print "    ~~~The whole records count is 43 W ~~ \n"
    trainSet = []; testSet = []
    tmpUser = 0; tmpItem = 0; whetherBecomeTrain = True  # 用于纪录上一行的 UserID 和 ItemID，如果新的一行 User 或 Item 不同，则会随机分配到 TrainSet 或者 TestSet。否则就会与上一行分配结果相同
    for line in fr.readlines()[1:30000]:  # [1:] 是为了去掉开头的 userID	bookmarkID	tagID	timestamp
        curLine = line.strip().split('\t')[0:3]
        for i in range(3):   #字符串转换为数字
            curLine[i] = int(curLine[i])
        #print(curLine)
        if (curLine[0] != tmpUser) or (curLine[1] != tmpItem): #新的一行 User 或 Item 不同
            randomNumber = random.randrange(0,5) #取 0,1,2,3,4
            if randomNumber != 0:
                trainSet.append(curLine)
                whetherBecomeTrain = True
            else:
                testSet.append(curLine)
                whetherBecomeTrain = False
        else:
            if whetherBecomeTrain:
                trainSet.append(curLine)
            else:
                testSet.append(curLine)
        #更新 tmpUser tmpItem
        tmpUser = curLine[0]; tmpItem = curLine[1]
    #print "trainSet = ",trainSet[0:40]
    #print "testSet = ", testSet[0:40]
    print "______split Data From Delicious DataSet:COMPLETE ______"
    return trainSet, testSet #格式为 userID |	bookmarkID	|  tagID
        
        



#程序运行时间起点
startTime = time.clock()


trainSet, testSet = SplitDataFromDeliciousDataSetDeliciousBookmarks()
InitStat(trainSet) # user_tags,tag_items,user_items
InitStatTestSet(testSet)
recallRate = Recall(trainSet, testSet, 30)
#precisionRate = Precision(trainSet, testSet, 15)
print "recallRate = ",recallRate 
#print "precisionRate = ", precisionRate


#程序运行时间终点
endTime = time.clock()
print "\n--------program complete : %f s--------" % (endTime-startTime)