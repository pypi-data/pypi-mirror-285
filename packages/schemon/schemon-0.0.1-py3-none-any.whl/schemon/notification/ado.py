import sys
import requests
import json
import urllib.parse
from requests.auth import HTTPBasicAuth


def create_pr_thread(
    organization,
    project,
    repository_id,
    pull_request_id,
    pat,
    content,
    comment_type="text",
    status="active",
):
    """
    Creates a thread in a pull request on Azure DevOps.

    Args:
        organization (str): The name of the Azure DevOps organization.
        project (str): The name of the project.
        repository_id (str): The ID of the repository.
        pull_request_id (int): The ID of the pull request.
        pat (str): The personal access token for authentication.
        content (str): The content of the comment.
        comment_type (str): The type of the comment. Defaults to 'text'.
        status (str): The status of the comment thread. Defaults to 'active'.

    Returns:
        dict: The response from the Azure DevOps API.
    """

    encoded_organization = urllib.parse.quote(organization)
    encoded_project = urllib.parse.quote(project)
    url = f"https://dev.azure.com/{encoded_organization}/{encoded_project}/_apis/git/repositories/{repository_id}/pullRequests/{pull_request_id}/threads?api-version=7.1-preview.1"

    headers = {"Content-Type": "application/json"}

    data = {
        "comments": [{"content": content, "commentType": comment_type}],
        "status": status,
    }

    response = requests.post(
        url, headers=headers, data=json.dumps(data), auth=HTTPBasicAuth("", pat)
    )

    if response.status_code == 200:
        print("Thread created successfully.")
    else:
        print(f"Failed to create thread. Status code: {response.status_code}")
        sys.exit(1)

    return response.json()
