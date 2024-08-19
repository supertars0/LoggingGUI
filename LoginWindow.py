import tkinter as tk
from tkinter import messagebox
import os
import paramiko

current_directory = os.path.dirname(os.path.abspath(__file__))


class CreateLoginWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.log_in = self.parent.log_in
        self.title("登录linux服务器")
        self.geometry("300x250")
        self.wm_iconbitmap('{}\logo.ico'.format(current_directory))

        self.server_ip_text = tk.Label(self, text='服务器地址')
        self.server_ip_text.pack(pady=15)
        self.server_ip = tk.Entry(self, width=30)
        self.server_ip.pack(pady=5)
        self.server_username_text = tk.Label(self, text='用户名:')
        self.server_username_text.pack(pady=5)
        self.server_username = tk.Entry(self, width=30)
        self.server_username.pack(pady=5)

        self.server_password_test = tk.Label(self, text='密码:')
        self.server_password_test.pack(pady=5)
        self.server_password = tk.Entry(self, width=30, show='*')
        self.server_password.pack(pady=5)

        self.login_button = tk.Button(self, text='登录', command=self.login)
        self.login_button.pack(pady=5)

    def login(self):

        hostname = self.server_ip.get()
        username = self.server_username.get()
        password = self.server_password.get()
        port = 22
        self.parent.client = paramiko.SSHClient()
        self.parent.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥
        if hostname and username and password:
            # 连接到服务器
            try:
                self.parent.client.connect(hostname, port, username, password)
            except paramiko.ssh_exception:
                messagebox.showerror("error", "登录失败")
                self.log_in.config(state="normal")
            else:
                stdin, stdout, stderr = self.parent.client.exec_command("hostname -I | awk '{print $1}'")
                output = stdout.read().decode()
                self.parent.show_ip.config(text="当前服务器:{}".format(output), font=("Arial", 9))
                self.log_in.config(state="disabled", text="已连接")
            finally:
                self.destroy()
        else:
            messagebox.showerror("error", "请输入完整连接信息！")
