# coding=utf-8

import os

'''
从一堆文件里面搜索特定的字符串，返回的结果形式为: [('文件名', 行号), ('文件名', 行号), ...]
'''

# 支持搜索的文件格式
file_type_set = ['smali', 'txt']
# 是否区分大小写，False不区分，True区分
case_sensitive = False
# 要搜索的关键词列表
targets = ['getDeviceId']

def printlist(list):
    for i in list:
        if type(i) == list:
            printlist(i)
        else:
            print '    ' + str(i)

def searchInFile(fileName, target):
    result = []
    file = open(fileName)
    line = file.readline()
    line_count = 1
    while line:
        if case_sensitive == False:
            target = target.lower()
            line = line.lower()
        if target in line:
            result.append(line_count)
        line = file.readline()
        line_count = line_count + 1
    if len(result) == 0:
        return None
    return (fileName, result)

def main(root_dir):
    total_result = {x: [] for x in targets}

    paths = os.walk(root_dir)

    for one_path in paths:
        files = one_path[2]
        for file in files:
            suffix = file.split('.')[-1:][0]
            if suffix in file_type_set:

                for target in targets:
                    # 对每一个文件都搜索所有的关键词
                    result = searchInFile(one_path[0] + os.sep + file, target)
                    if result != None:
                        tmp = total_result[target]
                        tmp.append(result)
                        total_result[target] = tmp


    for (k, v) in total_result.iteritems():
        print k + ': '
        for item in v:
            print '    ' + item[0] + ': '
            printlist(item[1])




if __name__ == '__main__':
    root_dir = r'E:\tools\android\AndroidKiller_v1.3.1\projects\test'
    main(root_dir)





