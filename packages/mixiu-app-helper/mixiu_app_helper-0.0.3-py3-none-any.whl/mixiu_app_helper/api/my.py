# -*- coding: utf-8 -*-
"""
# ---------------------------------------------------------------------------------------------------------
# ProjectName:  mixiu-app-helper
# FileName:     my.py
# Description:  TODO
# Author:       zhouhanlin
# CreateDate:   2024/07/16
# Copyright ©2011-2024. Hunan xxxxxxx Company limited. All rights reserved.
# ---------------------------------------------------------------------------------------------------------
"""
from poco.proxy import UIObjectProxy
from airtest_helper.core import DeviceApi
from airtest_helper.platform import ANDROID_PLATFORM


class MyApi(DeviceApi):

    def get_my(self) -> UIObjectProxy:
        d_type = ""
        name = ""
        if self.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.mixiu.com:id/tvTabItemText4"
        return self.get_po(d_type=d_type, name=name, text="我的")

    def touch_my(self) -> bool:
        my_poco = self.get_my()
        if my_poco.exists() is True:
            my_poco.click()
            return True
        return False

    def get_current_uid(self) -> str:
        poco = self.get_po(
            d_type="android.widget.LinearLayout", name="com.mixiu.com:id/llUidAddress"
        ).child(name="android.widget.TextView")[1]
        if poco.exists():
            return poco.get_text().strip()
        return ""
