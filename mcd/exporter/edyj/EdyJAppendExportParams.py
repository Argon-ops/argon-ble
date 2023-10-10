

import bpy
import mathutils
import math


def Append(params, extra_export_settings):
    for extraKey, extraVal in extra_export_settings.items():
        if extraKey in params:
            print(F"WARNING: overwriting param: {extraKey} : with existing value: {params[extraKey]}")
        params[extraKey] = extraVal