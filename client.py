import socket

from msg import *
from util import warp, parse


class Client:
    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = (ip, port)

    # 发送消息并解析返回
    def send(self, data):
        self.socket.sendto(data, self.server)
        receive_data, addr = self.socket.recvfrom(1024)
        return parse(receive_data)


server_ip = '127.0.0.1'
server_port = 5000


def start():
    client = Client(server_ip, server_port)
    # 准备连接
    message_type, message_body = client.send(connect())
    if message_type != 'welcome':
        raise Exception("意外的返回消息类型 " + message_type)
    print("[ - ] 成功连接服务器")
    print(message_body)


if __name__ == '__main__':
    start()
