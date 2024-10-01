import sys
import socket
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QFileDialog, \
    QComboBox


class ClientApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('客户端')
        layout = QVBoxLayout()

        # 用户名输入
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        layout.addWidget(self.username_input)

        # 密码输入
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        # 协议选择
        self.protocol_combo = QComboBox(self)
        self.protocol_combo.addItem("TCP")
        self.protocol_combo.addItem("UDP")
        layout.addWidget(self.protocol_combo)

        # 登录按钮
        self.login_btn = QPushButton("登录", self)
        self.login_btn.clicked.connect(self.login)
        layout.addWidget(self.login_btn)

        # 文本区域，用于发送消息
        self.message_area = QTextEdit(self)
        layout.addWidget(self.message_area)

        # 发送按钮
        self.send_btn = QPushButton("发送", self)
        self.send_btn.clicked.connect(self.send_message)
        layout.addWidget(self.send_btn)

        # 发送文件按钮
        self.send_file_btn = QPushButton("发送文件", self)
        self.send_file_btn.clicked.connect(self.send_file)
        layout.addWidget(self.send_file_btn)

        self.setLayout(layout)
        self.client_socket = None
        self.protocol = "TCP"
        self.server_address = ('127.0.0.1', 8080)  # 服务器地址

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.protocol = self.protocol_combo.currentText()

        if username and password:
            if self.protocol == "TCP":
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(self.server_address)
                self.client_socket.send(f'{username}:{password}'.encode('utf-8'))

                # 接收服务器的登录结果
                response = self.client_socket.recv(1024).decode('utf-8')
                if response == "登录成功":
                    print("登录成功")
                else:
                    print("登录失败")
                    self.client_socket.close()
            elif self.protocol == "UDP":
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                # 使用 sendto 发送数据到服务器
                self.client_socket.sendto(f'{username}:{password}'.encode('utf-8'), self.server_address)

                # 使用 recvfrom 接收服务器的响应
                response, _ = self.client_socket.recvfrom(1024)
                response = response.decode('utf-8')
                if response == "登录成功":
                    print("登录成功")
                else:
                    print("登录失败")
                    self.client_socket.close()

    def send_message(self):
        message = self.message_area.toPlainText()
        if self.client_socket:
            if self.protocol == "TCP":
                self.client_socket.send(message.encode('utf-8'))
            elif self.protocol == "UDP":
                self.client_socket.sendto(message.encode('utf-8'), self.server_address)

    def send_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择文件")
        if file_name and self.client_socket:
            with open(file_name, 'r') as file:
                data = file.read()
                if self.protocol == "TCP":
                    self.client_socket.send(data.encode('utf-8'))
                elif self.protocol == "UDP":
                    self.client_socket.sendto(data.encode('utf-8'), self.server_address)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    client_app = ClientApp()
    client_app.show()
    sys.exit(app.exec_())
