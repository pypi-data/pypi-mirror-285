# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     log.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/07/15
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import logging

# 定义日志格式
# log_format = "%(asctime)s - %(message)s"
log_format = ('%(asctime)s - [PID-%(process)d] - [Thread-%(thread)d] - [%(levelname)s] - %(message)s ' +
              '- <%(funcName)s> - [Line-%(lineno)d] - %(filename)s')
date_format = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("airtest")


def init_logging(loglevel: str = "debug"):
    if loglevel == "debug":
        level = logging.DEBUG
        # logger.setLevel(logging.DEBUG)
    elif loglevel == "info":
        level = logging.INFO
        # logger.setLevel(logging.INFO)
    elif loglevel == "warning":
        level = logging.WARNING
        # logger.setLevel(logging.WARNING)
    else:
        level = logging.ERROR
        # logger.setLevel(logging.ERROR)
    logger.setLevel(level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# init_logging()


def get_logger(name):
    log = logging.getLogger(name)
    return log
