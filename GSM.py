import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("学生管理系统")
        self.root.geometry("900x600")
        
        # 学生数据存储
        self.students = []
        self.load_data()
        
        # 创建UI组件
        self.create_widgets()
        
        # 默认显示所有学生
        self.refresh_student_list()
    
    def create_widgets(self):
        # 设置样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # 标题
        title_label = ttk.Label(
            main_frame, 
            text="学生信息管理系统", 
            font=("微软雅黑", 16, "bold"),
            foreground="#2c3e50"
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 搜索区域
        search_frame = ttk.LabelFrame(main_frame, text="搜索与操作", padding="10")
        search_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索:").grid(row=0, column=0, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.grid(row=0, column=1, padx=(0, 10))
        
        search_btn = ttk.Button(search_frame, text="搜索", command=self.search_student)
        search_btn.grid(row=0, column=2, padx=(0, 10))
        
        reset_btn = ttk.Button(search_frame, text="重置搜索", command=self.refresh_student_list)
        reset_btn.grid(row=0, column=3, padx=(0, 10))
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(btn_frame, text="添加学生", command=self.add_student_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑学生", command=self.edit_student_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除学生", command=self.delete_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="导出数据", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关于", command=self.show_about).pack(side=tk.LEFT, padx=5)
        
        # 学生列表
        list_frame = ttk.LabelFrame(main_frame, text="学生列表", padding="10")
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建树状视图
        columns = ("学号", "姓名", "性别", "年龄", "专业", "电话", "邮箱")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # 设置列标题和宽度
        col_widths = [80, 100, 60, 60, 150, 120, 180]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=50)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set(f"学生总数: {len(self.students)}")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def refresh_student_list(self, students=None):
        """刷新学生列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 显示学生数据
        display_students = students if students is not None else self.students
        for student in display_students:
            self.tree.insert("", tk.END, values=(
                student.get("id", ""),
                student.get("name", ""),
                student.get("gender", ""),
                student.get("age", ""),
                student.get("major", ""),
                student.get("phone", ""),
                student.get("email", "")
            ))
        
        # 更新状态
        self.status_var.set(f"学生总数: {len(self.students)} | 显示: {len(display_students)}")
    
    def search_student(self):
        """搜索学生"""
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            self.refresh_student_list()
            return
        
        results = []
        for student in self.students:
            # 在所有字段中搜索关键词
            for key, value in student.items():
                if keyword in str(value).lower():
                    results.append(student)
                    break
        
        self.refresh_student_list(results)
    
    def add_student_window(self):
        """打开添加学生窗口"""
        self.open_student_dialog("添加学生")
    
    def edit_student_window(self):
        """打开编辑学生窗口"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个学生")
            return
        
        # 获取选中的学生信息
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        
        # 查找学生数据
        student = None
        for s in self.students:
            if str(s.get("id", "")) == str(student_id):
                student = s
                break
        
        if student:
            self.open_student_dialog("编辑学生", student)
    
    def open_student_dialog(self, title, student=None):
        """打开学生信息对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x450")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中对话框
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 创建表单
        form_frame = ttk.Frame(dialog, padding="20")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # 表单字段
        fields = [
            ("学号:", "id"),
            ("姓名:", "name"),
            ("性别:", "gender"),
            ("年龄:", "age"),
            ("专业:", "major"),
            ("电话:", "phone"),
            ("邮箱:", "email")
        ]
        
        entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=5)
            
            if key == "gender":
                # 性别使用下拉框
                gender_var = tk.StringVar()
                gender_combo = ttk.Combobox(form_frame, textvariable=gender_var, state="readonly", width=30)
                gender_combo['values'] = ("男", "女", "其他")
                gender_combo.grid(row=i, column=1, sticky=tk.W, pady=5)
                entries[key] = gender_var
            else:
                entry = ttk.Entry(form_frame, width=33)
                entry.grid(row=i, column=1, sticky=tk.W, pady=5)
                entries[key] = entry
            
            # 如果是编辑模式，填充数据
            if student and key in student:
                if key == "gender":
                    entries[key].set(student[key])
                else:
                    entries[key].insert(0, str(student[key]))
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        def save_student():
            """保存学生信息"""
            new_student = {}
            for key, entry in entries.items():
                if key == "gender":
                    value = entry.get()
                else:
                    value = entry.get().strip()
                
                if key in ["id", "age"]:
                    if not value:
                        messagebox.showerror("错误", f"{key}不能为空")
                        return
                    if not value.isdigit():
                        messagebox.showerror("错误", f"{key}必须为数字")
                        return
                
                if key == "id" and title == "添加学生":
                    # 检查学号是否已存在
                    for s in self.students:
                        if str(s.get("id", "")) == str(value):
                            messagebox.showerror("错误", "学号已存在")
                            return
                
                new_student[key] = value
            
            if title == "添加学生":
                self.students.append(new_student)
                messagebox.showinfo("成功", "学生添加成功")
            else:
                # 更新学生信息
                for i, s in enumerate(self.students):
                    if str(s.get("id", "")) == str(new_student["id"]):
                        self.students[i] = new_student
                        break
                messagebox.showinfo("成功", "学生信息更新成功")
            
            self.save_data()
            self.refresh_student_list()
            dialog.destroy()
        
        ttk.Button(button_frame, text="保存", command=save_student).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def delete_student(self):
        """删除学生"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个学生")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的学生吗？"):
            # 获取选中的学生学号
            item = self.tree.item(selected[0])
            student_id = item["values"][0]
            
            # 从数据中删除
            self.students = [s for s in self.students if str(s.get("id", "")) != str(student_id)]
            
            # 更新显示和保存数据
            self.save_data()
            self.refresh_student_list()
            messagebox.showinfo("成功", "学生删除成功")
    
    def on_double_click(self, event):
        """双击学生项打开编辑窗口"""
        self.edit_student_window()
    
    def export_data(self):
        """导出数据到文件"""
        try:
            with open("students_data.json", "w", encoding="utf-8") as f:
                json.dump(self.students, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("成功", f"数据已导出到 students_data.json\n共导出 {len(self.students)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"导出数据时出错: {str(e)}")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """学生管理系统 v1.0
        
功能：
1. 添加、编辑、删除学生信息
2. 搜索学生
3. 数据导出
        
使用Tkinter开发
        """
        messagebox.showinfo("关于", about_text)
    
    def load_data(self):
        """加载数据"""
        if os.path.exists("students_data.json"):
            try:
                with open("students_data.json", "r", encoding="utf-8") as f:
                    self.students = json.load(f)
            except:
                self.students = []
        else:
            # 如果没有数据文件，创建一些示例数据
            self.students = [
                {"id": "1001", "name": "张三", "gender": "男", "age": "20", "major": "计算机科学", "phone": "13800138001", "email": "zhangsan@example.com"},
                {"id": "1002", "name": "李四", "gender": "女", "age": "21", "major": "软件工程", "phone": "13800138002", "email": "lisi@example.com"},
                {"id": "1003", "name": "王五", "gender": "男", "age": "22", "major": "数据科学", "phone": "13800138003", "email": "wangwu@example.com"},
                {"id": "1004", "name": "赵六", "gender": "女", "age": "19", "major": "人工智能", "phone": "13800138004", "email": "zhaoliu@example.com"}
            ]
            self.save_data()
    
    def save_data(self):
        """保存数据"""
        try:
            with open("students_data.json", "w", encoding="utf-8") as f:
                json.dump(self.students, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存数据时出错: {str(e)}")

def main():
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()