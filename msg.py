from util import warp, check_code


# connect 新的连接
def connect():
    return warp("connect", "")


def register(data):
    return warp("register", data)


def login(data):
    return warp("login", data)


def logout(token):
    return warp("logout", token)


# welcome 服务端欢迎信息
def welcome(msg):
    return warp("welcome", msg)


# 计算校验码并发送确认信息
def ok(data):
    return warp("ok", check_code(data))


# 操作错误消息
def error(msg):
    return warp("error", msg)


# 登录成功，返回 Token
def send_token(token):
    return warp("send_token", token)
