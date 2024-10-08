import os
import tkinter as tk
import traceback
import LoginWindow
import SelectWindow
import ShellWindow
from tkinter import messagebox

# 获取当前工作目录
current_directory = os.path.dirname(os.path.abspath(__file__))
package_name = "deploy.tar.gz"
module_list = ["seago-bom", "seago-sso", "seago-platform"]


class WelcomeWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        self.package_name = package_name
        self.module_list = module_list
        # 调用 Tk 类的构造函数
        tk.Tk.__init__(self, *args, **kwargs)
        # 设置窗口图标
        self.wm_iconbitmap('{}\logo.ico'.format(current_directory))
        # 设置窗口标题
        self.directory = None
        self.client = None
        self.title("虎魄部署程序")
        # 禁止用户改变窗口大小
        self.resizable(False, False)
        # 设置初始大小
        self.geometry("600x450")
        # 中心logo
        self.img = tk.PhotoImage(file='{}\logo.ppm'.format(current_directory))
        self.seago_logo = tk.Label(self, image=self.img)
        self.seago_logo.pack(pady=5)
        # 欢迎文本
        self.welcome_text = tk.Label(self, text="欢迎使用虎魄系统", font=("Arial", 24))
        self.welcome_text.pack(pady=5)
        # 服务器ip提示
        self.show_ip = tk.Label(self, text="当前服务器:未连接", font=("Arial", 9))
        self.show_ip.place(relx=0.01, rely=0.01)

        self.log_in = tk.Button(text='登录服务器', command=self.login_server)
        self.log_in.place(relx=0.01, rely=0.08)

        # 安装目录文本
        self.directory_label = tk.Label(self, text="请选择安装目录:")
        self.directory_label.place(relx=0.1, rely=0.3)
        # 目录输入框
        self.directory_entry = tk.Entry(self, width=70)
        self.directory_entry.place(relx=0.1, rely=0.35)
        # 目录选择按钮
        self.browse_button = tk.Button(self, text="刷新", command=self.browse_directory)
        self.browse_button.place(relx=0.1, rely=0.41)
        # 模块选择框
        self.app_text = tk.Label(self, text="安装的模块")
        self.app_text.place(relx=0.1, rely=0.5)
        # 模块选择框
        self.app_list = tk.Label(self, text="", width=70, height=5, bg="gray")
        self.app_list.place(relx=0.1, rely=0.6)
        # 模块选择按钮
        self.select_button = tk.Button(self, text="选择模块", command=self.select_window)
        self.select_button.place(relx=0.1, rely=0.81)

        # 开始部署按钮
        self.deploy_start = tk.Button(self, text="开始部署", command=self.execute_shell)
        self.deploy_start.place(relx=0.83, rely=0.81)

        self.deploy_dir = None
        self.deploy_ip = None
        self.deploy_app = None

    def login_server(self):
        LoginWindow.CreateLoginWindow(self)

    def select_window(self):
        SelectWindow.CreateSelectWindow(self)

    def execute_shell(self):
        self.deploy_dir = self.directory_entry.get()
        self.deploy_app = self.app_list.cget("text")
        if self.deploy_dir and self.deploy_ip and self.deploy_app:
            self.withdraw()
            self.deploy_start.config(state=tk.DISABLED)
            ShellWindow.CreateShellWindow(self)
        else:
            messagebox.showerror("error", "请输入完整部署信息！")

    def browse_directory(self):
        stdin, stdout, stderr = self.client.exec_command(
            "df --output=target | tail -n +2 | xargs -I {} df -h {} | sort -k4 -h | tail -n 1 | awk '{print $NF}'")
        self.directory = stdout.read().decode("utf-8")
        if self.directory == "/\n":
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, "/opt")
        elif self.directory == "/home\n":
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, "/home")
        else:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, self.directory)

    def update_app_text(self, data):
        app_list = ",".join(data)
        self.app_list.config(text=app_list)


if __name__ == "__main__":
    try:
        app = WelcomeWindow()
        app.mainloop()
    except Exception as e:
        print("程序出错:", e)
        traceback.print_exc()
        input("按任意键退出...")
