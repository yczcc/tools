# code/python
各种python脚本。

### 脚本文件说明
#### VisualStudio_vcxproj_build.py
VisualStudio工程文件（`.vcxproj`和`.vcxproj.filters`）自动更新，默认只处理后缀为`cpp`、`cc`、`cxx`、`c`、`h`、`hpp`、`hxx`、`txt`的文件。
在使用此脚本前，尽量保证VS工程是空工程。
##### 使用说明
1. 修改脚本中的`VS_VCXPROJ_NAME`、`VS_VCXPROJ_DIR`、`SOURCE_DIR`三个变量，
其中`VS_VCXPROJ_NAME`为VS工程名称（也就是工程文件的名称），
`VS_VCXPROJ_NAME`为VS工程文件所在目录（绝对路径，使用反斜杠模式），
`SOURCE_DIR`为工程对应的源代码文件目录（绝对路径，使用反斜杠模式）。  
2. 运行脚本`python VisualStudio_vcxproj_build.py`，在工程目录下覆盖更新工程文件，为了谨慎，可提前备份`.vcxproj`和`.vcxproj.filters`这两个文件。
#### convert2utf8.py
源代码文件编码转换成utf-8，默认只处理后缀为`cpp`、`cc`、`cxx`、`c`、`h`、`hpp`、`hxx`的文件。
##### 使用说明
1. 修改脚本中的`SOURCE_DIR_WINDOWS`或者`SOURCE_DIR_LINUX`，其中`SOURCE_DIR_WINDOWS`为Windows系统下的源代码目录，
`SOURCE_DIR_LINUX`为Linux系统下的源代码目录，按照系统对应设置其中之一即可。  
2. 运行脚本`python convert2utf8.py`，在源码目录下覆盖更新文件，为了谨慎，可提前备份源码文件。

 未完待续  
