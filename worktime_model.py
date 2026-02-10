# model/worktime_model.py
import pandas as pd

class WorkTimeModel:
    def __init__(self):
        self.df = None

    def load_excel(self, file_path):
        self.df = pd.read_excel(file_path)
        self.df['階段結束時間'] = pd.to_datetime(self.df['階段結束時間'])

    def get_names(self):
        return sorted(self.df['承接者'].unique())

    def filter_data(self, names, from_date, to_date):
        return self.df[
            (self.df['承接者'].isin(names)) &
            (self.df['階段結束時間'] >= from_date) &
            (self.df['階段結束時間'] <= to_date)
        ]

    def pivot_hours(self, df):
        pivot = df.groupby('工時分類名稱')['階段耗時'].sum().reset_index()
        total = pivot['階段耗時'].sum()
        pivot['percent'] = round(pivot['階段耗時'] / total * 100, 2)
        return pivot, total
    def summary_by_person(self, df, from_date, to_date ):
        # ===== 1. Tổng giờ khai báo =====
        declared = (
            df.groupby('承接者')['階段耗時']
            .sum()
            .reset_index(name='declared_hours')
        )

        # ===== 2. Tạo calendar từ from_date -> to_date =====
        all_days = pd.date_range(from_date, to_date, freq='D')

        # Loại Chủ nhật (weekday: Monday=0, Sunday=6)
        working_days = all_days[all_days.weekday != 6]
        standard_days = len(working_days)

        # ===== 3. Giờ tiêu chuẩn =====
        declared['standard_hours'] = standard_days * 8

        # ===== 4. Chênh lệch =====
        declared['difference'] = (
            declared['standard_hours'] - declared['declared_hours']
        )

        return declared