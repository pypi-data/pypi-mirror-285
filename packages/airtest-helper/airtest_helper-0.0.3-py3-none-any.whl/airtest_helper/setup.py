# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     setup.py
# Description:  TODO
# Author:       zhouhanlin
# CreateDate:   2024/07/16
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import sys
import argparse
from airtest.cli.parser import runner_parser
from airtest.cli.runner import setup_by_args
from airtest.report.report import get_parger as report_parser
from airtest.core.android.constant import TOUCH_METHOD, CAP_METHOD


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


def cli_setup(args=None) -> bool:
    """future api for setup env by cli"""
    if not args:
        if len(sys.argv) < 2:
            return False
        args = sys.argv

    ap = argparse.ArgumentParser()
    if "--report" in args:
        from airtest.report.report import main as report_main
        ap = report_parser(ap)
        args = ap.parse_args(args)
        report_main(args)
        exit(0)
    else:
        ap = runner_parser(ap)
        args = ap.parse_args(args)
        setup_by_args(args)
    return True
