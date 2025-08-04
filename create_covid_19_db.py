
import pandas as pd
import sqlite3


class CreateCovid19DB:
    """
    此類別負責處理 COVID-19 的時間序列資料與每日報告，
    並將結果存入 SQLite 資料庫中的 time_series 與 daily_report 資料表。
    """

    def create_time_series(self):
        """
        處理 time_series_covid19_confirmed_global.csv、time_series_covid19_deaths_global.csv、
        time_series_covid19_vaccine_global.csv 三個檔案，並合併成統一格式的 DataFrame。
        回傳欄位包含：country, reported_on, confirmed, deaths, doses_administered。
        """
        confirmed = pd.read_csv("data/time_series_covid19_confirmed_global.csv")  # 讀取全球確診數據
        deaths = pd.read_csv("data/time_series_covid19_deaths_global.csv")  # 讀取全球死亡數據
        vaccine = pd.read_csv("data/time_series_covid19_vaccine_global.csv")  # 讀取全球疫苗接種數據

        id_variables = ["Province/State", "Country/Region", "Lat", "Long"]
        melted_confirmed = pd.melt(confirmed, id_vars=id_variables, var_name="Date", value_name="Confirmed") # 將確診數據從寬格式轉為長格式
        melted_deaths = pd.melt(deaths, id_vars=id_variables, var_name="Date", value_name="Deaths")  # 將死亡數據從寬格式轉為長格式

        # 將日期欄位轉為 datetime64[ns] 格式 => ISO 8601
        melted_confirmed["Date"] = pd.to_datetime(melted_confirmed["Date"], format="%m/%d/%y")
        melted_deaths["Date"] = pd.to_datetime(melted_confirmed["Date"], format="%m/%d/%y")

        # 移除確診與死亡數據中的緯度與經度欄位
        melted_confirmed = melted_confirmed.drop(["Lat", "Long"], axis=1)
        melted_deaths = melted_deaths.drop(["Lat", "Long"], axis=1)

        vaccine["Province_State"] = vaccine["Province_State"].astype(object) # 統一資料類型: float -> object
        vaccine["Date"] = pd.to_datetime(vaccine["Date"])   # 將疫苗數據中的日期欄位轉為 datetime64[ns]
        # 將疫苗數據的欄位名稱改為與確診、死亡數據一致
        vaccine = vaccine.rename(columns={"Province_State": "Province/State", "Country_Region": "Country/Region"})

        # 移除疫苗數據中不需要的欄位
        vaccine = vaccine.drop(labels=["UID", "People_at_least_one_dose"], axis=1) 

        # 定義合併三份資料的關鍵欄位
        join_keys = ["Province/State", "Country/Region", "Date"]
        time_series = pd.merge(melted_confirmed, melted_deaths, left_on=join_keys, right_on=join_keys, how="left")  #將確診數據與死亡數據依照 join_keys 合併 => 新增 Deaths
        time_series = pd.merge(time_series, vaccine, left_on=join_keys, right_on=join_keys, how="left") # 再將疫苗數據合併進來 => 新增 Doses_admin

        time_series = time_series.drop(["Province/State"], axis=1) # 由於我們只要國家層級，因此將 Province/State 欄位移除

        # 以 Country/Region 與 Date 進行群組，加總確診、死亡與施打疫苗數
        time_series = time_series.groupby(["Country/Region", "Date"])[["Confirmed", "Deaths", "Doses_admin"]].sum().reset_index()
        time_series.columns = ["country", "reported_on", "confirmed", "deaths", "doses_administered"]  # 將欄位名稱轉為統一格式

        # 將 doses_administered 由 float 轉為 int 型態，與 confirmed/deaths 一致
        time_series["doses_administered"] = time_series["doses_administered"].astype(int) 

        return time_series


    def create_daily_report(self):
        """
        讀取單日 (03-09-2023.csv) 報告，並將欄位標準化。
        回傳欄位包含：country, province, county, confirmed, deaths, latitude, longitude。
        """
        daily_report = pd.read_csv("data/03-09-2023.csv")  # 讀取每日報告資料 (03-09-2023)
        daily_report = daily_report[["Country_Region", "Province_State", "Admin2", "Confirmed", "Deaths", "Lat", "Long_"]]  # 篩選需要的欄位
        daily_report.columns = ["country", "province", "county", "confirmed", "deaths", "latitude", "longitude"]  # 將欄位名稱統一命名

        return daily_report


    def create_database(self):
        """
        主函式：將處理好的 time_series 與 daily_report 資料寫入 SQLite 資料庫。
        """

        time_series = self.create_time_series()  # 取得處理後的時間序列資料

        # 將 reported_on 欄位由 datetime64[ns] 轉為 ISO 8601 字串格式 (YYYY-MM-DD)
        # SQLite 資料庫本身沒有 DATE 型態，若不轉為字串將會導致資料庫誤判型別
        # 透過 x.strftime("%Y-%m-%d") 轉為標準字串，確保儲存後仍可正常進行日期查詢與排序
        time_series["reported_on"] = time_series["reported_on"].map(lambda x: x.strftime("%Y-%m-%d"))
        
        daily_report = self.create_daily_report()  # 取得處理後的每日報告資料

        connection = sqlite3.connect("data/covid_19.db")
        time_series.to_sql(name="time_series", con=connection, index=False, if_exists="replace")  # 將 time_series 寫入資料庫，若已存在則覆蓋
        daily_report.to_sql(name="daily_report", con=connection, index=False,if_exists="replace")  # 將 daily_report 寫入資料庫，若已存在則覆蓋
        connection.close()


def test():
    create_covid_19_db = CreateCovid19DB()
    create_covid_19_db.create_database()

if __name__ == "__main__":
    test()









