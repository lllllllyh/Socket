import socket
import sys
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLineEdit

# 模拟的用户数据库，包含合法的用户名和密码
valid_users = {"admin": "admin123", "user1": "user123", "user2": "user456", "1": "1", "2": "2"}

class ServerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("服务器")
        self.setGeometry(900, 250, 800, 800)

        self.status_label = QLabel("服务器状态: 未启动", self)
        self.text_area = QTextEdit(self)
        self.text_area.setReadOnly(True)

        self.protocol_label = QLabel("协议:")
        self.protocol_input = QLineEdit(self)
        self.protocol_input.setPlaceholderText("输入协议类型 (tcp/udp)")

        self.port_label = QLabel("端口:")
        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("输入端口")
        self.port_input.setText("8080")

        self.start_button = QPushButton("启动服务器", self)
        self.start_button.clicked.connect(self.start_server)

        self.stop_button = QPushButton("停止服务器", self)
        self.stop_button.setDisabled(True)
        self.stop_button.clicked.connect(self.stop_server)

        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.protocol_label)
        layout.addWidget(self.protocol_input)
        layout.addWidget(self.port_label)
        layout.addWidget(self.port_input)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.text_area)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.server_socket = None
        self.server_running = False
        self.clients = []
        self.client_addresses = []  # For UDP
        self.client_usernames = {}  # For tracking usernames of TCP clients

    def log_message(self, message):
        self.text_area.append(message)

    def start_server(self):
        try:
            port = int(self.port_input.text())
            protocol = self.protocol_input.text().strip().lower()

            self.server_running = True
            if protocol == "tcp":
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.bind(('127.0.0.1', port))
                self.server_socket.listen(5)
                threading.Thread(target=self.run_tcp_server, daemon=True).start()
            elif protocol == "udp":
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.server_socket.bind(('127.0.0.1', port))
                threading.Thread(target=self.run_udp_server, daemon=True).start()
            else:
                self.log_message("不支持的协议类型")
                return

            self.status_label.setText("服务器状态: 运行中")
            self.start_button.setDisabled(True)
            self.stop_button.setDisabled(False)

        except Exception as e:
            self.log_message(f"服务器启动失败: {str(e)}")

    def stop_server(self):
        self.server_running = False
        if self.server_socket:
            self.server_socket.close()
        self.status_label.setText("服务器状态: 已停止")
        self.start_button.setDisabled(False)
        self.stop_button.setDisabled(True)

    def run_tcp_server(self):
        self.log_message("TCP 服务器正在监听...")
        while self.server_running:
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_tcp_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                self.log_message(f"TCP 服务器错误: {str(e)}")

    def run_udp_server(self):
        self.log_message("UDP 服务器正在监听...")
        while self.server_running:
            try:
                message, addr = self.server_socket.recvfrom(1024)
                self.handle_udp_message(message, addr)
            except Exception as e:
                self.log_message(f"UDP 服务器错误: {str(e)}")

    def handle_tcp_client(self, client_socket):
        try:
            while self.server_running:
                data = client_socket.recv(1024).decode('utf-8')
                if data:
                    if data.startswith("REGISTER,"):
                        _, username, password = data.split(',')
                        if username in valid_users:
                            client_socket.send("注册失败: 用户名已存在".encode('utf-8'))
                            self.log_message(f"注册失败: 用户名 {username} 已存在")
                        else:
                            valid_users[username] = password
                            client_socket.send("注册成功".encode('utf-8'))
                            self.log_message(f"用户 {username} 注册成功")
                    elif data.startswith("LOGIN,"):
                        _, username, password = data.split(',')
                        if username in valid_users and valid_users[username] == password:
                            client_socket.send("登录成功".encode('utf-8'))
                            self.client_usernames[client_socket] = username
                            self.log_message(f"用户 {username} 登录成功")
                        else:
                            client_socket.send("登录失败".encode('utf-8'))
                            self.log_message(f"用户 {username} 登录失败")
                    elif data.startswith("MESSAGE:"):
                        message = data[8:]
                        username = self.client_usernames.get(client_socket, "未知用户")
                        formatted_message = f"{username}: {message}"
                        self.broadcast(formatted_message)
                    else:
                        client_socket.send("未知请求".encode('utf-8'))
                else:
                    break
        except Exception as e:
            self.log_message(f"处理 TCP 客户端请求时出现错误: {str(e)}")
        finally:
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            if client_socket in self.client_usernames:
                del self.client_usernames[client_socket]
            client_socket.close()



    def handle_udp_message(self, message, addr):
        try:
            message = message.decode('utf-8')
            if message.startswith("REGISTER,"):
                _, username, password = message.split(',')
                if username in valid_users:
                    self.server_socket.sendto("注册失败: 用户名已存在".encode('utf-8'), addr)
                    self.log_message(f"注册失败: 用户名 {username} 已存在")
                else:
                    valid_users[username] = password
                    self.server_socket.sendto("注册成功".encode('utf-8'), addr)
                    self.log_message(f"用户 {username} 注册成功")
            elif message.startswith("LOGIN,"):
                _, username, password = message.split(',')
                if username in valid_users and valid_users[username] == password:
                    self.server_socket.sendto("登录成功".encode('utf-8'), addr)
                    self.client_addresses.append((username, addr))
                    self.log_message(f"用户 {username} 登录成功")
                else:
                    self.server_socket.sendto("登录失败".encode('utf-8'), addr)
                    self.log_message(f"用户 {username} 登录失败")
            elif message.startswith("MESSAGE:"):
                message_content = message[8:]
                username = next((user for user, address in self.client_addresses if address == addr), "未知用户")
                formatted_message = f"{username}: {message_content}"
                self.broadcast_udp(formatted_message, addr)
            else:
                self.server_socket.sendto("未知请求".encode('utf-8'), addr)
        except Exception as e:
            self.log_message(f"处理 UDP 客户端请求时出现错误: {str(e)}")


    def broadcast(self, message):
        for client in self.clients:
            try:
                client.send(f"{message}".encode('utf-8'))
            except Exception as e:
                self.log_message(f"广播消息失败: {str(e)}")

    def broadcast_udp(self, message, sender_addr):
        for addr in self.client_addresses:
            try:
                if addr != sender_addr:
                    self.server_socket.sendto(f"{message}".encode('utf-8'), addr)
            except Exception as e:
                self.log_message(f"UDP 广播消息失败: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ServerWindow()
    window.show()
    sys.exit(app.exec_())
