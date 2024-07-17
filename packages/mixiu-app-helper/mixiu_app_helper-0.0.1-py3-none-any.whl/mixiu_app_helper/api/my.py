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


class MyApi(object):

    @classmethod
    def get_my(cls, api: DeviceApi) -> UIObjectProxy:
        d_type = ""
        name = ""
        if api.platform == ANDROID_PLATFORM:
            d_type = "android.widget.TextView"
            name = "com.mixiu.com:id/tvTabItemText4"
        return api.get_po(d_type=d_type, name=name, text="我的")

    @classmethod
    def touch_my(cls, api: DeviceApi) -> bool:
        my_poco = cls.get_my(api=api)
        if my_poco.exists() is True:
            my_poco.click()
            return True
        return False
