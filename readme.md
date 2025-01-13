使用条件

1、 安装依赖库

```commandline
pip install bs4
pip install requests
```

2、 配置 Cookie

3、说明
当前除了**构造类**对拍未实现大部分功能均已实现 后面看时间是否会实现 因为构造类题目力扣并不多



## 使用方法


由 [generator.index.py](./generator/index.py) 下面几个接口
 - `create_next_contest` 获取最近的周赛或者双周赛
 - `create_week_contest_by_contest_id` 根据输入指定**序号**拉取对应场次的周赛
 - `create_bi_week_contest_by_contest_id` 根据输入指定**序号**拉取对应场次的双周赛
 - `create_today_question` 自动拉取今天的每日一题 参数为指定目录前缀
 - `parse_problem_by_urls` 输入题目链接自动获取 参数为指定目录前缀

> 使用模板

```py


from generator.contest import create_next_contest,create_week_contest_by_contest_id,create_bi_week_contest_by_contest_id


if __name__ == '__main__':
    
    create_next_contest()
    # create_week_contest_by_contest_id()
    # create_bi_week_contest_by_contest_id()

    

```

上面演示在 [contest](./contest) 目录下

