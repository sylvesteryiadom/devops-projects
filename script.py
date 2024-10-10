#!/usr/bin/env python3

"""
This script exports all tickets from a Jira Service Desk project into a CSV file.

Usage:
  python export_jira_tickets.py -p <project_key> -u <username> -a <api_token> -o <output_file> [-h]

Options:
  -p <project_key>   Jira project key (e.g., "SERVICEDESK")
  -u <username>     Jira username
  -a <api_token>     Jira API token
  -o <output_file>   Output CSV file name (e.g., "tickets.csv")
  -h --help          Show this help message and exit

Example:
  python export_jira_tickets.py -p SERVICEDESK -u myusername -a myapitoken -o tickets.csv
"""

import argparse
import csv
import requests
from typing import List, Dict

# Define global constants for API endpoints
JIRA_BASE_URL = "https://your-jira-instance.atlassian.net/rest/api/3/"
JIRA_SEARCH_ENDPOINT = "search"
JIRA_ISSUE_ENDPOINT = "issue"

def get_jira_tickets(project_key: str, username: str, api_token: str) -> List[Dict]:
    """
    Fetches all tickets from the specified Jira project.

    Args:
        project_key: The Jira project key (e.g., "SERVICEDESK").
        username: The Jira username.
        api_token: The Jira API token.

    Returns:
        A list of dictionaries, where each dictionary represents a Jira ticket.
    """

    # Construct the JQL query to fetch all tickets in the project
    jql_query = f"project = {project_key}"

    # Set up authentication headers
    headers = {
        "Authorization": f"Basic {requests.utils.quote(f'{username}:{api_token}')}",
        "Accept": "application/json",
    }

    # Initialize an empty list to store the tickets
    tickets = []

    # Set the initial starting point for pagination
    start_at = 0

    # Loop through the results, fetching tickets in batches of 50
    while True:
        # Construct the API request URL
        url = f"{JIRA_BASE_URL}{JIRA_SEARCH_ENDPOINT}?jql={jql_query}&startAt={start_at}&maxResults=50"

        # Send the API request
        response = requests.get(url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Add the fetched tickets to the list
            tickets.extend(data["issues"])

            # Update the starting point for the next batch
            start_at += 50

            # If there are no more tickets, break the loop
            if len(data["issues"]) < 50:
                break

        else:
            # Handle errors gracefully
            print(f"Error fetching tickets: {response.status_code} - {response.text}")
            break

    return tickets

def get_ticket_details(ticket_id: str, username: str, api_token: str) -> Dict:
    """
    Fetches detailed information for a specific Jira ticket.

    Args:
        ticket_id: The Jira ticket ID (e.g., "SERVICEDESK-123").
        username: The Jira username.
        api_token: The Jira API token.

    Returns:
        A dictionary containing detailed information about the Jira ticket.
    """

    # Set up authentication headers
    headers = {
        "Authorization": f"Basic {requests.utils.quote(f'{username}:{api_token}')}",
        "Accept": "application/json",
    }

    # Construct the API request URL
    url = f"{JIRA_BASE_URL}{JIRA_ISSUE_ENDPOINT}/{ticket_id}"

    # Send the API request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        return response.json()

    else:
        # Handle errors gracefully
        print(f"Error fetching ticket details: {response.status_code} - {response.text}")
        return {}

def export_tickets_to_csv(tickets: List[Dict], output_file: str) -> None:
    """
    Exports the fetched Jira tickets to a CSV file.

    Args:
        tickets: A list of dictionaries, where each dictionary represents a Jira ticket.
        output_file: The name of the output CSV file.
    """

    # Open the output CSV file in write mode
    with open(output_file, "w", newline="") as csvfile:
        # Create a CSV writer object
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "key",
                "summary",
                "status",
                "priority",
                "assignee",
                "reporter",
                "created",
                "updated",
                "resolution",
                "description",
                # Add more fields as needed
            ],
        )

        # Write the header row
        writer.writeheader()

        # Iterate through the list of tickets and write each ticket's data to the CSV file
        for ticket in tickets:
            # Extract relevant information from the ticket dictionary
            ticket_data = {
                "key": ticket["key"],
                "summary": ticket["fields"]["summary"],
                "status": ticket["fields"]["status"]["name"],
                "priority": ticket["fields"]["priority"]["name"],
                "assignee": ticket["fields"]["assignee"]["displayName"]
                if "assignee" in ticket["fields"] and ticket["fields"]["assignee"] is not None
                else "",
                "reporter": ticket["fields"]["reporter"]["displayName"],
                "created": ticket["fields"]["created"],
                "updated": ticket["fields"]["updated"],
                "resolution": ticket["fields"]["resolution"]["name"]
                if "resolution" in ticket["fields"] and ticket["fields"]["resolution"] is not None
                else "",
                "description": ticket["fields"]["description"],
                # Add more fields as needed
            }

            # Write the ticket data to the CSV file
            writer.writerow(ticket_data)

if __name__ == "__main__":
    # Create an ArgumentParser object to handle command line arguments
    parser = argparse.ArgumentParser(description="Export Jira tickets to CSV.")

    # Add arguments for project key, username, API token, and output file
    parser.add_argument("-p", "--project", required=True, help="Jira project key")
    parser.add_argument("-u", "--username", required=True, help="Jira username")
    parser.add_argument("-a", "--api_token", required=True, help="Jira API token")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file name")

    # Parse the command line arguments
    args = parser.parse_args()

    # Get the values of the parsed arguments
    project_key = args.project
    username = args.username
    api_token = args.api_token
    output_file = args.output

    # Fetch all tickets from the specified Jira project
    tickets = get_jira_tickets(project_key, username, api_token)

    # Export the fetched tickets to the specified CSV file
    export_tickets_to_csv(tickets, output_file)

    # Print a success message
    print(f"Jira tickets exported to {output_file}")
