import json
import math
import os
import re
import time

import requests

from generator.generator_template import generator_template, TEST_CASE_DIR
from generator.parse_test_case import parse_case

applicationJSON = "application/json"
applicationHTML = "text/html; charset=utf-8"
LC_PREFIX = "https://leetcode.cn"
# LC_PREFIX = "https://leetcode.com"
LC_PROBLEM_PREFIX = LC_PREFIX + "/problems"
LC_LOGIN = LC_PREFIX + "/accounts/login/"
graphql = LC_PREFIX + "/graphql/"
API_PREFIX = LC_PREFIX + "/contest/api/info/"

# // 经典模式url
LC_CLASS_THEME_PREFIX = LC_PREFIX + "/classic/problems"





def get_header():
    cookie_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../cookie.txt")
    # print(cookie_file_path)
    try:
        if not os.path.exists(cookie_file_path):
            with open(cookie_file_path, mode='w+', encoding='utf-8') as f:
                f.write("")
            raise Exception('cookie文件已创建请填写cookie')
        file = open(cookie_file_path, mode='r+', encoding='utf-8')
        cxk = file.read()
        file.close()
        h = {
            'Host': LC_PREFIX.replace("https://", ''),
            'Referer': LC_PREFIX,
            'Origin': LC_PREFIX + '/',
            'Connection': 'keep-alive',
            'Cookie': cxk,
            'Accept': '*/*',
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            'Sec-Ch-Ua-Platform': 'Windows',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
            'Accept-Language': 'zh-CN,zh;q:0.9,en;q:0.8,en-GB;q:0.7,en-US;q:0.6',
            'Cache-Control': 'max-age:3600'
        }

        return h
    except Exception as e:
        print(e)
        return {}


def response_post_default(json_str=None, contentType=applicationJSON, method='POST', url=graphql):
    req_header = {}
    for k, v in get_header().items():
        req_header[k] = v
    req_header['Content-Type'] = contentType
    if json_str:
        json_str = json.loads(json.dumps(json_str))
    return requests.request(url=url, verify=True, timeout=20000, method=method, headers=req_header,
                            json=json_str)


def custom_url_response(url, method='POST', data='', contentType=None):
    req_header = {}
    for k, v in get_header().items():
        req_header[k] = v
    req_header['Content-Type'] = contentType if contentType else applicationJSON
    return requests.request(url=url, timeout=20000, method=method, headers=req_header, data=data)


def get_user_name():
    user_info = {
        "variables": {},
        "query": "\n        query globalData {\n          userStatus {\n            isSignedIn\n            isPremium\n            username\n            realName\n            avatar\n            userSlug\n            isAdmin\n            checkedInToday\n            useTranslation\n            premiumExpiredAt\n            isTranslator\n            isSuperuser\n            isPhoneVerified\n            isVerified\n          }\n          jobsMyCompany {\n            nameSlug\n          }\n          commonNojPermissionTypes\n        }\n      "
    }
    try:
        res = response_post_default(user_info)
        if res.status_code == 200:
            s = json.loads(res.text)
            username = s['data']['userStatus']['username']
            return username
    except:
        pass
    return None


def contestQuestion(contestSlug, questionSlug):
    json_str = {
        "query": "\n    query contestQuestion($contestSlug: String, $questionSlug: String) {\n  contestDetail(contestSlug: $contestSlug) {\n    startTime\n    duration\n    titleSlug\n    failCount\n    enableContestDynamicLayout\n    isDynamicLayout\n    hasCompletedContest\n    isVirtualContest\n  }\n  contestQuestion(contestSlug: $contestSlug, questionSlug: $questionSlug) {\n    totalAc\n    totalSubmission\n    totalTriedUser\n    totalAcUser\n    languageList {\n      id\n      name\n      verboseName\n    }\n    submittableLanguageList {\n      id\n      name\n      verboseName\n    }\n    question {\n      status\n      questionId\n      questionFrontendId\n      enableRunCode\n      enableSubmit\n      enableTestMode\n      metaData\n      title\n      titleSlug\n      difficulty\n      categoryTitle\n      codeSnippets {\n        code\n        lang\n        langSlug\n      }\n      exampleTestcaseList\n      canSeeQuestion\n      envInfo\n      content\n      translatedTitle\n      translatedContent\n    }\n  }\n}\n    ",
        "variables": {
            "contestSlug": f"{contestSlug}",
            "questionSlug": f"{questionSlug}"
        },
        "operationName": "contestQuestion"
    }
    try:
        r = response_post_default(json_str=json_str, contentType=applicationJSON)
        if r.status_code == 200:
            cur_json = json.loads(r.text)
            return cur_json['data']['contestQuestion']['question']
        else:
            return {}
    except:
        return {}


def handler_question_info(question_info={}, name='', dir_prefix='', username='', access_url=''):
    if question_info is None:
        question_info = {}
    if "codeSnippets" not in question_info:
        raise Exception("解析失败！请检查cookie是否过期!!!")
    try:
        code = ''
        for s in question_info['codeSnippets']:
            if "lang" in s and s['lang'] == 'Python3':
                code = s['code']
                break
        example = ''
        is_example_test_case = False
        if "exampleTestcases" in question_info:
            example = question_info['exampleTestcases']
            is_example_test_case = True
        elif "exampleTestcaseList" in question_info:
            example = question_info['exampleTestcaseList']
            is_example_test_case = False
        elif "jsonExampleTestcases" in question_info:
            example = question_info['jsonExampleTestcases']
            is_example_test_case = False

        content = question_info['content']
        is_ZH = False
        if "Please switch to Chinese" in question_info['content']:
            # print(question_info)
            if "translatedContent" in question_info:
                content = question_info["translatedContent"]
                is_ZH = True

        # 解析案例
        test_case = parse_case(content, example, is_example_test_case=is_example_test_case,
                               is_ZH=is_ZH)
        if not test_case:
            pass
        if code:
            generator_template(code=code, py_file=os.path.join(dir_prefix,f"{name}.py"),
                               input_file=os.path.join(dir_prefix,TEST_CASE_DIR,f"{name}.txt"), test_case=test_case,
                               username=username,
                               access_url=access_url)
    except Exception as e:
        print(e)


def get_title_slug_by_url(url: str):
    try:
        if LC_PREFIX in url:
            return url.split("problems/")[-1].split("/")[0]
    except:
        pass
    return url


def parse_problem_by_url(url='', pre_dir=''):
    '''
    :param url: 请求路径 这个url只要包含题目 title_slug 即可
    :param pre_dir: 指定生成文件目录前缀
    :return:
    '''
    from bs4 import BeautifulSoup
    username = get_user_name()
    if username is None or not username:
        raise BaseException("请检查Cookies是否过期！")
    try:
        url = f'{LC_PROBLEM_PREFIX}/{get_title_slug_by_url(url)}'
        print("access_url", url)
        h = custom_url_response(
            url=url,
            method='get', contentType=applicationHTML)
        if h.status_code != 200:
            print('响应失败！')
            return

        cur_path = os.path.join(os.getcwd(), pre_dir)
        if not os.path.exists(cur_path):
            os.makedirs(cur_path)
        dirs = os.listdir(cur_path)

        py_cnt = 1
        for cur_file in dirs:
            if os.path.splitext(cur_file)[1] == ".py":
                py_cnt += 1

        soup = BeautifulSoup(h.text, 'lxml')
        element = soup.select_one('[id="__NEXT_DATA__"]')
        ok = False
        if element:
            json_str = json.loads(element.text)
            v = json_str['props']['pageProps']['dehydratedState']['queries']
            for state in v:
                if 'queryHash' in state:
                    if 'question' in state['state']['data']:
                        question = state['state']['data']['question']
                        ok = True
                        handler_question_info(question_info=question, name=str(py_cnt), dir_prefix=cur_path,
                                              username=username,
                                              access_url=f'{LC_PROBLEM_PREFIX}/{question["titleSlug"]}')
        if not ok:
            print('解析失败')
    except Exception as e:
        print(e)


def parse_problem_by_urls(pre_dir=''):
    print("请输入题目链接(可批量处理) 输入两次回车开始解析:\n")

    def read_input_in_chunks():
        full_input = ''
        while True:
            chunk = input()
            if not chunk:
                break
            full_input += chunk
        return full_input

    full_input = read_input_in_chunks()
    urls = full_input
    time.sleep(1)
    pattern = re.compile(r'(https?://\S+)')
    result = pattern.findall(urls)
    # print(result)
    for url in result:
        if LC_PREFIX in url:
            parse_problem_by_url(url, pre_dir)
            time.sleep(2)


def get_no_contest(contest_no, contest_title_slug):
    is_bi_week = 'biweekly-contest' in contest_title_slug
    dir_name = 'biweek' if is_bi_week else 'week'
    dir_prefix = os.path.join(os.getcwd(), str(dir_name), str(contest_no))
    try:
        res = custom_url_response(url=f'{API_PREFIX}{contest_title_slug}/', method='GET')
        if res.status_code != 200:
            print('请求失败')
            return
        index = 0
        if not res.text or "questions" not in json.loads(res.text) or len(json.loads(res.text)['questions']) == 0:
            print('请确保周赛存在或者检查cookie是否过期')
            return
        username = get_user_name()
        if username is not None:
            print('\nhello!', f"\"{username}\"")
        if is_bi_week:
            print(f'第 {contest_no} 场双周赛即将开始!\n')
        else:
            print(f'第 {contest_no} 场周赛即将开始!\n')

        for question in json.loads(res.text)['questions']:
            try:
                title_slug = question['title_slug']
                access_url = f'{LC_PREFIX}/contest/{contest_title_slug}/problems/{title_slug}'
                print('\naccess_url: ', access_url)
                print('title: ', question['title'], 'credit: ', question['credit'])
                question_info = contestQuestion(contestSlug=contest_title_slug, questionSlug=question['title_slug'])
                name = chr(index + ord('a'))
                handler_question_info(question_info=question_info, name=name, dir_prefix=dir_prefix, username=username,
                                      access_url=access_url)
                time.sleep(2)
            except Exception as e:
                print(e)
            index += 1
        print(
            '----------------------------------解析完毕，如果有案例解析失败，请自行复制案例----------------------------------')
    except Exception as e:
        print(e)


def get_next_contest_info():
    s = {
        "operationName": 'null',
        "query": "{\n  contestUpcomingContests {\n    containsPremium\n    title\n    cardImg\n    titleSlug\n    description\n    startTime\n    duration\n    originStartTime\n    isVirtual\n    isLightCardFontColor\n    company {\n      watermark\n      __typename\n    }\n    __typename\n  }\n}\n",
        "variables": {}
    }
    infos = []
    try:
        r = response_post_default(s)
        if r.status_code == 200:
            data = json.loads(r.text)
            for cur_data in data['data']['contestUpcomingContests']:
                contest_info = {}
                diff_time = cur_data['originStartTime'] - time.time()
                contest_info['title'] = cur_data['title']
                contest_info['titleSlug'] = cur_data['titleSlug']
                contest_info['contest_no'] = int(re.search('\\d+', cur_data['titleSlug']).group(0))
                contest_info['diff_day'] = int(diff_time / (60 * 60 * 24))
                contest_info['diff_time'] = diff_time
                contest_info['diff_minute'] = math.ceil(
                    (diff_time / (60 * 60 * 24) - diff_time // (60 * 60 * 24)) * 24 * 60)
                # contest_info['origin'] = cur_data
                infos.append(contest_info)
        else:
            print('请求失败')
    except Exception as e:
        print(e)
    return infos


def create_next_contest():
    '''
    自动拉取最近周赛 如果超过60min会自动退出 少于60min 会根据比赛时间等待 ！
    :return:
    '''
    infos = get_next_contest_info()
    cur_info = {}
    for info in infos:
        if len(cur_info) == 0:
            cur_info = info
        else:
            if cur_info['diff_time'] > info['diff_time']:
                cur_info = info
    if len(cur_info) == 0:
        print(f'未获取到任何比赛信息 请到官方地址查看 {LC_PREFIX}/contest/')
        return
    if cur_info['diff_day'] > 0:
        print('\n距离最近比赛', cur_info['title'], '还有', cur_info['diff_day'], '天!')
    else:
        minute = cur_info['diff_minute']
        if minute <= 60:
            for t in range(0, minute):
                print(f"距离{cur_info['title']}开始还剩:{(minute - t)}分钟 请等待 ！")
                time.sleep(60 * 1)
            time.sleep(10)
            get_no_contest(cur_info['contest_no'], cur_info['titleSlug'])
        else:
            print(f"距离 {cur_info['title']} 开始还剩:{minute}分钟 请在一个小时内等待 ！")
    # print((cur_info['diff_time'] / (60 * 60 * 24) - cur_info['diff_time'] // (60 * 60 * 24)) * 24 * 60)


def create_contest_by_contest_id(is_bi_week=False):
    cur_text = '双' if is_bi_week else ''
    infos = get_next_contest_info()
    # print(infos)
    cur_info = {}
    for info in infos:
        ok = 'biweekly-contest' in info['titleSlug']
        if is_bi_week:
            if ok:
                cur_info = info
                break
        else:
            if not ok:
                cur_info = info
                break
    if 'contest_no' not in cur_info:
        raise BaseException("请检查Cookies是否过期！")
    contest_max_no = cur_info['contest_no']
    minute = cur_info['diff_minute']
    cur_id = 0
    if cur_info['diff_day'] == 0:
        print(f'当前类型比赛最大序号:{contest_max_no}, 距离{cur_info["title"]} 还剩下 {minute} 分钟')
    else:
        print(f'当前类型比赛最大序号:{contest_max_no}, 距离{cur_info["title"]} 还剩下 {cur_info["diff_day"]} 天')
    while True:
        contest_id = input(f'请输入{cur_text}周赛序号 (exit退出):\n')
        if contest_id.lower() == 'exit':
            break
        try:
            cur_id = int(contest_id)
            if cur_id < 0:
                print(f'请输入一个大于0并且不能超过当前{cur_text}周赛 ({contest_max_no}) 最大序号')
                continue
            else:
                get_no_contest(contest_id,
                               f'biweekly-contest-{contest_id}' if is_bi_week else f'weekly-contest-{contest_id}')
                break
        except Exception as e:
            if cur_id == contest_max_no:
                print('当前比赛未开始获取失败！')
            else:
                print(e)
            continue


def create_week_contest_by_contest_id():
    create_contest_by_contest_id(is_bi_week=False)


def create_bi_week_contest_by_contest_id():
    create_contest_by_contest_id(is_bi_week=True)


def questionEditorData(title_slug):
    '''
    查询编辑器状态 可以获取到代码块内容
    :param title_slug:
    :return:
    '''
    json_str = {
        "query": "query questionEditorData($titleSlug: String!) { question(titleSlug: $titleSlug) {\n    questionId\n    questionFrontendId\n    codeSnippets {\n      lang\n      langSlug\n      code\n    }\n    envInfo\n    enableRunCode\n    hasFrontendPreview\n    frontendPreviews\n  }\n}\n    ",
        "variables": {
            "titleSlug": f"{title_slug}"
        },
        "operationName": "questionEditorData"
    }
    try:
        res = response_post_default(json_str=json_str, contentType=applicationJSON)
        if res.status_code == 200:
            return json.loads(res.text)['data']['question']
        else:
            return {}
    except Exception as e:
        print(e)


def query_today():
    '''
    查询今天的每日一题信息
    :return:
    '''
    json_str = {
        "query": "\n    query questionOfToday {\n  todayRecord {\n    date\n    userStatus\n    question {\n      "
                 "questionId\n      frontendQuestionId: questionFrontendId\n      difficulty\n      title\n      "
                 "titleCn: translatedTitle\n      titleSlug\n      paidOnly: isPaidOnly\n      freqBar\n      "
                 "isFavor\n      acRate\n      status\n      solutionNum\n      hasVideoSolution\n      topicTags {\n "
                 "       name\n        nameTranslated: translatedName\n        id\n      }\n      extra {\n        "
                 "topCompanyTags {\n          imgUrl\n          slug\n          numSubscribed\n        }\n      }\n   "
                 " }\n    lastSubmission {\n      id\n    }\n  }\n}\n    ",
        "variables": {},
        "operationName": "questionOfToday"
    }
    try:
        r = response_post_default(json_str=json_str, contentType=applicationJSON)
        if r.status_code == 200:
            cur_json = json.loads(r.text)
            return cur_json['data']['todayRecord'][0]['question']
        else:
            return {}
    except:
        return {}


def create_today_question(pre_dir=''):
    '''
    每日一题
    :param pre_dir: 创建目录
    :return:
    '''
    info = query_today()
    title_slug = info['titleSlug']
    if title_slug:
        url = LC_PROBLEM_PREFIX + '/' + title_slug
        print("title:    ", info['titleCn'])
        parse_problem_by_url(url=url, pre_dir=pre_dir)


def test_response():
    json_str = {
        "operationName": "globalData",
        "query": "\n    query globalData {\n  userStatus {\n    isSignedIn\n    isPremium\n    username\n    realName\n    avatar\n    userSlug\n    isAdmin\n    checkedInToday\n    useTranslation\n    premiumExpiredAt\n    isTranslator\n    isSuperuser\n    isPhoneVerified\n    isVerified\n    completedFeatureGuides\n  }\n  jobsMyCompany {\n    nameSlug\n  }\n}\n    ",
        "variables": {}
    }
    res = response_post_default(json_str)
    return res


def login():
    '''
    后续使用login方式登录
    :return:
    '''
    res = test_response()
    print(res.text)
