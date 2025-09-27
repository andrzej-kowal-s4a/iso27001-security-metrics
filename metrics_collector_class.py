from utilis.jira_helper import JiraConfig, JiraRequestor
import logging

logger = logging.getLogger(__name__)

supported_statuses = [
    "Triage",
    "Contain/mitigate",
    "Eradicate/remediate",
    "Recovery",
    "Lessons learned",
    "Closed",
]


class MetricsCollector:
    def __init__(self):
        self.requestor = JiraRequestor(JiraConfig.from_os_environment_variables())
        self.supported_statuses = supported_statuses

    def collect_metrics(self, jql: str) -> dict:
        metrics = {}

        logger.info(f"Collecting metrics for JQL: {jql}")
        work_items = self.requestor.request(jql, fields=["key", "summary", "created"])

        logger.info(f"Found {len(work_items['issues'])} issues")

        for work_item in work_items["issues"]:
            # logger.info(f"Processing issues {work_item}")
            key = work_item["key"]
            logger.info(f"Processing issue {key}")
            # summary = work_item["fields"]["summary"]

            # update the metrics with the initial status and the created time
            work_item_created_time = work_item["fields"]["created"]
            metrics[key] = {}
            metrics[key]["Initial"] = work_item_created_time.split("T")[
                0
            ]  # only the date

            item_changelog = self.requestor.changelog(key)

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
