

import sqlite3
import pandas as pd
import gradio as gr


connection = sqlite3.connect("data/covid_19.db")
time_series = pd.read_sql("""SELECT * FROM time_series;""", con=connection)  # 從 time_series 資料表撈取所有資料，讀入為 pandas DataFrame
connection.close()

# 將 reported_on 欄位轉換為 pandas datetime64[ns] 型態 (時間戳記格式)
# 這樣才能進行時間序列繪圖與時間運算
time_series["reported_on"] = pd.to_datetime(time_series["reported_on"])

# 篩選國家為 Taiwan* 的資料，只留下台灣的數據
# 注意：資料來源將 Taiwan 記錄為 Taiwan*，需特別處理
time_series = time_series[time_series["country"] == "Taiwan*"] 

# 使用 Gradio 建立網頁介面
with gr.Blocks() as demo:
    gr.Markdown("""# Covid 19 Country Time Series""")  # 加入網頁標題 (Markdown 格式)
    gr.LinePlot(time_series, x="reported_on", y="confirmed") # 繪製「確診數」的時間序列折線圖
    gr.LinePlot(time_series, x="reported_on", y="deaths")  # 繪製「死亡數」的時間序列折線圖
    gr.LinePlot(time_series, x="reported_on", y="doses_administered") # 繪製「疫苗接種數」的時間序列折線圖

demo.launch()