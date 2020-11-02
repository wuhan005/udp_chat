from util import warp, check_code


# 客户端建立新的连接
def connect():
    return warp("connect", "")


# 客户端注册
def register(data):
    return warp("register", data)


# 客户端登录
def login(data):
    return warp("login", data)


# 客户端登出
def logout(data):
    return warp("logout", data)


# 客户端进入群聊
def enter_group(data):
    return warp("enter_group", data)


# 客户端发送群聊消息
def group_message(data):
    return warp("group_message", data)


# 服务端群发群聊消息
def receive_group_message(data):
    return warp('receive_group_message', data)


# 服务端发送私有消息
def receive_private_message(data):
    return warp('receive_private_message', data)


# 客户端退出群聊
def exit_group(data):
    return warp("exit_group", data)


# 客户端发送私有消息
def send_private(data):
    return warp("send_private", data)


# welcome 服务端欢迎信息
def welcome(msg):
    return warp("welcome", msg)


# 计算校验码并发送确认信息
def ok(msg_type, data):
    return warp("ok", {
        'type': msg_type,
        'code': check_code(data)
    })


# 操作错误消息
def error(msg):
    return warp("error", msg)


# 登录成功，返回 Token
def send_token(data):
    return warp("send_token", data)
