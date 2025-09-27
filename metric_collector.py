from metrics_collector_class import MetricsCollector
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# jql = 'project = SECURITY AND issuetype="Security Incident"'
# jql = 'project = SECURITY AND status = Closed AND issuetype="Security Incident"'


def update_last_status(df: pd.DataFrame, status: str, start_date: str):
    """'
    Update the last status for the given date.
    It will increment the amount of the issues count by 1 from start date to today for the given status.
    """

    # date - start the date to fill till today
    today = datetime.now().strftime("%Y-%m-%d")
    # last date plus one day
    updated_start_date = (pd.to_datetime(start_date) + pd.Timedelta(days=1)).strftime(
        "%Y-%m-%d"
    )

    logger.debug(
        f"Filling dataframe with last status {status} from {updated_start_date} to {today}"
    )

    for date in pd.date_range(updated_start_date, today):
        date = date.strftime("%Y-%m-%d")

        df = increment(df, date, status)

    return df


def increment(df: pd.DataFrame, date: str, status: str):
    """
    Increment the amount for the given date and status.
    It will increment the amount of the issues count by 1 on the given date and status.
    """

    if date not in df.index:
        df.loc[date, status] = 1
    elif status in df.columns:
        df.loc[date, status] = df.loc[date, status] + 1
    else:
        df.loc[date, status] = 1
    return df


def process_metrics(metrics: dict):
    df = pd.DataFrame()
    for key in metrics.keys():
        logger.info(f"Processing metrics for {key}: {metrics[key]}")
        # transitions contain tuples of (status, date)
        transitions = metrics[key].items()
        # sort by date
        transitions = sorted(transitions, key=lambda x: x[1])
        # dates_to_statuses_dict is a transposed dictionary of dates to statuses
        dates_to_statuses_dict = {date: status for status, date in transitions}

        issue_start = transitions[0][1]
        issue_end = transitions[-1][1]
        logger.info(f"I am processing the time frame {issue_start} to {issue_end}")

        # create loop over the dates from issue_start to issue_end
        status = None

        for date in pd.date_range(issue_start, issue_end):
            date = date.strftime("%Y-%m-%d")
            # logger.info(f"Processing date {date}")
            # get the status for the date
            if date in dates_to_statuses_dict:
                status = dates_to_statuses_dict[date]

            df = increment(df, date, status)

            # print(df)

        last_status, last_date = transitions[-1]

        logger.info(f"Update data with last status {last_status} from {last_date}")
        df = update_last_status(df, last_status, last_date)

    return df.sort_index()
    # it is a initial date when issue has been created


def fill_nan(df: pd.DataFrame):
    """
    Fill the NaN values with the last amount from the previous dates.
    """
    # fill the closed dates from the previous dates

    statuses = df.columns

    for status in statuses:
        last_amount = 0
        for date in df.index:
            if not pd.isna(df.loc[date, status]):
                last_amount = df.loc[date, status]
            else:
                df.loc[date, status] = last_amount

    return df


def create_df(metrics: dict) -> pd.DataFrame:
    df = process_metrics(metrics)
    df = fill_nan(df)
    # df = df.fillna(0)
    return df


if __name__ == "__main__":
    jql = "project = SECURITY AND status = Closed AND issuetype='Security Incident'"

    collector = MetricsCollector()
    metrics = collector.collect_metrics(jql)

    df = create_df(metrics)
    # save to csv
    df.to_csv("data/metrics.csv")
