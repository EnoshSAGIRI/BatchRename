import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import datetime
import re
from pathlib import Path

class BatchRenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("批量文件重命名工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置样式
        self.style = ttk.Style()
        self.style.configure("TButton", font=("微软雅黑", 10))
        self.style.configure("TLabel", font=("微软雅黑", 10))
        self.style.configure("TRadiobutton", font=("微软雅黑", 10))
        
        # 变量初始化
        self.folder_path = tk.StringVar()
        self.prefix = tk.StringVar()
        self.sort_method = tk.StringVar(value="name")
        self.files = []
        self.preview_data = []
        
        # 创建界面
        self.create_widgets()
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 文件夹选择区域
        folder_frame = ttk.LabelFrame(main_frame, text="选择文件夹", padding="10")
        folder_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="浏览...", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        # 重命名设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="重命名设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)
        
        # 前缀设置
        prefix_frame = ttk.Frame(settings_frame)
        prefix_frame.pack(fill=tk.X, pady=5)
        ttk.Label(prefix_frame, text="文件名前缀:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(prefix_frame, textvariable=self.prefix, width=30).pack(side=tk.LEFT, padx=5)
        
        # 排序方式
        sort_frame = ttk.LabelFrame(settings_frame, text="排序方式", padding="10")
        sort_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(sort_frame, text="按文件名", variable=self.sort_method, value="name").pack(anchor=tk.W)
        ttk.Radiobutton(sort_frame, text="按修改时间", variable=self.sort_method, value="mtime").pack(anchor=tk.W)
        ttk.Radiobutton(sort_frame, text="按创建时间", variable=self.sort_method, value="ctime").pack(anchor=tk.W)
        ttk.Radiobutton(sort_frame, text="按文件大小", variable=self.sort_method, value="size").pack(anchor=tk.W)
        
        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="预览", command=self.preview_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="执行重命名", command=self.execute_rename).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.RIGHT, padx=5)
        
        # 预览区域
        preview_frame = ttk.LabelFrame(main_frame, text="预览", padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 创建Treeview用于显示预览结果
        columns = ("原文件名", "新文件名")
        self.preview_tree = ttk.Treeview(preview_frame, columns=columns, show="headings")
        
        # 设置列标题
        for col in columns:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=scrollbar.set)
        
        self.preview_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.status_var.set(f"已选择文件夹: {folder_selected}")
            self.load_files()
    
    def load_files(self):
        folder = self.folder_path.get()
        if not folder:
            return
        
        try:
            # 获取文件夹中的所有文件（不包括子文件夹）
            self.files = [f for f in Path(folder).iterdir() if f.is_file()]
            self.status_var.set(f"已加载 {len(self.files)} 个文件")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件时出错: {str(e)}")
            self.status_var.set("加载文件失败")
    
    def natural_sort_key(self, s):
        """实现Windows风格的自然排序键函数"""
        # 将字符串分割为文本和数字部分的列表
        return [int(text) if text.isdigit() else text.lower()
                for text in re.split(r'(\d+)', s)]
    
    def sort_files(self):
        sort_method = self.sort_method.get()
        
        if sort_method == "name":
            # 使用自然排序算法，与Windows资源管理器排序方式一致
            self.files.sort(key=lambda x: self.natural_sort_key(x.name))
        elif sort_method == "mtime":
            self.files.sort(key=lambda x: x.stat().st_mtime)
        elif sort_method == "ctime":
            self.files.sort(key=lambda x: x.stat().st_ctime)
        elif sort_method == "size":
            self.files.sort(key=lambda x: x.stat().st_size)
    
    def generate_new_names(self):
        prefix = self.prefix.get()
        self.preview_data = []
        
        for i, file in enumerate(self.files, 1):
            # 保留原始扩展名
            extension = file.suffix
            new_name = f"{prefix}{i:03d}{extension}"
            self.preview_data.append((file.name, new_name, file))
    
    def preview_rename(self):
        if not self.files:
            messagebox.showinfo("提示", "请先选择一个文件夹")
            return
        
        # 清空预览树
        for item in self.preview_tree.get_children():
            self.preview_tree.delete(item)
        
        # 按选定方式排序文件
        self.sort_files()
        
        # 生成新文件名
        self.generate_new_names()
        
        # 更新预览
        for old_name, new_name, _ in self.preview_data:
            self.preview_tree.insert("", tk.END, values=(old_name, new_name))
        
        self.status_var.set("预览已更新")
    
    def execute_rename(self):
        if not self.preview_data:
            messagebox.showinfo("提示", "请先预览重命名结果")
            return
        
        try:
            success_count = 0
            for old_name, new_name, file_path in self.preview_data:
                new_path = file_path.parent / new_name
                file_path.rename(new_path)
                success_count += 1
            
            messagebox.showinfo("成功", f"已成功重命名 {success_count} 个文件")
            self.status_var.set(f"已成功重命名 {success_count} 个文件")
            
            # 重新加载文件
            self.load_files()
            # 清空预览
            for item in self.preview_tree.get_children():
                self.preview_tree.delete(item)
        except Exception as e:
            messagebox.showerror("错误", f"重命名过程中出错: {str(e)}")
            self.status_var.set("重命名失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = BatchRenameApp(root)
    root.mainloop()