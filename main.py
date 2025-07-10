# Import Librarires

import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from prophet import Prophet
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import mean_squared_error , mean_absolute_error ,r2_score


# Sidebar Inputs

st.sidebar.title("Stock Price Forecaster")
ticker=st.sidebar.text_input("Enter Stock Ticker/Symbol",value="AAPL")
period_unit=st.sidebar.radio("Choose A Time Unit For History",("Years","Months"),horizontal=True)
if period_unit=="Years":
    years_back=st.sidebar.slider("Years Of History",1,10,3)
    start=date.today() - timedelta(days=365*years_back)
    end=date.today()
else:
    months_back=st.sidebar.slider("Months Of History",1,11,3)
    start=date.today() - timedelta(days=30*months_back)
    end=date.today()
forecast_period=st.sidebar.slider("Forecast Period (Days)",7,90,30)

# Data Download 

@st.cache_data
# For Prophet: Adjusted Close Only
@st.cache_data
def load_prophet_data(sym, start, end):
    df = yf.download(sym, start=start, end=end, auto_adjust=True)  # adjusted
    df.reset_index(inplace=True)
    df = df[["Date", "Close"]].rename(columns={"Date": "ds", "Close": "y"})
    if isinstance(df.columns, pd.MultiIndex):
        df.columns=[col[0] if isinstance(col,tuple) else col for col in df.columns]

    return df

# 2) For Candlestick + Volume: Raw OHLCV
@st.cache_data
def load_ohlcv(sym, start, end):
    df = yf.download(sym, start=start, end=end, auto_adjust=False) # raw
    df.reset_index(inplace=True)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns=[col[0] if isinstance(col,tuple) else col for col in df.columns]

    return df

# Showing Raw Closing Price With Candlesticks

data=load_ohlcv(ticker,start,end)
st.subheader(f"Raw Closing Price - {ticker}")

fig= make_subplots(
    rows=2,cols=1 , shared_xaxes=True,
    row_heights=[0.7,0.3] , vertical_spacing=0.02,
    specs=[[{"type":"candlestick"}],
           [{"type":"bar"}]]
)

# Candlestick Trace
fig.add_trace(go.Candlestick(
    x=data["Date"],
    open=data["Open"],
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    name="Price"
),row=1,col=1

)

# Volume
vol_colors = []

for i in range(len(data)):
    if data["Close"][i] >= data["Open"][i]:
        vol_colors.append("rgba(0,255,0,0.5)")   # green for up days
    else:
        vol_colors.append("rgba(255,0,0,0.5)")  # red for down days

fig.add_trace(go.Bar(
    x=data["Date"],
    y=data["Volume"],
    marker_color=vol_colors ,
    showlegend=False,
    name="Volume"
),row=2,col=1

)

# Layout 
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    yaxis2_title="Volume",
    height=600,
    margin=dict(t=40,b=20),
    xaxis_rangeslider_visible=False
)

# Display In Streamlit
st.plotly_chart(fig,use_container_width=True)

# Prophet Forecasting

prophet_data=load_prophet_data(ticker,start,end)

# Train Test Split
train_df=prophet_data[:-forecast_period]
test_df=prophet_data[-forecast_period:]

m=Prophet(daily_seasonality=False,weekly_seasonality=True,yearly_seasonality=True)
m.fit(train_df)
future=m.make_future_dataframe(periods=forecast_period)
forecast=m.predict(future)

st.subheader("Forecast Vs Actual")
fig_forecast=go.Figure()

# Forecasted Value
fig_forecast.add_trace(go.Scatter(
    x=forecast["ds"], 
    y=forecast["yhat"],
    mode="lines",
    name="Predicted Price",
    line=dict(color="white",width=2)
))

# Actual Value
fig_forecast.add_trace(go.Scatter(
    x=prophet_data["ds"],
    y=prophet_data["y"],
    mode="lines",
    name="Actual Price",
    line=dict(color="red",width=3),
    

))
fig_forecast.update_layout(
    title="Stock Prices Forecast Vs Actual",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    height=500
)
st.plotly_chart(fig_forecast,use_container_width=True)

# Evaluation Metrics

forecast_indexed = forecast.set_index("ds")
common_dates = test_df["ds"][test_df["ds"].isin(forecast_indexed.index)]
y_pred = forecast_indexed.loc[common_dates, "yhat"].values
y_true = test_df.set_index("ds").loc[common_dates, "y"].values


rmse=np.sqrt(mean_squared_error(y_true,y_pred))
mae=mean_absolute_error(y_true,y_pred)
r2=r2_score(y_true,y_pred)

st.subheader("Model Performance On Hold Out")
st.write(f"RMSE : {rmse:,.2f}")
st.write(f"MAE : {mae:,.2f}")
st.write(f"R2 Score : {r2:,.3f}")

# Forecast CSV Download

csv=forecast[["ds","yhat","yhat_lower","yhat_upper"]].to_csv(index=False).encode()
st.download_button(
    label="Download Forecast (CSV)",
    data=csv,
    file_name=f"{ticker}_forecast.csv",
    mime="text/csv"
)