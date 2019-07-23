# -*- coding: utf-8 -*-
import os, time, datetime, shutil, uuid

SOURCE_DIR_ROOT = "Z:code/src/"
SOURCE_DIR = "/modules"

# 获取目录下所有的文件路径
def list_dir(path, list_name):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            list_dir(file_path, list_name)
        else:
            file_path = file_path.replace('\\', '/')
            file_path = os.path.dirname(file_path)
            list_name.append(file_path)

# 获取指定目录下所有的文件信息，并按照指定的文件类型分类
def get_source_info_by_dir(source_dir):
    file_name_data_txt = 'dir.txt'
    file_data = open(file_name_data_txt, "w+")
    file_lists = os.listdir(source_dir)
    files = []
    file_infos = {}
    list_dir(source_dir, files)
    files = list(set(files))
    for file in files:
        file_data.write(file)
        file_data.write('\n')
    file_data.close()

if __name__ == '__main__':
    get_source_info_by_dir(SOURCE_DIR_ROOT + SOURCE_DIR)