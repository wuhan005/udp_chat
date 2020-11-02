import socket
import threading
import time

from msg import *
from util import *


class Client:
    login_status = False
    group_status = False
    account = ''
    token = ''

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = (ip, port)

    # 发送消息并解析返回
    def send(self, data):
        self.socket.sendto(data, self.server)
        receive_data, addr = self.socket.recvfrom(1024)
        return parse(receive_data)

    # 发送信息，不处理返回
    def just_send(self, data):
        self.socket.sendto(data, self.server)

    def menu(self):
        while True:
            clear()
            print("====菜单====")
            print("1. 注册")

            if self.login_status is False:
                print("2. 登录")
            else:
                print("2. 登出")
                print("3. 公共聊天室【群发】")
                print("4. 单独聊天【私发】")

            print("============")

            choice = input()
            if choice == '1':
                self.register()
            elif choice == '2':
                if self.login_status is False:
                    self.login()
                else:
                    self.logout()
            elif choice == '3' and self.login_status is True:
                self.group()
                print(1111111)

    # 用户注册
    def register(self):
        while True:
            account = input("[ - ] 注册 请输入用户名：")
            password = input("[ - ] 注册 请输入密码：")
            register_payload = {
                'account': account,
                'password': password
            }
            message_type, message_body = self.send(register(register_payload))
            if message_type == 'error':
                print('[ x ] ' + message_body)
                continue
            if message_type != 'ok':
                raise Exception("意外的返回消息类型 " + message_type)
            if message_body != check_code(register_payload):
                raise Exception("错误的消息校验码")

            print('[ - ] 注册成功')
            break

    # 用户登录
    def login(self):
        while True:
            account = input("[ - ] 登录 请输入用户名：")
            password = input("[ - ]登录 请输入密码：")
            login_payload = {
                'account': account,
                'password': password
            }
            message_type, message_body = self.send(login(login_payload))
            if message_type == 'error':
                print('[ x ] ' + message_body)
                continue
            elif message_type == 'send_token':
                # 保存 Token，更新登录状态
                self.account = account
                self.token = message_body
                self.login_status = True
                print('[ - ] 登录成功')
                break
            else:
                print('[ x ] 意外的返回：%s - %s' % (message_type, message_body))

    # 用户登出
    def logout(self):
        while True:
            logout_payload = {
                'account': self.account,
                'token': self.token
            }
            message_type, message_body = self.send(logout(logout_payload))
            if message_type == 'error':
                print('[ x ] ' + message_body)
                continue
            if message_type != 'ok':
                raise Exception("意外的返回消息类型 " + message_type)
            if message_body != check_code(logout_payload):
                raise Exception("错误的消息校验码")

            # 清除 Token，更新登录状态
            self.token = ''
            self.account = ''
            self.login_status = False
            print("登出成功！")
            break

    # 群聊
    def group(self):
        clear()

        if not self.login_status:
            raise Exception('未登录')

        group_payload = {
            'account': self.account,
            'token': self.token,
        }

        # 发送进入聊天室信息
        message_type, message_body = self.send(enter_group(group_payload))
        if message_type == 'error':
            print('[ x ] ' + message_body)
            return
        if message_type != 'ok':
            raise Exception("意外的返回消息类型 " + message_type)
        if message_body != check_code(group_payload):
            raise Exception("错误的消息校验码")

        self.group_status = True

        # 另起一个线程开始读取收到的消息
        group_thread = threading.Thread(target=self.receive_group_message)
        group_thread.start()

        while True:
            msg = input()

            group_message_payload = {
                'account': self.account,
                'token': self.token,
                'message': msg
            }

            if msg == '/exit':
                self.group_status = False
                break

            # 不接收处理响应
            self.just_send(group_message(group_message_payload))

        # 发送退出消息
        self.just_send(exit_group(group_payload))

    def receive_group_message(self):
        print('[ - ] 进入公共聊天室，输入 /exit 退出')
        while True and self.group_status:
            receive_data, addr = self.socket.recvfrom(1024)
            data_type, receive_data = parse(receive_data)
            if data_type == 'receive_group_message':
                print("[%s] %s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), receive_data['from'],
                                       receive_data['message']))

        print('[ - ] 退出公共聊天室')

    # 私聊
    def private(self):
        clear()
        target = input('输入聊天目标账号：')
        ask_private_payload = {
            'account': self.account,
            'token': self.token,
            'target': target,
        }
        message_type, message_body = self.send(ask_private(ask_private_payload))
        if message_type == 'error':
            print('[ x ] ' + message_body)
            return
        if message_type != 'ok':
            raise Exception("意外的返回消息类型 " + message_type)
        if message_body != check_code(ask_private_payload):
            raise Exception("错误的消息校验码")

        print('[ - ] 开始聊天吧~')


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

    client.menu()


if __name__ == '__main__':
    start()
