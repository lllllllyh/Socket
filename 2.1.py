import sys
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QFileDialog, QLabel, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('🌟 客户端 - 美化版 🌟')
        self.setGeometry(400, 200, 500, 600)
        layout = QVBoxLayout()

        # 顶部欢迎标题
        title_label = QLabel("客户端连接界面", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 16, QFont.Bold))
        title_label.setStyleSheet("color: darkgreen; background-color: lightgray; padding: 10px; border-radius: 10px;")
        layout.addWidget(title_label)

        # 用户信息输入
        user_info_box = QGroupBox("用户信息", self)
        user_layout = QVBoxLayout()

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("请输入用户名")
        user_layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        user_layout.addWidget(self.password_input)

        user_info_box.setLayout(user_layout)
        layout.addWidget(user_info_box)

        # 协议选择（点击切换按钮）
        protocol_box = QGroupBox("选择协议", self)
        protocol_layout = QHBoxLayout()

        self.tcp_btn = QPushButton("TCP", self)
        self.udp_btn = QPushButton("UDP", self)

        self.tcp_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.udp_btn.setStyleSheet("background-color: #ccc; color: black; padding: 10px; border-radius: 5px;")

        self.tcp_btn.clicked.connect(self.select_tcp)
        self.udp_btn.clicked.connect(self.select_udp)

        protocol_layout.addWidget(self.tcp_btn)
        protocol_layout.addWidget(self.udp_btn)

        protocol_box.setLayout(protocol_layout)
        layout.addWidget(protocol_box)

        # 登录按钮
        self.login_btn = QPushButton("登录", self)
        self.login_btn.setStyleSheet("background-color: #5cb85c; color: white; padding: 10px; border-radius: 5px;")
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        # 消息区域
        self.message_area = QTextEdit(self)
        self.message_area.setPlaceholderText("输入要发送的消息...")
        layout.addWidget(self.message_area)

        # 发送消息按钮
        self.send_btn = QPushButton("发送消息", self)
        self.send_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.send_btn)

        # 发送文件按钮
        self.send_file_btn = QPushButton("发送文件", self)
        self.send_file_btn.setStyleSheet("background-color: #f0ad4e; color: white; padding: 10px; border-radius: 5px;")
        self.send_file_btn.clicked.connect(self.send_file)
        layout.addWidget(self.send_file_btn)

        # 日志区域
        self.log_area = QTextEdit(self)
        self.log_area.setReadOnly(True)
        self.log_area.setFont(QFont('Courier', 10))
        self.log_area.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc; padding: 10px;")
        layout.addWidget(self.log_area)

        self.setLayout(layout)
        self.client_socket = None
        self.protocol = "TCP"
        self.server_address = ('127.0.0.1', 8080)  # 默认服务器地址

    def select_tcp(self):
        """选择TCP协议"""
        self.protocol = "TCP"
        self.tcp_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.udp_btn.setStyleSheet("background-color: #ccc; color: black; padding: 10px; border-radius: 5px;")
        self.log_area.append("已选择 TCP 协议。")

    def select_udp(self):
        """选择UDP协议"""
        self.protocol = "UDP"
        self.udp_btn.setStyleSheet("background-color: #5bc0de; color: white; padding: 10px; border-radius: 5px;")
        self.tcp_btn.setStyleSheet("background-color: #ccc; color: black; padding: 10px; border-radius: 5px;")
        self.log_area.append("已选择 UDP 协议。")

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username and password:
            self.log_area.append(f"尝试登录，用户名: {username}, 协议: {self.protocol}")
            if self.protocol == "TCP":
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(self.server_address)
                self.client_socket.send(f'{username}:{password}'.encode('utf-8'))

                # 接收服务器的登录结果
                response = self.client_socket.recv(1024).decode('utf-8')
                if response == "登录成功":
                    self.log_area.append("✅ 登录成功")
                else:
                    self.log_area.append("❌ 登录失败")
                    self.client_socket.close()
            elif self.protocol == "UDP":
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.client_socket.sendto(f'{username}:{password}'.encode('utf-8'), self.server_address)

                response, _ = self.client_socket.recvfrom(1024)
                response = response.decode('utf-8')
                if response == "登录成功":
                    self.log_area.append("✅ 登录成功")
                else:
                    self.log_area.append("❌ 登录失败")
                    self.client_socket.close()

    def send_message(self):
        message = self.message_area.toPlainText()
        if self.client_socket and message:
            if self.protocol == "TCP":
                self.client_socket.send(message.encode('utf-8'))
            elif self.protocol == "UDP":
                self.client_socket.sendto(message.encode('utf-8'), self.server_address)
            self.log_area.append(f"📨 发送消息: {message}")

    def send_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_name and self.client_socket:
            with open(file_name, 'r') as file:
                data = file.read()
                if self.protocol == "TCP":
                    self.client_socket.send(data.encode('utf-8'))
                elif self.protocol == "UDP":
                    self.client_socket.sendto(data.encode('utf-8'), self.server_address)
            self.log_area.append(f"📁 发送文件: {file_name}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_app = ClientApp()
    client_app.show()
    sys.exit(app.exec_())
