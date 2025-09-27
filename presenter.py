from dash import Dash
import plotly.express as px
import pandas as pd
from metric_collector import (
    collect_metrics,
    process_metrics,
    fill_nan_with_last_amounts_from_previous_dates,
)


metrics = collect_metrics()
df = process_metrics(metrics)
df = fill_nan_with_last_amounts_from_previous_dates(df)
# Fill NaN values with 0
df = df.fillna(0)

df.to_csv("data/metrics_filled.csv")


app = Dash(__name__)

# Melt the dataframe to long format for plotly
df_melted = df.reset_index().melt(
    id_vars="index", var_name="Status", value_name="Count"
)
df_melted.rename(columns={"index": "Date"}, inplace=True)

fig = px.area(df_melted, x="Date", y="Count", color="Status")
fig.show()


# app.run(debug=True)
