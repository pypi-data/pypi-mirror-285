# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     lib.py
# Description:  TODO
# Author:       zhouhanlin
# CreateDate:   2024/07/16
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from collections import OrderedDict
from poco.proxy import UIObjectProxy


def get_ui_object_proxy_attr(ui_object_proxy: UIObjectProxy) -> OrderedDict:
    ordered_dict = OrderedDict()
    ordered_dict["type"] = (
        ui_object_proxy.attr("type").strip()
        if isinstance(ui_object_proxy.attr("type"), str)
        else ui_object_proxy.attr("type")
    )
    ordered_dict["name"] = (
        ui_object_proxy.attr("name").strip()
        if isinstance(ui_object_proxy.attr("name"), str)
        else ui_object_proxy.attr("name")
    )
    ordered_dict["text"] = (
        ui_object_proxy.attr("text").strip()
        if isinstance(ui_object_proxy.attr("text"), str)
        else ui_object_proxy.attr("text")
    )
    ordered_dict["desc"] = (
        ui_object_proxy.attr("desc").strip()
        if isinstance(ui_object_proxy.attr("desc"), str)
        else ui_object_proxy.attr("desc")
    )
    ordered_dict["enabled"] = (
        ui_object_proxy.attr("enabled").strip()
        if isinstance(ui_object_proxy.attr("enabled"), str)
        else ui_object_proxy.attr("enabled")
    )
    ordered_dict["visible"] = (
        ui_object_proxy.attr("visible").strip()
        if isinstance(ui_object_proxy.attr("visible"), str)
        else ui_object_proxy.attr("visible")
    )
    ordered_dict["resourceId"] = (
        ui_object_proxy.attr("resourceId").strip()
        if isinstance(ui_object_proxy.attr("resourceId"), str)
        else ui_object_proxy.attr("resourceId")
    )
    ordered_dict["zOrders"] = (
        ui_object_proxy.attr("zOrders").strip()
        if isinstance(ui_object_proxy.attr("zOrders"), str)
        else ui_object_proxy.attr("zOrders")
    )
    ordered_dict["package"] = (
        ui_object_proxy.attr("package").strip()
        if isinstance(ui_object_proxy.attr("package"), str)
        else ui_object_proxy.attr("package")
    )
    ordered_dict["anchorPoint"] = (
        ui_object_proxy.attr("anchorPoint").strip()
        if isinstance(ui_object_proxy.attr("anchorPoint"), str)
        else ui_object_proxy.attr("anchorPoint")
    )
    ordered_dict["dismissable"] = (
        ui_object_proxy.attr("dismissable").strip()
        if isinstance(ui_object_proxy.attr("dismissable"), str)
        else ui_object_proxy.attr("dismissable")
    )
    ordered_dict["checkable"] = (
        ui_object_proxy.attr("checkable").strip()
        if isinstance(ui_object_proxy.attr("checkable"), str)
        else ui_object_proxy.attr("checkable")
    )
    ordered_dict["scale"] = (
        ui_object_proxy.attr("scale").strip()
        if isinstance(ui_object_proxy.attr("scale"), str)
        else ui_object_proxy.attr("scale")
    )
    ordered_dict["boundsInParent"] = (
        ui_object_proxy.attr("boundsInParent").strip()
        if isinstance(ui_object_proxy.attr("boundsInParent"), str)
        else ui_object_proxy.attr("boundsInParent")
    )
    ordered_dict["focusable"] = (
        ui_object_proxy.attr("focusable").strip()
        if isinstance(ui_object_proxy.attr("focusable"), str)
        else ui_object_proxy.attr("focusable")
    )
    ordered_dict["touchable"] = (
        ui_object_proxy.attr("touchable").strip()
        if isinstance(ui_object_proxy.attr("touchable"), str)
        else ui_object_proxy.attr("touchable")
    )
    ordered_dict["longClickable"] = (
        ui_object_proxy.attr("longClickable").strip()
        if isinstance(ui_object_proxy.attr("longClickable"), str)
        else ui_object_proxy.attr("longClickable")
    )
    ordered_dict["size"] = (
        ui_object_proxy.attr("size").strip()
        if isinstance(ui_object_proxy.attr("size"), str)
        else ui_object_proxy.attr("size")
    )
    ordered_dict["pos"] = (
        ui_object_proxy.attr("pos").strip()
        if isinstance(ui_object_proxy.attr("pos"), str)
        else ui_object_proxy.attr("pos")
    )
    ordered_dict["focused"] = (
        ui_object_proxy.attr("focused").strip()
        if isinstance(ui_object_proxy.attr("focused"), str)
        else ui_object_proxy.attr("focused")
    )
    ordered_dict["checked"] = (
        ui_object_proxy.attr("checked").strip()
        if isinstance(ui_object_proxy.attr("checked"), str)
        else ui_object_proxy.attr("checked")
    )
    ordered_dict["editalbe"] = (
        ui_object_proxy.attr("editalbe").strip()
        if isinstance(ui_object_proxy.attr("editalbe"), str)
        else ui_object_proxy.attr("editalbe")
    )
    ordered_dict["selected"] = (
        ui_object_proxy.attr("selected").strip()
        if isinstance(ui_object_proxy.attr("selected"), str)
        else ui_object_proxy.attr("selected")
    )
    ordered_dict["scrollable"] = (
        ui_object_proxy.attr("scrollable").strip()
        if isinstance(ui_object_proxy.attr("scrollable"), str)
        else ui_object_proxy.attr("scrollable")
    )
    return ordered_dict
