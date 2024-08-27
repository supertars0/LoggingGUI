import os
import threading
import tkinter as tk
from tkinter import messagebox, ttk

# 获取当前工作目录
current_directory = os.path.dirname(os.path.abspath(__file__))


class CreateShellWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.ssh_client = self.parent.client
        self.process = None
        self.title("实时 Shell 输出")
        self.geometry("1200x600")
        self.wm_iconbitmap('{}\logo.ico'.format(current_directory))
        # 创建 Text 小部件用于显示输出
        self.text_area = tk.Text(self, wrap=tk.WORD)
        self.text_area.pack(expand=True, fill='both')

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", length=1200, mode="determinate")
        self.progress_bar.pack(pady=20)
        self.stop_button = tk.Button(self, text="结束部署", command=self.stop_shell_command)
        self.stop_button.pack(pady=10)

        threading.Thread(target=self.file_transport).start()


    def run_shell_command(self):

        # 使用线程来运行 Shell 命令，以免阻塞主线程
        shell_thread = threading.Thread(target=self.execute_command)
        shell_thread.start()

    def execute_command(self):
        # 执行 Shell 命令

        command = "sh /opt/args_test.sh {} {} {}".format(self.parent.deploy_dir,
                                                      self.parent.deploy_app, self.parent.deploy_ip)
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            for line in iter(stdout.readline, ""):
                self.text_area.insert(tk.END, line)
                self.text_area.see(tk.END)
                self.text_area.update_idletasks()
        except Exception as e:
            messagebox.showerror(f"执行失败：{e}\n")
        finally:
            self.ssh_client.close()

    def stop_shell_command(self):
        if self.ssh_client:
            self.ssh_client.close()
        self.quit()
        self.parent.destroy()

    def file_transport(self):
        local_file = current_directory + "/" + self.parent.package_name
        remote_file = self.parent.deploy_dir + "/" + self.parent.package_name
        sftp = self.parent.client.open_sftp()
        filesize = os.path.getsize(local_file)

        self.progress_bar['maximum'] = filesize

        def progress_callback(transferred, total):
            self.progress_bar['value'] = transferred
            self.update_idletasks()

        # 在主线程中更新 GUI 的 Text 小部件
        self.text_area.insert(tk.END, "文件传输中...\n")
        self.text_area.see(tk.END)
        self.text_area.update_idletasks()

        # 在单独的线程中进行文件传输
        try:
            sftp.put(local_file, remote_file, callback=progress_callback)
            # 文件传输完成后在主线程中更新 GUI
            self.text_area.insert(tk.END, "文件传输完成，开始执行脚本...\n")
            self.run_shell_command()
        except Exception as e:
            messagebox.showerror("传输失败", f"文件传输失败：{e}\n")
        finally:
            sftp.close()

        self.text_area.see(tk.END)
        self.text_area.update_idletasks()


