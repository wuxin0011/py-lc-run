import json
import math
import os
import random
import re
import time

import requests

LC_PREFIX = "https://leetcode.cn"
# LC_PREFIX = "https://leetcode.com"
applicationJSON = "application/json"
applicationHTML = "text/html; charset=utf-8"
LC_PROBLEM_PREFIX = LC_PREFIX + "/problems"
graphql = LC_PREFIX + "/graphql/"
# 自定义支持提交的代码种类 按照顺序
support_submit_lang_List = ['python3', 'java', 'cpp']


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
    except Exception as e:
        print('用户名获取异常:', e)
    return None


def get_today_problem():
    user_info = {
        "query": "\n    query questionOfToday {\n  todayRecord {\n    date\n    userStatus\n    question {\n      questionId\n      frontendQuestionId: questionFrontendId\n      difficulty\n      title\n      titleCn: translatedTitle\n      titleSlug\n      paidOnly: isPaidOnly\n      freqBar\n      isFavor\n      acRate\n      status\n      solutionNum\n      hasVideoSolution\n      topicTags {\n        name\n        nameTranslated: translatedName\n        id\n      }\n      extra {\n        topCompanyTags {\n          imgUrl\n          slug\n          numSubscribed\n        }\n      }\n    }\n    lastSubmission {\n      id\n    }\n  }\n}\n    ",
        "variables": {},
        "operationName": "questionOfToday"
    }

    try:
        res = response_post_default(user_info)
        if res.status_code == 200:
            s = json.loads(res.text)
            titleSlug = s['data']['todayRecord'][0]['question']['titleSlug']
            url = LC_PROBLEM_PREFIX + "/" + titleSlug
            return [titleSlug, url, s]
    except Exception as e:
        print('用户名获取异常:', e)
    return None


def get_today_problem_content(titleSlug):
    user_info = {
        "query": "\n    query discussTopic($slug: String) {\n  solutionArticle(slug: $slug, orderBy: DEFAULT) {\n    ...solutionArticle\n    content\n    next {\n      slug\n      title\n    }\n    prev {\n      slug\n      title\n    }\n  }\n}\n    \n    fragment solutionArticle on SolutionArticleNode {\n  ipRegion\n  rewardEnabled\n  canEditReward\n  uuid\n  title\n  content\n  slateValue\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  canSee\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    tagType\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    certificationLevel\n    isDiscussAdmin\n    isDiscussStaff\n    profile {\n      userAvatar\n      userSlug\n      realName\n      reputation\n    }\n  }\n  summary\n  topic {\n    id\n    subscribed\n    commentCount\n    viewCount\n    post {\n      id\n      status\n      voteStatus\n      isOwnPost\n    }\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  favoriteCount\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n  }\n  question {\n    titleSlug\n    questionFrontendId\n  }\n}\n    ",
        "variables": {"slug": titleSlug}, "operationName": "discussTopic"}

    try:
        res = response_post_default(user_info)
        if res.status_code == 200:
            text = json.loads(res.text)
            # print(text)
            content = text['data']['solutionArticle']['content']
            return [content, text]
    except Exception as e:
        print('用户名获取异常:', e)
    return None


def get_user_solution(slug):
    user_info = {
        "query": "\n    query discussTopic($slug: String) {\n  solutionArticle(slug: $slug, orderBy: DEFAULT) {\n    ...solutionArticle\n    content\n    next {\n      slug\n      title\n    }\n    prev {\n      slug\n      title\n    }\n  }\n}\n    \n    fragment solutionArticle on SolutionArticleNode {\n  ipRegion\n  rewardEnabled\n  canEditReward\n  uuid\n  title\n  content\n  slateValue\n  slug\n  sunk\n  chargeType\n  status\n  identifier\n  canEdit\n  canSee\n  reactionType\n  reactionsV2 {\n    count\n    reactionType\n  }\n  tags {\n    name\n    nameTranslated\n    slug\n    tagType\n  }\n  createdAt\n  thumbnail\n  author {\n    username\n    certificationLevel\n    isDiscussAdmin\n    isDiscussStaff\n    profile {\n      userAvatar\n      userSlug\n      realName\n      reputation\n    }\n  }\n  summary\n  topic {\n    id\n    subscribed\n    commentCount\n    viewCount\n    post {\n      id\n      status\n      voteStatus\n      isOwnPost\n    }\n  }\n  byLeetcode\n  isMyFavorite\n  isMostPopular\n  favoriteCount\n  isEditorsPick\n  hitCount\n  videosInfo {\n    videoId\n    coverUrl\n    duration\n  }\n  question {\n    titleSlug\n    questionFrontendId\n  }\n}\n    ",
        "variables": {"slug": slug}, "operationName": "discussTopic"}
    try:
        res = response_post_default(user_info)
        if res.status_code == 200:
            text = json.loads(res.text)
            return text
    except Exception as e:
        print('用户题解获取异常:', e)
    return None


def parse_solution_code(text=''):
    '''
    解析solution 的 代码部分内容
    :param text:
    :return: 返回内容 {lang:[]}
    '''
    code_lang_list = {}
    lang = ''
    code = ''
    end = '```'
    i = 0
    add_code_start = False
    while i < len(text):
        c = text[i]
        if c == '`' and i + 3 < len(text) and text[i:i + 3] == end:
            i += 3
            if add_code_start:
                lang = lang.lower()
                if lang and lang not in code_lang_list:
                    code_lang_list[lang] = []
                if code and lang:
                    code_lang_list[lang].append(code)
                add_code_start = False
                code = ''
                lang = ''
            else:
                while i < len(text) and text[i] != ' ':
                    lang += text[i]
                    i += 1
                while i < len(text) and text[i] == ' ': i += 1
        elif c == '[' and i + 4 < len(text) and text[i + 1: i + 4] == 'sol':
            add_code_start = True
            while i < len(text) and text[i] != ']':
                i += 1
            i += 1
            code = ''
        elif add_code_start:
            code += c
            i += 1
        else:
            i += 1
    return code_lang_list


def get_some_solution_list(questionSlug):
    user_info = {"query": "\n    query questionTopicsList($questionSlug: String!, $skip: Int, $first: Int, $orderBy:"
                          " SolutionArticleOrderBy, $userInput: String, $tagSlugs: [String!]) {\n  questionSolutionArticles(\n  "
                          "  questionSlug: $questionSlug\n    skip: $skip\n    first: $first\n    orderBy: $orderBy\n   "
                          " userInput: $userInput\n    tagSlugs: $tagSlugs\n  ) {\n    totalNum\n    edges {\n    "
                          "  node {\n        rewardEnabled\n        canEditReward\n        uuid\n        title\n      "
                          "  slug\n        sunk\n        chargeType\n        status\n        identifier\n        canEdit\n "
                          "      canSee\n        reactionType\n        hasVideo\n        favoriteCount\n        upvoteCount\n       "
                          " reactionsV2 {\n          count\n          reactionType\n        }\n        tags {\n          name\n     "
                          "     nameTranslated\n          slug\n          tagType\n        }\n        createdAt\n        thumbnail\n "
                          "       author {\n          username\n          certificationLevel\n          profile {\n        "
                          "    userAvatar\n            userSlug\n            realName\n            reputation\n      "
                          "    }\n        }\n        summary\n        topic {\n          id\n          commentCount\n  "
                          "       viewCount\n          pinned\n        }\n        byLeetcode\n        isMyFavorite\n     "
                          "   isMostPopular\n        isEditorsPick\n        hitCount\n        videosInfo {\n          videoId\n  "
                          "        coverUrl\n          duration\n        }\n      }\n    }\n  }\n}\n "
                          "   ",
                 "variables": {"questionSlug": questionSlug, "skip": 0, "first": 15, "orderBy": "DEFAULT",
                               "userInput": "",
                               "tagSlugs": []}, "operationName": "questionTopicsList"}
    try:
        res = response_post_default(user_info)
        if res.status_code == 200:
            text = json.loads(res.text)
            return [text['data']['questionSolutionArticles']['edges'], text]
    except Exception as e:
        print('题解列表获取失败:', e)
    return None


def submit(lang, code, titleTlug, questionId):
    '''
    提交代码
    :param lang: 语言类型
    :param code: 代码
    :param titleTlug: 题目识别码
    :param questionId: questionId
    :return:
    '''
    json_str = {
        "lang": lang,
        "question_id": questionId,
        "typed_code": code,
    }
    url = f'{LC_PREFIX}/problems/{titleTlug}/submit/'
    try:
        res = response_post_default(json_str=json_str, contentType=applicationJSON, method='POST', url=url)
        if res.status_code == 200:
            text = json.loads(res.text)
            time.sleep(5)
            return (True, text['submission_id'])
    except Exception as e:
        print('提交异常:', e)
    return (False, '')


def query_submit_result(submitId):
    '''
    查询提交结果
    :param submitId
    :return:
    '''
    url = f'https://leetcode.cn/submissions/detail/{submitId}/check/'
    try:
        res = custom_url_response(url=url, method='GET', contentType=applicationJSON)
        if res.status_code == 200:
            return json.loads(res.text)
    except Exception as e:
        pass
    return {}


def auto_submit():
    for _ in range(10):
        todayInfo = get_today_problem()
        if todayInfo is None:
            print('查询不到当天题目 重试中...')
            return
        titleTlug = todayInfo[0]
        questionID = todayInfo[2]['data']['todayRecord'][0]['question']['questionId']
        for info in get_some_solution_list(titleTlug)[0]:
            try:
                temp = get_user_solution(info['node']['slug'])
                # print(temp)
                t = temp['data']['solutionArticle']

                result = parse_solution_code(t['content'])
                # print('keys',result.keys())
                if len(result) == 0:
                    continue
                ok = 0
                for key in support_submit_lang_List:
                    if key in result:
                        ok = 1
                        break
                if not ok: continue
                print('****************部分信息****************')
                print(t['title'], t['author']['username'], t['ipRegion'])
                # print(parse_solution_code(t['content']))
                print('****************解析结果****************')
                for lang in support_submit_lang_List:
                    if lang == 'python3': lang = 'python'
                    if lang not in result: continue
                    codes = result[lang]
                    if len(codes) == 0: continue
                    for _, code in enumerate(codes, 1):
                        # print(f'解法{_}')
                        # print(code)
                        code = '# 该代码由脚本自动提交 https://github.com/wuxin0011/py-lc-run/tree/main/generator/auto_submit_today.py \n' + code
                        submitInfo = submit('python3' if lang == 'python' else lang, code, titleTlug, questionID)
                        if submitInfo[0]:
                            for _ in range(100):
                                time.sleep(random.randint(1, 5))
                                submit_result = query_submit_result(submitInfo[1])
                                if len(submit_result.keys()) == 1 and 'status_msg' not in submit_result:
                                    print('submit_result', submit_result)
                                    continue
                                # print('submit_result',submit_result)
                                if len(submit_result) > 0 and 'status_msg' in submit_result and submit_result[
                                    'status_msg'] == 'Accepted':
                                    print('submit success !!!')
                                    print(f'submit url = {LC_PREFIX}/submissions/detail/{submitInfo[1]}/')
                                    print(code)
                                    return
                    print('\n')
            except Exception as e:
                print('error', e)

auto_submit()
