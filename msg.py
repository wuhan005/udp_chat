from util import warp


# connect 新的连接
def connect():
    return warp("connect", "")


# welcome 服务端欢迎信息
def welcome(msg):
    return warp("welcome", msg)
