# -*- coding: utf-8 -*-
from lxml import etree
import os, time, datetime, shutil, uuid

VS_VCXPROJ_NAME = 'xxx'
VS_VCXPROJ_DIR = 'E:/xxx/Workspace/VS2013/Server/xxx'
SOURCE_DIR = "Z:/code/xxx"

VS_VCXPROJ_FILE_TYPE_CLCOMPILE = 'ClCompile'
VS_VCXPROJ_FILE_TYPE_CLINCLUDE = 'ClInclude'
VS_VCXPROJ_FILE_TYPE_TEXT = 'Text'
VS_VCXPROJ_FILE_TYPE_NONE = 'None'
VS_VCXPROJ_FILE_TYPE_VAILD = [
    VS_VCXPROJ_FILE_TYPE_CLCOMPILE,
    VS_VCXPROJ_FILE_TYPE_CLINCLUDE,
    VS_VCXPROJ_FILE_TYPE_TEXT]
VS_VCXPROJ_FILE_TYPE = {
    'cpp': VS_VCXPROJ_FILE_TYPE_CLCOMPILE, 'CPP': VS_VCXPROJ_FILE_TYPE_CLCOMPILE,
    'c': VS_VCXPROJ_FILE_TYPE_CLCOMPILE, 'C': VS_VCXPROJ_FILE_TYPE_CLCOMPILE,
    'h': VS_VCXPROJ_FILE_TYPE_CLINCLUDE, 'H': VS_VCXPROJ_FILE_TYPE_CLINCLUDE,
    'txt': VS_VCXPROJ_FILE_TYPE_TEXT, 'TXT': VS_VCXPROJ_FILE_TYPE_TEXT
}

def list_dir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            list_dir(file_path, list_name)
        else:
            file_path = file_path.replace('\\', '/')
            list_name.append(file_path)

def get_source_info_by_dir(source_dir):
    file_lists = os.listdir(source_dir)
    files = []
    file_infos = {}
    list_dir(source_dir, files)
    for file in files:
        vs_vcxproj_file_type = ''
        # 获取文件名后缀
        file_postfix = os.path.splitext(file)[-1][1:]
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
    # 检查待操作的工程文件
    vs_vcxproj_file_name = vs_vcxproj_dir + '/' + vs_vcxproj_name + '.vcxproj'
    if not os.access(vs_vcxproj_file_name, os.R_OK):
        print '[ERROR]vs_vcxproj_file_name can\'t read. ', vs_vcxproj_file_name
        ret = -1
    if not os.access(vs_vcxproj_file_name, os.W_OK):
        print '[ERROR]vs_vcxproj_file_name can\'t write. ', vs_vcxproj_file_name
        ret = -1

    vs_vcxproj_filters_file_name = vs_vcxproj_dir + '/' + vs_vcxproj_name + '.vcxproj.filters'
    if not os.access(vs_vcxproj_filters_file_name, os.R_OK):
        print '[ERROR]vs_vcxproj_filters_file_name can\'t read. ', vs_vcxproj_filters_file_name
        ret = -1
    if not os.access(vs_vcxproj_filters_file_name, os.W_OK):
        print '[ERROR]vs_vcxproj_filters_file_name can\'t write. ', vs_vcxproj_filters_file_name
        ret = -1

    files_info = get_source_info_by_dir(source_dir)
    if 0 == len(files_info):
        ret = -2

    if 0 != ret:
        print '[ERROR]got error ret=', ret
        return

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
        if 'yczcc' != node_label:
            continue
        # node.set('Label', 'zccgis')
        vs_vcxproj_xml_root.remove(node)

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
                etree.SubElement(itemgroup, VS_VCXPROJ_FILE_TYPE_NONE, attrib={'Include': file['file']})
    indent(vs_vcxproj_xml_root)
    vs_vcxproj_xml_tree.write(vs_vcxproj_file_name, pretty_print=True, xml_declaration=True, encoding='utf-8')

    # 处理 vcxproj.filters 文件
    vs_vcxproj_filters_xml_tree = etree.parse(vs_vcxproj_filters_file_name)
    vs_vcxproj_filters_xml_root = vs_vcxproj_filters_xml_tree.getroot()

    path_list = files_info['PATH_LIST']
    filter_path_list = []
    for node in vs_vcxproj_filters_xml_root:
        node_item = tag_uri_and_name(node)
        if 'ItemGroup' != node_item[1]:
            continue
        node_label = node.get('Label')
        if None == node_label:
            filter_item_list = node.getchildren()
            for filter_item in filter_item_list:
                node.remove(filter_item)

            for filter_path in path_list:
                filter_item_node = etree.SubElement(node, 'Filter', attrib={'Include': filter_path})
                filter_item_uuid = str(uuid.uuid5(uuid.NAMESPACE_OID, filter_path))
                etree.SubElement(filter_item_node, 'UniqueIdentifier').text = '{' + filter_item_uuid + '}'
            continue
        elif 'yczcc' != node_label:
            continue
        vs_vcxproj_filters_xml_root.remove(node)

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
                    item_filter = etree.SubElement(itemgroup, VS_VCXPROJ_FILE_TYPE_NONE, attrib={'Include': file['file']})
                    if "" != file['path']:
                        etree.SubElement(item_filter, 'Filter').text = file['path']
    indent(vs_vcxproj_filters_xml_root)
    vs_vcxproj_filters_xml_tree.write(vs_vcxproj_filters_file_name, pretty_print=True, xml_declaration=True, encoding='utf-8')

    os.remove(vs_vcxproj_file_name_bak)
    os.remove(vs_vcxproj_filters_file_name_bak)

if __name__ == '__main__':
    modify_origin_vs_vcxproj_xml(VS_VCXPROJ_DIR, VS_VCXPROJ_NAME, SOURCE_DIR)
