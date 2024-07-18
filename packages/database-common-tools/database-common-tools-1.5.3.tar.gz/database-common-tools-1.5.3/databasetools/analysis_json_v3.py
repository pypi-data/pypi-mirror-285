# -*- coding: utf-8 -*-

import jsonpath
import json


##################################################
# functions field resolution
##################################################

def dump_doc_field_array(doc, path, value):
    values = jsonpath.jsonpath(doc, path)
    status = False
    if isinstance(values, list):
        status = True if 0 < len(values) else False
        return status, values
    return status, value


def dump_doc_field_object(doc, path, value):
    values = jsonpath.jsonpath(doc, path)
    status = False
    if isinstance(values, list):
        values = values[0]
        if isinstance(values, dict):
            status = True
            return status, values
    return status, value


def dump_doc_field_str(doc, path, value):
    values = jsonpath.jsonpath(doc, path)
    status = False
    if isinstance(values, list) and 1 == len(values):
        if isinstance(values[0], float) or \
                isinstance(values[0], int) or \
                isinstance(values[0], str):
            status = True if 0 < len(values) else False
            return status, str(values[0])
    return status, value


def dump_doc_field_type(doc, path, value, toType):
    values = jsonpath.jsonpath(doc, path)
    status = False
    if isinstance(values, list) and 1 == len(values):
        if isinstance(values[0], float) or \
                isinstance(values[0], int) or \
                isinstance(values[0], str):
            status = True if 0 < len(values) else False
            try:
                return status, toType(values[0])
            except Exception as e:
                return status, value
    return status, value

# 针对是一行的数据 转换为数组存储情况
def dump_doc_field_type2array(doc, path, value,toType):
    values = jsonpath.jsonpath(doc, path)
    status = False
    if isinstance(values, list) and 1 == len(values):
        if isinstance(values[0], float) or \
                isinstance(values[0], int) or \
                isinstance(values[0], str):
            array = [toType(x) for x in values[0].split(',') if x.strip()]
            status = True if 0 < len(values) else False
            return status, array
    return status, value


if __name__ == '__main__':
    doc = {
		"id" : "hi2234586312",
		"aspect" : "0.67",
		"width" : 3840,
		"height" : 5760,
		"image_type" : "photo",
		"race" : [],
		"person_num" : 1,
		"age" : ["20s"],
		"gender" : "female",
		"category_ids" : "",
		"preview260_url" : "provider_image/preview260/2234586312.jpg",
		"id" : 949735,
		"real_name" : "赵旭"
	}
    print(dump_doc_field_type2array(doc,'$.category_ids',[],int))

    print(jsonpath.jsonpath(doc, '$.category_ids'))
