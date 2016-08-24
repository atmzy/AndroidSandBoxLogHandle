from DealString import *
from DealWithLog import *

rootPath = r'E:\android\paper related\anti-emulator\logs\sanddroid-4\sf'
apisPath = r'E:\python\AndroidSandBoxLogHandle\apis-sf.txt'


if __name__ == '__main__':
    print 'start.'
    findApiList(rootPath, apisPath)
    dealWithLogMain(rootPath, apisPath)