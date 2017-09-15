#!/usr/bin/env python
# -*- coding: utf-8 -*-

class PageResult(object):
    def __init__(self, query, take=20, skip=0):
        self.data_list = query.limit(take).offset(skip).all()
        self.total_count = query.count()
        self.data_skip = skip
        self.data_take = take

    def to_dict(self,data2dict_func):
        return {
            "dataList": [data2dict_func(data) for data in self.data_list],
            "totalCount": self.total_count,
            "dataTake": self.data_take,
            "dataSkip": self.data_skip
        }