
from base64 import b64encode
import pandas
import plotly.graph_objects as go
from statsmodels.tsa.api import ExponentialSmoothing
from datetime import timedelta, datetime
import pandas as pd
import numpy as np

df = pandas.read_csv(
    '/Users/genesis.thomas/workspace/python/generic/PerfectoCustomReport/src/perfecto/output1.csv', low_memory=False)

df = df[(df["Status"] == "FAILED")]


def forecast_failures(df):

    if len(df.week.unique()) > 1:
        seasonal_periods = 5
        predict_days = 5
    else:
        seasonal_periods = 2
        predict_days = 2
    df["startHour"] = pandas.to_datetime(
        pandas.to_datetime(df["startTime"], format="%Y-%m-%d %H:%M:%S")
        .dt.to_period("H")
        .astype(str)
    )
    
    df_hour = df['startHour'].value_counts().rename_axis('Hour').reset_index(
        name='counts').sort_values(by=['Hour'], ascending=True)
    df_hour = df_hour.set_index(["Hour"])
    df_hour = df_hour.resample('H').mean().replace(np.nan, 0)

    start_time = str(df_hour.index[-1])
    future_time = str(df_hour.index[-1] + timedelta(days=predict_days))
    futureDate = str((datetime.strptime(
        future_time, "%Y-%m-%d %H:%M:%S") + timedelta(days=1)).date())
    predict_df = pd.DataFrame(
        {'Hour': pd.date_range(
            start_time.split(" ")[0], futureDate, freq='1H')}
    )
    predict_df = predict_df.set_index(["Hour"])
    predict_df['counts'] = 0
    y_hat_avg = predict_df.copy()
    y_hat_avg['forecast'] = ExponentialSmoothing(
        df_hour['counts'], seasonal_periods=seasonal_periods, trend='add', seasonal='add').fit().predict(start=start_time, end=future_time)
    y_hat_avg[y_hat_avg < 0] = 0
    y_hat_avg['forecast'] = y_hat_avg['forecast'].replace(
        np.nan, 0).round(0).astype(int)

    # Past data top 3
    top_dates = df_hour.sort_values(by=['counts'], ascending=False).head(3)
    vals = []
    for tgl, tot in zip(top_dates.index, top_dates["counts"]):
        val = "%d" % (tot)
        vals.append(val)
    top_dates['tgl'] = vals

    fig = go.Figure(data=go.Scatter(x=top_dates.index, y=top_dates['counts'],
                                    textposition='top center',
                                    textfont=dict(color='#233a77'),
                                    mode='markers+text',
                                    marker=dict(color='red', size=3),
                                    visible=True, name="Top 3 Total Failures",
                                    text=top_dates["tgl"]))

# fig.add_traces(data=go.Scatter(x=df_hour.index.astype(dtype=str),
#                                 y=df_hour['counts'],
#                                 visible = True,
#                                 marker_color='red',
#                                 name = "Failures (line)",
#                                 text="counts"))

    fig.add_traces(data=go.Bar(x=df_hour.index.astype(dtype=str),
                               y=df_hour['counts'], visible=True, name="Actual Total Failures",
                               marker_color='tomato', text=df_hour["counts"]))

# fig.add_traces(data=go.Scatter(x=y_hat_avg.index.astype(dtype=str),
#                           y=y_hat_avg['forecast'],visible = True, name = "Failure Forecast (line)",
#                           marker_color='orange', text="forecast"))

    fig.add_traces(data=go.Bar(x=y_hat_avg.index.astype(dtype=str),
                               y=y_hat_avg['forecast'], visible=True, name="Forecast",
                               marker_color='orange', text=y_hat_avg["forecast"]))

    fig.update_layout(bargap=0.01, showlegend=True, autosize=True, height=400, width=1200, title={"text": "Weekly Failures Trend per hour", "y": 0.97, "x": 0.5,
                                                                                                  "xanchor": "center", "yanchor": "top"})
    fig.update_xaxes(
        rangeslider_visible=False)
    fig.show()
    img = fig.to_image(format="png", engine="kaleido")

    summary = '<img alt="execution summary" id="box" style="height: 400px;width: 1200px !important;" src="data:image/png;base64, {}" >'.format(
        b64encode(img).decode("utf-8"))
    return summary


print(forecast_failures(df))
