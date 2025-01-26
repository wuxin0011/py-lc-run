ZH_INPUT_FLAG = '输入'
ZH_OUTPUT_FLAG = '输出'
ZH_EXPLAIN_FLAG = '解释'
ZH_TIP_FLAG = '提示'
EN_INPUT_FLAG = 'Input'
EN_OUTPUT_FLAG = 'Output'
EN_EXPLAIN_FLAG = 'Explanation'
EN_EXPLAIN_FLAG1 = 'Explaination'
EN_TIP_FLAG = 'tips'
ERROR_TEST_CASE_FLAG = 'this_case_parse_error'


def replace(s: str, newLine=True,remove_space = False):
    try:
        s = s.replace(ZH_INPUT_FLAG, '')
        s = s.replace(ZH_OUTPUT_FLAG, '')
        s = s.replace(ZH_EXPLAIN_FLAG, '')
        s = s.replace(ZH_TIP_FLAG, '')
        s = s.replace(EN_INPUT_FLAG, '')
        s = s.replace(EN_OUTPUT_FLAG, '')
        s = s.replace(EN_EXPLAIN_FLAG, '')
        s = s.replace(EN_EXPLAIN_FLAG, '')
        s = s.replace(EN_TIP_FLAG, '')
        s = s.replace('<span class="example-io">', '')
        s = s.replace('<span class="example-block">', '')
        s = s.replace('<span class="example">', '')
        s = s.replace('&quot;', '')
        s = s.replace('<span>', '')
        s = s.replace('</span>', '')
        s = s.replace('<strong>', '').replace('</strong>', '')
        s = s.replace('<p>', '').replace('</p>', '')
        s = s.replace('<b>', '').replace('</b>', '')
        s = s.replace('<br>', '').replace('</br>', '')
        s = s.replace('<h>', '').replace('</h>', '')
        s = s.replace('<code>', '').replace('</code>', '')
        s = s.replace('<pre>', '').replace('</pre>', '')
        if newLine:
            s = s.replace('\n', '')
        s = s.replace('\\n', '')
        s = s.replace('\\\"', '')
        s = s.replace('\"', '')
        s = s.replace('\'', '')
        s = s.replace('>', '')
        s = s.replace('<', '')
        s = s.replace('`', '')
        s = s.replace(':', '')
        s = s.replace('：', '')
        s = s.replace(';', '')
        if remove_space:
            s = s.replace(' ','')
        else:
            # 过滤案例两边的多余的 ' '
            n = len(s)
            fi = -1
            la = -1
            for i in range(n):
                if s[i] != ' ':
                    fi = i
                    break
            for i in range(n - 1, -1, -1):
                if s[i] != ' ':
                    la = i
                    break
            if 0 <= fi <= la:
                return s[fi:la + 1]
        return s if s else " "
    except:
        return s


def handler_input_example(s='', is_example_test_case=False, is_ZH=False):
    if not s:
        return ''
    if is_example_test_case:
        return s.split("\n")
    d = 0
    cur = ''
    input_example = []
    if is_ZH:
        print("中文输入解析暂未实现")
    else:
        if isinstance(s, str):
            s = s.replace("\\\"", "")
            for c in s:
                if c == '\"' or c == '\'':
                    d += 1
                    if d % 2 == 1:
                        cur = ''
                    else:
                        input_example.append(cur.replace('\\n', '\n'))
                        cur = ''
                else:
                    if d % 2 == 0 and c == ',' and c:
                        cur = ''
                    else:
                        cur += c
        else:
            try:
                for c in s:
                    input_example.append(c)
            except:
                pass

    return input_example


def match_flag_words(text: str, flags=None):
    '''
    由于匹配flag内容不同，有时候会改变，因此需要加入多模式匹配
    '''
    if flags is None:
        flags = []
    for flag in flags:
        i = text.find(flag)
        if i != -1:
            return [i, flag, text.count(flag)]
    return [-1, ERROR_TEST_CASE_FLAG, 0]


def parse_case_new(html, is_ZH=False):
    from bs4 import BeautifulSoup
    input_str_flags = [ZH_INPUT_FLAG] if is_ZH else [EN_INPUT_FLAG, EN_INPUT_FLAG.lower()]
    out_str_flags = [ZH_OUTPUT_FLAG] if is_ZH else [EN_OUTPUT_FLAG, EN_OUTPUT_FLAG.lower()]
    explain_str_flags = [ZH_EXPLAIN_FLAG] if is_ZH else [EN_EXPLAIN_FLAG, EN_EXPLAIN_FLAG1, EN_EXPLAIN_FLAG.lower(),
                                                         EN_EXPLAIN_FLAG1.lower()]
    tip_str_flags = [ZH_TIP_FLAG] if is_ZH else [EN_TIP_FLAG, EN_TIP_FLAG.lower()]
    try:
        soup = BeautifulSoup(html, 'lxml')
        outputs = []
        flag_start = "<pre>"
        flag_end = "</pre>"
        start_cnt = html.count(flag_start)
        end_cnt = html.count(flag_end)
        if start_cnt == end_cnt and end_cnt > 0:
            pres = soup.select('pre')
            for pre in pres:
                i, out_str_flag, _ = match_flag_words(pre.text, out_str_flags)
                j, explain_str_flag, _ = match_flag_words(pre.text, explain_str_flags)
                if i != -1:
                    if j != -1 and i < j:
                        outputs.append(replace(pre.text[i + len(out_str_flag):j]))
                    else:
                        outputs.append(replace(pre.text[i + len(out_str_flag):]))
                else:
                    outputs.append(ERROR_TEST_CASE_FLAG)
        else:
            divs = soup.select('[class="example-block"]')
            if divs:
                for element in divs:
                    if not element: continue
                    i, out_str_flag, _ = match_flag_words(element.text, out_str_flags)
                    j, explain_str_flag, _ = match_flag_words(element.text, explain_str_flags)
                    k, tip_str_flag, _ = match_flag_words(element.text, tip_str_flags)
                    if 0 < i < j:
                        outputs.append(replace(element.text[i + len(out_str_flag):j]))
                    elif 0 < i < k:
                        outputs.append(replace(element.text[i + len(out_str_flag):k - 4]))
                    elif 0 < i and k == -1:
                        outputs.append(replace(element.text[i + len(out_str_flag)]))
                    else:
                        tags = element.select('[class="example-io"]')
                        if tags:
                            outputs.append(replace(tags[-1].text))
                        else:
                            tags = element.select('[class="example"]')
                            if tags:
                                outputs.append(replace(tags[-1].text))
                            else:
                                outputs.append(ERROR_TEST_CASE_FLAG)
            else:
                # 最后的兼容
                _, input_str_flag, in_cnt = match_flag_words(html, input_str_flags)
                _, out_str_flag, out_cnt = match_flag_words(html, out_str_flags)
                _, explain_str_flag, explain_cnt = match_flag_words(html, explain_str_flags)
                if out_cnt != 0:
                    j, out_str_flag, _ = match_flag_words(html, out_str_flags)
                    k, explain_str_flag, _ = match_flag_words(html, explain_str_flags)
                    while 0 < j < k:
                        outputs.append(replace(html[j + len(out_str_flag):k]))
                        html = html[k + len(explain_str_flag):]
                        j, out_str_flag, _ = match_flag_words(html, out_str_flags)
                        k, explain_str_flag, _ = match_flag_words(html, explain_str_flags)
                    tip_index, tip_str_flag, _ = match_flag_words(html, tip_str_flags)
                    if explain_cnt > 0 and explain_cnt != out_cnt and html.find(
                            explain_str_flag) == -1 and tip_index != -1:
                        j, out_str_flag, _ = match_flag_words(html, out_str_flags)
                        k, tip_str_flag, _ = match_flag_words(html, tip_str_flags)
                        while 0 < j < k:
                            for x in range(4, -1, -1):
                                if k - x < j:
                                    continue
                                outputs.append(replace(html[j + len(out_str_flag):k - x]))
                                html = html[k + len(tip_str_flag):]
                                j, out_str_flag, _ = match_flag_words(html, out_str_flags)
                                k, tip_str_flag, _ = match_flag_words(html, tip_str_flags)
                                break

        return outputs
    except Exception as e:
        print('parse output testcase error', e)
        return []


def parse_case(html_str, exampleTestcaseList, is_example_test_case=False, is_ZH=False):
    all_test_cases = []
    try:
        handler_input = handler_input_example(exampleTestcaseList, is_example_test_case, is_ZH)
        outputs = parse_case_new(html_str[:], is_ZH)
        out_len = len(outputs)
        n = len(handler_input)
        if out_len == 0 or n % out_len != 0:
            print('案例解析失败！请手动copy😥')
            return '\n'.join([replace(s) for s in handler_input])
        group = n // out_len
        k = 0
        j = 0
        for i in range(n):
            k += 1
            all_test_cases.append(replace(handler_input[i], False))
            all_test_cases.append("\n")
            if group == k:
                all_test_cases.append(replace(outputs[j], False))
                if i != n - 1:
                    all_test_cases.append("\n\n")
                if outputs[j].find(ERROR_TEST_CASE_FLAG) != -1:
                    print(f'第 {j + 1} 案例解析错误 请手动copy😥')
                k = 0
                j += 1

        return ''.join(all_test_cases)
    except Exception as e:
        print(f"案例解析错误: {e}")
        return ''.join(all_test_cases)
