import socket

import datetime
import json
import time
from msg import *
from util import parse, md5


class Server:
    salt = 'here_is_very_s3cret_s@lt'

    welcome_msg = '''
UDP Server

服务器时间: %s
==================================
    '''

    handlers = {}
    user_data = {}
    group_chat = {}

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

        self.add_handler("connect", self.connect)
        self.add_handler('register', self.register)
        self.add_handler('login', self.login)
        self.add_handler('logout', self.logout)
        self.add_handler('enter_group', self.enter_group)
        self.add_handler('group_message', self.group_message)
        self.add_handler('exit_group', self.exit_group)
        self.add_handler('send_private', self.send_private)

    # 返回消息给客户端
    def send_to(self, addr, data):
        self.socket.sendto(data, addr)

    # 接受消息
    def receive_message(self):
        data, addr = self.socket.recvfrom(1024)
        return parse(data), addr

    # 添加处理函数
    def add_handler(self, name, handler):
        self.handlers[name] = handler

    # 根据消息类型调用处理函数
    def handle(self, client_addr, message_type, message_body):
        return self.handlers[message_type](client_addr, message_body)

    # Handler: 新的客户端
    def connect(self, addr, body):
        return welcome(self.welcome_msg % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Handler: 用户注册
    def register(self, addr, body):
        account = body['account']
        password = body['password']

        # 判断用户名是否重复
        if account in self.user_data:
            return error('register', "用户名重复，换一个名字吧~")

        # 存储用户信息
        self.user_data[account] = {'password': password}
        print('新用户注册：%s' % account)
        return ok('register', body)

    # Handler: 用户登录
    def login(self, addr, body):
        account = body['account']
        password = body['password']

        # 判断用户名是否重复
        if account not in self.user_data or self.user_data[account]['password'] != password:
            return error('login', "用户名或密码错误")

        # 签发用户 Token
        token = md5(str(time.time()) + account + self.salt)
        self.user_data[account]['token'] = token
        # 保存登录用户地址
        self.user_data[account]['addr'] = addr
        print('用户登录成功：%s - %s' % (account, token))
        return send_token({
            'account': account,
            'token': token
        })

    # Handler: 用户登出
    def logout(self, addr, body):
        account = body['account']
        token = body['token']

        # 判断用户名，Token 是否正确
        if account not in self.user_data or self.user_data[account]['token'] != token:
            return error('auth', "用户名不存在")

        # 删除 Token
        del self.user_data[account]['token']
        del self.user_data[account]['addr']
        print('用户登出：%s' % account)
        return ok('logout', body)

    # Handler: 用户进入群聊
    def enter_group(self, addr, body):
        account = body['account']
        token = body['token']

        # 判断用户名，Token 是否正确
        if account not in self.user_data or self.user_data[account]['token'] != token:
            return error('auth', "用户名不存在")

        # 添加当前用户添加到公共服务器中
        self.group_chat[account] = token

        print('用户 %s 进入群聊' % account)
        return ok('enter_group', body)

    # Handler: 用户发送群聊消息
    def group_message(self, addr, body):
        account = body['account']
        token = body['token']
        message = body['message']

        # 判断用户名，Token 是否正确
        if account not in self.user_data or self.user_data[account]['token'] != token:
            return error('auth', "用户名不存在")

        # 如果当前用户意外不在群聊名单里，则加上
        self.group_chat[account] = token

        # 广播群聊消息
        for to_account in self.group_chat:
            to_addr = self.user_data[to_account]['addr']
            self.send_to(to_addr, receive_group_message({
                'from': account,
                'message': message,
            }))

        print('用户 %s 发送群聊消息: %s' % (account, message))
        return ok('group_message', body)

    # Handler: 用户退出群聊
    def exit_group(self, addr, body):
        account = body['account']
        token = body['token']

        # 判断用户名，Token 是否正确
        if account not in self.user_data or self.user_data[account]['token'] != token:
            return error('auth', "用户名不存在")

        # 将当前用户从公共服务器中移除
        if account in self.group_chat:
            del self.group_chat[account]

        print('用户 %s 退出群聊' % account)
        return ok('exit_group', body)

    # Handler: 用户发送私有消息
    def send_private(self, addr, body):
        account = body['account']
        token = body['token']
        target = body['target']
        message = body['message']

        # 判断用户名，Token 是否正确
        if account not in self.user_data or self.user_data[account]['token'] != token:
            return error('auth', "用户名不存在")

        # 判断该用户是否存在并登陆
        if target in self.user_data and self.user_data[account]['addr'] != '':
            to_addr = self.user_data[target]['addr']
            self.send_to(to_addr, receive_private_message({
                'from': account,
                'message': message,
            }))
        else:
            print('用户 %s 发送私有消息给 %s: %s，发送失败！' % (account, target, message))
            return

        print('用户 %s 发送私有消息给 %s: %s' % (account, target, message))


def start():
    server = Server("0.0.0.0", 5000)
    print("server start...")

    # 接收消息
    while True:
        (message_type, message_body), client_addr = server.receive_message()
        callback = server.handle(client_addr, message_type, message_body)
        # 不为 None 则代表该类消息需要回复
        if callback is not None:
            server.send_to(client_addr, callback)


if __name__ == '__main__':
    start()
