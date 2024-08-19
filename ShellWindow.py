import queue
import tkinter as tk
import subprocess
import threading
from tkinter import messagebox
import os

# 获取当前工作目录
current_directory = os.path.dirname(os.path.abspath(__file__))


class CreateShellWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.process = None
        self.title("实时 Shell 输出")
        self.geometry("1200x600")
        self.wm_iconbitmap('{}\logo.ico'.format(current_directory))

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
        command = u"./args_test.sh {} {}".format(self.parent.directory_entry.get(),
                                                 self.parent.app_list.cget("text"))
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
            messagebox.showinfo("info", u"部署成功")
            self.quit()
            self.parent.destroy()
        if self.process.returncode == 1:
            messagebox.showerror("error", u"部署失败！")
            self.quit()
            self.parent.destroy()
        # 继续检查队列

        self.after(100, self.update_text_area)

    def stop_shell_command(self):

        if self.process:
            self.process.terminate()  # 终止正在运行的进程
            messagebox.showerror("error", u"部署失败！")
            self.process = None
        self.quit()
        self.parent.destroy()
