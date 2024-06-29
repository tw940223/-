
from flask import Flask, render_template
import pyodbc
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
import traceback

app = Flask(__name__)

def get_data():
    try:
        conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                              'Server=LAPTOP-QV5BBV9V\\SQLEXPRESS;'
                              'Database=comebuy;'
                              'Trusted_Connection=yes;')
        sql = '''SELECT * FROM comebuy'''
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception as e:
        print(f"Error in get_data: {e}\n{traceback.format_exc()}")
        raise

def create_charts(df):
    regions = {
        '北部': ['台北市', '新北市', '基隆市', '桃園市', '新竹市', '新竹縣'],
        '中部': ['台中市', '苗栗縣', '彰化縣', '南投縣', '雲林縣'],
        '南部': ['台南市', '高雄市', '嘉義市', '嘉義縣', '屏東縣'],
        '東部': ['宜蘭縣', '花蓮縣', '台東縣'],
        '外島': ['澎湖縣', '金門縣', '連江縣']
    }

    def extract_region(address):
        for region, cities in regions.items():
            if any(city in address for city in cities):
                return region
        return '其他'

    df['Region'] = df['FullAddress'].apply(extract_region)
    df.drop_duplicates(subset=['ShopName', 'FullAddress'], inplace=True)
    df = df[df['Region'] != '其他']  # 移除 "其他" 類別
    region_counts = df['Region'].value_counts()

    plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 長條圖
    fig, ax = plt.subplots(figsize=(12, 8))
    region_counts.plot(kind='bar', ax=ax)
    ax.set_title('各地區店家數量分布')
    ax.set_xlabel('地區')
    ax.set_ylabel('店家數量')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    for container in ax.containers:
        ax.bar_label(container)
    
    bar_chart = io.BytesIO()
    plt.savefig(bar_chart, format='png')
    bar_chart.seek(0)
    bar_chart_base64 = base64.b64encode(bar_chart.getvalue()).decode()

    # 圓餅圖
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.pie(region_counts, labels=region_counts.index, autopct='%1.1f%%', startangle=140)
    ax.set_title('各地區店家數量分布')
    
    pie_chart = io.BytesIO()
    plt.savefig(pie_chart, format='png')
    pie_chart.seek(0)
    pie_chart_base64 = base64.b64encode(pie_chart.getvalue()).decode()

    return bar_chart_base64, pie_chart_base64

@app.route('/')
def index():
    try:
        df = get_data()
        bar_chart, pie_chart = create_charts(df)
        return render_template('index.html', bar_chart=bar_chart, pie_chart=pie_chart)
    except Exception as e:
        error_message = f"An error occurred: {e}\n{traceback.format_exc()}"
        print(error_message)
        return error_message

if __name__ == '__main__':
    try:
        app.run(debug=True)
    except Exception as e:
        print(f"An error occurred during startup: {e}\n{traceback.format_exc()}")

