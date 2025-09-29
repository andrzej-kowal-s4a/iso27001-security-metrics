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

REDUCED_STATUSES = {
    "Initial": (
        "Initial",
        "INITIAL",
        "Triage",
        "Business need assessment",
        "Identify",
    ),
    "In Progress": (
        "In Progress",
        "Planning",
        "Response implementation",
        "Control",
        "Analysis and Verification",
        "Work on resolution",
        "Contain/mitigate",
        "Eradicate/remediate",
        "Response planing",
        "Training in Progress",
        "Ready for development",
        "Major Upgrade",
        "Verification",
        "Audit",
    ),
    "Waiting": (
        "Waiting 4 Product",
        "Waiting 4 Order",
        "Waiting 4 Deployment",
        "Waiting for customer",
        "Waiting 4 Delivery",
        "Waiting 4 Fix",
        "Waiting for Release",
    ),
    "Blocked": (
        "Blocked",
        "On Hold",
        "Provide more information",
        "Hibernated",
    ),
    "Closed": ("Closed", "Compliant", "TEST", "Reopened"),
}


def get_reduced_status(status_name: str) -> str:
    """
    Return the reduced status category for a given status name.

    Args:
        status_name (str): The original status name

    Returns:
        str: The reduced status category ("Initial", "In Progress", "Blocked", or "Closed")
             Returns "Unknown" if status is not found in any category
    """
    for reduced_status, status_list in REDUCED_STATUSES.items():
        if isinstance(status_list, tuple):
            if status_name in status_list:
                return reduced_status
        elif status_name == status_list:
            return reduced_status

    # Return "Unknown" for any status not found in the mapping
    return "Unknown"


class MetricsCollector:
    def __init__(self):
        self.requestor = JiraRequestor(JiraConfig.from_os_environment_variables())
        self.supported_statuses = supported_statuses

    def _extract_statuses(self, work_items: dict) -> list:
        statuses = [
            work_item["fields"]["status"]["name"] for work_item in work_items["issues"]
        ]
        # return the unique statuses
        return list(set(statuses))

    def collect_metrics(self, jql: str, reduce_statuses: bool = True) -> dict:
        metrics = {}

        logger.info(f"Collecting metrics for JQL: {jql}")
        work_items = self.requestor.request(
            jql, fields=["key", "summary", "created", "status"]
        )
        logger.info(f"Found {len(work_items['issues'])} issues")

        # get the status of the work items
        unique_statuses = self._extract_statuses(work_items)
        logger.info(f"Found {len(unique_statuses)} unique statuses: {unique_statuses}")

        # add unique statuses to the supported statuses
        self.supported_statuses.extend(unique_statuses)

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
                    fromStatus, toStatus = item["fromString"], item["toString"]

                    if reduce_statuses:
                        reduced_toString = get_reduced_status(toStatus)
                    else:
                        reduced_toString = toStatus

                    if toStatus in supported_statuses:
                        logger.debug(
                            f"{created_time}, {fromStatus} -> {toStatus}. Used reduced status: {reduced_toString}"
                        )

                        # take only the date from the created_time
                        created_time = created_time.split("T")[0]

                        metrics[key][reduced_toString] = created_time

            # print the metrics for the key
            logger.debug(f"Metrics for {key}: {metrics[key]}")
            # save to file json
            # with open(f"data/{key}.json", "w") as f:
            #     json.dump(metrics[key], f)
        return metrics
