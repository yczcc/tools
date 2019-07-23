# -*- coding: utf-8 -*-
from lxml import etree
import os, time, datetime, shutil, uuid, sys, re

VS_VCXPROJ_NAME = 'ProjectName'
VS_VCXPROJ_DIR = 'E:/Workspace/VS2013/solutionName/projectName'
SOURCE_DIR = "E:/Workspace/Code/projectName"

VS_VCXPROJ_FILE_TYPE_CLCOMPILE = 'ClCompile'
VS_VCXPROJ_FILE_TYPE_CLINCLUDE = 'ClInclude'
VS_VCXPROJ_FILE_TYPE_TEXT = 'Text'
VS_VCXPROJ_FILE_TYPE_NONE = 'None'
VS_VCXPROJ_FILE_TYPE_VAILD = [
    VS_VCXPROJ_FILE_TYPE_CLCOMPILE,
    VS_VCXPROJ_FILE_TYPE_CLINCLUDE,
    VS_VCXPROJ_FILE_TYPE_TEXT]
VS_VCXPROJ_FILE_TYPE = {
    'cpp': VS_VCXPROJ_FILE_TYPE_CLCOMPILE, # c++源文件
    'cc': VS_VCXPROJ_FILE_TYPE_CLCOMPILE, # c++源文件
    'cxx': VS_VCXPROJ_FILE_TYPE_CLCOMPILE, # c++源文件
    'c': VS_VCXPROJ_FILE_TYPE_CLCOMPILE, # c源文件
    'h': VS_VCXPROJ_FILE_TYPE_CLINCLUDE, # c++/c头文件
    'hpp': VS_VCXPROJ_FILE_TYPE_CLINCLUDE, # c++头文件
    'hxx': VS_VCXPROJ_FILE_TYPE_CLINCLUDE, # c++头文件
    'txt': VS_VCXPROJ_FILE_TYPE_TEXT # 文本文件
}

# 过滤指定目录
DIR_IGNORE_TYPE = ['.git', '.svn']
# 过滤指定后缀的文件
FILE_IGNORE_TYPE = ['o', 'd', 'tgz']

def to_unicode(string):
    ret = ''
    for v in string:
        ret = ret + hex(ord(v)).upper().replace('0X', '\\u')
    return ret

# 获取目录下所有的文件路径
def list_dir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            # 过滤目录名
            if file not in DIR_IGNORE_TYPE:
                list_dir(file_path, list_name)
        else:
            # 过滤指定后缀文件
            file_postfix = os.path.splitext(file_path)[-1][1:]
            if file_postfix not in FILE_IGNORE_TYPE:
                file_path = file_path.replace('\\', '/')
                list_name.append(file_path)

# 获取指定目录下所有的文件信息，并按照指定的文件类型分类
def get_source_info_by_dir(source_dir):
    file_lists = os.listdir(source_dir)
    files = []
    file_infos = {}
    list_dir(source_dir, files)
    for file in files:
        vs_vcxproj_file_type = ''
        # 获取文件名后缀
        file_postfix = os.path.splitext(file)[-1][1:]
        # 文件名后缀全部转换为小写字母后比较
        file_postfix = file_postfix.lower()
        file_name = os.path.split(file)[-1][1:]
        file_path = file[len(source_dir)+1:-len(file_name)-2]
        file_path = file_path.replace('/', '\\')
        # 获取vs工程文件名对应属性类型
        if VS_VCXPROJ_FILE_TYPE.has_key(file_postfix):
            vs_vcxproj_file_type = VS_VCXPROJ_FILE_TYPE[file_postfix]
        else:
            vs_vcxproj_file_type = VS_VCXPROJ_FILE_TYPE_NONE
        if "" != file_path:
            file_infos.setdefault('PATH_LIST', []).append(file_path)
        file_infos.setdefault(vs_vcxproj_file_type, []).append(
            {'path': file_path, 'file': file})

    # PATH_LIST中记录当前目录下所有文件所在路径（相对路径）
    file_infos['PATH_LIST']=list(set(file_infos['PATH_LIST']))
    # check dir whole set
    path_whole_index = 0
    for path in file_infos['PATH_LIST']:
        path_tmp_list = path.split('\\')
        path_whole = ''
        for path_tmp in path_tmp_list:
            if '' != path_whole:
                path_whole = path_whole + '\\' + path_tmp
            else:
                path_whole = path_tmp
            if path_whole not in file_infos['PATH_LIST']:
                file_infos.setdefault('PATH_LIST', []).insert(path_whole_index, path_whole)
                path_whole_index=path_whole_index+1
    return file_infos

def tag_uri_and_name(elem):
    if elem.tag[0] == "{":
        uri, ignore, tag = elem.tag[1:].partition("}")
    else:
        uri = None
        tag = elem.tag
    return uri, tag

def indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def modify_origin_vs_vcxproj_xml(vs_vcxproj_dir, vs_vcxproj_name, source_dir):
    #获得当前时间
    time_now = datetime.datetime.now()
    #转换为指定的格式:
    time_str = time_now.strftime("%Y%m%d%H%M%S")
    ret = 0
    # 检查待操作的工程文件vcxproj
    vs_vcxproj_file_name = vs_vcxproj_dir + '/' + vs_vcxproj_name + '.vcxproj'
    if not os.access(vs_vcxproj_file_name, os.R_OK):
        print '[ERROR]vs_vcxproj_file_name can\'t read. ', vs_vcxproj_file_name
        ret = -1
        return ret
    if not os.access(vs_vcxproj_file_name, os.W_OK):
        print '[ERROR]vs_vcxproj_file_name can\'t write. ', vs_vcxproj_file_name
        ret = -1
        return ret
    # 检查待操作的工程文件filters
    vs_vcxproj_filters_file_name = vs_vcxproj_dir + '/' + vs_vcxproj_name + '.vcxproj.filters'
    if not os.access(vs_vcxproj_filters_file_name, os.R_OK):
        print '[ERROR]vs_vcxproj_filters_file_name can\'t read. ', vs_vcxproj_filters_file_name
        ret = -1
        return ret
    if not os.access(vs_vcxproj_filters_file_name, os.W_OK):
        print '[ERROR]vs_vcxproj_filters_file_name can\'t write. ', vs_vcxproj_filters_file_name
        ret = -1
        return ret

    files_info = get_source_info_by_dir(source_dir)
    if 0 == len(files_info):
        ret = -2
        return ret

    if 0 != ret:
        print '[ERROR]got error ret=', ret
        return ret

    vs_vcxproj_file_name_bak = vs_vcxproj_file_name + '-' + time_str
    vs_vcxproj_filters_file_name_bak = vs_vcxproj_filters_file_name + '-' + time_str
    open(vs_vcxproj_file_name_bak, "wb").write(open(vs_vcxproj_file_name, "rb").read())
    open(vs_vcxproj_filters_file_name_bak, "wb").write(open(vs_vcxproj_filters_file_name, "rb").read())

    # 处理 vcxproj 文件
    vs_vcxproj_xml_tree = etree.parse(vs_vcxproj_file_name)
    vs_vcxproj_filters_xml_tree = etree.parse(vs_vcxproj_filters_file_name)
    vs_vcxproj_xml_root = vs_vcxproj_xml_tree.getroot()
    for node in vs_vcxproj_xml_root:
        node_item = tag_uri_and_name(node)
        if 'ItemGroup' != node_item[1]:
            continue
        node_label = node.get('Label')
        if None == node_label or 'yczcc' == node_label:  # 其中无Label的ItemGroup为VS自动生成的，可能需要补充
            vs_vcxproj_xml_root.remove(node)
    # 添加工程文件
    for file_type in files_info:
        if 'PATH_LIST' == file_type:
            continue
        if file_type in VS_VCXPROJ_FILE_TYPE_VAILD:
            itemgroup = etree.SubElement(vs_vcxproj_xml_root, 'ItemGroup', attrib={'Label':'yczcc'})
            for file in files_info[file_type]:
                etree.SubElement(itemgroup, file_type, attrib={'Include':file['file']})
        else:
            itemgroup = etree.SubElement(vs_vcxproj_xml_root, 'ItemGroup', attrib={'Label': 'yczcc'})
            for file in files_info[file_type]:
                file_temp = file['file'].decode("gbk", errors='ignore')
                # if re.findall(r'[\u4e00-\u9fff]+', file_temp):
                #     file_temp = file_temp.decode("gbk", errors='ignore')
                #     print file_temp
                etree.SubElement(itemgroup, VS_VCXPROJ_FILE_TYPE_NONE, attrib={'Include': file_temp})
    indent(vs_vcxproj_xml_root)
    vs_vcxproj_xml_tree.write(vs_vcxproj_file_name, pretty_print=True, xml_declaration=True, encoding='utf-8')

    # 处理 vcxproj.filters 文件
    vs_vcxproj_filters_xml_tree = etree.parse(vs_vcxproj_filters_file_name)
    vs_vcxproj_filters_xml_root = vs_vcxproj_filters_xml_tree.getroot()

    path_list = files_info['PATH_LIST']
    filter_path_list = []
    for node in vs_vcxproj_filters_xml_root:
        node_item = tag_uri_and_name(node)
        if 'ItemGroup' != node_item[1]: # 所有的文件存储在ItemGroup节点中
            continue
        node_label = node.get('Label')
        if None == node_label or 'yczcc' == node_label: # 其中无Label的ItemGroup为VS自动生成的，可能需要补充
            vs_vcxproj_filters_xml_root.remove(node)

    # 添加工程文件目录相对路径unique id
    itemgroup_ui = etree.SubElement(vs_vcxproj_filters_xml_root, 'ItemGroup', attrib={'Label': 'yczcc'})
    for filter_path in path_list:
        filter_item_node = etree.SubElement(itemgroup_ui, 'Filter', attrib={'Include': filter_path})
        filter_item_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, filter_path))
        etree.SubElement(filter_item_node, 'UniqueIdentifier').text = '{' + filter_item_uuid + '}'
    # 添加工程文件目录
    for file_type in files_info:
        if 'PATH_LIST' == file_type:
            continue
        else:
            if file_type in VS_VCXPROJ_FILE_TYPE_VAILD:
                itemgroup = etree.SubElement(vs_vcxproj_filters_xml_root, 'ItemGroup', attrib={'Label': 'yczcc'})
                for file in files_info[file_type]:
                    item_filter = etree.SubElement(itemgroup, file_type, attrib={'Include': file['file']})
                    if "" != file['path']:
                        etree.SubElement(item_filter, 'Filter').text = file['path']
            else:
                itemgroup = etree.SubElement(vs_vcxproj_filters_xml_root, 'ItemGroup', attrib={'Label': 'yczcc'})
                for file in files_info[file_type]:
                    file_temp = file['file'].decode("gbk", errors='ignore')
                    item_filter = etree.SubElement(itemgroup, VS_VCXPROJ_FILE_TYPE_NONE, attrib={'Include': file_temp})
                    if "" != file['path']:
                        etree.SubElement(item_filter, 'Filter').text = file['path']
    indent(vs_vcxproj_filters_xml_root)
    vs_vcxproj_filters_xml_tree.write(vs_vcxproj_filters_file_name, pretty_print=True, xml_declaration=True, encoding='utf-8')

    os.remove(vs_vcxproj_file_name_bak)
    os.remove(vs_vcxproj_filters_file_name_bak)
    return 0

"""
    参数1：VS项目名称，例如 projectName
    参数2：VS项目绝对路径，例如 E:/Workspace/VS2013/solutionName/projectName
    参数3：VS项目的源码绝对路径，例如 E:/Workspace/Code/projectName
    e.g.: python VisualStudio_vcxproj_build.py projectName E:/Workspace/VS2013/solutionName/projectName E:/Workspace/Code/projectName
"""
if __name__ == '__main__':
    paramLen = len(sys.argv)
    if 4 != paramLen:
        if 2 == paramLen and "-h" == sys.argv[1]:
            print('e.g.: python VisualStudio_vcxproj_build.py ProjectName SolutionName/projectName Code/projectName')
            exit(0)
        print('script param length=%s is error, use inner default param!!!' % paramLen)
        vs_vcxproj_name = VS_VCXPROJ_NAME
        vs_vcxproj_dir = VS_VCXPROJ_DIR
        source_dir = SOURCE_DIR
    else:
        vs_vcxproj_name = sys.argv[1]
        vs_vcxproj_dir = sys.argv[2]
        source_dir = sys.argv[3]
    """
        处理windows环境下目录标识方法，把反斜杠(\)统一转换成正斜杠(/)
    """
    vs_vcxproj_dir = vs_vcxproj_dir.replace('\\', '/')
    source_dir = source_dir.replace('\\', '/')
    print('VS project name: ', vs_vcxproj_name)
    print('VS project path: ', vs_vcxproj_dir)
    print('VS source path: ', source_dir)
    # 执行转换
    ret = modify_origin_vs_vcxproj_xml(vs_vcxproj_dir, vs_vcxproj_name, source_dir)
    if 0 == ret:
        print('[SUCCESS]***')
    else:
        print('[FAILED]!!!')
    exit(ret)