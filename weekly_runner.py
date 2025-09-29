import plotly.express as px
from datetime import datetime
from metric_collector import (
    create_df,
)
from metric_collector import MetricsCollector
import logging

logger = logging.getLogger(__name__)

# metrics to track wth JQL
metrics = [
    (
        "SECURITY-280-Incidents-Major-plus",
        'project = security and issuetype = "Security Incident" and priority >= Major and status != Closed',
    ),
    (
        "SECURITY-280-Incidents",
        'project = security and issuetype = "Security Incident" and status != Closed',
    ),
    (
        "SECURITY-280-Security-Issues",
        'project not in (SERVICE) AND ( labels in ("security", "incident", "breach") OR summary ~ "breach" OR summary ~ "incident" OR description ~ "breach" OR description ~ "incident" OR description ~ "breach" ) and status != CLOSED ORDER BY priority DESC',
    ),
]


def generate_report(name: str, jql: str):
    today = datetime.now().strftime("%Y-%m-%d")
    collector = MetricsCollector()
    metrics = collector.collect_metrics(jql)
    df = create_df(metrics)

    df.to_csv(f"output/{name}_{today}.csv")
    df_melted = df.reset_index().melt(
        id_vars="index", var_name="Status", value_name="Count"
    )
    df_melted.rename(columns={"index": "Date"}, inplace=True)

    fig = px.area(
        df_melted,
        x="Date",
        y="Count",
        color="Status",
        title=f"Security Metrics: {name.replace('-', ' ').replace('_', ' ').title()}",
    )

    # Customize the legend
    fig.update_layout(
        legend=dict(
            orientation="v",  # vertical orientation
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            title="Security Issue Status",
            bgcolor="rgba(255, 255, 255, 0.8)",
            bordercolor="rgba(0, 0, 0, 0.2)",
            borderwidth=1,
        ),
        # Add some margin for the legend
        margin=dict(r=150),
    )

    # Customize hover information
    fig.update_traces(
        hovertemplate="<b>Status: %{fullData.name}</b><br>"
        + "Date: %{x}<br>"
        + "Count: %{y} issues<br>"
        + "<extra></extra>"
    )

    # Add axis labels and formatting
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="Number of Issues")

    # Add a subtitle with additional context
    fig.add_annotation(
        text=f"Generated on {today} | Data shows cumulative issue counts by status over time",
        xref="paper",
        yref="paper",
        x=0.5,
        y=-0.1,
        xanchor="center",
        yanchor="top",
        showarrow=False,
        font=dict(size=10, color="gray"),
    )

    fig.write_html(f"output/fig_{name}_{today}.html")

    fig.show()


if __name__ == "__main__":
    for metric in metrics:
        logger.info(f"Generating report for {metric[0]}")
        generate_report(metric[0], metric[1])
