# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     __init__.py
# Description:  TODO
# Author:       mfkifhss2023
# CreateDate:   2024/07/15
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
import sys
import airtest_helper.log

# 重载模块
sys.modules['airtest.utils.logger'] = airtest_helper.log

import airtest_helper.logwraper

# 重载模块
sys.modules['airtest.utils.logwraper'] = airtest_helper.logwraper

import airtest_helper.settings

# 重载模块
sys.modules['airtest.core.settings'] = airtest_helper.settings
