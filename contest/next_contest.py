

from generator.contest import create_next_contest

'''
获取当前马上进行的周赛|双周赛 如果距离比赛开始超过半个小时以上程序自动退出
'''
if __name__ == '__main__':
    create_next_contest()

