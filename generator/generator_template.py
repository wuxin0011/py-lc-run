import os

SOLUTION_CLASS_NAME = 'Solution'
NOT_FOUND_METHOD = "NOT_FIND_RUN_METHOD_NAME"
CONSTRUCTOR_FLAG = "__constructor__"
TEST_CASE_DIR = "__test_case__"


def find_run_method_name(code: str):
    '''
    找到执行函数的方法名
    :param s:
    :return: (classname,methodname)
    '''

    if len(code) == 0:
        return SOLUTION_CLASS_NAME, NOT_FOUND_METHOD

    k = code.find(SOLUTION_CLASS_NAME)
    class_name = SOLUTION_CLASS_NAME
    if k != -1:
        cur_code = code[k:]
        i = cur_code.find('def')
        j = cur_code.find('self')
        if i > j:
            return SOLUTION_CLASS_NAME, NOT_FOUND_METHOD
        method_name = cur_code[i:j].replace('def', '').replace(' ', '').replace('(', '')
        return SOLUTION_CLASS_NAME, method_name
    else:
        i = code.find("class")
        j = code.find(":")
        if 0 <= i < j:
            class_name = code[i:j].replace('class', '').replace(' ', '')
            method_name = CONSTRUCTOR_FLAG
        else:
            method_name = NOT_FOUND_METHOD
        return class_name, method_name


def handler_return_type(code):
    so_index = code.find(SOLUTION_CLASS_NAME)
    if so_index != -1:
        pre = code[:so_index + len(SOLUTION_CLASS_NAME) + 2]
        i = pre.rfind("class")
        if i != -1:
            pre = pre[i:]
        suf = code[2 + len(SOLUTION_CLASS_NAME) + so_index:]
    else:
        j = code.find("__init__")
        i = -1
        if j != -1:
            i = j
        if i == -1:
            i = code.find("def")
        if i == -1:
            return code
        pre = code[:i]
        suf = code[i:]
    def_cnt = suf.count("def")
    suf = suf.replace(':\n', ":\n        pass\n", def_cnt)
    pass_cnt = suf.count("pass")
    if pass_cnt == 0:
        suf = suf + "\n        pass\n"
    return pre + suf


def default_template(username='', access_url=''):
    '''
    模板头部
    :param username:
    :param access_url:
    :return:
    '''
    template_header = f'''
# ------------------------template auto generator---------------------------------------
from generator.index import leetcode_run,ListNode,TreeNode,testcase
import os

# -----------------------------------------------------------------

from itertools import *
import math
from heapq import heappop, heappush, heapify, heappushpop, heapreplace
from typing import *
from collections import Counter, defaultdict, deque
from bisect import bisect_left, bisect_right
# from sortedcontainers import SortedList, SortedSet, SortedKeyList, SortedItemsView, SortedKeysView, SortedValuesView
from functools import cache, cmp_to_key, lru_cache
# -----------------------------------------------------------------

# @author: {username}
# @access_url: {access_url}\n\n


inf = math.inf
fmax = lambda x, y: x if x > y else y
fmin = lambda x, y: x if x < y else y
MOD = 10 ** 9 + 7

# @testcase(test=-1,start= 1,end = 0x3ffffff,use = True)
'''
    return template_header


def default_end(class_name='Solution', method="method", input_file='in.txt'):
    '''
    模板结尾
    :param class_name:
    :param method:
    :param input_file:
    :return:
    '''
    template_str = f'''\n
if __name__ == '__main__':
    leetcode_run(__class__={class_name}, __method__="{method}", __file__=os.getcwd() +"\\\\{TEST_CASE_DIR}\\\\{input_file}")
'''
    return template_str


def generator_template(code='', py_file='a.py', input_file='a.in', test_case='', username='', access_url=''):
    '''
    模板生成
    :param code: 代码块
    :param py_file: py 文件
    :param input_file:  对拍文件
    :param test_case: 测试案例
    :param username: 用户名
    :param access_url: 题目链接
    :return:
    '''

    class_name, method_name = find_run_method_name(code)
    py_content = ''
    py_content += default_template(username=username, access_url=access_url)
    py_content += handler_return_type(code)
    py_file_dir_name = os.path.dirname(py_file)
    input_file_dir_name = os.path.dirname(input_file)

    if not os.path.exists(py_file_dir_name):
        os.makedirs(py_file_dir_name)
    if not os.path.exists(input_file_dir_name):
        os.makedirs(input_file_dir_name)

    py_content += default_end(class_name=class_name, method=method_name,
                              input_file=os.path.basename(input_file))
    try:

        # print(question_info)
        if not os.path.exists(py_file):
            with open(py_file, mode='w+', encoding='utf-8') as f:
                f.write(py_content)
                f.flush()
                f.close()
        with open(input_file, mode='w+', encoding='utf-8') as f:
            f.write(test_case)
            f.flush()
            f.close()
        print('template create success: ', py_file, "\n")
    except Exception as e:
        print('generator_template error:', e)
