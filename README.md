# Stock Price Forecasting App (Prophet + Streamlit)

An AI-powered forecasting tool that lets users select any stock symbol (e.g., `AAPL`, `INFY`) and predict its future prices using **Facebook Prophet**. Includes interactive **candlestick + volume charts**, **evaluation metrics**, and **downloadable forecast CSVs**. Built with **Streamlit**.

---

## Features

- Input any valid stock ticker (e.g., AAPL, MSFT, TSLA)
- Choose historical time range in **months or years**
- Forecast closing prices for up to **90 days into the future**
- Automatically fetch historical OHLCV data using **yfinance**
- Show **candlestick chart + volume bars** for price action
- Train a **Prophet forecasting model** with auto tuning
- Display:
  - Forecast vs Actual prices (clean dual-line chart)
  - Candlestick + Volume chart (Plotly)
  - Evaluation metrics: **RMSE**, **MAE**, **R²**
- Export forecast results to `.csv`
- Fully interactive and beginner-friendly UI via **Streamlit**

---

## 📸 App Screenshots

### 🔹 Candlestick + Volume
![Candlestick Chart](screenshots/candlestick.png)

### 🔹 Forecast vs Actual Prices
![Forecast vs Actual](screenshots/forecast.png)

### 🔹 Evaluation Metrics
![Metrics](screenshots/metrics.png)

### 🔹 Download Forecast as CSV
![Download CSV](screenshots/download.png)

---

## 🛠 How to Run Locally

```bash
git clone https://github.com/your-username/stock-price-forecasting-app.git
cd stock-price-forecasting-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run stock_forecasting_app.py
