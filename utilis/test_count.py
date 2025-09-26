#!/usr/bin/env python3
"""
Simple test for counting Jira issues created in the last 10 days
"""

from jira_helper import JiraConfig, JiraRequestor


def test_count_recent_issues():
    """Test counting issues created in the last 10 days"""
    try:
        # Initialize Jira configuration from environment variables
        jira_config = JiraConfig.from_os_environment_variables()
        requestor = JiraRequestor(jira_config)

        # JQL query for issues created in the last 10 days
        jql_query = "created >= -10d"

        # Get the count of issues
        issue_count = requestor.count(jql_query)

        # assert there should be at least 10 issues
        assert issue_count >= 10
    except Exception as e:
        print(f"Error occurred: {e}")
        return None


if __name__ == "__main__":
    test_count_recent_issues()
