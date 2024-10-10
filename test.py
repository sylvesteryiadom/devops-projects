import requests
import logging
from requests.auth import HTTPBasicAuth
import json
import csv
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BASE_URL                        = 'https://textco.atlassian.net'
# Edit the below url for each project you want to export
SERVICE_DESK_TICKETS_URL        = 'https://textco.atlassian.net/issues/VERISV3-5408?jql=project%20%3D%20%22VERISV3%22%20ORDER%20BY%20created%20DESC'
SERVICE_DESK_API                = f'{BASE_URL}/rest/servicedeskapi'
HEADERS                         = {'Accept': 'application/json'}
AUTH                            = HTTPBasicAuth("xxx.xx@text.com", "xxx")
LIMIT                           = 25

def write_json_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, sort_keys=True, indent=4, separators=(",", ": "))
        logger.info(f"JSON data written to {filename}")
        


def get_issues(limit=10):
    start_at = 0
    max_results = 1  # Setting max_results to 1 for testing
    all_issues_info = []
    
    while len(all_issues_info) < limit:
        try:            
            response = requests.get(SERVICE_DESK_TICKETS_URL + f"&startAt={start_at}&maxResults={max_results}", headers=HEADERS, verify="cacert.pem", auth=AUTH)
            response.raise_for_status()
            data = response.json()

            #write_json_to_file(data, f'response_{start_at}.json')
            # Ensure the 'issues' key exists
            if 'issues' not in data:
                logger.warning("No 'issues' key in response data.")
                break
            issues = data['issues']
            if not issues:
                logger.info("No more issues to process.")
                break
            
            for issue in issues:
                try:
                    fields = issue.get('fields', {})
                    issuetype = fields.get('issuetype', {})
                    priority = fields.get('priority', {})
                    components = fields.get('components', {})
                    component_names = ', '.join([comp.get('name', 'N/A') for comp in components])
                    clientType = fields.get('customfield_10221') or {}
                    #changelog = issue.get('changelog', {})
                    status = fields.get('customfield_10010', {})
                    currentStatus= status.get('currentStatus', {})
                    statusDate = currentStatus.get('statusDate', {})
                    affectedClients = fields.get('customfield_10211', {})
                    affectedClients = affectedClients if isinstance(affectedClients, list) else []
                    clientNames = ', '.join([client.get('value', 'N/A') for client in affectedClients])
                except AttributeError:
                    currentStatus = {}
                    
                #Data Mapping
                issue_info = {
                    'IssueID': issue.get('id', 'N/A'),
                    'IssueKey': issue.get('key', 'N/A'),
                    'IssueCreation': fields.get('created', 'N/A'),
                    'Summary': fields.get('summary', 'N/A'),
                    'ReporterName': fields.get('reporter', {}).get('displayName', 'N/A'),
                    'ReporterEmail': fields.get('reporter', {}).get('emailAddress', 'N/A'),
                    'Component': component_names,
                    'CurrentStatus': currentStatus.get('status', 'N/A'),
                    'StatusTime': statusDate.get('iso8601', 'N/A'),
                    'Description': fields.get('description', 'N/A'),
                    'IssueType': issuetype.get('name', 'N/A'),
                    'Severity': priority.get('name', 'N/A'),
                    'AffectedClient': clientNames,
                    'ClientType': clientType.get('value', 'N/A'),
                    #'Changelog': changelog.get('histories', []),
                    'FixResponseMessage': fields.get('customfield_10217', 'N/A'),
                    'FixRequestMessage': fields.get('customfield_10215', 'N/A'),
                    'FixRequestID': fields.get('customfield_10219', 'N/A'),
                    'FixSeqID': fields.get('customfield_10220', 'N/A'),
                    'DealID':fields.get('customfield_10218', 'N/A'),
                    'TrancheID':fields.get('customfield_10213', 'N/A'),
                    'GUIEmailAddress':fields.get('customfield_10212', 'N/A'),
                    'IssueDateAndTime':fields.get('customfield_10214', 'N/A'),
                    'Submitter':fields.get('customfield_10216', 'N/A'),
                    
                }
                all_issues_info.append(issue_info)
                logger.info(f"Issue ID: {issue_info['IssueID']}")
                logger.info(f"Issue Key: {issue_info['IssueKey']}")
                
                #double check the IssueID has been correctly grabbed (it should be 6 chars)
                if len(issue_info['IssueID']) != 6:
                    issue_info['IssueID'] = 'Invalid ID'

                
            start_at += max_results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to retrieve Service Desk IDs: {e}")
            break

    return all_issues_info

def get_comments(ticket_id):
    url = f'{SERVICE_DESK_API}/request/{ticket_id}/comment'
    try:
        response = requests.get(url, headers=HEADERS, verify="cacert.pem", auth=AUTH)
        response.raise_for_status()
        comments = response.json().get('values', [])
        
        public_comments = [
            {
                'id': comment['id'],
                'body': comment['body'],
                'author': comment['author']['displayName'],
                'created': comment['created']['iso8601']
            }
            for comment in comments if comment['public']
        ]
        
        non_public_comments = [
            {
                'ticket_ID': ticket_id,
                'Non_public_comment': comment['body']
            }
            for comment in comments if not comment['public']
        ]
        
        logger.info(f"Retrieved {len(public_comments)} public comments and {len(non_public_comments)} non-public comments for ticket {ticket_id}")
        
        # Save non-public comments to a CSV file
        if non_public_comments:
            with open('non_public_comments.csv', 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ticket_ID', 'Non_public_comment']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header only if file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()
                
                writer.writerows(non_public_comments)
        
        return public_comments
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve comments for ticket {ticket_id}: {e}")
        return []

def main():
    issues = get_issues(limit=1500)
    all_data = []
    total_issues = len(issues)

    for idx, issue in enumerate(issues, start=1):
        ticket_id = issue['IssueID']
        comments = get_comments(ticket_id)
        comment_json = json.dumps(comments)
        issue['Comments'] = comment_json
        all_data.append(issue)
        logger.info(f"Processed issue {idx}/{total_issues} - Issue ID: {ticket_id}")

    # Write to CSV
    with open('issues_with_comments.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['IssueID', 'IssueKey', 'IssueCreation', 'Summary', 'ReporterEmail', 'ReporterName',
                                                  'Description','Severity','IssueType' ,'Comments', 'Component','ClientType','AffectedClient','Submitter','FixResponseMessage','FixRequestMessage',
                                                  'Permissions', 'FixRequestID','FixSeqID','DealID','TrancheID','IssueDateAndTime','GUIEmailAddress','CurrentStatus', 'StatusTime'])
        writer.writeheader()
        for data in all_data:
            writer.writerow(data)
    
    print("Data has been exported to issues_with_comments.csv")

if __name__ == '__main__':
    main()
