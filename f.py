import requests
import time
import sys
import datetime

ACCESS_TOKEN = 'YOUR API KEY'  # Replace with your token

usage = """
Follows all GitHub users listed in a file using the GitHub API.

Usage: python f.py [input_filename]

Example:
    python f.py followers.txt
"""

def countdown(seconds):
    for remaining in range(seconds, 0, -1):
        print(f"\r⏳ Pausing for {remaining} seconds... Press Ctrl+C to exit.", end='', flush=True)
        time.sleep(1)
    print("\r⏳ Pause complete! Resuming...          ")

def is_following(username, headers):
    url = f"https://api.github.com/user/following/{username}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 204:
        return True
    elif resp.status_code == 404:
        return False
    else:
        return False

def follow_user(username, headers):
    url = f"https://api.github.com/user/following/{username}"
    response = requests.put(url, headers=headers)
    return response

def main():
    if len(sys.argv) < 2:
        print(usage)
        sys.exit(-1)

    input_filename = sys.argv[1]

    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': f'token {ACCESS_TOKEN}'
    }

    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            usernames = [line.strip() for line in infile if line.strip()]

        print(f"Loaded {len(usernames)} usernames from {input_filename}.")

        idx = 0
        total = len(usernames)

        while idx < total:
            username = usernames[idx]

            if is_following(username, headers):
                idx += 1
                continue

            print(f"({idx+1}/{total}) Following: {username} ... ", end="")
            resp = follow_user(username, headers)

            remaining = int(resp.headers.get('X-RateLimit-Remaining', 0))
            reset_time = int(resp.headers.get('X-RateLimit-Reset', 0))

            try:
                resp_json = resp.json()
            except Exception:
                resp_json = {}

            # If a specific error message is found, stop the script
            if 'message' in resp_json and "You can't perform that action at this time." in resp_json['message']:
                print("\n⚠️ Error: 'You can't perform that action at this time.' detected.")
                print("Script stopped due to API limit or other restrictions.")
                sys.exit(1)

            if remaining == 0:
                reset_dt = datetime.datetime.fromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n⚠️ API limit reached. Reset at: {reset_dt}")
                print("Script stopped to avoid violating the limit.")
                sys.exit(1)

            if resp.status_code == 204:
                print("Success!")
            elif resp.status_code == 404:
                print("User not found.")
            elif resp.status_code == 403:
                reset_dt = datetime.datetime.fromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S')
                print(f"⚠️ Forbidden (possibly rate limited). Reset at: {reset_dt}")
                print("Script stopped to avoid violating the limit.")
                sys.exit(1)
            elif resp.status_code == 401:
                print("Unauthorized. Check your ACCESS_TOKEN.")
                sys.exit(1)
            else:
                print(f"Failed with status code {resp.status_code}.")

            idx += 1
            time.sleep(1/30)

    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
