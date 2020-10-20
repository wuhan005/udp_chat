import json


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
