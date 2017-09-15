#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
# class Reg_Rule:
#     VALUE = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
#     RECORD = r'^[\d\w\.]+$'
regRule = {
    'value': r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$',
    'record': r'^[\d\w\.\-]+$',
    'searchurl': r'^\/+api\/codesearch\/\?q\=(.*)&p\=.*$'
}
def reg_parser(string,rule):
    pattern = re.compile(regRule[rule])

    return pattern.match(string)