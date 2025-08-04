
import sqlite3
import pandas as pd
import gradio as gr
import plotly.graph_objects as go


connection = sqlite3.connect("data/covid_19.db")
daily_report = pd.read_sql("""SELECT * FROM daily_report;""", con=connection)  # 從 daily_report 資料表中讀取所有資料到 pandas DataFrame
connection.close()

# 建立 Plotly 的地圖 (Scattermapbox)
fig = go.Figure(
    go.Scattermapbox(
        lat=daily_report["latitude"],  # 設定點的緯度
        lon=daily_report["longitude"],  # 設定點的經度
        mode="markers",  # 使用標記點 (marker) 模式
        marker={
            "size": daily_report["confirmed"],  # 根據確診人數調整點的大小
            "color": daily_report["confirmed"],  # 根據確診人數決定顏色
            "sizemin": 2,  # 設定最小點大小為 2
            # sizeref 是為了讓 marker 的最大大小控制在適當範圍
            # 最大值會被縮放到 2500 單位，其他點按比例縮放
            "sizeref": daily_report["confirmed"].max() / 2500,
            "sizemode": "area"  # 點的大小與確診數成面積比
        }
    )
)

# 設定地圖樣式與視角
fig.update_layout(
    mapbox_style="open-street-map",  # 使用 OpenStreetMap 的底圖
    mapbox=dict(
        zoom=2,  # 預設地圖縮放等級
        center=go.layout.mapbox.Center(lat=0, lon=0)  # 地圖中心點為 (0, 0) 的經緯度
    )
)


# 使用 Gradio 建立網頁介面
with gr.Blocks() as demo:
    gr.Markdown("""# Covid 19 Global Map""")  # 頁面標題
    gr.Plot(fig)  # 顯示 Plotly 畫出的地圖

# 啟動 Gradio 介面 (預設 localhost:7860)
demo.launch()