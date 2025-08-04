# Project 5: The Pandemic Era

## Introduction

This project, "The Pandemic Era," utilizes the COVID-19 time series and daily reports data provided by CSSE at Johns Hopkins University [csse\_covid\_19\_data](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data). The dataset spans from 2020-01-22 to 2023-03-09, including daily case counts and vaccination data.

We built an interactive dashboard to visualize the pandemic trends using `pandas` and `sqlite3` to structure the data and `gradio` to develop the frontend interface for proof-of-concept.

## ⚙️ How to Reproduce

* Install [Miniconda](https://docs.anaconda.com/miniconda)
* Create the environment from `environment.yml`:

```bash
conda env create -f environment.yml
```

* Place the following 4 CSV files into the `data/` folder:

  * `03-09-2023.csv`
  * `time_series_covid19_confirmed_global.csv`
  * `time_series_covid19_deaths_global.csv`
  * `time_series_covid19_vaccine_global.csv`

* Run the script to build the SQLite database:

```bash
python create_covid_19_db.py
```

* Launch the Gradio app to explore the dashboard:

```bash
python app.py
```

Visit `http://127.0.0.1:7860` in your browser to interact with the dashboard.

## 📁 Project Structure

```
COVID_19_PANDEMIC/
├── data/
│   ├── 03-09-2023.csv
│   ├── covid_19.db
│   ├── time_series_covid19_confirmed_global.csv
│   ├── time_series_covid19_deaths_global.csv
│   └── time_series_covid19_vaccine_global.csv
├── app.py
├── create_covid_19_db.py
├── proof_of_concept_line.py
├── proof_of_concept_map.py
├── environment.yml
└── README.md
```

## 🚀  Live Demo (Hugging Face Spaces)

You can try out the interactive version of this app deployed on Hugging Face Spaces:

🔗 **[Launch the Covid-19 Dashboard 🌍](https://huggingface.co/spaces/AustinKang66666/covid_19_pandemic)**

No local setup needed — explore directly in your browser!

## 📊 Environment Setup (environment.yml)

```yaml
name: covid_19_pandemic
channels:
  - conda-forge
dependencies:
  - python=3.12
  - pandas=2.3.1
  - numpy=2.0.1
  - plotly=6.0.1
  - sqlite=3.50.2
  - pip:
      - gradio==5.39.0
```

## 🔧 Features & Functionality

* **Global Map Visualization**: An interactive world map displaying COVID-19 confirmed cases and deaths by region. Hover over points to view detailed data.
* **Country Time Series Analysis**: Select a country to view time series line charts of confirmed cases, deaths, and vaccination progress.
* **Real-time Filtering**: Dropdown selections allow dynamic updates of maps and graphs.

> This project demonstrates how to integrate data processing with a user-friendly web interface for pandemic monitoring and analysis.
