import os
import urllib3

# Globals
http = urllib3.PoolManager()
token = os.environ['GH_PAT']
owner = ""
repo = ""
branch = ""
event_type = ""


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

    valid_types = ["trigger-workflow", "trigger-workflow01"]

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
                event_type = "trigger-workflow01"
                break
            case _:
                print("Invalid input")


def get_headers():
    return {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-Github-Api-Version": "2022-11-28"
    }


def get_data(event_type, arguement):
    return {
        "event_type": event_type,
        "client_payload": {
            "target_branch": branch,
            "target_repository": repo,
            "target_argument": arguement
        }
    }


def call_dispatch():
    set_branch()
    set_event_type()

    arguement = input("Enter the argument you wish to send to GitHub: ")

    resp = http.request(
        "POST",
        f"https://api.github.com/repos/{owner}/{repo}/dispatches",
        headers=get_headers(),
        json=get_data("trigger-workflow", arguement),
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
        user_response = ""
        print("\n--- Welcome to Github Trigger Workflow Testing ---\n")
        set_owner()
        set_repo()

        quit = ["q", "quit", "n", "no"]

        while(user_response.lower() not in quit):
            call_dispatch()

            user_response = input ("\nWould you like to continue? [y/n]: ")


        print("Thank you for using Github Trigger Workflow Testing!")
        exit(0)
    except Exception as e:
        print(e)
        exit(1)


if __name__ == '__main__':
    main()