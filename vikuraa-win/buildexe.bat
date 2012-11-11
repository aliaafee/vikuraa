mkdir src
mkdir src\dist
mkdir src\dist\res
copy /Y ..\res\*.* src\dist\res
copy /Y ..\vikuraa\*.py src\
copy /Y setup.py src\
cd src
C:\Python27\python.exe setup.py py2exe
del dist\vikuraa.exe
ren dist\__main__.exe vikuraa.exe
pause