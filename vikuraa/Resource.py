import os.path

DirName = os.path.dirname(os.path.abspath(__file__))
DirName, fileName = os.path.split(DirName)
ResDir = os.path.join(DirName, 'res')
licensePath = os.path.join(DirName, 'license.txt')

def GetFileName(resource):
    return os.path.join(ResDir, resource)
