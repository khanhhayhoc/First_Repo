# controller/worktime_controller.py
from tkinter import filedialog
import matplotlib.pyplot as plt
import pandas as pd

class WorkTimeController:
    def __init__(self, model, view):
        self.model = model
        self.view = view

        self.view.btn_upload.config(command=self.load_excel)
        self.view.btn_search.config(command=self.search)

    def load_excel(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.model.load_excel(file_path)
            self.view.set_names(self.model.get_names())

    def search(self):
        names = self.view.get_selected_names()
        if not names:
            return
        all_names = names
        
        from_date = pd.to_datetime(self.view.from_date.get())
        to_date   = pd.to_datetime(self.view.to_date.get()) + pd.Timedelta(days=1)
        to_date_raw = pd.to_datetime(self.view.to_date.get())

        # 1️⃣ lọc dữ liệu gốc
        df_filtered = self.model.filter_data(names, from_date, to_date).copy()

        # 2️⃣ summary
        summary_df = self.model.summary_by_person(
            df_filtered,
            from_date,
            to_date_raw 
        )

        # 3️⃣ pivot theo hạng mục (bảng + pie)
        pivot_df, _ = self.model.pivot_hours(df_filtered)

        # 4️⃣ tạo cột ngày (string để làm column)
        df_filtered['ngay'] = pd.to_datetime(
            df_filtered['階段結束時間']
        ).dt.strftime('%d/%m')


        # 5️⃣ tạo danh sách ngày đầy đủ (trừ CN)
        #df_filtered['has_record'] = 1
        all_people = all_names
        all_days = pd.date_range(
            start=from_date,
            end=to_date_raw ,
            freq='D'
        )
        all_days = all_days[all_days.weekday != 6]
        all_days_str = all_days.strftime('%d/%m')

        full_index = pd.MultiIndex.from_product(
            [all_people, all_days_str],
            names=['承接者', 'ngay']
        )

        full_df = pd.DataFrame(index=full_index).reset_index()

        df_sum = (
            df_filtered
            .groupby(['承接者', 'ngay'], as_index=False)['階段耗時']
            .sum()
            .rename(columns={'階段耗時': 'gio'})
        )

        merged = full_df.merge(
            df_sum,
            on=['承接者', 'ngay'],
            how='left'
        )

        merged['gio'] = merged['gio'].fillna(0)


        # 9️⃣ LOGIC NGHIỆP VỤ
        # - 0 giờ  -> chưa đánh (PHẢI HIỆN)
        # - <8 hoặc >8 -> thiếu / dư (PHẢI HIỆN)
        # - =8 -> đủ (KHÔNG HIỆN)
        abnormal = merged[merged['gio'] != 8]
        pivot_name_day = abnormal.pivot(
            index='承接者',
            columns='ngay',
            values='gio'
        )
        pivot_name_day = pivot_name_day.dropna(axis=1, how='all')
        pivot_name_day = pivot_name_day.reindex(
            index=all_people
        ).fillna('')

        pivot_name_day = pivot_name_day.reset_index()


        # 9️⃣ hiển thị
        self.view.show_summary(summary_df)
        self.view.show_pivot(pivot_df)
        self.view.show_pie_chart(pivot_df)
        self.view.show_name_day_pivot(pivot_name_day)



    def draw_pie(self, pivot_df):
        plt.figure(figsize=(5,5))
        plt.pie(
            pivot_df['階段耗時'],
            labels=pivot_df['工時分類名稱'],
            autopct='%1.1f%%'
        )
        plt.title("Tỷ lệ giờ công theo hạng mục")
        plt.show()