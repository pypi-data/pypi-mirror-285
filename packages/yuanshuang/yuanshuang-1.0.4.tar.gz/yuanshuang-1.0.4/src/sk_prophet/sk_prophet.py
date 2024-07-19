# coding=utf-8
import datetime
import numpy as np
from matplotlib import pyplot as plt
from sqlalchemy import create_engine
from prophet import Prophet
import pandas as pd

def get_engine(db_type, db_user, db_pwd, db_host, db_port, db_name):
    """获取数据库引擎"""
    print(db_type, db_user, db_pwd, db_host, db_port, db_name)
    if db_type == "mysql":
        return create_engine(f"mysql+pymysql://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}?charset=utf8")
    if db_type == "oracle":
        return create_engine(f"oracle+cx_oracle://{db_user}:{db_pwd}@{db_host}:{db_port}/{db_name}")


class ProphetAdv(object):
    """基于prophet模型搭建的销售预测模型"""
    def __init__(self, season_scaler=0.5, predict_model="", future_days=180):
        # 季节因子大小
        self.scaler = season_scaler
        # 最大巅峰值个数
        self.threshold_val_max = 10
        # 最小巅峰值个数
        self.threshold_val_min = 5
        # 未来天数
        self.future_days = future_days
        # 差异化倍数
        self.multiple = 0.8
        # 预测变量
        self.predict_model = predict_model
        # 差异序列
        self.diff_sequence_time = None
        # 预测值
        self.forecast = None
        # 预测值汇总
        self.forecast_sum = None

    def predict(self, df):
        """
        :param df: dataframe columns ['ds', 'y']
        :return: tuple(dataframe,dataframe) (columns ['ds', 'y', 'yhat', 'accuracy'], columns ['ds', 'y', 'yhat'])
        """
        # 负数处理
        df["y"] = df["y"].apply(lambda x:0 if(x <=0) else x)
        # 自定义节假日
        self_holidays = []
        # 获取所有的月份
        df["yf"] = df["ds"].apply(lambda item: item.strftime("%Y-%m"))
        yf_list = list(df["yf"])
        # 峰值动态点数据处理 降低差异化数值
        for yf in yf_list:
            # 获取当前月份下所有的数据
            yf_df = df[df["yf"] == yf].copy()
            # 按照销量排序
            yf_df.sort_values(by="y", ascending=False, inplace=True)
            if len(yf_df) > self.threshold_val_max:
                max_ds = list(yf_df[:self.threshold_val_max]["ds"])
                # 自定以节假日
                holiday = pd.DataFrame({
                    "holiday": "{}".format(yf+"_holiday"),
                    "ds": pd.to_datetime(max_ds),
                    "lower_window": 0,
                    "upper_window": 1
                })
                self_holidays.append(holiday)
            elif len(yf_df) <= self.threshold_val_max:
                max_ds = list(yf_df[:self.threshold_val_min]["ds"])
                # 自定以节假日
                holiday = pd.DataFrame({
                    "holiday": "{}".format(yf + "_holiday"),
                    "ds": pd.to_datetime(max_ds),
                    "lower_window": 0,
                    "upper_window": 1
                })
                self_holidays.append(holiday)
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        # 设置峰值动态点
        self_holidays_df = pd.concat(self_holidays)
        model.holidays = self_holidays_df
        # 设置对应国家的节假日
        model.add_country_holidays("CN")
        # 季节变化因子大小
        model.holidays_prior_scale = self.scaler
        # 拟合模型
        model.fit(df)
        # 创建未来序列
        future = model.make_future_dataframe(periods=self.future_days, freq='D')
        # 创建差异序列 数据末端到未来序列顶端的时间序列
        diff_days = pd.date_range(
            df["ds"].max() + datetime.timedelta(days=1),
            end=future["ds"].max(), freq="D")
        # 记录差异序列
        self.diff_sequence_time = diff_days
        diff_days_df = pd.DataFrame(diff_days, columns=["ds"])
        # 设置差异序列初始值
        diff_days_df["y"] = 0
        # 预测未来数据
        forecast = model.predict(future)
        df = pd.concat([df, diff_days_df])
        forecast["y"] = list(df["y"])
        # 查询预测值小于0的数据节点
        forecast_fs = forecast.query(" yhat <=0 ")
        # 对预测值小于0的预测节点值进行处理
        for index, row in forecast_fs.iterrows():
            ds = row["ds"]
            month = ds.month
            year = ds.year
            day = ds.day
            # 寻找对应的年月日
            temp_df = forecast[(forecast["ds"].dt.year == year - 1) & (forecast["ds"].dt.month == month) & (forecast["ds"].dt.day==day)]
            if temp_df is not None and temp_df.empty == False:
                y = temp_df.iloc[0]["y"]
                forecast.at[index, "yhat"] = y * self.multiple
            else:
                forecast.at[index, "yhat"] = 0
        # 获取对应的 预测区间 预测值 以及时间序列
        sum_df = forecast[["ds", "y", "yhat", "yhat_lower", "yhat_upper"]].copy()
        # 按月分组并求和
        monthly_sum = sum_df.groupby(sum_df['ds'].dt.to_period('M')).agg({"y": "sum", "yhat": "sum"})
        # 如果预测值小于0 那么就将预测值设置为去年同期的数据
        monthly_sum.reset_index("ds", inplace=True, drop=False)
        self.forecast = forecast
        self.forecast_sum = monthly_sum
        return forecast, monthly_sum


    def draw_plot(self, forecast, monthly_sum):
        plt.figure(figsize=(20, 8))
        x_axis = np.arange(len(forecast))
        x_test_axis = np.arange(len(forecast))
        plt.plot(x_axis, forecast["yhat"], label="yhat", color="black", linewidth=3, markersize=2, marker="o")
        plt.plot(x_test_axis, forecast["y"], label="y", color="red", linewidth=3, markersize=2, marker="o")
        forecast["ds_ticks"] = forecast["ds"].apply(lambda x: x.strftime('%Y-%m-%d'))
        plt.xticks(x_axis[::7], forecast["ds_ticks"][::7], rotation=45)
        plt.title("{}".format(self.predict_model))
        plt.legend("best")
        plt.show()

        plt.figure(figsize=(20, 8))
        monthly_sum["ds_str"] = monthly_sum["ds"].apply(lambda x: x.strftime("%Y-%m"))
        x_ = list(monthly_sum["ds_str"])
        y_ = list(monthly_sum["y"])
        yhat_ = list(monthly_sum["yhat"])
        plt.bar(x_, y_, color="blue", alpha=1)
        plt.bar(x_, yhat_, color="red", alpha=0.5)
        plt.title("{}".format(self.predict_model))
        plt.legend("best")
        plt.show()