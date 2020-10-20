import json
import hashlib
import os


# 解析消息体
def parse(message):
    message = json.loads(message)
    return message['t'], message['b']


# 包装消息体
def warp(message_type, message_body):
    return bytes(json.dumps({
        't': message_type,
        'b': message_body,
    }), encoding="utf8")


# 计算消息校验码
def check_code(data):
    data = json.dumps(data).encode('utf-8')
    md5 = hashlib.md5()
    md5.update(data)
    return md5.hexdigest()


def md5(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()


# 清屏
def clear():
    os.system('clear')
