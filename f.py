import requests
import time
import sys
import math
import datetime

ACCESS_TOKEN = '[put your API key here]'  # Replace with your GitHub token

usage = """
Follows all GitHub users listed in a file using the GitHub API.

Usage: python f.py [input_filename]

Example:
    python f.py followers.txt
"""

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
        'Accept': 'application/vnd.github.v3+json'
    }
    if ACCESS_TOKEN and ACCESS_TOKEN != '[put your API key here]':
        headers['Authorization'] = f'token {ACCESS_TOKEN}'
    else:
        print("Error: Please set your GitHub API token in the script.")
        sys.exit(1)

    try:
        with open(input_filename, 'r', encoding='utf-8') as infile:
            usernames = [line.strip() for line in infile if line.strip()]
        
        print(f"Loaded {len(usernames)} usernames from {input_filename}.")

        for idx, username in enumerate(usernames, 1):
            print(f"({idx}/{len(usernames)}) Following: {username} ... ", end="")
            resp = follow_user(username, headers)
            
            # Rate limit handling
            remaining = int(resp.headers.get('X-RateLimit-Remaining', 0))
            reset_time = int(resp.headers.get('X-RateLimit-Reset', 0))
            if remaining == 0:
                wait_seconds = max(1, int(reset_time - time.time()) + 1)
                print(f"\nRate limit reached. Waiting {wait_seconds} seconds.")
                time.sleep(wait_seconds)
                # Retry the same username after sleeping
                resp = follow_user(username, headers)

            if resp.status_code == 204:
                print("Success!")
            elif resp.status_code == 404:
                print("User not found.")
            elif resp.status_code == 403:
                print("Forbidden (possibly rate limited).")
            elif resp.status_code == 401:
                print("Unauthorized. Check your ACCESS_TOKEN.")
                sys.exit(1)
            else:
                print(f"Failed with status code {resp.status_code}.")
            
            # Be polite, avoid hitting rate limits
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
