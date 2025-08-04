
import sqlite3
import pandas as pd
import gradio as gr
import plotly.graph_objects as go

# ===========================================
# 讀取 SQLite 資料庫內的 daily_report 與 time_series 資料表
# ===========================================
connection = sqlite3.connect("data/covid_19.db")
daily_report = pd.read_sql("""SELECT * FROM daily_report;""", con=connection)  # 從 daily_report 資料表中讀取所有資料到 pandas DataFrame
time_series = pd.read_sql("""SELECT * FROM time_series;""", con=connection) # 從 time_series 資料表撈取所有資料，讀入為 pandas DataFrame
connection.close()

# 計算全世界累積確診、死亡人數 => daily_report時間:(03-09-2023)，採用累記個數
total_cases = daily_report["confirmed"].sum()
total_deaths = daily_report["deaths"].sum()

# 因為 time_series 採用的是隨時間的累積個數   => 取用 "2023-03-09" 來計算疫苗接種數
latest_time_series = time_series[time_series["reported_on"] == "2023-03-09"]
total_vaccinated = latest_time_series["doses_administered"].sum()

# 將 reported_on 欄位轉換為 pandas datetime64[ns] 型態 (時間戳記格式)
# 這樣才能進行時間序列繪圖與時間運算 => 後續畫 Gradio折線圖 會用到這個欄位作為 x 軸 !!
time_series["reported_on"] = pd.to_datetime(time_series["reported_on"])

# 取得確診數前 30 名的國家清單，用於下拉選單預設值
sum_confirmed_by_country = daily_report.groupby("country")["confirmed"].sum().sort_values(ascending=False)
top_confirmed = sum_confirmed_by_country.index[:30].to_list()



# =============================================================
# Function: filter_global_map
# 功能：根據選取的國家名稱，過濾 daily_report 資料，
#       並依據確診數與死亡數繪製地圖 (Plotly Scattermapbox)
#       並自定義 hover 顯示內容。
# =============================================================
def filter_global_map(country_names):

    # 根據選取的國家過濾 daily_report
    filtered_daily_report = daily_report[daily_report["country"].isin(country_names)]

    # 取出 hover 需要顯示的資訊
    countries = filtered_daily_report["country"].to_numpy()
    provinces = filtered_daily_report["province"].to_numpy()
    counties = filtered_daily_report["county"].to_numpy()
    confirmed = filtered_daily_report["confirmed"].to_numpy()
    deaths = filtered_daily_report["deaths"].to_numpy()

    # 建立 hover 的資訊列表
    information_when_hovered = []

    # 因為資料部份只有三種類型:
    # [1] country  [2] (country, province)  [3] (country, province, county) 
    # 因此從 county開始判定回去 county -> province -> country
    for country, province, county, c, d in zip(countries, provinces, counties, confirmed, deaths):
        if county is not None:
            marker_information = [(country, province, county), c, d]
        elif province is not None:
            marker_information = [(country, province), c, d]
        else:
            marker_information = [country, c, d]

        information_when_hovered.append(marker_information)


    # 使用 Plotly Scattermapbox 繪製地圖標記點
    fig = go.Figure(
        go.Scattermapbox(  
            name="",   # trace 名稱設為空字串，避免 hover 顯示 trace 0 => 要用自訂的 hovertemplate
            lat=filtered_daily_report["latitude"],  # 設定點的緯度
            lon=filtered_daily_report["longitude"],  # 設定點的經度
            customdata=information_when_hovered,  # hover 顯示用的自訂資料
            hoverinfo="text",
            # 顯示 customdata 陣列中的第 0 個元素 (地點資訊：國家/省/縣) 
            # 換行並顯示 customdata[1]，即確診人數
            # 再換行並顯示 customdata[2]，即死亡人數
            hovertemplate="Location: %{customdata[0]}<br>Confirmed: %{customdata[1]}<br>Deaths: %{customdata[2]}",
            mode="markers",  # 使用標記點 (marker) 模式
            marker={
                "size": filtered_daily_report["confirmed"],  # 根據確診人數調整點的大小
                "color": filtered_daily_report["confirmed"],  # 根據確診人數決定顏色
                "sizemin": 2,  # 設定最小點大小為 2
                # sizeref 是為了讓 marker 的最大大小控制在適當範圍
                # 最大值會被縮放到 2500 單位，其他點按比例縮放
                "sizeref": filtered_daily_report["confirmed"].max() / 2500,
                "sizemode": "area"  # 點的大小與確診數成面積比
            }
        )
    )

    # 設定地圖樣式與視角
    fig.update_layout(
        height=800,  # 圖表高度
        mapbox_style="open-street-map",  # 使用 OpenStreetMap 的底圖
        mapbox=dict(
            zoom=2,  # 預設地圖縮放等級
            center=go.layout.mapbox.Center(lat=0, lon=0)  # 地圖中心點為 (0, 0) 的經緯度
        )
    )

    return fig  # 回傳 Plotly 圖表



# =============================================================
# Gradio Tab 1: Global Map 介面區塊
# 包含：數據統計、國家選單、更新按鈕、地圖 Plot 區塊
# =============================================================
with gr.Blocks() as global_map_tab:
    gr.Markdown("""# Covid 19 Global Map""")  # 頁面標題

    # 數據統計資訊區 (三個 Label 顯示總確診、總死亡、總疫苗接種數)
    with gr.Row():
        gr.Label(f"{total_cases:,}", label="Total cases")
        gr.Label(f"{total_deaths:,}", label="Total deaths")
        gr.Label(f"{total_vaccinated:,}", label="Total doses administered")
    
    # 國家下拉式選單 + 更新按鈕區
    with gr.Column():
        countries = gr.Dropdown(choices=daily_report["country"].unique().tolist(),
                                label="Select countries:", 
                                multiselect=True,   # 支援多選
                                value=top_confirmed  # 預設選擇確診數前 30 名國家
        )
        btn = gr.Button(value="Update") # 更新按鈕
        global_map = gr.Plot() # 地圖顯示區塊

    # 當頁面載入時，自動執行 filter_global_map 並將結果顯示在 global_map (自動帶入上述的預設值: 預設選擇確診數前 30 名國家)
    global_map_tab.load(fn=filter_global_map,
                        inputs=countries,
                        outputs=global_map)
    
    # 當按下 Update 按鈕時，重新執行 filter_global_map 並更新 global_map
    btn.click(fn=filter_global_map,
              inputs=countries,
              outputs=global_map)




# =============================================================
# Function: filter_time_series
# 功能：根據選取的國家名稱，過濾 time_series 資料，
#       並將相同資料回傳給 3 個折線圖 (Confirmed / Deaths / Doses)
# =============================================================
def filter_time_series(selected_country):
    filtered_df = time_series[time_series["country"] == selected_country]
    return filtered_df, filtered_df, filtered_df  # 回傳給 3 個 LinePlot => 準備給 [plt_confirmed, plt_deaths, plt_doses] 去進行折線圖作圖


# =============================================================
# Gradio Tab 2: Country Time Series 折線圖區塊
# 包含：國家選單、確診數折線圖、死亡數折線圖、疫苗施打數折線圖
# =============================================================
with gr.Blocks() as country_time_series_tab:
    gr.Markdown("""# Covid 19 Country Time Series""")  # 加入網頁標題 (Markdown 格式)

    # 國家下拉式選單 (Dropdown)
    with gr.Row():
        country_dropdown = gr.Dropdown(choices=time_series["country"].unique().tolist(),
                                       label="Select a country:",
                                       value="Taiwan*"  # 預設選擇 Taiwan*
        )
    
    # 三個時間序列折線圖元件 (LinePlot)
    plt_confirmed = gr.LinePlot(label="Confirmed Cases", x="reported_on", y="confirmed")  # 折線圖：確診數
    plt_deaths = gr.LinePlot(label="Deaths", x="reported_on", y="deaths")  # 折線圖：死亡數
    plt_doses = gr.LinePlot(label="Doses Administered", x="reported_on", y="doses_administered")  # 折線圖：疫苗施打數

    # 當頁面載入時，自動載入 Taiwan* 資料(上述下拉式選單 value預設值)，並繪製上述3組折線圖
    # inputs 放入 filter_time_series 後會 return 3組一樣的 df 個別傳入 plt_confirmed, plt_deaths, plt_doses 進行折線圖繪製
    country_time_series_tab.load(fn=filter_time_series,
                                 inputs=country_dropdown,
                                 outputs=[plt_confirmed, plt_deaths, plt_doses] 
    )

    # 綁定 Dropdown 的變更事件，當選單變更時，重新過濾並更新折線圖 => 3 個圖表都會更新
    country_dropdown.change(
        fn=filter_time_series,
        inputs=country_dropdown,
        outputs=[plt_confirmed, plt_deaths, plt_doses]
    )


# =============================================================
# Gradio TabbedInterface 介面：
# 把上面兩個 Gradio介面: global_map_tab, country_time_series_tab 命名成 Global Map 與 Country Time Series，
# 並將這兩個 Blocks 區塊包成分頁 (Tab)
# =============================================================
demo = gr.TabbedInterface([global_map_tab, country_time_series_tab], ["Global Map", "Country Time Series"])

demo.launch()  # 啟動 Gradio 介面

