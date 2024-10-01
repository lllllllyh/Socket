import sys
import socket
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import QTimer

class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("客户端")
        self.setGeometry(900, 250, 800, 600)

        self.protocol_label = QLabel("协议:")
        self.protocol_input = QLineEdit(self)
        self.protocol_input.setPlaceholderText("输入协议类型 (tcp/udp)")
        self.protocol_input.setText("tcp")

        self.port_label = QLabel("端口:")
        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("输入端口")
        self.port_input.setText("8080")

        self.username_label = QLabel("用户名:")
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("输入用户名")

        self.password_label = QLabel("密码:")
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("输入密码")
        
        self.register_label = QLabel("注册:")
        self.register_button = QPushButton("注册", self)
        self.register_button.clicked.connect(self.register_user)

        self.connect_button = QPushButton("连接", self)
        self.connect_button.clicked.connect(self.connect_to_server)

        self.message_input = QLineEdit(self)
        self.message_input.setPlaceholderText("输入消息...")

        self.send_button = QPushButton("发送", self)
        self.send_button.clicked.connect(self.send_message)

        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.register_label)
        layout.addWidget(self.register_button)
        layout.addWidget(self.protocol_label)
        layout.addWidget(self.protocol_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.connect_button)
        layout.addWidget(self.message_input)
        layout.addWidget(self.send_button)
        layout.addWidget(self.text_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.client_socket = None
        self.receive_thread = None
    
    def register_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            self.show_error("用户名和密码不能为空")
            return

        response = self.send_registration(username, password)
        if response['status'] == 'success':
            self.show_message("注册成功")
        else:
            self.show_error(response['message'])

    def send_registration(self, username, password):
        try:
            # 示例：连接服务器并发送注册请求
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect(('127.0.0.1', 8080))  # 端口应与服务器端设置的端口一致
            registration_message = f"REGISTER,{username},{password}"
            self.server_socket.send(registration_message.encode('utf-8'))

            response = self.server_socket.recv(1024).decode('utf-8')
            self.server_socket.close()
            return {'status': 'success' if response == '注册成功' else 'error', 'message': response}
        except Exception as e:
            self.show_error(f"连接服务器失败: {str(e)}")
            return {'status': 'error', 'message': '连接服务器失败'}

    def show_message(self, message):
        QMessageBox.information(self, "信息", message)

    def show_error(self, message):
        QMessageBox.critical(self, "错误", message)

    def connect_to_server(self):
        username = self.username_input.text()
        password = self.password_input.text()
        port = self.port_input.text()
        protocol = self.protocol_input.text().strip().lower()

        if not username or not password or not port or not protocol:
            QMessageBox.warning(self, "输入错误", "所有字段都必须填写")
            return

        try:
            port = int(port)

            if protocol == "tcp":
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(('127.0.0.1', port))
                self.client_socket.send(f"LOGIN,{username},{password}".encode('utf-8'))
                response = self.client_socket.recv(1024).decode('utf-8')
                if response == "登录成功":
                    self.text_area.append("连接成功")
                    self.receive_thread = threading.Thread(target=self.receive_tcp, daemon=True)
                    self.receive_thread.start()
                else:
                    QMessageBox.warning(self, "登录失败", response)
            elif protocol == "udp":
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.client_socket.sendto(f"LOGIN,{username},{password}".encode('utf-8'), ('127.0.0.1', port))
                response, _ = self.client_socket.recvfrom(1024)
                response = response.decode('utf-8')
                if response == "登录成功":
                    self.text_area.append("连接成功")
                    self.receive_thread = threading.Thread(target=self.receive_udp, daemon=True)
                    self.receive_thread.start()
                else:
                    QMessageBox.warning(self, "登录失败", response)
            else:
                QMessageBox.warning(self, "协议错误", "不支持的协议类型")
                return

        except Exception as e:
            QMessageBox.warning(self, "连接错误", str(e))

    def send_message(self):
        message = self.message_input.text()
        if not message:
            QMessageBox.warning(self, "发送错误", "消息不能为空")
            return

        protocol = self.protocol_input.text().strip().lower()
        if protocol == "tcp":
            self.client_socket.send(f"MESSAGE:{message}".encode('utf-8'))
        elif protocol == "udp":
            self.client_socket.sendto(f"MESSAGE:{message}".encode('utf-8'), ('127.0.0.1', int(self.port_input.text())))

        self.message_input.clear()

    def receive_tcp(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if data:
                    self.text_area.append(data)
                else:
                    break
            except Exception as e:
                self.text_area.append(f"接收错误: {str(e)}")
                break

    def receive_udp(self):
        while True:
            try:
                data, _ = self.client_socket.recvfrom(1024)
                self.text_area.append(data.decode('utf-8'))
            except Exception as e:
                self.text_area.append(f"接收错误: {str(e)}")
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientWindow()
    window.show()
    sys.exit(app.exec_())
