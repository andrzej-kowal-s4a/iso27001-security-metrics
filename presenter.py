import plotly.express as px
from metric_collector import (
    create_df,
)
from metric_collector import MetricsCollector

# jql = 'project = SECURITY AND issuetype="Security Incident"'
jql = 'project not in (SERVICE) AND ( labels in ("security", "incident", "breach") OR summary ~ "breach" OR summary ~ "incident" OR description ~ "breach" OR description ~ "incident" OR description ~ "breach" ) and status != CLOSED ORDER BY priority DESC'


def main():
    collector = MetricsCollector()
    metrics = collector.collect_metrics(jql)
    df = create_df(metrics)

    df.to_csv("data/metrics_filled.csv")

    # Melt the dataframe to long format for plotly
    df_melted = df.reset_index().melt(
        id_vars="index", var_name="Status", value_name="Count"
    )
    df_melted.rename(columns={"index": "Date"}, inplace=True)

    fig = px.area(df_melted, x="Date", y="Count", color="Status")
    fig.show()


if __name__ == "__main__":
    main()
