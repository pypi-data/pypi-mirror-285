import sys
import requests
import urllib.parse


def construct_url(base_url, params):
    """
    Constructs a URL with query parameters.

    Args:
        base_url (str): The base URL without query parameters.
        params (dict): A dictionary of query parameters.

    Returns:
        str: The full URL with query parameters.
    """
    url_parts = list(urllib.parse.urlparse(base_url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update(params)
    url_parts[4] = urllib.parse.urlencode(query)

    return urllib.parse.urlunparse(url_parts)


def create_pr_thread_gitlab(project_id, merge_request_id, pat, body):
    """
    Creates a thread (comment) on a GitLab merge request.

    Args:
        project_id (int): The ID of the GitLab project.
        merge_request_id (int): The ID of the merge request.
        pat (str): The personal access token for authentication.
        body (str): The content of the thread (comment).

    Returns:
        dict: The JSON response from the GitLab API.
    """

    endpoint = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/notes"    
    url = construct_url(endpoint, {"private_token": pat})
    headers = {"private_token": pat}
    data = {"body": body}

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 201:
        print("Merge request note (comment) created successfully.")
    else:
        print(
            f"Failed to create merge request note (comment). Status code: {response.status_code}"
        )
        sys.exit(1)

    return response.json()
