ZH_INPUT_FLAG = '输入'
ZH_OUTPUT_FLAG = '输出'
ZH_EXPLAIN_FLAG = '解释'
ZH_TIP_FLAG = '提示'
EN_INPUT_FLAG = 'Input'
EN_OUTPUT_FLAG = 'Output'
EN_EXPLAIN_FLAG = 'Explanation'
EN_TIP_FLAG = 'tips'
ERROR_TEST_CASE_FLAG = 'this_case_parse_error'


def replace(s: str,newLine = True):
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
    s = s.replace(' ', '')
    s = s.replace('`', '')
    s = s.replace(':', '')
    s = s.replace('：', '')
    s = s.replace(';', '')
    return s if s else " "


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



def parse_case_new(html, is_ZH=False):
    from bs4 import BeautifulSoup
    input_str_flag = ZH_INPUT_FLAG if is_ZH else EN_INPUT_FLAG
    out_str_flag = ZH_OUTPUT_FLAG if is_ZH else EN_OUTPUT_FLAG
    explain_str_flag = ZH_EXPLAIN_FLAG if is_ZH else EN_EXPLAIN_FLAG
    tip_str_flag = ZH_TIP_FLAG if is_ZH else EN_TIP_FLAG
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
                i = pre.text.find(out_str_flag)
                j = pre.text.find(explain_str_flag)
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
                in_cnt = html.count(input_str_flag)
                out_cnt = html.count(out_str_flag)
                explain_cnt = html.count(explain_str_flag)
                if out_cnt != 0:
                    j = html.find(out_str_flag)
                    k = html.find(explain_str_flag)
                    while 0 < j < k:
                        outputs.append(replace(html[j + len(out_str_flag):k]))
                        html = html[k + len(explain_str_flag):]
                        j = html.find(out_str_flag)
                        k = html.find(explain_str_flag)
                    if explain_cnt > 0 and explain_cnt != out_cnt and html.find(explain_str_flag) == -1 and html.find(
                            tip_str_flag) != -1:
                        j = html.find(out_str_flag)
                        k = html.find(tip_str_flag)
                        while 0 < j < k:
                            for x in range(4, -1, -1):
                                if k - x < j: continue
                                outputs.append(replace(html[j + len(out_str_flag):k - x]))
                                html = html[k + len(tip_str_flag):]
                                j = html.find(out_str_flag)
                                k = html.find(tip_str_flag)
                                break

        return outputs
    except Exception as e:
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
            return '\n'.join(handler_input)
        group = n // out_len
        k = 0
        j = 0
        for i in range(n):
            k += 1
            all_test_cases.append(replace(handler_input[i],False))
            all_test_cases.append("\n")
            if group == k:
                all_test_cases.append(replace(outputs[j],False))
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
