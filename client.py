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
    payload_queue = []

    # 多线程信号量
    ready_signal = True  # 初始化完毕
    register_signal = False  # 注册事件处理完毕
    login_signal = False  # 登录事件处理完毕
    logout_signal = False  # 登出事件处理完毕

    def __init__(self, ip: str, port: int):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server = (ip, port)

    # 发送消息
    def send(self, data):
        self.socket.sendto(data, self.server)

    def menu(self):
        while True:
            print("====菜单====")

            if self.login_status is False:
                print("1. 注册")
                print("2. 登录")
            else:
                print("2. 登出")
                print("3. 公共聊天室【群发】")
                print("4. 私发消息")

            print("============")

            choice = input()
            if choice == '1' and self.login_status is False:
                self.register()
                clear()
            elif choice == '2':
                if self.login_status is False:
                    self.login()
                else:
                    clear()
                    self.logout()
            elif choice == '3' and self.login_status is True:
                clear()
                self.group()
            elif choice == '4' and self.login_status is True:
                clear()
                self.private_message()

    # 用户注册
    def register(self):
        while True:
            account = input("[ - ] 注册 请输入用户名：")
            password = input("[ - ] 注册 请输入密码：")
            register_payload = {
                'account': account,
                'password': password
            }

            self.payload_queue.append(register_payload)
            self.send(register(register_payload))
            self.register_signal = True
            while self.register_signal:
                pass
            break

    # 用户登录
    def login(self):
        account = input("[ - ] 登录 请输入用户名：")
        password = input("[ - ]登录 请输入密码：")
        login_payload = {
            'account': account,
            'password': password
        }
        self.send(login(login_payload))
        self.login_signal = True
        while self.login_signal:
            pass
        clear()

    # 用户登出
    def logout(self):
        while True:
            logout_payload = {
                'account': self.account,
                'token': self.token
            }
            self.payload_queue.append(logout_payload)
            self.send(logout(logout_payload))

            self.logout_signal = True
            while self.logout_signal:
                pass

            # 清除 Token，更新登录状态
            self.token = ''
            self.account = ''
            self.login_status = False
            print("登出成功！")
            break

    # 群聊
    def group(self):
        if not self.login_status:
            raise Exception('未登录')

        group_payload = {
            'account': self.account,
            'token': self.token,
        }

        # 发送进入聊天室信息
        self.payload_queue.append(group_payload)
        self.send(enter_group(group_payload))

        self.group_status = True
        print('[ - ] 进入公共聊天室，输入 /exit 退出')

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

            self.payload_queue.append(group_message_payload)
            self.send(group_message(group_message_payload))

        # 发送退出消息
        self.payload_queue.append(group_payload)
        self.send(exit_group(group_payload))
        clear()

    # 私发消息
    def private_message(self):
        target = input('输入目标账号：')
        message = input('请输入消息内容：')
        send_private_payload = {
            'account': self.account,
            'token': self.token,
            'target': target,
            'message': message,
        }
        self.payload_queue.append(send_private_payload)
        self.send(send_private(send_private_payload))
        clear()

    # 接受服务端消息处理器
    def receive_message_handler(self):
        while True:
            receive_data, addr = self.socket.recvfrom(1024)
            data_type, receive_data = parse(receive_data)
            # 服务端报文确认消息，遍历报文队列进行匹配
            if data_type == 'ok':
                ok_flag = False
                for i in range(len(self.payload_queue)):
                    p = self.payload_queue[i]
                    if check_code(p) == receive_data['code']:
                        ok_flag = True
                        # 从报文队列中剔除
                        del self.payload_queue[i]
                        break

                if receive_data['type'] == 'register':
                    self.register_signal = False

                if receive_data['type'] == 'logout':
                    self.logout_signal = False

                if ok_flag is False:
                    raise Exception("错误的消息校验码" + receive_data['code'])

            # 错误消息
            elif data_type == 'error':
                error_type = receive_data['type']
                error_message = receive_data['message']
                if error_type == 'login':
                    print('[ x ] ' + error_message)
                    time.sleep(2)
                    self.login_signal = False  # 更新信号量
                elif error_type == 'register':
                    print('[ x ] ' + error_message)
                    time.sleep(2)
                    self.register_signal = False  # 更新信号量
                elif error_type == 'logout':
                    print('[ x ] ' + error_message)
                    time.sleep(2)
                    self.logout_signal = False  # 更新信号量
                else:
                    print('[ x ] ' + error_message)


            # 接收到服务器下发的 Token
            elif data_type == 'send_token':
                # 保存 Token，更新登录状态
                self.account = receive_data['account']
                self.token = receive_data['token']
                self.login_status = True
                print('[ - ] 登录成功...')
                time.sleep(1)
                self.login_signal = False  # 更新信号量

            # 进入群聊后接收群聊消息
            elif data_type == 'receive_group_message' and self.group_status:
                print("[%s] %s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), receive_data['from'],
                                       receive_data['message']))

            # 接收私有消息
            elif data_type == 'receive_private_message':
                from_account = receive_data['from']
                message = receive_data['message']
                print('收到来自 %s 的私有消息: %s' % (from_account, message))

            # 登录欢迎消息
            elif data_type == 'welcome':
                print("[ - ] 成功连接服务器")
                print(receive_data)
                self.ready_signal = False

            else:
                print("意外的返回消息类型 " + data_type)


server_ip = '127.0.0.1'
server_port = 5000


def start():
    client = Client(server_ip, server_port)
    # 启动接收消息线程
    group_thread = threading.Thread(target=client.receive_message_handler)
    group_thread.start()

    # 准备连接
    client.send(connect())
    while client.ready_signal:
        pass
    client.menu()


if __name__ == '__main__':
    start()
