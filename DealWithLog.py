#coding=utf-8
import json
import os
import time
from operator import itemgetter, attrgetter, methodcaller

import subprocess


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
            if (len(filtedLogPaths) == 4):  # 只处理存在完整的四个日志的样本
                calcEachSimilarity(filtedLogPaths, path[0], os.path.join(rootPath, 'result.txt'), apisDict)



# def findapi(x):
#     '''
#     获取json日志中的api
#     :param x: json字符串
#     :return: api字符串
#     '''
#     try:
#         dataDict = json.loads(x)
#     except Exception as ex:
#         # pdb.set_trace()
#         print 'something wrong in logfile...'
#         return
#
#     for k, v in dataDict.items():
#
#         for kk, vv in v.items():
#             # print kk
#             # print vv
#             if kk == 'api':
#                 strs = vv.split('->')
#                 api = strs[-1].replace('#', '->')
#                 return api.encode('utf-8')
#
# def findClassNameAndTid(x):
#     '''
#     获取一条日志记录中的类名和ThreadId
#     :param x: 日志记录字符串
#     :return: [classname, tid]
#     '''
#     try:
#         dataDict = json.loads(x)
#     except Exception as ex:
#         print 'something wrong in logfile...'
#         return
#     for k, v in dataDict.items():
#         for kk, vv in v.items():
#             if kk =='tid_blabla':
#                 strs = vv.split ('@@')
#                 return (strs[0], int(strs[1]))

def findClassNameAndTid(x):
    '''
    获取一条日志记录中的类名和ThreadId
    :param x: 日志记录字符串
    :return: classname@@tid
    '''
    try:
        dataDict = json.loads(x)
    except Exception as ex:
        print 'something wrong in logfile...'
        return
    for k, v in dataDict.items():
        for kk, vv in v.items():
            if kk =='tid_blabla':

                return vv

def findFileOperationType(x):
    '''
    获取该条记录的操作类型
    :param x:
    :return:
    '''
    try:
        dataDict = json.loads(x)
    except Exception as ex:
        print 'something wrong in logfile...'
        return
    for k, v in dataDict.items():
        for kk, vv in v.items():
            if kk == 'operType':
                return vv

def findFilePath(x):
    try:
        dataDict = json.loads(x)
    except Exception as ex:
        print 'something wrong in logfile...'
        return
    for k, v in dataDict.items():
        for kk, vv in v.items():
            if kk == 'filePath':
                return vv

def isFileOper(x):
    try:
        dataDict = json.loads(x)
    except Exception as ex:
        print 'something wrong in logfile...'
        return
    for k, v in dataDict.items():
        if (k == 'fileOper'):
            return True
        else:
            return False

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
                # return api.encode('utf-8')
                return api

def substring(s1, s2):
    count = min(len(s1), len(s2))
    rtn = ''
    for i in range(count):
        if s1[i] == s2[i]:
            rtn = rtn + s1[i]
        else:
            break
    return rtn

def baksmali_finished(workpath):
    if os.path.exists(os.path.join(workpath, 'out')) and os.path.exists(os.path.join(workpath, 'out/apktool.yml')):
        return True

def is_backsmali_succeed(workpath):
    if os.path.exists(os.path.join(workpath, 'out/apktool.yml')):
        return True


def baksmali(workpath, apkname):
    '''

    :param workpath: apk log目录路径，其中包含原始的apk文件
    :param apkname: apk文件名字
    :return: apk log目录路径
    '''

    if baksmali_finished(workpath):
        return os.path.join(workpath, 'out')

    args = ['java', '-jar', r'E:\tools\android\AndroidKiller_v1.3.1\bin\apktool\apktool\ShakaApktool.jar', 'd',
             os.path.join(workpath, apkname), '-o', os.path.join(workpath, 'out')]
    ret = None
    # 运行adb命令
    # print args
    adbProcess = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = adbProcess.communicate()
    # print ret[0]

    if is_backsmali_succeed(workpath):  #反编译成功
        return os.path.join(workpath, 'out')
    # if "\xce\xc4\xbc\xfe...\r\n" in ret[0]:  #反编译成功
    #     return os.path.join(workpath, 'out')


def findclasses(workpath):
    '''

    :param workpath: apk log目录路径
    :return: 找到的所有类名list
    '''
    ret = []
    paths = os.walk(workpath)
    prefix = os.path.join(workpath, 'out/smali')
    for path in paths:
        files = path[2]
        for file in files:
            strs = file.split('.')
            if strs[-1] == 'smali':

                classpath = path[0][len(prefix) + 1:]

                packagename = classpath.replace('\\', '.')
                ret.append(packagename + '.' + strs[0])

    return  ret

def dealLog(logpath, classes, apisDict):
    '''

    :param logpath: 一个log文件的路径
    :param classes: 所有类的list
    :return: 以类名和tid为key，api编号list为value的list
    '''

    fileOperDict = {}
    file = open(logpath)

    result = {}
    # thread_result = []
    line = file.readline()
    while line:
        # 记录对同一个文件的同一个操作的是否第一次出现，如果不是就忽略
        if (isFileOper(line)):
            operType = findFileOperationType(line)
            filePath = findFilePath(line)
            if (not filePath in fileOperDict):
                fileOperDict[filePath] = operType
            else:
                if (operType == fileOperDict[filePath]):
                    line = file.readline()
                    continue
                else:
                    fileOperDict[filePath] = operType

        x = findClassNameAndTid(line)
        y = findapi(line)
        if x and (y in apisDict) :
            strs = x.split('->')
            for classname in strs:# attention

                if classname in classes:
                    key = classname + '@@' + strs[-1:][0].split('@@')[-1:][0]
                    value = apisDict[y]
                    if key in result:
                        result[key].append(value)
                    else:
                        result[key] = [value]
                    break
        line = file.readline()
    return result

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

def staticApiNumberEachThread(log):
    rtn = []
    for t in log:
        rtn.append(len(t[1]))
    return  rtn

def compareDiff(log1, log2):

    '''
    比较的是什么都没有伪装的和有一部分伪装的，也就是(2, 1), (3, 1), (4, 1)之间的差别，
    而且从理论上来说，日志1的结果不应该比其他几个的结果更多，
    所以不用交换顺序， 直接以第一个参数的日志2/3/4为基础进行处理，判断日志1是否比这些多运行了一些内容

    :param log1: 日志2/3/4
    :param log2: 日志1
    :return:
    '''




    # 统计各个thread中的API 个数
    local1 = log1
    local2 = log2

    apiNumberInThread1 = staticApiNumberEachThread(local1)
    apiNumberInThread2 = staticApiNumberEachThread(local2)

    totalThread1 = len(local1)
    totalThread2 = len(local2)

    totalApi1 = sum(apiNumberInThread1)
    totalApi2 = sum(apiNumberInThread2)



    # 比较时需要totalThread1 >= totalThread2（不用管这一部分。。。）
    # if totalThread1 < totalThread2:
    #     local1, local2 = local2, local1
    #     apiNumberInThread1, apiNumberInThread2 = apiNumberInThread2, apiNumberInThread1
    #     totalApi1, totalApi2 = totalApi2, totalApi1
    #     totalThread1, totalThread2 = totalThread2, totalThread1




    total_diff = 0
    total_diff_list = []
    diff_list = []
    count_of_local1 = 0
    count_of_local2 = 0
    threadName1 = 'xxx'
    while count_of_local1 < len(local1):
        threadName1 = local1[count_of_local1][0].split('@@')[0]
        # 查找 local1 中类名相同的记录
        sameThreadName1 = [local1[count_of_local1]]
        # 如果没找到相同的需要受到给count_of_local1加1
        found_same = False
        while (count_of_local1 + 1 < len(local1)) and (local1[count_of_local1 + 1][0].split('@@')[0] == threadName1):
            sameThreadName1.append(local1[count_of_local1 + 1])
            count_of_local1 = count_of_local1 + 1
            found_same = True
        # if not found_same:
        count_of_local1 = count_of_local1 + 1

        # 查找 local2 中类名相同的记录
        sameThreadName2 = []
        for t in local2:
            if t[0].split('@@')[0] == threadName1:
                sameThreadName2.append(t)
            elif len(sameThreadName2) > 0:
                break
        # 开始进行比较
        count1 = len(sameThreadName1)
        count2 = len(sameThreadName2)
        diff = 0
        for i in range(count1):
            max_diff = 0
            for j in range(count2):

                diff = levenshtein(sameThreadName1[i][1], sameThreadName2[j][1])
                # import pdb
                # pdb.set_trace()
                # z = total_diff + apiNumberInThread1[count_of_local1 - count + i] * 1.0 / totalApi1 * diff
                # total_diff = z
                if len(sameThreadName2[j][1]) == 0:  # 表明log2中该进程没有任何行为
                    diff = 1.0
                if (diff > max_diff):
                    max_diff = diff


            total_diff_list.append((apiNumberInThread1[count_of_local1 - count1 + i], max_diff))
            diff_list.append((threadName1, max_diff))


        #处理没有对齐的
        #突然发现好像没什么用了，先不要了
        # if len(sameThreadName1) > len(sameThreadName2):
        #     while count < len(sameThreadName1):
        #
        #         diff_list.append((threadName1, diff))
        #         count = count + 1
        # else:
        #     while count < len(sameThreadName2):
        #         diff_list.append((threadName1, diff))
        #         count = count + 1
    total_diff = 0
    apinumber_list = [x[0] for x in total_diff_list]
    apinumber_sum = sum(apinumber_list)
    for a_diff in total_diff_list:
        total_diff = total_diff + a_diff[0] * 1.0 / apinumber_sum * a_diff[1]
    return (total_diff, diff_list)



        #
        #
        #
        # threadName2 = local2[count_of_local2].split('@@')[0]
        # if threadName1 == threadName2:
        #     diff = levenshtein(local1[count_of_local1][1], local2[count_of_local2][1])
        #     total_diff = total_diff + apiNumberInThread1[count_of_local1] / totalApi1 * diff * 1.0
        #     diff_list.append((threadName1, diff))
        #     count_of_local2 = count_of_local2 + 1
        # else:
        #     count_of_local2 = count_of_local2 + 1





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

    #for debug
    # if logDir.split('\\')[-1] != 'weather-1Weather_Widget_Forecast_Radar_0cf3e2cd.apk':
    #     return
    #for debug end

    print 'playing with ' + repr(logDir.split('\\')[-1])
    # 获取apk文件路径
    apkPath = ''
    files = os.listdir(logDir)
    for file in files:
        if file.split('.')[-1] == 'apk':
            apkPath = os.path.join(logDir, file)
    if apkPath == '':
        print 'does not find apk file, return from calcEachSimilarity...'
        return

    # 反编译apk
    workPath = baksmali(logDir, apkPath)
    if not workPath:
        print 'something wrong of baksmali in ' + logDir
        return
    print 'baksmali succeed.'

    classNames = findclasses(logDir)

    # 依次处理各个日志文件
    apiNumerals = []
    for logFilePath in filtedLogPaths:


        result = dealLog(logFilePath, classNames, apisDict)
        tmp = zip(result.keys(), result.values())
        tmp = sorted(tmp, key=itemgetter(0))
        apiNumerals.append(tmp)


    #相似度比较结果
    result = {}
    #api统计结果
    staticResult = {}
    #api序列
    sortedApiList = []
    for i in range(len(apiNumerals)):
        ## 只比较没有伪装的模拟器与其他模拟器之间的相似度
        #  前两个为没有伪装，后两个为全部伪装，比较相同类别两个间的区别和第一个及第二个之间的区别
        # if (i == 0) :
            for j in range(len(apiNumerals)):
                # if j <= i:
                #     continue
                if j <= i:
                    continue
                # print levenshtein(apiNumerals[i], apiNumerals[j]);
                # diff = levenshtein(apiNumerals[i], apiNumerals[j])
                # 比较的是后三个日志与第一个日志之间的区别， 顺序不可以颠倒
                rtn = compareDiff(apiNumerals[j], apiNumerals[i])
                diff = 0
                if rtn:
                    diff = float(rtn[0])
                # sortedApiList = sorted(apisDict.iteritems(), key=lambda d: d[1], reverse=False)
                # apiStatic = staticApiNumberDiff(apiNumerals[i], apiNumerals[j], sortedApiList)
                result[str((i + 1)) + ',' + str((j + 1))] = str(diff)
                # staticResult[str(i + 1) + ',' + str(j + 1)] = apiStatic
                staticResult[str(i + 1) + ',' + str(j + 1)] = str(rtn[1])


    # 输出结果
    # 每个app单独的结果文件
    resultFile = open(os.path.join(logDir, 'result.txt'), 'wb')
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
        # resultFile.write(str(k) + ':' + str(result2[i]) + os.linesep)
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

def dealWithLogMain(rootPath, apisPath):
    # for a_path in path_list:
        # rootPath =   os.path.join(r'E:\android\paper related\anti-emulator\logs\Apk-pure-3', a_path)
        # rootPath = r'E:\android\paper related\anti-emulator\logs\sanddroid-4\test-4'
        # apisPath = r'E:\python\AndroidSandBoxLogHandle\apis-sanddroid-4.txt'
        calcSimilarity(rootPath, apisPath)

if __name__ == '__main__':
    # path_list = ['business', 'communication', 'education', 'entertainment', 'news_and_magazines', 'shopping',
    #              'social', 'tools', 'weather']
    path_list = ['weather']
    # rootPath = r'E:\android\paper related\anti-emulator\logs\ApkLog-malware-2'
    for a_path in path_list:
        # rootPath =   os.path.join(r'E:\android\paper related\anti-emulator\logs\Apk-pure-3', a_path)
        rootPath = r'E:\android\paper related\anti-emulator\logs\sanddroid-4\test-4'
        apisPath = r'E:\python\AndroidSandBoxLogHandle\apis-sanddroid-4.txt'
        calcSimilarity(rootPath, apisPath)

    # diff = levenshtein('1234567890', '12345678')
    # diff = levenshtein('1234323','')
    #  print diff



