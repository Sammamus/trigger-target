import os
import time
import uuid

import urllib3

from datetime import datetime, timezone

# Globals
# http = urllib3.PoolManager()
token = os.environ['GH_PAT']
owner = ""
repo = ""
branch = ""
event_type = ""
workflows = []
query_date = ""
workflow_uuid = ""
workflow_run_id = ""
workflow_found = False


def set_owner():
    global owner
    owner = input("Enter your owner: ")


def set_repo():
    global repo
    repo = input("Enter your repository: ")


def set_branch():
    global branch

    valid_branches = ["main", "test01", "test02"]

    while(True):
        print("\n--- Valid branches ---")

        count = 0
        for branch in valid_branches:
            print(f"\t{count} - {branch}")
            count += 1

        user_response = int(input("\nEnter your branch numeric value: "))

        match user_response:
            case 0:
                branch = valid_branches[0]
                break
            case 1:
                branch = valid_branches[1]
                break
            case 2:
                branch = valid_branches[2]
                break
            case _:
                print("Invalid input")


def set_event_type():
    global event_type

    valid_types = ["trigger-workflow", "completely-different-name"]

    while(True):
        print("\n--- Valid Event Types ---")

        count = 0
        for t in valid_types:
            print(f"\t({count}) - {t}")
            count += 1

        user_response = int(input("Please enter the numeral for the event type: "))

        match user_response:
            case 0:
                event_type = "trigger-workflow"
                break
            case 1:
                event_type = "completely-different-name"
                break
            case _:
                print("Invalid input")


def get_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-Github-Api-Version": "2022-11-28"
    }


def get_data(argument):
    return {
        "ref": "main",
        "inputs": {
            "target_branch": branch,
            "target_repository": f"{owner}/{repo}",
            "target_argument": argument
        }
    }


def create_client():
    return urllib3.PoolManager()


def set_workflows():
    global workflows

    http = create_client()

    resp = http.request(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/actions/workflows",
        headers=get_headers()
    )
    if resp.status == 200:
        print("Successfully fetched workflows")
        print(resp.data)

        response = resp.json()

        for w in response['workflows']:
            file = w['path'].split('/')[-1]
            workflows.append({'name': w['name'], 'id': w['id'], 'file': file})

    elif resp.status > 399:
        print(resp.data)
        raise Exception(resp.status)
    else:
        print("Failed to fetch workflows")
        print(resp.status)
        print(resp.data)


def select_workflow():
    output = ""

    print("\n--- Workflows ---")
    count = 0
    for w in workflows:
        print(f"\t({count}) {w}")
        count += 1

    while(True):
        workflow = int(input("\nPlease select a workflow: "))

        match workflow:
            case 0:
                output = workflows[0]['file']
                break
            case 1:
                output = workflows[1]['file']
                break
            case _:
                print("Invalid input")

    return output


def list_workflow_runs():
    global workflow_run_id, workflow_found

    http = create_client()

    resp = http.request(
        "GET",
        f"https://api.github.com/repos/{owner}/{repo}/actions/runs?created=>{query_date}",
        headers=get_headers()
    )
    if resp.status == 200:
        print("Successfully fetched workflow runs")
        # print(resp.data)

        response = resp.json()

        for run in response['workflow_runs']:
            if run['name'] == workflow_uuid:
                print("Workflow run found!")
                workflow_found = True
                workflow_run_id = run['id']

        if not workflow_found:
            print("Workflow run not found!")

        # print(json.dumps(response, indent=2))

        # for w in response['workflows']:
        #     file = w['path'].split('/')[-1]
        #     workflows.append({'name': w['name'], 'id': w['id'], 'file': file})

    elif resp.status > 399:
        print(resp.data)
        raise Exception(resp.status)
    else:
        print("Failed to fetch workflows")
        print(resp.status)
        print(resp.data)


def monitor_workflow_runs():
    if workflow_found:

        happy_endings = [
            "completed",
            "success"
        ]

        bad_endings = [
            "cancelled",
            "failure"
        ]

        count = 0
        status = ""

        while count <= 5:

            if count == 5:
                status = f"Monitor Timeout after {count} checks"
                break

            http = create_client()
            resp = http.request(
                "GET",
                f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{workflow_run_id}",
                headers=get_headers()
            )

            if resp.status == 200:
                response = resp.json()

                if response['status'] in happy_endings:
                    status = response['status']
                    break

                if response['status'] in bad_endings:
                    status = response['status']
                    break

            elif resp.status > 399:
                print(resp.data)
                raise Exception(resp.status)
            else:
                status = "Failed to fetch workflows"
                # print(resp.status)
                # print(resp.data)
                break

            count += 1
            time.sleep(30)

        print("\n--- Workflow Status ---")
        print(f"\t- Workflow Run ID: {workflow_run_id}")
        print(f"\t- Workflow Name: {workflow_uuid}")
        print(f"\t- Status: {status}")


def call_dispatch():
    global query_date, workflow_uuid

    query_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    http = create_client()
    workflow_id = select_workflow()
    set_branch()
    # set_event_type()

    workflow_uuid = f"test-{uuid.uuid4().hex}"

    resp = http.request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches",
        headers=get_headers(),
        json=get_data(workflow_uuid),
    )

    if resp.status == 204:
        print("Successfully triggered workflow")
        print(resp.data)
    elif resp.status > 399:
        print(resp.data)
        raise Exception(resp.status)
    else:
        print("Failed to trigger workflow?")
        print(resp.status)
        print(resp.data)


def main():
    try:
        global workflow_found

        user_response = ""

        print("\n--- Welcome to Github Trigger Workflow Testing ---\n")
        set_owner()
        set_repo()
        set_workflows()

        quit = ["q", "quit", "n", "no"]

        while(user_response.lower() not in quit):
            workflow_found = False
            call_dispatch()
            time.sleep(30)
            list_workflow_runs()
            monitor_workflow_runs()

            user_response = input ("\nWould you like to continue? [y/n]: ")

        print("Thank you for using Github Trigger Workflow Testing!")
        exit(0)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    main()