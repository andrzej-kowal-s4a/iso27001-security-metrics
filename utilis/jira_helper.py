import json
import logging
import os
from requests.auth import HTTPBasicAuth
import requests as requests

MAX_RESULTS = 200

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JiraRequestException(Exception):
    def __init__(self, message):
        self.message = message


class JiraConfig:
    url: str  # Url of Jira server
    token: str  # Token for authentication
    username: str  # Username for authentication
    headers: dict = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }  # Headers for request

    @classmethod
    def from_os_environment_variables(cls):
        url = os.environ["JIRA_URL"]

        if not url:
            raise ValueError(
                "JIRA_URL is not set in operational system environment variables"
            )

        token = os.environ["JIRA_TOKEN"]
        if not token:
            raise ValueError(
                "JIRA_TOKEN is not set in operational system environment variables"
            )

        username = os.environ["JIRA_USERNAME"]
        if not username:
            raise ValueError(
                "JIRA_USERNAME is not set in operational system environment variables"
            )

        return cls(url, token, username)

    def __init__(self, url: str, token: str, username: str):
        logger.info("Initializing JiraConfig")
        logger.info("Loading config from operational system environment variables")

        self.url = url
        self.token = token
        self.username = username
        self.auth = HTTPBasicAuth(self.username, self.token)


class JiraRequestor:
    def __init__(self, jira_config):
        self.jira_config = jira_config

    def request(self, jql_query: str, fields=None):
        """
        Execute JQL query using the new API endpoint with pagination support.

        Args:
            jql_query (str): The JQL query to execute
            fields (list, optional): List of fields to return. If None, returns default fields.

        Returns:
            dict: Combined response with all issues
        """
        if fields is None:
            fields = ["*all"]  # Return all fields by default for backward compatibility

        json_response = self._execute_request(jql_query, fields=fields)

        # Handle pagination using nextPageToken
        while json_response.get("nextPageToken"):
            partial_response = self._execute_request(
                jql_query, fields=fields, next_page_token=json_response["nextPageToken"]
            )
            json_response["issues"].extend(partial_response["issues"])
            json_response["nextPageToken"] = partial_response.get("nextPageToken")

        return json_response

    def count(self, jql_query):
        """
        Get the count of issues matching the JQL query without returning the actual issues.

        Args:
            jql_query (str): The JQL query to execute

        Returns:
            int: Number of issues matching the query
        """
        # Use maxResults=0 to get only the count without fetching issues

        response = self.request(jql_query, fields=["key"])

        # print(response)

        # save response to file
        with open("response.json", "w") as f:
            json.dump(response, f)

        return len(response["issues"])

    def changelog(self, issue_key: str):
        """
        Get the changelog for an issue
        """
        headers = self.jira_config.headers.copy()

        response = requests.request(
            "GET",
            f"{self.jira_config.url}/rest/api/3/issue/{issue_key}/changelog?startAt=0&maxResults=100",
            headers=headers,
            auth=self.jira_config.auth,
        )

        json_response = json.loads(response.text)

        return json_response

    def _execute_request(self, jql_query, fields=None, next_page_token=None):
        """
        Execute JQL request using the new POST /rest/api/3/search/jql endpoint.

        Args:
            jql_query (str): The JQL query to execute
            fields (list, optional): List of fields to return
            next_page_token (str, optional): Token for pagination

        Returns:
            dict: JSON response from Jira API
        """
        if fields is None:
            fields = ["*all"]

        # Prepare request body for POST request
        request_body = {"jql": jql_query, "maxResults": MAX_RESULTS, "fields": fields}

        # Add pagination token if provided
        if next_page_token:
            request_body["nextPageToken"] = next_page_token

        # Update headers for JSON content
        headers = self.jira_config.headers.copy()

        response = requests.request(
            "POST",
            f"{self.jira_config.url}/rest/api/3/search/jql",
            headers=headers,
            auth=self.jira_config.auth,
            json=request_body,
        )

        json_response = json.loads(response.text)

        if "errorMessages" in json_response.keys():
            print(
                f"JQL query: {jql_query} generated error: {json_response['errorMessages']}"
            )
            raise JiraRequestException(
                f"I got error: {json_response['errorMessages']} when executing JQL query: {jql_query}"
            )

        return json_response
