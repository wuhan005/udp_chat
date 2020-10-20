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

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

        self.add_handler("connect", self.connect)
        self.add_handler('register', self.register)
        self.add_handler('login', self.login)
        self.add_handler('logout', self.logout)

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
            return error("用户名重复，换一个名字吧~")

        # 存储用户信息
        self.user_data[account] = {'password': password}
        print('新用户注册：%s' % account)
        return ok(body)

    # Handler: 用户登录
    def login(self, addr, body):
        account = body['account']
        password = body['password']

        # 判断用户名是否重复
        if account not in self.user_data or self.user_data[account]['password'] != password:
            return error("用户名或密码错误")

        # 签发用户 Token
        token = md5(str(time.time()) + account + self.salt)
        self.user_data[account]['token'] = token
        print('用户登录成功：%s - %s' % (account, token))
        return send_token(token)

    # Handler: 用户登出
    def logout(self, addr, body):
        account = body['account']
        token = body['token']

        # 判断用户名，Token 是否正确
        if account not in self.user_data or self.user_data[account]['token'] != token:
            return error("用户名不存在")

        # 删除 Token
        del self.user_data[account]['token']
        print('用户登出：%s' % account)
        return ok(body)


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
