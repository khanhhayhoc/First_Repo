import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import ttk
from tkcalendar import DateEntry
import matplotlib
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # hoặc 'SimHei'
plt.rcParams['axes.unicode_minus'] = False


class WorkTimeView(tk.Tk):
    def __init__(self):
        super().__init__()
        style = ttk.Style()
        style.theme_use("clam")
        self.pie_canvas = None
        self.pie_fig = None
        self.pie_ax = None
        self.pie_wedges = None

        style.configure(
            "Treeview",
            foreground="black",
            rowheight=28,
            fieldbackground="white",
            bordercolor="#bfbfbf",
            borderwidth=1,
            relief="solid"
        )

        style.configure(
            "Treeview.Heading",
            font=("Arial", 10, "bold"),
            background="#e9ecef",
            foreground="black",
            borderwidth=1,
            relief="solid"
        )

        style.map(
            "Treeview",
            background=[("selected", "#e9ecef")],
            foreground=[("selected", "black")]
        )
        
        

        

        self.title("Phân tích giờ công")
        self.state("zoomed") 

        # ================= UPLOAD =================
        self.btn_upload = tk.Button(self, text="Upload Excel")
        self.btn_upload.pack(pady=5)

        # ================= FILTER =================
        self.filter_container = tk.Frame(self, height=260)
        self.filter_container.pack(fill=tk.X, padx=10, pady=5)
        self.filter_container.pack_propagate(False)

        self.filter_name = tk.LabelFrame(
            self.filter_container,
            text="Filter Name",
            width=250,
            height=240
        )
        self.filter_name.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.filter_name.pack_propagate(False)


        self.filter_day = tk.LabelFrame(
            self.filter_container,
            text="Filter Day",
            width=250,
            height=240
        )
        self.filter_day.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.filter_day.pack_propagate(False)


        self.filter_pivot = tk.LabelFrame(
            self.filter_container,
            text="Abnormal Hours",
            height=240
        )
        self.filter_pivot.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.filter_pivot.pack_propagate(False)


        #tk.Label(filter_frame, text="Tên").grid(row=0, column=0, padx=5)
        name_frame = tk.Frame(self.filter_name)
        name_frame.pack(anchor="nw", padx=5, pady=5)  # 👈 BẮT BUỘC

        tk.Label(
        name_frame,
        text="承接者",
        font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=(0, 5))

        # ===== FILTER NGƯỜI KHAI BÁO =====
        filter_name_frame = tk.Frame(name_frame)
        filter_name_frame.pack(anchor="w", pady=(0, 5))

        self.search_name_var = tk.StringVar()
        self.search_name_var.trace_add("write", self.on_search_name)
        tk.Entry(
            filter_name_frame,
            textvariable=self.search_name_var,
            width=25
        ).pack(side=tk.LEFT, padx=(0, 5))
       
        tk.Button(
            filter_name_frame,
            text="✓",
            fg="#4CAF50", 
            width=3,
            command=self.select_all_names
        ).pack(side=tk.LEFT)

        tk.Button(
            filter_name_frame,
            text="✗",
            fg="#F44336",
            width=3,
            command=self.clear_all_names
        ).pack(side=tk.LEFT)

        listbox_frame = tk.Frame(name_frame)
        listbox_frame.pack()

        scrollbar = tk.Scrollbar(listbox_frame, orient=tk.VERTICAL)

        self.lb_names = tk.Listbox(
            listbox_frame,
            selectmode=tk.MULTIPLE,
            height=10,          # 👈 cao hơn
            width=25,           # 👈 rộng hơn
            font=("Arial", 11), # 👈 chữ to hơn
            yscrollcommand=scrollbar.set,
            exportselection=False
        )

        scrollbar.config(command=self.lb_names.yview)

        self.lb_names.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(self.filter_day, text="From Date").pack(anchor="w")
        self.from_date = DateEntry(
            self.filter_day,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        self.from_date.pack(anchor="w", pady=2)

        tk.Label(self.filter_day, text="To Date").pack(anchor="w")
        self.to_date = DateEntry(
            self.filter_day,
            width=12,
            background="darkblue",
            foreground="white",
            borderwidth=2,
            date_pattern="yyyy-mm-dd"
        )
        self.to_date.pack(anchor="w", pady=2)

        self.btn_search = tk.Button(self.filter_day,  text=" Search ",
        bg="#ffcc00",      # vàng nổi
        fg="black",
        padx=20,
        relief="raised")
        self.btn_search.pack(anchor="w", pady=5)
        # ===== MINI PIVOT: TÊN × NGÀY =====
        

        self.frame_name_day = tk.Frame(
            self.filter_pivot,
            bd=1,
            relief="solid"
        )
        self.frame_name_day.pack(
            fill=tk.BOTH,
            expand=True,
            pady=(10, 0)
        )

        tk.Label(
            self.frame_name_day,
            text="人员 / 日期 工时",
            font=("Arial", 9, "bold")
        ).pack(anchor="w", padx=5, pady=(2, 2))

        self.name_day_container = tk.Frame(self.frame_name_day)
        self.name_day_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=3
        )

        self.name_day_table = None

        self.category_colors = {
            "Admin activities": "#1f77b4",
            "ITSM": "#ff7f0e",
            "Leave": "#d62728",
            "Major Project": "#2ca02c",
            "Training": "#9467bd",
            "Optimization": "#8c564b",
            "User Requirement": "#e377c2"
        }
        # tk.Label(
        #     legend_frame,
        #     text="项目", # hạng mục 
        #     font=("Arial", 9, "bold")
        # ).pack(anchor="w", pady=(0, 5))

        # for name, color in self.category_colors.items():
        #     row = tk.Frame(legend_frame)
        #     row.pack(anchor="w", pady=2)

        #     tk.Label(
        #         row,
        #         width=2,
        #         height=1,
        #         bg=color
        #     ).pack(side=tk.LEFT)

        #     tk.Label(
        #         row,
        #         text=f" {name}",
        #         font=("Arial", 9)
        #     ).pack(side=tk.LEFT)

        # ================= RESULT AREA =================
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10,pady=(0, 10)   # 👈 sát lên filter
                               )

        # -------- LEFT: SUMMARY TABLE --------
        self.frame_summary = tk.Frame(self.result_frame, bd=1, relief="solid")
        self.frame_summary.pack(side=tk.LEFT,
        fill=tk.BOTH,
        expand=False,
        padx=5)
        self.frame_summary.config(width=500)
        tk.Label(self.frame_summary, text="工时汇总", font=("Arial", 12, "bold")).pack(pady=5)
        self.summary_table_container = tk.Frame(self.frame_summary)
        self.summary_table_container.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )
        self.summary_table = ttk.Treeview(
            self.summary_table_container,
            columns=("stt" , "name", "standard", "declared", "diff"),
            show="headings"
        )
        self.summary_table.tag_configure("odd", background="#ffffff")
        self.summary_table.tag_configure("even", background="#f5f5f5")
        self.summary_table.tag_configure(
            "total",
            background="#FFF3CD",   # vàng nhạt
            foreground="#D09F0C",
            font=("Arial", 10, "bold")
        )
        self.summary_table.heading("stt", text="序号") #STT 
        self.summary_table.heading("name", text="承接者") # tên 
        self.summary_table.heading("standard", text="标准工时") # giờ tiêu chuẩn 
        self.summary_table.heading("declared", text="申报工时") # giờ khai báo 
        self.summary_table.heading("diff", text="差异") # chênh lệch 

        self.summary_table.column("stt", width=80, anchor="center")
        self.summary_table.column("name", width=120)
        self.summary_table.column("standard", width=100, anchor="e")
        self.summary_table.column("declared", width=100, anchor="e")
        self.summary_table.column("diff", width=100, anchor="e")

       

        summary_scrollbar = ttk.Scrollbar(
            self.summary_table_container,
            orient="vertical",
            command=self.summary_table.yview
        )

        self.summary_table.configure(yscrollcommand=summary_scrollbar.set)

        self.summary_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        summary_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # -------- MIDDLE: PIVOT --------
        self.frame_pivot = tk.Frame(self.result_frame, bd=1, relief="solid")
        self.frame_pivot.pack(side=tk.LEFT,
        fill=tk.BOTH,
        expand=False,
        padx=5)
        self.frame_pivot.config(width=450)

        tk.Label(self.frame_pivot, text="按项目汇总", font=("Arial", 12, "bold")).pack(pady=5)
       

        self.pivot_table = ttk.Treeview(
            self.frame_pivot,
            columns=("category", "hours", "percent"),
            show="headings",
            height=12
        )
        self.pivot_table.bind("<ButtonRelease-1>", self.on_pivot_click)
        self.pivot_table.tag_configure("odd", background="#ffffff")
        self.pivot_table.tag_configure("even", background="#f5f5f5")
        self.pivot_table.tag_configure(
            "total",
            background="#E1F5FE",   # xanh nhạt
            foreground="#01579B",
            font=("Arial", 10, "bold")
        )

        self.pivot_table.heading("category", text="项目") # hạng mục 
        self.pivot_table.heading("hours", text="总工时") # tổng giờ 
        self.pivot_table.heading("percent", text="%")

        self.pivot_table.column("category", width=200)
        self.pivot_table.column("hours", width=100, anchor="e")
        self.pivot_table.column("percent", width=100, anchor="e")

        self.pivot_table.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # -------- RIGHT: PIE CHART --------
        self.frame_chart = tk.Frame(self.result_frame, bd=1, relief="solid")
        self.frame_chart.pack( side=tk.LEFT,
        fill=tk.BOTH,
        expand=True,     # 👈 CHỈ CÁI NÀY ĐƯỢC GIÃN
        padx=5)

        tk.Label(self.frame_chart, text="工时饼图", font=("Arial", 12, "bold")).pack(pady=5)

    # ================= API FOR CONTROLLER =================

 
    
    def set_names(self, names):
        self.all_names = list(names)   # 👈 lưu danh sách gốc
        self.lb_names.delete(0, tk.END)

        for n in self.all_names:
            self.lb_names.insert(tk.END, n)
    

    def select_all_names(self):
        self.lb_names.select_set(0, tk.END)

    def clear_all_names(self):
        self.lb_names.selection_clear(0, tk.END)

    def get_selected_names(self):
        return [self.lb_names.get(i) for i in self.lb_names.curselection()]
    
 

    def on_pivot_click(self, event):
        item = self.pivot_table.identify_row(event.y)
        if not item:
            return

        category = self.pivot_table.item(item, "values")[0]
        if category == "总工时":
            return

        self.highlight_category = category
        self.update_pie_highlight()

    def show_summary(self, df):
        self.summary_table.delete(*self.summary_table.get_children())
         # ✅ KHAI BÁO BIẾN TỔNG
        total_standard = 0
        total_declared = 0
        total_diff = 0
        for i, (_, r) in enumerate(df.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            standard = int(r["standard_hours"])
            declared = round(r["declared_hours"], 2)
            diff = round(r["difference"], 2)

            total_standard += standard
            total_declared += declared
            total_diff += diff
            self.summary_table.insert(
                "",
                "end",
                values=(
                    i+1,
                    r["承接者"],
                    int(r["standard_hours"]),
                    round(r["declared_hours"], 2),
                    round(r["difference"], 2)
                ),
                tags=(tag,)
            )
             # 👉 DÒNG TỔNG
        self.summary_table.insert(
            "",
            "end",
            values=(f"共 {len(df)} 人", "总工时", total_standard, total_declared, total_diff),
            tags=("total",)
        )

        #self.summary_table.tag_configure("total", font=("Arial", 10, "bold"))

    def show_pivot(self, pivot_df):
        self.last_pivot_df = pivot_df
        self.highlight_category = None
        self.pivot_table.delete(*self.pivot_table.get_children())
        total_hours = 0   # ✅ KHAI BÁO
        for i, (_, r) in enumerate(pivot_df.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            hours = float(r["階段耗時"])
            percent = round(r["percent"], 2)

            total_hours += hours

            self.pivot_table.insert(
                "",
                "end",
                values=(
                    r["工時分類名稱"],
                    round(r["階段耗時"], 2),
                    f"{r['percent']}%"
                ),
                tags=(tag,)
            )
        self.pivot_table.insert(
            "",
            "end",
            values=("总工时", round(total_hours, 2), "100%"),
            tags=("total",)
        )

        #self.pivot_table.tag_configure("total", font=("Arial", 10, "bold"))
    def clear_chart(self):
        for w in self.frame_chart.winfo_children():
            if isinstance(w, tk.Canvas):
                w.destroy()

    def on_search_name(self, *args):
        keyword = self.search_name_var.get().lower()

        self.lb_names.delete(0, tk.END)

        for name in self.all_names:
            if keyword in name.lower():
                self.lb_names.insert(tk.END, name)

    def show_table(self, pivot_df):
        self.pivot_table.delete(*self.pivot_table.get_children())
        for _, r in pivot_df.iterrows():
            self.pivot_table.insert("", "end", values=(
                r["工時分類名稱"],
                round(r["階段耗時"], 2),
                f"{r['percent']}%"
            ))


    def show_pie_chart(self, pivot_df):
       # self.clear_chart()

        if pivot_df.empty:
            return

        # ----- map màu theo tên hạng mục -----
        color_map = {
            "Admin activities": "#1f77b4",
            "ITSM": "#ff7f0e",
            "Leave": "#d62728",
            "Major Project": "#2ca02c",
            "Training": "#9467bd",
            "Optimization": "#8c564b",
            "User Requirement": "#e377c2"
        }
        total_hours = pivot_df["階段耗時"].sum()
        labels = pivot_df["工時分類名稱"]
        values = pivot_df["階段耗時"]
        colors = [color_map.get(l, "#7f7f7f") for l in labels]

         # ---- explode để highlight ----
        explode = [0] * len(labels)
        

        fig = Figure(figsize=(7, 7), dpi=100)
        ax = fig.add_subplot(111)
        #ax.set_position([0.30, 0.12, 0.65, 0.75])
        wedges, _, _ = ax.pie(
            values,
            colors=colors,
            explode=explode,   # ✅ QUAN TRỌNG
            autopct="%1.1f%%",
            startangle=90
        )
        # ===== LEGEND NẰM TRONG BIỂU ĐỒ =====
        fig.legend(
            wedges,
            labels,
            loc="lower left",
            bbox_to_anchor=(0.01, 0.01),   # 👈 SÁT GÓC DƯỚI TRÁI
            fontsize=8,
            frameon=False,
            labelspacing=0.4,
            handlelength=1
        )

        self.pie_fig = fig
        self.pie_ax = ax
        self.pie_wedges = wedges

        if self.pie_canvas:
            self.pie_canvas.get_tk_widget().destroy()

        self.pie_canvas = FigureCanvasTkAgg(fig, master=self.frame_chart)
        self.pie_canvas.draw()
        self.pie_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ax.set_title(
            f"按项目的工时占比\n总工时: {round(total_hours, 2)}",
            fontsize=12,
            pad=12
        )

        # ----- legend phía dưới -----
     
    def update_pie_highlight(self):
        if not self.pie_wedges:
            return

        labels = list(self.last_pivot_df["工時分類名稱"])

        for i, wedge in enumerate(self.pie_wedges):
            if labels[i] == self.highlight_category:
                wedge.set_radius(1.1)
                wedge.set_edgecolor("black")
                wedge.set_linewidth(2)
            else:
                wedge.set_radius(1.0)
                wedge.set_edgecolor("white")
                wedge.set_linewidth(1)

        self.pie_canvas.draw_idle()
    def show_name_day_pivot(self, pivot_df):
        # clear cũ
        for w in self.name_day_container.winfo_children():
            w.destroy()

        columns = list(pivot_df.columns)

        # ===== FRAME CHÍNH =====
        body_frame = tk.Frame(self.name_day_container)
        body_frame.pack(fill=tk.BOTH, expand=True)

        # ===== CANVAS =====
        canvas = tk.Canvas(body_frame, height=180)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ===== SCROLLBAR DỌC (BÊN PHẢI BẢNG) =====
        scrollbar_y = ttk.Scrollbar(
            body_frame,
            orient="vertical",
            command=canvas.yview
        )
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

        # ===== SCROLLBAR NGANG (DƯỚI BẢNG) =====
        scrollbar_x = ttk.Scrollbar(
            self.name_day_container,
            orient="horizontal",
            command=canvas.xview
        )
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        canvas.configure(
            xscrollcommand=scrollbar_x.set,
            yscrollcommand=scrollbar_y.set
        )

        # ===== TABLE FRAME =====
        table_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=table_frame, anchor="nw")

        # ===== TREEVIEW =====
        height = min(len(pivot_df), 5)

        self.name_day_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
            #height=height
        )

        self.name_day_table.tag_configure("odd", background="#ffffff")
        self.name_day_table.tag_configure("even", background="#f0f0f0")

        for col in columns:
            self.name_day_table.heading(col, text=col)
            if col == "承接者":
                self.name_day_table.column(col, width=160, anchor="w", stretch=False)
            else:
                self.name_day_table.column(col, width=80, anchor="center", stretch=False)

        for i, (_, r) in enumerate(pivot_df.iterrows()):
            tag = "even" if i % 2 == 0 else "odd"
            self.name_day_table.insert(
                "",
                "end",
                values=list(r),
                tags=(tag,)
            )

        self.name_day_table.pack(fill=tk.BOTH, expand=True)

        # ===== UPDATE SCROLL =====
        table_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))
