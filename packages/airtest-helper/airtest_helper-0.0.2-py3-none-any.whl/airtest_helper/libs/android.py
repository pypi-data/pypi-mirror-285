# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     android.py
# Description:  TODO
# Author:       zhouhanlin
# CreateDate:   2024/07/17
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import re
import shlex
import subprocess
import typing as t
from airtest_helper.log import logger
from airtest.core.android.constant import TOUCH_METHOD, CAP_METHOD

__all__ = ['stop_app', 'get_screen_size_via_adb', 'get_connected_devices', 'adb_touch', 'get_adbcap_url',
           'get_javacap_url', 'get_minicap_url']


def stop_app(app_name, device_id: str, timeout=10) -> None:
    # 构造ADB命令
    adb_cmd = "adb.exe -s {} shell am force-stop {}".format(device_id, app_name)
    # 将命令字符串分割成列表
    cmd_list = shlex.split(adb_cmd)
    try:
        # 执行ADB命令并设置超时时间
        subprocess.run(cmd_list, timeout=timeout, check=True)
        logger.info("execute cmd: {}".format(adb_cmd))
    except subprocess.TimeoutExpired:
        logger.error("Timeout occurred. Failed to stop the app.")
    except subprocess.CalledProcessError:
        logger.error("Failed to stop the app.")
    except Exception as e:
        logger.error("An error occurred: {}".format(e))


def get_screen_size_via_adb(device_id: str) -> t.Tuple[int, int]:
    # 使用ADB命令获取设备屏幕大小
    try:
        output = subprocess.check_output(['adb', '-s', device_id, 'shell', 'wm', 'size']).decode('utf-8')
        match = re.search(r'Physical size: (\d+)x(\d+)', output)
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            return width, height
    except subprocess.CalledProcessError as e:
        logger.error("Error: ADB command failed: {}".format(e))
    return 0, 0


def get_connected_devices() -> list:
    devices = list()
    try:
        # 执行 adb 命令获取设备列表信息
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        # 检查是否成功执行 adb 命令
        if result.returncode == 0:
            # 解析 adb 输出，获取设备列表信息
            output_lines = result.stdout.strip().split('\n')
            # 第一行是标题，需要跳过
            devices = [line.split('\t')[0] for line in output_lines[1:] if line.strip()]
        else:
            logger.error("Failed to execute adb command.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    return devices


def adb_touch(v: tuple, device_id: str, timeout: int = 10) -> None:
    """
    adb 模拟操作点击，规避有些UI上无法直接点击
    """
    adb_cmd = "adb.exe -P 5037 -s {} shell input tap {} {}".format(device_id, v[0], v[1])
    # 将命令字符串分割成列表
    cmd_list = shlex.split(adb_cmd)
    try:
        # 执行ADB命令并设置超时时间
        subprocess.run(cmd_list, timeout=timeout, check=True)
        logger.info("execute cmd: ", adb_cmd)
    except subprocess.TimeoutExpired:
        logger.error("Timeout occurred,Failed to execute adb cmd.")
    except subprocess.CalledProcessError:
        logger.error("Failed to execute adb cmd.")
    except Exception as e:
        logger.error("An error occurred: {}".format(e))


def get_minicap_url(device_id: str) -> str:
    return "android://127.0.0.1:5037/{}?cap_method={}&touch_method={}".format(
        device_id, CAP_METHOD.MINICAP, TOUCH_METHOD.ADBTOUCH
    )


def get_adbcap_url(device_id: str) -> str:
    return "android://127.0.0.1:5037/{}?cap_method={}&touch_method={}".format(
        device_id, CAP_METHOD.ADBCAP, TOUCH_METHOD.ADBTOUCH
    )


def get_javacap_url(device_id: str) -> str:
    return "android://127.0.0.1:5037/{}?cap_method={}&touch_method={}".format(
        device_id, CAP_METHOD.JAVACAP, TOUCH_METHOD.ADBTOUCH
    )
