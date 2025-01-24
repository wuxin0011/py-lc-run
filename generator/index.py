import inspect
import re
import typing
from collections import deque

from generator.generator_template import CONSTRUCTOR_FLAG
from generator.parse_test_case import replace

GENER_INDEX_STR = 'generator.index.'
TREE_NODE_STR = 'generator.index.TreeNode'
LIST_NODE_STR = 'generator.index.ListNode'
LEFT_OPTIONAL = 'typing.Optional['
RIGHT_OPTIONAL = ']'
LEFT_OPTIONAL_RE = 'typing.Optional\['
RIGHT_OPTIONAL_RE = '\]'
LEFT_List = 'typing.List['
RIGHT_List = ']'
LEFT_List_RE = 'typing.List\['
RIGHT_List_RE = '\]'

MATCH_TYPE = f'str|int|bool|float|{TREE_NODE_STR}|{LIST_NODE_STR}'


def testcase(test=-1, start=1, end=0x3ffffff, use=True):
    '''
    参数说明
    :param use: 是否启用这个优先级最高默认启用 如果 False 表示这个包装器失效
    :param test:  默认为-1 表示 [start,end] 用例生效 ，如果需要测试某一个用力 直接使用 test=x ，这时 [start,end] 将会失效
    :param start: 在 test 不为 -1 情况下 测试案例从 start 开始
    :param end:   在 test 不为 -1 情况下 测试案例 end 结束
    :return:
    '''

    def wrapper(f):
        setattr(f, "start", max(1, start))
        setattr(f, "end", max(1, end))
        setattr(f, "use", use)
        setattr(f, "test", test)
        return f

    return wrapper


# ------------------------------------------------------引用类-----------------------------------------------
class TreeNode:
    def __init__(self, val=-1, left=None, right=None):
        self.left = left
        self.right = right
        self.val = val
    @staticmethod
    def create_tree(ls):
        if not ls or len(ls) == 0 or ls[0] is None or TreeNode.is_null_node(ls[0]):
            return None
        q = deque()
        root = TreeNode(int(ls[0]))
        q.append(root)
        i = 1
        while i < len(ls) and q:
            size = len(q)
            while size > 0 and i < len(ls):
                size -= 1
                node = q.popleft()
                if node is None:
                    continue
                if not TreeNode.is_null_node(ls[i]):
                    left = TreeNode(int(ls[i]))
                    node.left = left
                    q.append(left)
                i += 1
                if i >= len(ls):
                    break
                if not TreeNode.is_null_node(ls[i]):
                    right = TreeNode(int(ls[i]))
                    node.right = right
                    q.append(right)
                i += 1
        return root

    @staticmethod
    def deepEqual(result, expect):
        if result is expect:
            return True
        if result is None or expect is None:
            return False
        rq = []
        eq = []
        rq.append(result)
        eq.append(expect)
        while len(rq) > 0 and len(eq) > 0:
            s1 = len(rq)
            s2 = len(eq)
            if s1 != s2:
                return False
            size = s1
            while size > 0:
                size -= 1
                rNode = rq.pop(0)
                eNode = eq.pop(0)
                if rNode is None or eNode is None:
                    return False
                if rNode.val != eNode.val:
                    return False
                if rNode.left is not None:
                    rq.append(rNode.left)
                if rNode.right is not None:
                    rq.append(rNode.right)
                if eNode.left is not None:
                    eq.append(eNode.left)
                if eNode.right is not None:
                    eq.append(eNode.right)
        return len(rq) == len(eq)

    @staticmethod
    def is_null_node(s):
        return s is None or len(s) == 0 or s == "null" or s == "#"


class ListNode:
    def __init__(self, val=-1, next=None):
        self.next = next
        self.val = val

    @staticmethod
    def deepEqual(result, expect):
        if result is expect:
            return True
        if result is None or expect is None:
            return False
        while result is not None and expect is not None:
            if result.val != expect.val:
                return False
            result = result.next
            expect = expect.next
        if result is not expect:
            return False
        return True

    @staticmethod
    def create_ListNode(x):
        try:
            new_node = ListNode(-1, None)
            cur = new_node
            for v in x:
                if v == 'null' or v == '#' or v is None or v == 'None':
                    cur.next = None
                    break
                else:
                    cur.next = ListNode(int(v))
                    cur = cur.next
            return new_node.next
        except:
            return None

    @staticmethod
    def print_ListNode(node):
        s = ''
        s += '{'
        while node:
            s += str(node.val)
            if node.next:
                s += ","
            node = node.next
        s += "}"
        print(s)
        return s


# --------------------------------------------------字符串内容解析------------------------------------------


class ParseInput:
    @staticmethod
    def build_match(d, s=MATCH_TYPE, left=LEFT_List_RE, right='\]'):
        if len(s) == 0: return ''
        cur = ''
        ss = s.split('|')
        cur += '('
        for i, c in enumerate(ss):
            cur += '('
            cur += c
            cur += ')'
            if i != len(ss) - 1:
                cur += '|'
        cur += ')'
        m = cur
        ans = ''
        for _ in range(d):
            ans += left
        ans += m
        for _ in range(d):
            ans += right
        return ans

    @staticmethod
    def build_match_type(deep, t, left=LEFT_List, right=']'):
        ans = ''
        for _ in range(deep):
            ans += left
        ans += t
        for _ in range(deep):
            ans += right
        return ans
    @staticmethod
    def remove_outer(temp: str):
        fi = temp.find('[')
        la = temp.rfind(']')
        if fi == -1 or la == -1:
            return temp
        return temp[fi + 1:la]

    @staticmethod
    def handler_constructor_input_test(s: str):
        ans = []
        s = ParseInput.remove_outer(s)
        args = []
        d = 0
        cur = ''
        need_dot = False
        for c in s:
            if ParseInput.is_ignore_str(c):
                continue
            if c == ',' and d == 0:
                args = []
                cur = ''
                need_dot = True
                continue
            if c == '[':
                d += 1
                if d == 1:
                    args = []
                    cur = ''
                else:
                    cur += c
                need_dot = True
            elif c == ']':
                d -= 1
                if d == 0:
                    if need_dot:
                        if cur:
                            args.append(cur)
                        ans.append(args)
                        cur = ''
                        args = []
                elif d == 1:
                    if cur:
                        args.append(cur)
                    ans.append(args)
                    args = []
                    cur = ''
                    need_dot = False
                else:
                    cur += c
            elif c == ',':
                if d == 0:
                    pass
                elif d == 1:
                    args.append(cur)
                    cur = ''
                else:
                    cur += c
                need_dot = True
            else:
                cur += c
        return ans

    @staticmethod
    def handler_constructor_input_filter(s: str):
        s = ParseInput.remove_outer(s)
        if not s or len(s) == 0:
            return []
        args = []
        d = 0
        cur = ''
        for c in s:
            if ParseInput.is_ignore_str(c):
                continue
            if c == '[':
               d += 1
               cur += c
            elif c == ']':
                d -= 1
                cur += c
                if d == 0:
                    args.append(cur)
                    cur = ''
            elif c == ',':
                if d == 0:
                    if cur:
                        args.append(cur)
                        cur = ''
                else:
                    cur += c
            else:
                cur += c
        if cur:
            args.append(cur)
        return args
    @staticmethod
    def handler_constructor_input(s: str):
        ans = []
        s = ParseInput.remove_outer(s)
        d = 0
        cur = ''
        for c in s:
            if ParseInput.is_ignore_str(c):
                continue
            if c == '[':
                cur += c
                d += 1
                if d == 1:
                    pass
            elif c == ']':
                cur += c
                d -= 1
                if d == 0:
                    ans.append(ParseInput.handler_constructor_input_filter(cur))
                    cur = ''
            elif c == ',':
                if cur:
                    cur += c
                else:
                    cur = ''
            else:
                cur += c
        return ans

    @staticmethod
    def ignore_optional_or_type(s: str):
        return (s
                .replace("typing.", "")
                .replace("Optional", "")
                .replace("<class ", "")
                .replace(">", "")
                .replace("\'", "")
                .replace(GENER_INDEX_STR, "")
                )

    # 解析字符串相关
    @staticmethod
    def is_ignore_str(c: str):
        return c == '\n' or c == '\t' or c == '\f' or c == '\r' or c == ' '

    @staticmethod
    def parse_list(deep, input_str, type_name):
        # print(deep, input_str, type_name)

        input_str = ParseInput.parse_list_str(deep, input_str, type_name)
        only_name = ''
        if ListNode.__name__ in type_name or TreeNode.__name__ in type_name:
            only_name = type_name
        else:
            for name in MATCH_TYPE.split('|'):
                if ParseInput.build_match_type(deep, name) == type_name:
                    only_name = name
                    break
                if ParseInput.build_match_type(deep, name, left='List[') == type_name:
                    only_name = name
                    break
                if ParseInput.build_match_type(deep, t=name, left='typing.Optional[') == type_name:
                    only_name = name
                    break
        if len(only_name) == 0:
            return []
        return ParseInput.parse_one_type_array_list(deep, input_str, only_name)

    @staticmethod
    def parse_one_str_array_list(input_str: str):
        if len(input_str) == 0:
            return []
        deep = 0
        ans = []
        cur = ''
        for c in input_str:
            if ParseInput.is_ignore_str(c):
                continue
            if c == '[':
                deep += 1
            elif c == ']':
                deep -= 1
                if deep == 0:
                    ans.append(cur)
                    cur = ''
                    break
            elif c == ',':
                ans.append(cur)
                cur = ''
            else:
                cur += c
        return ans

    @staticmethod
    def parse_two_str_array_list(input_str: str):
        if len(input_str) == 0:
            return [[]]
        deep, ans, one, cur = 0, [], [], ''
        for c in input_str:
            if ParseInput.is_ignore_str(c):
                continue
            if c == '[':
                deep += 1
                if deep == 1:
                    pass
                elif deep == 2:
                    one = []
            elif c == ']':
                deep -= 1
                if deep == 1:
                    one.append(cur)
                    ans.append(one[:])
                    one = []
                    cur = ''
                elif deep == 0:
                    break
            elif c == ',':
                one.append(cur)
                cur = ''
            else:
                cur += c
        return ans

    @staticmethod
    def parse_three_str_array_list(input_str: str):
        if len(input_str) == 0:
            return [[[]]]
        deep, ans, two, one, cur = 0, [], [], [], ''
        for c in input_str:
            if ParseInput.is_ignore_str(c):
                continue
            if c == '[':
                deep += 1
                if deep == 1:
                    pass
                elif deep == 2:
                    two = []
                elif deep == 3:
                    one = []
            elif c == ']':
                deep -= 1
                if deep == 0:
                    break
                elif deep == 1:
                    ans.append(two)
                    two = []
                    cur = ''
                elif deep == 2:
                    one.append(cur)
                    cur = ''
                    two.append(one[:])
                    one = []
            elif c == ',':
                if deep == 1:
                    pass
                elif deep == 2:
                    pass
                elif deep == 3:
                    one.append(cur)
                    pass
                cur = ''
            else:
                cur += c
        return ans

    @staticmethod
    def parse_list_str(deep=1, input_str='[]', type_name='List[int]'):
        '''
        将输入list类型转换为对应list 默认转换为 list[str]
        :param deep:
        :param input_str:
        :param type_name:
        :return:
        '''
        typing_cnt = deep
        if typing_cnt == 1 or (ListNode.__name__ in type_name or TreeNode.__name__ in type_name):
            return ParseInput.parse_one_str_array_list(input_str)
        if typing_cnt == 2:
            return ParseInput.parse_two_str_array_list(input_str)
        if typing_cnt == 3:
            return ParseInput.parse_three_str_array_list(input_str)
        else:
            raise Exception(type_name + " not implements ! place implements")

    @staticmethod
    def parse_one_type_array_list(deep=0, input_str=typing.Any, name=''):
        '''
        递归处理列表
        :param deep:
        :param input_str:
        :param name:
        :return:
        '''
        if deep == 0:
            return []
        elif deep == 1:
            if len(input_str) == 0:
                return []
            ans = []
            if name is None:
                raise BaseException("type_name not allow None")

            if ListNode.__name__ in name:
                return ListNode.create_ListNode(input_str)
            elif TreeNode.__name__ in name:
                return TreeNode.create_tree(input_str)

            for x in input_str:
                if ParseInput.is_ignore_str(x): continue
                try:
                    v = None
                    if name == int.__name__:
                        v = int(x)
                    elif name == str.__name__:
                        v = str(x)
                    elif name == bool.__name__:
                        v = x.lower() == 'true'
                    elif name == float.__name__:
                        v = float(x)
                    else:
                        print("unknown type", name)
                    if v != None:
                        ans.append(v)
                except:
                    pass
            return ans
        else:
            return [ParseInput.parse_one_type_array_list(deep - 1, cur_str, name) for cur_str in input_str]


##################################################################################################


def parse_lc_type(**args):
    '''
    通过输入字符串，返回对应的数据类型
    :param args: 需要传入 args_type args_input
    :return:
    '''
    args_type = args['args_type']
    args_input = replace(args['args_input'])
    type_name = ParseInput.ignore_optional_or_type(str(args_type))
    if args_type is None:
        return args_input
    if type_name == "str":
        return args_input
    elif type_name == "int" or type_name == 'int':
        return int(args_input)
    elif type_name == "bool" or type_name == "bool":
        return args_input.lower() == 'true'
    elif type_name == "float" or type_name == "float":
        return float(args_input)
    elif type_name.find("[") != -1:
        # 这部分兼容上面处理方式
        # 这部分作旧版本兼容处理 => List[List[int]]

        is_tree_or_list_node = ListNode.__name__ in type_name or TreeNode.__name__ in type_name
        return ParseInput.parse_list(type_name.count("[") + int(is_tree_or_list_node), args_input, type_name)
    elif ListNode.__name__ in type_name or TreeNode.__name__ in type_name:
        return ParseInput.parse_list(1, args_input, type_name)
    raise BaseException("not implements:" + type_name)


class BaseUtil:
    @staticmethod
    def is_base_type(type_name):
        # 是否是基本类型
        bases = [int.__name__, bool.__name__, float.__name__]
        return type_name in bases

    @staticmethod
    def handler_list_or_node(deep, return_type_name, return_result, return_except):
        '''
        递归处理各级列表
        :param return_type_name: 类型名
        :param return_result: 返回结果
        :param return_except: 预期结果
        :param return_result: 全部相等
        :param deep: 深度
        :return:
        '''
        if return_result == return_except:
            return True

        if deep >= 1:
            if "List" in return_type_name:
                try:
                    if len(return_result) == len(return_except):
                        return all(BaseUtil.handler_list_or_node(deep - 1, return_type_name, return_result_node,
                                                                 return_except_node) for
                                   return_result_node, return_except_node in zip(return_result, return_except))
                    else:
                        return False
                except:
                    return False
            else:
                if ListNode.__name__ in return_type_name:
                    return ListNode.deepEqual(return_result, return_except)
                elif TreeNode.__name__ in return_type_name:
                    return TreeNode.deepEqual(return_result, return_except)
        return False


def parse_lc_input(**args):
    filename = args['filename']
    l = []
    with open(filename, mode='r+', encoding='utf-8') as f:
        l = f.readlines()
    s = [s.replace('\n', '') for s in l]
    return [x for x in s if len(x) > 0]


def get_arg_type_and_return_type_by_class(__class__, method_name='__init__'):
    '''
    获取返回类型
    类
    方法名
    '''
    if __class__ is None:
        raise Exception("class not allow null")
    if not hasattr(__class__, method_name):
        raise Exception("class not find method name :" + method_name)
    call_method = getattr(__class__, method_name)
    args_types = []
    sig = inspect.signature(call_method)
    for param_name, param in sig.parameters.items():
        if param.annotation != inspect.Parameter.empty:
            args_types.append(param.annotation)
    # 获取函数签名
    sig = inspect.signature(call_method)
    # 获取返回值类型提示
    return_type = sig.return_annotation if sig.return_annotation != inspect.Parameter.empty else None
    return args_types, return_type


def leetcode_run(**kwargs):
    '''
    调用函数入口
    :param class_name | __class__: 类
    :param method | __method__:  方法名
    :param filename | __file__: 文件路径
    :param __is_constructor__ : 是不是构造类
    :param filename | __file__: 文件路径
    :param kwargs:
    :return:
    '''
    __class__ = kwargs['__class__'] if "__class__" in kwargs else kwargs['class_name']
    __method__ = kwargs['__method__'] if "__method__" in kwargs else kwargs['method']
    __file__ = kwargs['__file__'] if "__file__" in kwargs else kwargs['filename']
    __is_constructor__ = True if "__is_constructor__" in kwargs else False
    __call_obj__ = kwargs['__call_obj__'] if "__call_obj__" in kwargs else None

    test_case_start = getattr(__class__, "start", 1)
    test_case_end = getattr(__class__, "end", 0x3ffffffff)
    test_case_use = getattr(__class__, "use", True)
    test_case_test = getattr(__class__, "test", -1)

    inputs = []
    if __is_constructor__:
        inputs = __file__
    else:
        if __file__:
            inputs = parse_lc_input(filename=__file__)
            if len(inputs) == 0:
                raise BaseException(f"输入文件{__file__}为空！ 请手动复制题目样例 ")

    if __method__ == CONSTRUCTOR_FLAG:
        method_names = None
        constructor_inputs = None
        read_cur_line = 1
        all_ok = True
        compare_times = 1
        for index in range(len(inputs)):
            if ParseInput.is_ignore_str(inputs[index]):
                continue
            if read_cur_line == 1:
                method_names = ParseInput.parse_one_str_array_list(inputs[index])
            elif read_cur_line == 2:
                constructor_inputs = ParseInput.handler_constructor_input(inputs[index])
                # 下面方法为测试阶段
                # constructor_inputs = ParseInput.handler_constructor_input_test(inputs[index])
            elif read_cur_line == 3:
                constructor_outputs = ParseInput.parse_one_str_array_list(inputs[index])
                # 处理完毕输入输出 开始构造对拍
                try:
                    if method_names and constructor_inputs and constructor_outputs and len(method_names) == len(
                            constructor_inputs) and len(constructor_inputs) == len(constructor_outputs):
                        # 初始化
                        args_types, return_type = get_arg_type_and_return_type_by_class(__class__, "__init__")
                        __call_obj__ = None
                        params = []
                        # 解析入参
                        for args_input, args_type in zip(constructor_inputs[0], args_types):
                            params.append(parse_lc_type(args_input=args_input, args_type=args_type))
                        __call_obj__ = __class__(*params)
                        ok = True
                        for temp_method_name,input_str,output_str in zip(method_names[1:], constructor_inputs[1:], constructor_outputs[1:]):
                            try:
                                v = leetcode_run(__class__=__class__, __method__=temp_method_name,__file__= [*input_str, output_str],__is_constructor__=True, __call_obj__=__call_obj__)
                                if not v:
                                    ok = False
                            except Exception as error:
                                print('call error',error,"method name = ",temp_method_name)
                                print()
                                ok = False
                        if not ok:
                            all_ok = False
                            print('run times',compare_times,'not ok')
                    else:
                        print('解析失败！参数格式错误！')
                        return False
                except Exception as e:
                    print(e)
                    return False
            if read_cur_line == 3:
                read_cur_line = 0
                compare_times += 1
            read_cur_line += 1
        if all_ok:
            print('Accepted!')
    else:

        args_types, return_type = get_arg_type_and_return_type_by_class(__class__, __method__)
        # 如果返回值是基本类型 需要处理成引用类型 基本类型如果没有返回值无法比较
        if not __is_constructor__ and return_type is None:
            for param_type in args_types:
                if not BaseUtil.is_base_type(param_type):
                    return_type = param_type
        i = 0

        compare_time = 1
        compare_result = []
        all_ok = True
        N = len(inputs)

        while i < N:
            if len(inputs[i]) == 0:
                i += 1
                continue
            params = []
            # 解析入参
            for arg in args_types:
                if i >= N:
                    raise BaseException("解析失败 ！ 输入越界 ！")
                # 必须读入结果 输入结果不能为空
                while ParseInput.is_ignore_str(inputs[i]): i += 1
                # 解析参数结果放入
                params.append(parse_lc_type(args_input=inputs[i], args_type=arg))
                i += 1
            # 不能输入None
            while i < N and ParseInput.is_ignore_str(inputs[i]): i += 1
            # 希望返回的结果
            return_except = parse_lc_type(args_input=inputs[i], args_type=return_type)

            if test_case_use:
                if test_case_test != -1 and compare_time != test_case_test or (
                        test_case_test == -1 and (compare_time > test_case_end or compare_time < test_case_start)):
                    i += 1
                    compare_time += 1
                    if (test_case_test != -1 and compare_time > test_case_test) or compare_time > test_case_end:
                        break
                    else:
                        continue

            call_run_method = getattr(__call_obj__ if __call_obj__ else __class__(), __method__)
            # 调用函数
            return_result = call_run_method(*params)

            # 处理返回值
            return_type_name = ParseInput.ignore_optional_or_type(str(return_type))
            contains_tree_node_list_node = (TreeNode.__name__ in return_type_name) or (ListNode.__name__ in return_type_name)
            if return_type is not None:
                is_ok = False
                deep = return_type_name.count('[')
                if contains_tree_node_list_node:
                    is_ok = BaseUtil.handler_list_or_node(deep=deep + 1, return_type_name=return_type_name,return_result=return_result, return_except=return_except)
                else:
                    is_ok = return_result == return_except
                    if not is_ok and deep > 0:
                        is_ok = BaseUtil.handler_list_or_node(deep=deep, return_type_name=return_type_name,return_result=return_result,return_except=return_except)
                compare_result.append((is_ok, return_result, return_except))
                if not is_ok:
                    print('result:', return_result if return_result != '' else '\"\"')
                    print('except:', return_except if return_except != '' else '\"\"')
                    if __is_constructor__:
                        print('method name :', __method__)
                    else:
                        print('compare times:', compare_time)
                    print()
                    all_ok = False
            else:
                if __is_constructor__:
                    return return_except == 'null'
                else:
                    print('返回类型为 none 请自行比较')
                    return False
            compare_time += 1
            i += 1

        if all_ok:
            if not __is_constructor__:
                print("Accepted!")
            return True
        return all_ok
