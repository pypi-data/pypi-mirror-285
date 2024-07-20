# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  airtest-helper
# FileName:     poco.py
# Description:  TODO
# Author:       zhouhanlin
# CreateDate:   2024/07/17
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from collections import OrderedDict
from poco.proxy import UIObjectProxy


def get_ui_object_proxy_attr(ui_object_proxy: UIObjectProxy) -> OrderedDict:
    ordered_dict = OrderedDict()
    # UI 元素的类型
    ordered_dict["type"] = (
        ui_object_proxy.attr("type").strip()
        if isinstance(ui_object_proxy.attr("type"), str)
        else ui_object_proxy.attr("type")
    )
    # UI 元素的名字，也称之该元素的唯一标识符（resource ID），通常用于在代码中查找和引用这个元素
    ordered_dict["name"] = (
        ui_object_proxy.attr("name").strip()
        if isinstance(ui_object_proxy.attr("name"), str)
        else ui_object_proxy.attr("name")
    )
    # UI 元素中显示的文本内容
    ordered_dict["text"] = (
        ui_object_proxy.attr("text").strip()
        if isinstance(ui_object_proxy.attr("text"), str)
        else ui_object_proxy.attr("text")
    )
    # 指示 UI 元素描述
    ordered_dict["desc"] = (
        ui_object_proxy.attr("desc").strip()
        if isinstance(ui_object_proxy.attr("desc"), str)
        else ui_object_proxy.attr("desc")
    )
    # 指示 UI 元素是否处于启用状态。启用状态下的元素可以被用户操作
    ordered_dict["enabled"] = ui_object_proxy.attr("enabled")
    # 指示 UI 元素是否可见
    ordered_dict["visible"] = ui_object_proxy.attr("visible")
    # 该元素的资源 ID，与 name 相同，只是以字节形式表示。
    ordered_dict["resourceId"] = (
        ui_object_proxy.attr("resourceId").decode('utf-8').strip()
        if isinstance(ui_object_proxy.attr("resourceId"), bytes)
        else ui_object_proxy.attr("resourceId")
    )
    # 描述 UI 元素在 z 轴上的排序，global 是全局 z 轴顺序，local 是局部 z 轴顺序。
    ordered_dict["zOrders"] = ui_object_proxy.attr("zOrders")
    # UI 元素所属应用程序的包名
    ordered_dict["package"] = (
        ui_object_proxy.attr("package").decode('utf-8').strip()
        if isinstance(ui_object_proxy.attr("package"), bytes)
        else ui_object_proxy.attr("package")
    )
    # UI 元素的锚点位置，一般用来定位元素的中心
    ordered_dict["anchorPoint"] = ui_object_proxy.attr("anchorPoint")
    # 指示 UI 元素是否可以被关闭或解散
    ordered_dict["dismissable"] = ui_object_proxy.attr("dismissable")
    # 指示 UI 元素是否可被勾选
    ordered_dict["checkable"] = ui_object_proxy.attr("checkable")
    # UI 元素的缩放比例
    ordered_dict["scale"] = ui_object_proxy.attr("scale")
    # UI 元素在父元素中的边界大小，用百分比表示
    ordered_dict["boundsInParent"] = ui_object_proxy.attr("boundsInParent")
    # 指示 UI 元素是否可以获得焦点
    ordered_dict["focusable"] = ui_object_proxy.attr("focusable")
    # 指示 UI 元素是否可以被触摸操作
    ordered_dict["touchable"] = ui_object_proxy.attr("touchable")
    # 指示 UI 元素是否支持长按操作
    ordered_dict["longClickable"] = ui_object_proxy.attr("longClickable")
    # UI 元素的尺寸，用百分比表示
    ordered_dict["size"] = ui_object_proxy.attr("size")
    # UI 元素在父元素中的位置，用百分比表示
    ordered_dict["pos"] = ui_object_proxy.attr("pos")
    # 指示 UI 元素是否当前具有焦点
    ordered_dict["focused"] = ui_object_proxy.attr("focused")
    # 指示 UI 元素是否处于被勾选状态
    ordered_dict["checked"] = ui_object_proxy.attr("checked")
    # 指示 UI 元素是否可编辑
    ordered_dict["editalbe"] = ui_object_proxy.attr("editalbe")
    # 指示 UI 元素是否处于被选中状态
    ordered_dict["selected"] = ui_object_proxy.attr("selected")
    # 指示 UI 元素是否可以滚动
    ordered_dict["scrollable"] = ui_object_proxy.attr("scrollable")
    return ordered_dict
