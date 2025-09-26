from utilis.jira_helper import JiraConfig, JiraRequestor
import json
import logging
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

jql = 'project = SECURITY AND issuetype="Security Incident"'
# jql = 'project = SECURITY AND status = Closed AND issuetype="Security Incident"'
jira_config = JiraConfig.from_os_environment_variables()
requestor = JiraRequestor(jira_config)


supported_statuses = [
    "Triage",
    "Contain/mitigate",
    "Eradicate/remediate",
    "Recovery",
    "Lessons learned",
    "Closed",
]


def collect_metrics() -> dict:
    metrics = {}

    logger.info(f"Collecting metrics for JQL: {jql}")
    work_items = requestor.request(jql, fields=["key", "summary", "created"])

    logger.info(f"Found {len(work_items['issues'])} issues")

    for work_item in work_items["issues"]:
        # logger.info(f"Processing issues {work_item}")
        key = work_item["key"]
        # summary = work_item["fields"]["summary"]

        # update the metrics with the initial status and the created time
        work_item_created_time = work_item["fields"]["created"]
        metrics[key] = {}
        metrics[key]["Initial"] = work_item_created_time.split("T")[0]  # only the date

        item_changelog = requestor.changelog(key)

        for changelog_item in item_changelog["values"]:
            created_time = changelog_item["created"]
            # each change at specific change can have multiple items
            for item in changelog_item["items"]:
                # TODO remove from string when the code start working correctly
                fromString, toString = item["fromString"], item["toString"]

                if toString in supported_statuses:
                    logger.debug(f"{created_time}, {fromString} -> {toString}")

                    # take only the date from the created_time
                    created_time = created_time.split("T")[0]

                    metrics[key][toString] = created_time

        # print the metrics for the key
        logger.debug(f"Metrics for {key}: {metrics[key]}")
        # save to file json
        # with open(f"data/{key}.json", "w") as f:
        #     json.dump(metrics[key], f)
    return metrics


def fill_df_with_last_status_till_today(df: pd.DataFrame, status: str, date: str):
    # date - start the date to fill till today
    today = datetime.now().strftime("%Y-%m-%d")
    logger.debug(f"Filling dataframe with last status {status} from {date} to {today}")
    for date in pd.date_range(date, today):
        date = date.strftime("%Y-%m-%d")
        # add to the dataframe
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

            # logger.info(f"Status for {date}: {status}")

            # add to the dataframe
            if date not in df.index:
                df.loc[date, status] = 1
            elif status in df.columns:
                df.loc[date, status] = df.loc[date, status] + 1
            else:
                df.loc[date, status] = 1
            # print(df)

        last_status, last_date = transitions[-1]

        logger.info(f"Update data with last status {last_status} from {last_date}")
        df = fill_df_with_last_status_till_today(df, last_status, last_date)

    # sort df by index
    df = df.sort_index()
    return df
    # it is a initial date when issue has been created


def fill_nan_with_last_amounts_from_previous_dates(df: pd.DataFrame):
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


if __name__ == "__main__":
    metrics = collect_metrics()
    df = process_metrics(metrics)
    df = fill_nan_with_last_amounts_from_previous_dates(df)
    # save to csv
    df.to_csv("data/metrics.csv")
