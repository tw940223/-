from flask import Flask, render_template_string
import pandas as pd
import pyodbc

app = Flask(__name__)

# 連接到 SQL Server 資料庫
def get_db_connection():
    conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                          'Server=LAPTOP-QV5BBV9V\SQLEXPRESS;'
                          'Database=comebuy;'
                          'Trusted_Connection=yes;')
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    query = "SELECT * FROM comebuy"
    df = pd.read_sql(query, conn)
    conn.close()
    
    # 將數據轉換為 HTML 表格
    html_table = df.to_html(classes='table table-striped', index=False)
    
    # 渲染模板
    html = f'''
    <!doctype html>
    <html lang="zh-Hant">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css">
        <title>Comebuy Stores</title>
      </head>
      <body>
        <div class="container">
          <h1 class="mt-5">Comebuy Stores</h1>
          {html_table}
        </div>
      </body>
    </html>
    '''
    
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
