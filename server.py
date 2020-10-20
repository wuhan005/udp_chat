import socket

import datetime
from msg import *
from util import parse


class Server:
    welcome_msg = '''
UDP Server

服务器时间: %s
==================================
    '''

    handlers = {}

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((ip, port))

        self.add_handler("connect", self.connect)

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
