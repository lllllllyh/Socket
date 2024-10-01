import sys
import socket
import threading#用于多线程
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QComboBox

class ServerApp(QWidget):#继承QWidgt
    def __init__(self):
        super().__init__()
        self.initUI()#初始化界面
        self.clients = {}  # 存储用户信息 {username: password}

    def initUI(self):
        self.setWindowTitle('服务器端')
        layout = QVBoxLayout()#垂直布局
        #QLineEdit创建三个文本输入框,setplaceholderText设置提示文字
        # 用户名输入
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        # 密码输入
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        layout.addWidget(self.password_input)

        # 重复密码输入
        self.reenter_password_input = QLineEdit(self)
        self.reenter_password_input.setPlaceholderText("重复密码")
        layout.addWidget(self.reenter_password_input)

        # QPushButton添加用户按钮,click.connect绑定按钮点击事件到add.user方法
        self.add_user_btn = QPushButton("添加用户", self)
        self.add_user_btn.clicked.connect(self.add_user)
        layout.addWidget(self.add_user_btn)

        # 协议选择QComboBox下拉菜单
        self.protocol_combo = QComboBox(self)
        self.protocol_combo.addItem("TCP")
        self.protocol_combo.addItem("UDP")
        layout.addWidget(self.protocol_combo)

        # QTextEdit日志区域
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # 开始服务器按钮
        self.start_btn = QPushButton("开始", self)
        self.start_btn.clicked.connect(self.start_server)
        layout.addWidget(self.start_btn)

        # 关闭连接按钮
        self.stop_btn = QPushButton("关闭连接", self)
        self.stop_btn.clicked.connect(self.stop_server)
        layout.addWidget(self.stop_btn)

        self.setLayout(layout)
        self.server_socket = None
        self.is_running = False
        self.protocol = "TCP"#设置默认

    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.reenter_password_input.text()

        if username and password == confirm_password:
            self.clients[username] = password
            self.log_area.append(f"用户 {username} 已添加。")
        else:
            self.log_area.append("密码不匹配或数据无效。")

    def start_server(self):
        self.protocol = self.protocol_combo.currentText()

        if self.protocol == "TCP":
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 8080))
            self.server_socket.listen(5)
        elif self.protocol == "UDP":
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind(('0.0.0.0', 8080))

        self.is_running = True
        self.log_area.append(f"服务器已启动，使用 {self.protocol} 协议监听端口 8080。")

        if self.protocol == "TCP":
            threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while self.is_running:
            client_socket, addr = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        self.log_area.append(f"来自 {addr} 的新连接")

        # 接收用户名和密码
        credentials = client_socket.recv(1024).decode('utf-8')
        username, password = credentials.split(':')

        # 验证用户名和密码
        if username in self.clients and self.clients[username] == password:
            client_socket.send("登录成功".encode('utf-8'))
            self.log_area.append(f"用户 {username} 登录成功。")
        else:
            client_socket.send("登录失败".encode('utf-8'))
            self.log_area.append(f"用户 {username} 登录失败，用户名或密码错误。")
            client_socket.close()
            return

        # 处理后续消息
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.log_area.append(f"收到来自 {username} 的消息：{data}")
        except ConnectionResetError:
            self.log_area.append(f"来自 {addr} 的连接已断开")
        finally:
            client_socket.close()

    def stop_server(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            self.log_area.append("服务器已关闭。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_app = ServerApp()
    server_app.show()
    sys.exit(app.exec_())
