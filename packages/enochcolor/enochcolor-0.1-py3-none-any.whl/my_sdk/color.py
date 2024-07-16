# !/usr/bin/env python3.9
# -*- coding:utf-8 -*-
# ---------------------------------------------------------
# @Time    : 2024/07/15 17:42
# @Author  : huwenxue
# @FileName: color.py
# ---------------------------------------------------------
# Common reference
import colour
# ---------------------------------------------------------
def delta_E(st,sp):
   delta_e=colour.delta_E(st,sp)
   return delta_e
