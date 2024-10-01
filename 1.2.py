import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QGroupBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ServerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.clients = {}  # 存储用户信息 {username: password}
        self.client_sockets = []  # 用于存储已连接的客户端套接字

    def initUI(self):
        self.setWindowTitle('服务器端 - 花里胡哨版')
        self.setGeometry(300, 300, 400, 500)
        layout = QVBoxLayout()

        # 创建顶部的欢迎标签
        title_label = QLabel("🌟 服务器管理工具 🌟", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setStyleSheet("color: darkblue; background-color: lightgray; padding: 10px; border-radius: 10px;")
        layout.addWidget(title_label)

        # 用户信息区域
        user_info_box = QGroupBox("用户信息", self)
        user_layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("请输入用户名")
        user_layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        user_layout.addWidget(self.password_input)

        self.reenter_password_input = QLineEdit(self)
        self.reenter_password_input.setPlaceholderText("请再次输入密码")
        self.reenter_password_input.setEchoMode(QLineEdit.Password)
        user_layout.addWidget(self.reenter_password_input)

        self.add_user_btn = QPushButton("➕ 添加用户", self)
        self.add_user_btn.setStyleSheet("background-color: #5cb85c; color: white; padding: 8px; border-radius: 5px;")
        self.add_user_btn.clicked.connect(self.add_user)
        user_layout.addWidget(self.add_user_btn)

        user_info_box.setLayout(user_layout)
        layout.addWidget(user_info_box)

        # 协议选择区域
        protocol_box = QGroupBox("选择协议", self)
        protocol_layout = QHBoxLayout()

        # TCP 和 UDP 切换按钮
        self.tcp_btn = QPushButton("TCP", self)
        self.udp_btn = QPushButton("UDP", self)

        # 设置初始按钮样式
        self.tcp_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.udp_btn.setStyleSheet("background-color: #ccc; color: black; padding: 10px; border-radius: 5px;")

        self.tcp_btn.clicked.connect(self.select_tcp)
        self.udp_btn.clicked.connect(self.select_udp)

        protocol_layout.addWidget(self.tcp_btn)
        protocol_layout.addWidget(self.udp_btn)

        protocol_box.setLayout(protocol_layout)
        layout.addWidget(protocol_box)

        # 日志区域
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont('Courier', 10))
        self.log_area.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px;")
        layout.addWidget(self.log_area)

        # 按钮区域
        button_layout = QHBoxLayout()

        self.start_btn = QPushButton("🚀 启动服务器", self)
        self.start_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.start_btn.clicked.connect(self.start_server)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("⛔ 停止服务器", self)
        self.stop_btn.setStyleSheet("background-color: #d9534f; color: white; padding: 10px; border-radius: 5px;")
        self.stop_btn.clicked.connect(self.stop_server)
        button_layout.addWidget(self.stop_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        self.server_socket = None
        self.is_running = False
        self.protocol = "TCP"  # 设置默认协议

    def select_tcp(self):
        """切换到TCP协议"""
        self.protocol = "TCP"
        self.tcp_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.udp_btn.setStyleSheet("background-color: #ccc; color: black; padding: 10px; border-radius: 5px;")
        self.log_area.append("已选择 TCP 协议。")

    def select_udp(self):
        """切换到UDP协议"""
        self.protocol = "UDP"
        self.udp_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.tcp_btn.setStyleSheet("background-color: #ccc; color: black; padding: 10px; border-radius: 5px;")
        self.log_area.append("已选择 UDP 协议。")

    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm_password = self.reenter_password_input.text()

        if username and password == confirm_password:
            self.clients[username] = password
            self.log_area.append(f"✅ 用户 {username} 已添加。")
        else:
            self.log_area.append("❌ 密码不匹配或数据无效。")

    def start_server(self):
        if self.protocol == "TCP":
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 8080))
            self.server_socket.listen(5)
        elif self.protocol == "UDP":
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_socket.bind(('0.0.0.0', 8080))

        self.is_running = True
        self.log_area.append(f"🌐 服务器已启动，使用 {self.protocol} 协议监听端口 8080。")

        if self.protocol == "TCP":
            threading.Thread(target=self.accept_clients).start()

    def accept_clients(self):
        while self.is_running:
            client_socket, addr = self.server_socket.accept()
            self.client_sockets.append(client_socket)  # 记录已连接的客户端
            threading.Thread(target=self.handle_client, args=(client_socket, addr)).start()

    def handle_client(self, client_socket, addr):
        self.log_area.append(f"🌟 来自 {addr} 的新连接")

        # 接收用户名和密码
        credentials = client_socket.recv(1024).decode('utf-8')
        username, password = credentials.split(':')

        # 验证用户名和密码
        if username in self.clients and self.clients[username] == password:
            client_socket.send("登录成功".encode('utf-8'))
            self.log_area.append(f"✅ 用户 {username} 登录成功。")
        else:
            client_socket.send("登录失败".encode('utf-8'))
            self.log_area.append(f"❌ 用户 {username} 登录失败，用户名或密码错误。")
            client_socket.close()
            return

        # 处理后续消息
        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break
                self.log_area.append(f"📨 收到来自 {username} 的消息：{data}")
                self.broadcast_message(f"{username}: {data}", client_socket)  # 将消息广播给其他客户端
        except ConnectionResetError:
            self.log_area.append(f"❌ 来自 {addr} 的连接已断开")
        finally:
            self.client_sockets.remove(client_socket)
            client_socket.close()

    def broadcast_message(self, message, sender_socket):
        """广播消息给其他客户端"""
        for client_socket in self.client_sockets:
            if client_socket != sender_socket:
                try:
                    client_socket.send(message.encode('utf-8'))
                except:
                    client_socket.close()
                    self.client_sockets.remove(client_socket)

    def stop_server(self):
        self.is_running = False
        if self.server_socket:
            self.server_socket.close()
            self.log_area.append("🔴 服务器已关闭。")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    server_app = ServerApp()
    server_app.show()
    sys.exit(app.exec_())
