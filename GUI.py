import queue
import tkinter as tk
import subprocess
import threading
from tkinter import filedialog as tkFileDialog
from tkinter import messagebox as tkMessageBox

def run_shell_command(command):
    try:
        # 执行 Shell 命令，并分别捕获标准输出和标准错误
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            return stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        # 捕获命令执行中的错误并提示用户
        tkMessageBox.showerror("命令执行错误", "命令执行失败: {e.output.decode('utf-8')}")


class WelcomeWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        # 调用 Tk 类的构造函数
        tk.Tk.__init__(self, *args, **kwargs)
        # 设置窗口图标
        self.wm_iconbitmap('E:/workspace/图形化部署/logo.ico')
        # 设置窗口标题
        self.directory = None
        self.title("虎魄部署程序")
        # 禁止用户改变窗口大小
        self.resizable(False, False)
        # 设置初始大小
        self.geometry("600x450")
        # 中心logo
        self.img = tk.PhotoImage(file='E:/workspace/图形化部署/logo.ppm')
        self.seago_logo = tk.Label(self, image=self.img)
        self.seago_logo.pack(pady=5)
        # 欢迎文本
        self.welcome_text = tk.Label(self, text="欢迎使用虎魄系统", font=("Arial", 24))
        self.welcome_text.pack(pady=5)
        # 服务器ip提示3
        self.server_ip = run_shell_command("hostname -I | awk '{print $1}'")
        self.show_ip = tk.Label(self, text="当前服务器ip为:{}".format(self.server_ip), font=("Arial", 9))
        self.show_ip.place(relx=0.01, rely=0.01)

        # 安装目录文本
        self.directory_label = tk.Label(self, text="请选择安装目录:")
        self.directory_label.place(relx=0.1, rely=0.3)
        # 目录输入框
        self.directory_entry = tk.Entry(self, width=70)
        self.directory_entry.place(relx=0.1, rely=0.35)
        # 目录选择按钮
        self.browse_button = tk.Button(self, text="浏览目录", command=self.browse_directory)
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

    def select_window(self):
        CreateSelectWindow(self)

    def execute_shell(self):
        self.withdraw()
        self.deploy_start.config(state=tk.DISABLED)
        CreateShellWindow(self)

    def browse_directory(self):
        self.directory = tkFileDialog.askdirectory()
        if self.directory:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, self.directory)

    def update_app_text(self, data):
        app_list = ",".join(data)
        self.app_list.config(text=app_list)


class CreateSelectWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        # 设置窗口图标
        self.selected_items = None
        self.wm_iconbitmap('./logo.ico')
        # 设置窗口标题
        self.title("选择想要安装的模块")
        # 禁止用户改变窗口大小
        self.resizable(False, False)
        # 设置初始大小
        self.geometry("600x450")
        self.parent = parent

        self.check_vars = []
        options = ["seago-bom", "seago-sso", "seago-platform"]
        for option in options:
            var = tk.IntVar()
            chk = tk.Checkbutton(self, text=option, variable=var, command=self.update_selection)
            chk.pack(anchor="w")
            self.check_vars.append((var, option))

        self.confirm_button = tk.Button(self, text="确认并关闭", command=self.on_confirm)
        self.confirm_button.pack(pady=20)

    def update_selection(self):
        self.selected_items = [option for var, option in self.check_vars if var.get() == 1]

    def on_confirm(self):
        data = list(self.selected_items)
        self.parent.update_app_text(data)  # 调用主窗口的 update_app_text 方法
        self.destroy()


class CreateShellWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.process = None
        self.title("实时 Shell 输出")
        self.geometry("1200x600")

        # 创建 Text 小部件用于显示输出
        self.text_area = tk.Text(self, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')
        # 终止进程
        self.stop_button = tk.Button(self, text="终止进程", command=self.stop_shell_command)
        self.stop_button.pack(pady=10)
        # 创建队列来处理线程与Tkinter主线程的通信
        self.queue = queue.Queue()
        # 设置更新方法来持续检查队列中的内容
        self.after(100, self.update_text_area)
        self.run_shell_command()

    def run_shell_command(self):

        # 使用线程来运行 Shell 命令，以免阻塞主线程
        thread = threading.Thread(target=self.execute_command)
        thread.start()

    def execute_command(self):
        # 执行 Shell 命令
        command = u"./args_test.sh {} {} {}".format(self.parent.directory_entry.get(),
                                                    self.parent.app_list.cget("text"), self.parent.server_ip)
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        # 持续读取输出并将其放入队列
        while True:
            if self.process is None:
                break  # 如果进程已经被终止，则退出循环
            line = self.process.stdout.readline()
            if not line:
                break
            self.queue.put(line.decode('utf-8'))

        # 检查子进程是否已经结束
        if self.process is not None:
            self.process.stdout.close()
            self.process.wait()

    def update_text_area(self):
        # 从队列中获取数据并更新 Text 小部件
        try:
            while True:
                text = self.queue.get_nowait()
                self.text_area.insert(tk.END, text)
                self.text_area.see(tk.END)
        except queue.Empty:
            pass

        if self.process.returncode == 0:  # 终止正在运行的进程
            tkMessageBox.showinfo("info", u"部署成功")
            self.quit()
            self.parent.destroy()
        if self.process.returncode == 1:
            tkMessageBox.showerror("error", u"部署失败！")
            self.quit()
            self.parent.destroy()
        # 继续检查队列

        self.after(100, self.update_text_area)

    def stop_shell_command(self):

        if self.process:
            self.process.terminate()  # 终止正在运行的进程
            tkMessageBox.showerror("error", u"部署失败！")
            self.process = None
        self.quit()
        self.parent.destroy()


if __name__ == "__main__":
    app = WelcomeWindow()
    app.mainloop()
