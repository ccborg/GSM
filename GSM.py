import tkinter as tk
from tkinter import ttk, messagebox, font
import json
import os

class StudentPointsSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("学生积分管理系统")
        self.root.geometry("800x550")
        
        # 设置窗口图标和最小化尺寸
        self.root.minsize(700, 500)
        
        # 学生数据存储
        self.students = []
        self.load_data()
        
        # 创建UI组件
        self.create_widgets()
        
        # 默认显示所有学生
        self.refresh_student_list()
    
    def create_widgets(self):
        # 设置全局字体和样式
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)
        
        # 创建自定义样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义颜色方案
        style.configure("Title.TLabel", 
                       font=("微软雅黑", 14, "bold"),
                       foreground="#1a5276")
        
        style.configure("Header.Treeview",
                       font=("微软雅黑", 10, "bold"),
                       background="#d6dbdf")
        
        style.map("Treeview", 
                 background=[("selected", "#3498db")],
                 foreground=[("selected", "white")])
        
        # 主容器
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 标题区域
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame,
            text="学生积分管理系统",
            style="Title.TLabel"
        )
        title_label.pack()
        
        # 统计信息
        self.stats_frame = ttk.LabelFrame(main_container, text="统计信息", padding="10")
        self.stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建统计标签
        self.total_students_var = tk.StringVar(value="学生总数: 0")
        self.avg_points_var = tk.StringVar(value="平均积分: 0.0")
        self.highest_points_var = tk.StringVar(value="最高积分: 0")
        self.lowest_points_var = tk.StringVar(value="最低积分: 0")
        
        ttk.Label(self.stats_frame, textvariable=self.total_students_var).pack(side=tk.LEFT, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.avg_points_var).pack(side=tk.LEFT, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.highest_points_var).pack(side=tk.LEFT, padx=15)
        ttk.Label(self.stats_frame, textvariable=self.lowest_points_var).pack(side=tk.LEFT, padx=15)
        
        # 工具栏
        toolbar = ttk.Frame(main_container)
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # 搜索框
        search_frame = ttk.Frame(toolbar)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(search_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind("<Return>", lambda e: self.search_student())
        
        search_btn = ttk.Button(search_frame, text="搜索", 
                               command=self.search_student,
                               width=8)
        search_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        clear_btn = ttk.Button(search_frame, text="清空", 
                              command=self.refresh_student_list,
                              width=8)
        clear_btn.pack(side=tk.LEFT)
        
        # 操作按钮
        btn_frame = ttk.Frame(toolbar)
        btn_frame.pack(side=tk.RIGHT)
        
        buttons = [
            ("添加学生", self.add_student_window, "#2ecc71"),
            ("编辑学生", self.edit_student_window, "#3498db"),
            ("删除学生", self.delete_student, "#e74c3c"),
            ("积分操作", self.points_operation_window, "#f39c12"),
            ("导出数据", self.export_data, "#9b59b6")
        ]
        
        for text, command, color in buttons:
            btn = ttk.Button(btn_frame, text=text, 
                           command=command,
                           width=10)
            btn.pack(side=tk.LEFT, padx=2)
        
        # 学生列表区域
        list_container = ttk.Frame(main_container)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # 学生列表表格
        columns = ("学号", "姓名", "性别", "积分")
        self.tree = ttk.Treeview(
            list_container,
            columns=columns,
            show="headings",
            height=15,
            style="Treeview"
        )
        
        # 配置列
        col_configs = [
            ("学号", 120, "center"),
            ("姓名", 150, "center"),
            ("性别", 80, "center"),
            ("积分", 100, "center")
        ]
        
        for col, width, anchor in col_configs:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=anchor, minwidth=80)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_container.columnconfigure(0, weight=1)
        list_container.rowconfigure(0, weight=1)
        
        # 绑定事件
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Delete>", lambda e: self.delete_student())
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_container, 
                              textvariable=self.status_var, 
                              relief=tk.SUNKEN, 
                              anchor=tk.W,
                              padding=(5, 2))
        status_bar.pack(fill=tk.X, pady=(10, 0))
    
    def refresh_student_list(self, students=None):
        """刷新学生列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 显示学生数据
        display_students = students if students is not None else self.students
        
        # 按积分排序（从高到低）
        display_students.sort(key=lambda x: int(x.get("points", 0)), reverse=True)
        
        for student in display_students:
            points = int(student.get("points", "0"))
            self.tree.insert("", tk.END, values=(
                student.get("id", ""),
                student.get("name", ""),
                student.get("gender", ""),
                str(points)
            ))
        
        # 更新统计信息
        self.update_statistics(display_students)
        
        # 更新状态
        self.status_var.set(f"显示 {len(display_students)} 名学生")
    
    def update_statistics(self, students=None):
        """更新统计信息"""
        target_students = students if students is not None else self.students
        
        total = len(target_students)
        if total > 0:
            points_list = [int(s.get("points", 0)) for s in target_students]
            avg_points = sum(points_list) / total
            max_points = max(points_list)
            min_points = min(points_list)
            
            self.total_students_var.set(f"学生总数: {total}")
            self.avg_points_var.set(f"平均积分: {avg_points:.1f}")
            self.highest_points_var.set(f"最高积分: {max_points}")
            self.lowest_points_var.set(f"最低积分: {min_points}")
        else:
            self.total_students_var.set("学生总数: 0")
            self.avg_points_var.set("平均积分: 0.0")
            self.highest_points_var.set("最高积分: 0")
            self.lowest_points_var.set("最低积分: 0")
    
    def search_student(self):
        """搜索学生"""
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh_student_list()
            return
        
        results = []
        for student in self.students:
            # 在学号、姓名和积分中搜索
            if (keyword in student.get("id", "") or 
                keyword.lower() in student.get("name", "").lower() or
                keyword in str(student.get("points", ""))):
                results.append(student)
        
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
        
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        
        student = self.find_student_by_id(student_id)
        if student:
            self.open_student_dialog("编辑学生", student)
        else:
            messagebox.showerror("错误", f"找不到学号为 {student_id} 的学生")
    
    def open_student_dialog(self, title, student=None):
        """打开学生信息对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("350x250")
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
            ("学号:", "id", False),
            ("姓名:", "name", False),
            ("性别:", "gender", True),
            ("初始积分:", "points", False)
        ]
        
        entries = {}
        for i, (label, key, is_combo) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=8)
            
            if is_combo:
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var, state="readonly", width=25)
                combo['values'] = ("男", "女")
                combo.grid(row=i, column=1, sticky=tk.W, pady=8)
                entries[key] = var
            else:
                entry = ttk.Entry(form_frame, width=27)
                entry.grid(row=i, column=1, sticky=tk.W, pady=8)
                entries[key] = entry
            
            # 填充现有数据
            if student and key in student:
                if is_combo:
                    entries[key].set(student[key])
                else:
                    entries[key].insert(0, str(student[key]))
            elif key == "points" and not student:
                entries[key].insert(0, "0")  # 默认积分为0
        
        # 按钮区域
        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill=tk.X)
        
        def save_student():
            """保存学生信息"""
            new_student = {}
            
            # 验证和收集数据
            for key, entry in entries.items():
                if key == "gender":
                    value = entry.get()
                else:
                    value = entry.get().strip()
                
                # 验证
                if key == "id":
                    if not value:
                        self.show_error("学号不能为空")
                        return
                    if not value.isdigit():
                        self.show_error("学号必须为数字")
                        return
                
                if key == "name":
                    if not value:
                        self.show_error("姓名不能为空")
                        return
                
                if key == "gender":
                    if not value:
                        self.show_error("请选择性别")
                        return
                
                if key == "points":
                    # 允许负数，检查是否为整数
                    try:
                        int(value)  # 验证是否为整数
                    except ValueError:
                        self.show_error("积分必须为整数")
                        return
                
                # 检查学号是否已存在（仅在添加新学生时检查）
                if key == "id" and title == "添加学生":
                    if self.find_student_by_id(value):
                        self.show_error("学号已存在")
                        return
                
                new_student[key] = value
            
            # 保存数据
            if title == "添加学生":
                self.students.append(new_student)
                self.show_success("学生添加成功")
                self.status_var.set(f"成功添加学生: {new_student['name']}")
            else:
                # 更新现有学生
                updated = False
                for i, s in enumerate(self.students):
                    if s.get("id") == new_student["id"]:
                        self.students[i] = new_student
                        updated = True
                        break
                
                if updated:
                    self.show_success("学生信息更新成功")
                    self.status_var.set(f"成功更新学生: {new_student['name']}")
                else:
                    self.show_error("更新失败，找不到该学生")
                    dialog.destroy()
                    return
            
            self.save_data()
            self.refresh_student_list()
            dialog.destroy()
        
        ttk.Button(button_frame, text="保存", command=save_student, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    def find_student_by_id(self, student_id):
        """根据学号查找学生"""
        for student in self.students:
            if str(student.get("id", "")) == str(student_id):
                return student
        return None
    
    def delete_student(self):
        """删除学生"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个学生")
            return
        
        item = self.tree.item(selected[0])
        student_id = str(item["values"][0])
        student_name = item["values"][1]
        
        if messagebox.askyesno("确认删除", f"确定要删除学生 [{student_name}] 吗？"):
            # 从数据中删除
            deleted_count = 0
            new_students = []
            
            for s in self.students:
                if str(s.get("id", "")) != student_id:
                    new_students.append(s)
                else:
                    deleted_count += 1
            
            if deleted_count > 0:
                self.students = new_students
                
                # 更新显示和保存数据
                self.save_data()
                self.refresh_student_list()
                self.show_success(f"学生 [{student_name}] 删除成功")
                self.status_var.set(f"已删除学生: {student_name}")
            else:
                self.show_error(f"找不到学号为 {student_id} 的学生")
    
    def on_double_click(self, event):
        """双击学生项打开编辑窗口"""
        self.edit_student_window()
    
    def points_operation_window(self):
        """积分操作主窗口 - 带滚动条版本"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择一个学生")
            return
        
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        student_name = item["values"][1]
        current_points = int(item["values"][3])
        
        # 创建积分操作窗口
        dialog = tk.Toplevel(self.root)
        dialog.title(f"积分操作 - {student_name}")
        dialog.geometry("520x500")  # 增大窗口尺寸以容纳更多内容
        dialog.resizable(True, True)  # 允许调整大小
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中对话框
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # 创建主容器 - 使用Canvas实现滚动
        main_canvas = tk.Canvas(dialog, highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=main_canvas.yview)
        scrollable_frame = ttk.Frame(main_canvas)
        
        # 配置滚动区域
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        # 在Canvas中创建窗口
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # 鼠标滚轮滚动支持
        def _on_mousewheel(event):
            if dialog.winfo_exists():  # 检查窗口是否还存在
                try:
                    main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                except tk.TclError:
                    pass  # 窗口已经关闭，忽略错误
        
        # 绑定鼠标滚轮事件到当前对话框
        dialog.bind("<MouseWheel>", _on_mousewheel)
        main_canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        
        # 布局滚动条和Canvas
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 主容器，使内容可以随窗口调整大小
        main_container = ttk.Frame(scrollable_frame, padding="15")
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # 学生信息区域 - 使用更清晰的布局
        info_frame = ttk.LabelFrame(main_container, text="📋 学生信息", padding="15")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 使用网格布局使信息对齐
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="学号:", font=("微软雅黑", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=student_id, font=("微软雅黑", 10)).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="姓名:", font=("微软雅黑", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text=student_name, font=("微软雅黑", 10)).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(info_frame, text="当前积分:", font=("微软雅黑", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # 根据积分正负显示不同颜色
        points_color = "#7f8c8d"  # 默认灰色（0分）
        if current_points > 0:
            points_color = "#2ecc71"  # 正数为绿色
        elif current_points < 0:
            points_color = "#e74c3c"  # 负数为红色
        
        ttk.Label(info_frame, text=str(current_points), 
                 font=("微软雅黑", 16, "bold"),
                 foreground=points_color).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 积分操作区域
        operation_frame = ttk.LabelFrame(main_container, text="🎯 积分操作", padding="15")
        operation_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 操作类型选择
        ttk.Label(operation_frame, text="选择操作类型:", font=("微软雅黑", 10)).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建操作类型按钮框架
        op_button_frame = ttk.Frame(operation_frame)
        op_button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 操作类型变量
        self.op_var = tk.StringVar(value="add")
        
        # 定义按钮颜色
        button_colors = {
            "add": {"normal": "#2ecc71", "active": "#27ae60", "selected": "#27ae60"},
            "subtract": {"normal": "#e74c3c", "active": "#c0392b", "selected": "#c0392b"},
            "set": {"normal": "#3498db", "active": "#2980b9", "selected": "#2980b9"}
        }
        
        # 创建操作按钮字典
        self.operation_buttons = {}
        
        # 创建操作按钮
        op_buttons = [
            ("➕ 增加积分", "add"),
            ("➖ 减少积分", "subtract"),
            ("⚙️ 设置积分", "set")
        ]
        
        for text, value in op_buttons:
            btn = tk.Button(
                op_button_frame,
                text=text,
                font=("微软雅黑", 10),
                width=15,
                height=2,
                bg=button_colors[value]["normal"],
                fg="white",
                activebackground=button_colors[value]["active"],
                activeforeground="white",
                relief=tk.RAISED,
                command=lambda v=value: self.select_operation(v, dialog)
            )
            btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.operation_buttons[value] = btn
        
        # 设置默认选中的按钮
        self.select_operation("add", dialog)
        
        # 积分值输入区域
        input_frame = ttk.Frame(operation_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(input_frame, text="积分值:", font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(0, 10))
        
        # 积分输入框
        self.points_var = tk.StringVar()
        points_entry = ttk.Entry(
            input_frame, 
            textvariable=self.points_var, 
            width=15,
            font=("微软雅黑", 10)
        )
        points_entry.pack(side=tk.LEFT, padx=(0, 10))
        points_entry.focus()  # 自动聚焦到输入框
        
        # 快捷按钮框架
        quick_buttons_frame = ttk.LabelFrame(operation_frame, text="🚀 快捷操作", padding="10")
        quick_buttons_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 创建快捷按钮 - 第一行
        quick_frame1 = ttk.Frame(quick_buttons_frame)
        quick_frame1.pack(fill=tk.X, pady=(5, 0))
        
        quick_buttons_row1 = [
            ("+1", 1),
            ("+5", 5),
            ("+10", 10),
            ("+20", 20),
            ("+50", 50),
            ("+100", 100)
        ]
        
        for text, value in quick_buttons_row1:
            btn = ttk.Button(
                quick_frame1,
                text=text,
                width=6,
                command=lambda v=value: self.points_var.set(str(int(self.points_var.get() or 0) + v))
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 创建快捷按钮 - 第二行
        quick_frame2 = ttk.Frame(quick_buttons_frame)
        quick_frame2.pack(fill=tk.X, pady=(5, 0))
        
        quick_buttons_row2 = [
            ("-1", -1),
            ("-5", -5),
            ("-10", -10),
            ("-20", -20),
            ("-50", -50),
            ("-100", -100)
        ]
        
        for text, value in quick_buttons_row2:
            btn = ttk.Button(
                quick_frame2,
                text=text,
                width=6,
                command=lambda v=value: self.points_var.set(str(int(self.points_var.get() or 0) + v))
            )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 创建快捷按钮 - 第三行
        quick_frame3 = ttk.Frame(quick_buttons_frame)
        quick_frame3.pack(fill=tk.X, pady=(5, 0))
        
        quick_buttons_row3 = [
            ("清空", "clear"),
            ("当前积分", "current"),
            ("设为0", "zero"),
            ("设为1", "one"),
            ("设为-1", "neg_one"),
            ("设为-10", "neg_ten")
        ]
        
        for text, value in quick_buttons_row3:
            if value == "clear":
                btn = ttk.Button(
                    quick_frame3,
                    text=text,
                    width=6,
                    command=lambda: self.points_var.set("0")
                )
            elif value == "current":
                btn = ttk.Button(
                    quick_frame3,
                    text=text,
                    width=6,
                    command=lambda: self.points_var.set(str(current_points))
                )
            elif value == "zero":
                btn = ttk.Button(
                    quick_frame3,
                    text=text,
                    width=6,
                    command=lambda: self.points_var.set("0")
                )
            elif value == "one":
                btn = ttk.Button(
                    quick_frame3,
                    text=text,
                    width=6,
                    command=lambda: self.points_var.set("1")
                )
            elif value == "neg_one":
                btn = ttk.Button(
                    quick_frame3,
                    text=text,
                    width=6,
                    command=lambda: self.points_var.set("-1")
                )
            elif value == "neg_ten":
                btn = ttk.Button(
                    quick_frame3,
                    text=text,
                    width=6,
                    command=lambda: self.points_var.set("-10")
                )
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # 操作建议区域
        suggestion_frame = ttk.LabelFrame(operation_frame, text="💡 操作说明", padding="10")
        suggestion_frame.pack(fill=tk.X, pady=(15, 0))
        
        suggestions = [
            "✅ 增加积分：奖励学生的优秀表现",
            "✅ 减少积分：扣除学生的违规行为积分",
            "✅ 设置积分：直接设置学生积分为指定值",
            "⚠️ 积分可以为负数，表示学生表现不佳",
            "📝 默认所有学生初始积分为0"
        ]
        
        for suggestion in suggestions:
            ttk.Label(suggestion_frame, text=f"• {suggestion}", font=("微软雅黑", 9)).pack(anchor=tk.W, pady=2)
        
        # 预测结果显示
        prediction_frame = ttk.Frame(operation_frame)
        prediction_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.prediction_var = tk.StringVar(value="")
        prediction_label = ttk.Label(
            prediction_frame,
            textvariable=self.prediction_var,
            font=("微软雅黑", 11, "bold")
        )
        prediction_label.pack(anchor=tk.CENTER)
        
        # 更新预测结果
        def update_prediction(*args):
            try:
                points_str = self.points_var.get().strip()
                if points_str:
                    try:
                        points = int(points_str)
                    except ValueError:
                        self.prediction_var.set("请输入整数")
                        prediction_label.configure(foreground="#e74c3c")
                        return
                    
                    op = self.op_var.get()
                    
                    if op == "add":
                        new_points = current_points + points
                        action = "增加"
                        color = "#2ecc71"
                    elif op == "subtract":
                        new_points = current_points - points
                        action = "减少"
                        color = "#e74c3c"
                    else:  # set
                        new_points = points
                        action = "设置为"
                        color = "#3498db"
                    
                    # 根据新积分值设置颜色
                    if new_points > 0:
                        points_color = "#2ecc71"  # 正数为绿色
                    elif new_points < 0:
                        points_color = "#e74c3c"  # 负数为红色
                    else:
                        points_color = "#7f8c8d"  # 零为灰色
                    
                    if new_points > current_points:
                        arrow = "↑"
                    elif new_points < current_points:
                        arrow = "↓"
                    else:
                        arrow = "→"
                    
                    self.prediction_var.set(f"{arrow} 操作后积分: {new_points} ({action} {points} 积分)")
                    prediction_label.configure(foreground=points_color)
                else:
                    self.prediction_var.set("请输入积分值")
                    prediction_label.configure(foreground="#7f8c8d")
            except:
                self.prediction_var.set("")
                prediction_label.configure(foreground="#7f8c8d")
        
        # 绑定事件
        self.points_var.trace("w", update_prediction)
        self.op_var.trace("w", update_prediction)
        
        # 按钮区域
        button_frame = ttk.LabelFrame(main_container, text="📥 确认操作", padding="15")
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 按钮容器
        btn_container = ttk.Frame(button_frame)
        btn_container.pack(expand=True)
        
        def apply_points():
            """应用积分操作"""
            points_str = self.points_var.get().strip()
            if not points_str:
                self.show_error("请输入积分值")
                points_entry.focus()
                return
            
            try:
                points = int(points_str)
            except ValueError:
                self.show_error("积分值必须是整数")
                points_entry.focus()
                return
            
            operation = self.op_var.get()
            
            # 找到学生并更新积分
            student = self.find_student_by_id(student_id)
            if student:
                current = int(student.get("points", 0))
                
                if operation == "add":
                    new_points = current + points
                    action = "增加"
                elif operation == "subtract":
                    new_points = current - points
                    action = "减少"
                else:  # set
                    new_points = points
                    action = "设置"
                
                student["points"] = str(new_points)
                
                # 保存并刷新
                self.save_data()
                self.refresh_student_list()
                
                # 显示操作记录
                self.status_var.set(f"{student_name} {action}了 {points} 积分，当前积分: {new_points}")
                
                # 记录操作历史
                self.record_operation_history(student_id, student_name, operation, points, current, new_points)
                
                dialog.destroy()
                self.show_success(f"成功{action} {points} 积分\n当前积分: {new_points}")
        
        # 创建操作按钮
        apply_btn = ttk.Button(
            btn_container, 
            text="✅ 确定应用", 
            command=apply_points, 
            width=15
        )
        apply_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(
            btn_container, 
            text="❌ 取消", 
            command=dialog.destroy, 
            width=15
        )
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 绑定回车键到确定按钮
        dialog.bind("<Return>", lambda e: apply_points())
        # 绑定ESC键到取消按钮
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        # 窗口关闭时清理事件绑定
        def on_close():
            # 清理事件绑定
            dialog.unbind("<MouseWheel>")
            main_canvas.unbind("<MouseWheel>")
            scrollable_frame.unbind("<MouseWheel>")
            dialog.destroy()
        
        dialog.protocol("WM_DELETE_WINDOW", on_close)
        
        # 初始化预测
        update_prediction()
        
        # 配置滚动区域的最小尺寸
        dialog.update_idletasks()
        min_height = min(600, main_canvas.winfo_reqheight())
        min_width = 520
        dialog.minsize(min_width, min_height)
    
    def select_operation(self, operation, dialog):
        """选择操作类型并更新按钮状态"""
        # 更新变量
        self.op_var.set(operation)
        
        # 定义按钮颜色
        button_colors = {
            "add": {"normal": "#2ecc71", "active": "#27ae60", "selected": "#27ae60"},
            "subtract": {"normal": "#e74c3c", "active": "#c0392b", "selected": "#c0392b"},
            "set": {"normal": "#3498db", "active": "#2980b9", "selected": "#2980b9"}
        }
        
        # 更新所有按钮状态
        for op, btn in self.operation_buttons.items():
            if op == operation:
                # 选中的按钮使用选中颜色
                btn.config(
                    bg=button_colors[op]["selected"],
                    relief=tk.SUNKEN,
                    state=tk.DISABLED
                )
            else:
                # 未选中的按钮使用正常颜色
                btn.config(
                    bg=button_colors[op]["normal"],
                    relief=tk.RAISED,
                    state=tk.NORMAL
                )
    
    def record_operation_history(self, student_id, student_name, operation, points, old_points, new_points):
        """记录积分操作历史"""
        try:
            history_file = "points_history.json"
            history = []
            
            if os.path.exists(history_file):
                with open(history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            
            # 添加新记录
            from datetime import datetime
            record = {
                "student_id": student_id,
                "student_name": student_name,
                "operation": operation,
                "points": points,
                "old_points": old_points,
                "new_points": new_points,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            history.append(record)
            
            # 只保留最近100条记录
            if len(history) > 100:
                history = history[-100:]
            
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"记录操作历史时出错: {e}")
    
    def export_data(self):
        """导出数据到文件"""
        try:
            with open("students_data.json", "w", encoding="utf-8") as f:
                json.dump(self.students, f, ensure_ascii=False, indent=2)
            self.show_success(f"数据已导出到 students_data.json\n共导出 {len(self.students)} 条记录")
        except Exception as e:
            self.show_error(f"导出数据时出错: {str(e)}")
    
    def show_success(self, message):
        """显示成功消息"""
        messagebox.showinfo("成功", message)
    
    def show_error(self, message):
        """显示错误消息"""
        messagebox.showerror("错误", message)
    
    def show_warning(self, message):
        """显示警告消息"""
        messagebox.showwarning("警告", message)
    
    def load_data(self):
        """加载数据"""
        if os.path.exists("students_data.json"):
            try:
                with open("students_data.json", "r", encoding="utf-8") as f:
                    self.students = json.load(f)
            except:
                self.students = []
        else:
            # 创建示例数据 - 所有学生默认分数为0
            self.students = [
                {"id": "1001", "name": "张三", "gender": "男", "points": "0"},
                {"id": "1002", "name": "李四", "gender": "女", "points": "0"},
                {"id": "1003", "name": "王五", "gender": "男", "points": "0"},
                {"id": "1004", "name": "赵六", "gender": "女", "points": "0"},
                {"id": "1005", "name": "钱七", "gender": "男", "points": "0"},
                {"id": "1006", "name": "孙八", "gender": "女", "points": "0"},
                {"id": "1007", "name": "周九", "gender": "男", "points": "0"},
                {"id": "1008", "name": "吴十", "gender": "女", "points": "0"}
            ]
            self.save_data()
    
    def save_data(self):
        """保存数据"""
        try:
            with open("students_data.json", "w", encoding="utf-8") as f:
                json.dump(self.students, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.show_error(f"保存数据时出错: {str(e)}")

def main():
    root = tk.Tk()
    
    # 设置窗口图标（可选）
    # try:
    #     root.iconbitmap("icon.ico")
    # except:
    #     pass
    
    app = StudentPointsSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()
