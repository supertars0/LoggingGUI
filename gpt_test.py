import tkinter as tk
from tkinter import ttk
import paramiko
from threading import Thread
import os

# 定义传输文件的函数
def transfer_file():
    # SSH 连接配置
    hostname = 'remote_host_ip'
    port = 22
    username = 'your_username'
    password = 'your_password'
    local_file = 'C:/path/to/your/localfile.txt'
    remote_file = '/path/to/remote/destinationfile.txt'
    script_path = '/path/to/your/script.sh'

    try:
        # 创建SSH客户端并连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        # 使用SFTP进行文件传输
        sftp = ssh.open_sftp()
        file_size = os.path.getsize(local_file)

        # 设置进度条最大值
        progress_bar['maximum'] = file_size

        def progress_callback(transferred, total):
            progress_bar['value'] = transferred
            root.update_idletasks()

        sftp.put(local_file, remote_file, callback=progress_callback)
        sftp.close()

        output_text.insert(tk.END, "文件传输完成，开始执行脚本...\n")
        output_text.see(tk.END)

        # 执行远程脚本
        stdin, stdout, stderr = ssh.exec_command(f'bash {script_path}')

        # 持续获取脚本输出并显示到窗口中
        for line in iter(stdout.readline, ""):
            output_text.insert(tk.END, line)
            output_text.see(tk.END)
            output_text.update_idletasks()

        ssh.close()

    except Exception as e:
        output_text.insert(tk.END, f"连接或执行失败: {e}\n")
        output_text.see(tk.END)

# 创建主窗口
root = tk.Tk()
root.title("文件传输与脚本执行")

# 创建进度条
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)

# 创建一个文本框来显示脚本输出
output_text = tk.Text(root, wrap='word', height=20, width=80)
output_text.pack(pady=20)

# 创建一个按钮来开始传输文件并执行脚本
start_button = tk.Button(root, text="传输文件并执行脚本", command=lambda: Thread(target=transfer_file).start())
start_button.pack(pady=10)

# 运行主循环
root.mainloop()
