import paramiko

def execute_ssh_command(hostname, port, username, password, command):
    try:
        # 创建一个 SSH 客户端对象
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # 自动添加主机密钥

        # 连接到服务器
        client.connect(hostname, port, username, password)

        # 执行命令
        stdin, stdout, stderr = client.exec_command(command)

        # 获取命令输出
        output = stdout.read().decode()
        error = stderr.read().decode()

        if output:
            print("输出:")
            print(output)
        if error:
            print("错误:")
            print(error)

    finally:
        # 关闭连接
        client.close()

# 使用你的服务器信息进行连接和命令执行
hostname = "192.168.56.129"
port = 22
username = "root"
password = "root"
command = "uname -a"

execute_ssh_command(hostname, port, username, password, command)
