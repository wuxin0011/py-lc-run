## 这个是干什么的 ？

一个本地模拟力扣周赛的工具，无需处理输入输出，更加方便debug，周赛快人一步 ！


## 效果预览

![dir](./asserts/dir.png)


## 使用文档



[vscode使用说明以及cookie获取方式](./use.md)




## 使用方法


由 [generator.index.py](./generator/index.py) 下面几个接口
 - `create_next_contest` 获取最近的周赛或者双周赛
 - `create_week_contest_by_contest_id` 根据输入指定**序号**拉取对应场次的周赛
 - `create_bi_week_contest_by_contest_id` 根据输入指定**序号**拉取对应场次的双周赛
 - `create_today_question` 自动拉取今天的每日一题 参数为指定目录前缀
 - `parse_problem_by_urls` 输入题目链接自动获取 参数为指定目录前缀



```py


from generator.contest import create_next_contest,create_week_contest_by_contest_id,create_bi_week_contest_by_contest_id


if __name__ == '__main__':
    
    create_next_contest()
    # create_week_contest_by_contest_id()
    # create_bi_week_contest_by_contest_id()

    

```

上面演示在 [contest](./contest) 目录下







### 测试案例

由 [generator.index](./generator/index.py) 提供的包装器 配合上面模板使用即可

```python
def testcase(test=-1, start= 1, end=0x3ffffff, use=True):
    '''
    参数说明
    :param use: 是否启用这个优先级最高默认启用 如果 False 表示这个包装器失效
    :param test:  默认为-1 表示 [start,end] 用例生效 ，如果需要测试某一个用力 直接使用 test=x ，这时 [start,end] 将会失效
    :param start: 在 test 不为 -1 情况下 测试案例从 start 开始
    :param end:   在 test 不为 -1 情况下 测试案例 end 结束
    :return:
    '''
```





### 👓 完整使用模板

```python
@testcase(test=-1,start= 1,end = 0x3ffffff,use = True)
class Solution:
    def minOperations(self, nums: List[int], k: int) -> int:
        pass
        
if __name__ == '__main__':
    leetcode_run(class_name=Solution, method="minOperations", filename=os.getcwd() +"\\__test_case__\\3.txt")

```

上面模板均自动生成，如果需要指定模板 请访问[这个文件](./generator/generator_template.py) 根据自己喜好修改 







## 3、其他



### ~~📣 未实现功能~~

当前除了**构造类**对拍未实现大部分功能均已实现 后面看时间是否会实现 因为构造类题目力扣并不多，后面看看会不会加进去



**现在已经实现**



### 👓 Java 版本

如果使用Java，可以使用[leetcode-template](https://github.com/wuxin0011/leetcode-template-simple)，这个功能更全面【实现了构造类对拍😍]


## Thanks

感谢 [JetBrains](https://www.jetbrains.com/?from=py-lc-run) 提供的 Open Source License

