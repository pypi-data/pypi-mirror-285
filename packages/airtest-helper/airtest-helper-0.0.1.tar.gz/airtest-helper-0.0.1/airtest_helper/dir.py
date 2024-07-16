# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     dir.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/07/15
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import os
import sys
import shutil
import typing as t
from airtest_helper.log import logger


def get_project_path():
    # 获取当前执行文件的绝对路径（兼容 Python 2 和 Python 3）
    exec_file_path = os.path.abspath(sys.argv[0])
    exec_file_path_slice = exec_file_path.split(os.path.sep)
    return os.path.sep.join(exec_file_path_slice[:-1])


def join_path(path_slice: list) -> t.LiteralString | str | bytes:
    return os.path.join(*path_slice)


def get_images_dir(is_created: bool = True) -> t.LiteralString | str | bytes:
    """
    获取image目录
    :param bool is_created: 目录是否已创建
    :return:
    """
    path = join_path([get_project_path(), "image"])
    if is_created is False:
        create_directory(dir_path=path)
    return path


def get_logs_dir(is_created: bool = True) -> t.LiteralString | str | bytes:
    path = join_path([get_project_path(), "log"])
    if is_created is False:
        create_directory(dir_path=path)
    return path


def get_bin_dir(is_created: bool = True) -> t.LiteralString | str | bytes:
    path = join_path([get_project_path(), "bin"])
    if is_created is False:
        create_directory(dir_path=path)
    return path


def is_exists(file_name: t.LiteralString | str | bytes) -> bool:
    if os.path.exists(file_name):
        return True
    else:
        return False


def is_file(file_path: str):
    return os.path.exists(file_path) and os.path.isfile(file_path)


def is_dir(file_path: str):
    return os.path.exists(file_path) and os.path.isdir(file_path)


def create_directory(dir_path):
    """
    创建目录，如果目录不存在则创建
    :param dir_path: 要创建的目录路径
    :return: True（创建成功）或 False（创建失败）
    """
    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except OSError:
        return False


def get_system_path():
    """
    获取当前系统的 PATH 环境变量
    :return: 当前系统的 PATH 环境变量，以列表形式返回各个路径
    """
    path_variable = os.environ.get('PATH')
    if path_variable:
        path_list = path_variable.split(os.pathsep)
        return path_list
    else:
        return []


def get_var_path(var: str) -> str:
    var_path = None
    path_list = get_system_path()
    for path in path_list:
        if var in path:
            var_path = path
            break
    return var_path


def move_file(src_file, dst_path):
    # 检查目标目录是否存在，如果不存在则创建目录
    if not is_dir(dst_path):
        create_directory(dst_path)
    try:
        # 移动文件
        shutil.move(src_file, dst_path)
        logger.info(f"文件已成功移动到目标目录：{dst_path}")
    except Exception as e:
        logger.error(f"移动文件时出现错误：{e}")
