# coding=utf-8
import os
import shutil

path_list = ['business', 'communication', 'education', 'entertainment', 'news_and_magazines', 'shopping',
             'social', 'tools', 'weather']
for a_path in path_list:
    workpath = os.path.join(r'E:\android\paper related\anti-emulator\logs\Apk-pure-3', a_path)

    paths = os.walk(workpath)

    count = 0
    total_line_number = 0
    for path in paths:
        files = path[2]

        for file in files:
            # print file
            if file.lower().endswith('.log'):

                log_file = open(os.path.join(path[0], file))
                line_number = 0
                line = log_file.readline()
                while line:
                    line_number = line_number + 1
                    line = log_file.readline()
                total_line_number = total_line_number + line_number
                count = count + 1

    print a_path + ': ' + str(total_line_number / count)
