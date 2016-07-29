#coding=utf-8
import json
import os
import time
from operator import itemgetter, attrgetter, methodcaller

def time_me(fn):
    def _wrapper(*args, **kwargs):
        start = time.clock()
        rtn = fn(*args, **kwargs)

        print "%s cost %s second"%(fn.__name__, time.clock() - start)

        return rtn
    return _wrapper


def calcSimilarity(rootPath, apisPath):
    '''
    :param rootPath: 日志文件根目录路径
    :param apisPath: apis.txt文件路径
    :return: none
    '''
    #生成api对应编号
    apisDict = {}
    apisFile = open(apisPath, 'rb')
    line = apisFile.readline()
    i = 0
    while line:
        line = line.replace('\r\n', '')
        apisDict[line] = i
        i = i + 1
        line = apisFile.readline()

    #遍历目录
    paths = os.walk(rootPath)
    for path in paths:
        filtedLogPaths = []
        if ('logcat_1.log.filted' in path[2]):
            for log in path[2]:
                if log.find('.log.filted') > 0:
                    filtedLogPaths.append(os.path.join(path[0],log))
            calcEachSimilarity(filtedLogPaths, path[0], os.path.join(rootPath, 'result-old.txt'), apisDict)


def findapi(x):
    '''
    获取json日志中的api
    :param x: json字符串
    :return: api字符串
    '''
    try:
        dataDict = json.loads(x)
    except Exception as ex:
        # pdb.set_trace()
        print 'something wrong in logfile...'
        return

    for k, v in dataDict.items():

        for kk, vv in v.items():
            # print kk
            # print vv
            if kk == 'api':
                strs = vv.split('->')
                api = strs[-1].replace('#', '->')
                return api.encode('utf-8')

def findClassNameAndTid(x):
    '''
    获取一条日志记录中的类名和ThreadId
    :param x: 日志记录字符串
    :return: [classname, tid]
    '''
    try:
        dataDict = json.loads(x)
    except Exception as ex:
        print 'something wrong in logfile...'
        return
    for k, v in dataDict.items():
        for kk, vv in v.items():
            if kk =='tid_blabla':
                strs = vv.split ('@@')
                return (strs[0], int(strs[1]))

@time_me
def levenshtein(s, t):
    if len(s) > len(t):
        s, t = t, s
    # 第一步
    n = len(s)
    m = len(t)
    print 'm = ', m
    print 'n = ', n

    if not m: return 0
    if not n: return 0

    # 第二步
    v0 = [i for i in range(0, m + 1)]
    v1 = [0] * (m + 1)

    # 第三步
    cost = 0
    for i in range(1, n + 1):
        v1[0] = i
        for j in range(1, m + 1):
            # 第四步,五步
            if s[i - 1] == t[j - 1]:
                cost = 0
            else:
                cost = 1

            # 第六步
            a = v0[j] + 1
            b = v1[j - 1] + 1
            c = v0[j - 1] + cost
            v1[j] = min(a, b, c)
        v0 = v1[:]
    # 第七步
    result = 1 - (v1[m] * 1.0 / m)
    return result

def staticApiNumberDiff(s, t, apiList):
    '''

    :param s: 一个api序列
    :param t: 另一个api序列
    :param apisDict: 按照从小到大的编号的api list
    :return: 所有api的统计对比结果字符串： '1/2 2/3 0/0 6/7'
    '''
    sDict = {}
    for i in s:
        if (not sDict.has_key(i)):
            sDict[i] = 1
        else:
            sDict[i] = sDict[i] + 1

    tDict = {}
    for i in t:
        if (not tDict.has_key(i)):
            tDict[i] = 1
        else:
            tDict[i] = tDict[i] + 1
    apiStaticList = []
    #
    for i in apiList:
        api = i[0]
        apiNumber = i[1]
        if sDict.has_key(apiNumber):
            sNumber = sDict[apiNumber]
        else:
            sNumber = 0
        if tDict.has_key((apiNumber)):
            tNumber = tDict[apiNumber]
        else:
            tNumber = 0
        apiStaticList.append((sNumber, tNumber))

    #把list处理为字符串
    rtnString = ''
    count = 0
    for i in apiStaticList:
        if (i[0] == 0 and i[1] == 0):
            count = count + 1
            continue
        rtnString = rtnString + str(count) + ':' + str(i[0]) + '/' + str(i[1]) + ' '
        count = count + 1
    return  rtnString


@time_me
def calcEachSimilarity(filtedLogPaths, logDir, resultPath, apisDict):
    '''

    :param filtedLogPaths: 一个含有某个APP所有处理过的分析日志的list
    :param logDir: 这些日志文件所在的目录路径
    :param resultPath: 整个日志文件夹的根目录下的结果文件路径
    :param apisDict: 每个api对应的编号关系字典
    :return: none
    '''
    #将各个日志文件中的api序列转化为对应的数字序列
    print 'playing with ' + repr(logDir.split('\\')[-1])
    apiNumerals = []
    logCount = 0
    maxApiNumber = 0
    for logFilePath in filtedLogPaths:
        eachApiNumeral = []
        logFile = open(logFilePath, 'rb')
        line = logFile.readline()
        while line:
            api = findapi(line)
            classAndTid = findClassNameAndTid(line)
            # y = sorted(x, key=itemgetter(1))
            # z = sorted(y, key=itemgetter(0), reverse=False)

            # if (api):
            #     apiNumber = apisDict[api]
            #     if classAndTid in eachApiNumeral:
            #         eachApiNumeral[classAndTid].append(apiNumber)
            #     else:
            #         eachApiNumeral[classAndTid] = [apiNumber]

            if (api):
                apiNumber = apisDict[api]
                eachApiNumeral.append(apiNumber)

                # if (apiNumber > maxApiNumber):
                #     maxApiNumber = apiNumber

            line = logFile.readline()
        # tmp = zip(eachApiNumeral.keys(), eachApiNumeral.values())
        # tmp2 = sorted(tmp, key=itemgetter(0))
        apiNumerals.append(eachApiNumeral)
        logCount = logCount + 1

    #相似度比较结果
    result = {}
    #api统计结果
    staticResult = {}
    #api序列
    sortedApiList = []
    for i in range(len(apiNumerals)):
        # 只比较没有伪装的模拟器与其他模拟器之间的相似度
        if (i != 0):
            continue
        for j in range(len(apiNumerals)):
            if j <= i:
                continue
            # print levenshtein(apiNumerals[i], apiNumerals[j]);
            diff = levenshtein(apiNumerals[i], apiNumerals[j])
            sortedApiList = sorted(apisDict.iteritems(), key=lambda d: d[1], reverse=False)
            apiStatic = staticApiNumberDiff(apiNumerals[i], apiNumerals[j], sortedApiList)
            result[str((i + 1)) + ',' + str((j + 1))] = str(diff)
            staticResult[str(i + 1) + ',' + str(j + 1)] = apiStatic

    # 输出结果
    # 每个app单独的结果文件
    resultFile = open(os.path.join(logDir, 'result-old.txt'), 'wb')
    # 所有测试app的结果文件，保存在本次运行的根目录下
    totalResultFile = open(resultPath, 'a+')
    resultStr = ''
    # 按key排序
    keys = result.keys()
    keys.sort()
    result2 = [result[key] for key in keys]
    i = 0
    for k in keys:
        resultFile.write(str(k) + ':' + str(result2[i]) + ' | ' + staticResult[k] + os.linesep)
        resultStr = resultStr + ' ' + str(result2[i])
        i = i + 1
    # for k,v in result.items():
    #     resultFile.write(str(k) + ':' + str(v) + ' | ' + staticResult[k] + os.linesep)
    #     resultStr = resultStr + ' ' + str(v)
    apkName = logDir.split('\\')[-1]
    totalResultFile.write(apkName + ': ' + resultStr + os.linesep)
    # resultFile.write(str(sortedApiList) + os.linesep)
    resultFile.close()
    totalResultFile.close()


if __name__ == '__main__':
    # rootPath = r'E:\android\paper related\anti-emulator\logs\ApkLog-malware-2'
    rootPath = r'E:\android\paper related\anti-emulator\logs\contagiominidump-2'
    apisPath = r'E:\python\AndroidSandboxController\apis-ctgd-2.txt'
    calcSimilarity(rootPath, apisPath)
   # diff = levenshtein('1234323','')
   #  print diff


