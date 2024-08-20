import os
import tkinter as tk

current_directory = os.path.dirname(os.path.abspath(__file__))


class CreateSelectWindow(tk.Toplevel):
    def __init__(self, parent):
        tk.Toplevel.__init__(self, parent)
        # 设置窗口图标
        self.selected_items = None
        self.wm_iconbitmap('{}\logo.ico'.format(current_directory))
        # 设置窗口标题
        self.title("选择想要安装的模块")
        # 禁止用户改变窗口大小
        self.resizable(False, False)
        # 设置初始大小
        self.geometry("600x450")
        self.parent = parent

        self.check_vars = []
        options = self.parent.module_list
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
