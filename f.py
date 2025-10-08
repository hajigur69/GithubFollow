import requests
import time
import sys
import datetime

# Replace with your token
ACCESS_TOKEN = 'YOUR API KEY'

usage = """
Follows all GitHub users listed in a file using the GitHub API.

Usage: python f.py [input_filename]

Example:
    python f.py followers.txt
"""

# Constants for GitHub API authentication
GITHUB_API_URL = "https://api.github.com/"
GITHUB_AUTH_HEADER = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def countdown(seconds):
    """Display countdown timer with option to cancel"""
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        if mins > 0:
            time_str = f"{mins}m {secs}s"
        else:
            time_str = f"{secs}s"
        print(f"\r⏳ Pausing for {time_str}... Press Ctrl+C to exit.", end='', flush=True)
        time.sleep(1)
    print("\r⏳ Pause complete! Resuming...                    ")

def is_following(username, headers):
    """Check if authenticated user is following a given GitHub user"""
    url = f"{GITHUB_API_URL}user/following/{username}"
    resp = requests.get(url, headers=headers)
    if resp.status_code == 204:
        return True
    elif resp.status_code == 404:
        return False
    else:
        return False

def follow_user(username, headers):
    """Follow a GitHub user"""
    url = f"{GITHUB_API_URL}user/following/{username}"
    response = requests.put(url, headers=headers)
    return response

def get_followers_count(headers):
    """Get current follower count from authenticated user's profile"""
    url = f"{GITHUB_API_URL}user"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('followers', 0)
    return None

def spot_check_followers(headers, expected_increase, last_count):
    """Perform spot check to verify followers increased"""
    print("\n" + "="*70)
    print("   🔍 SPOT CHECK: Verifying Follower Count")
    print("="*70)
    
    current_count = get_followers_count(headers)
    
    if current_count is None:
        print("   ⚠️  Unable to retrieve follower count")
        return last_count
    
    actual_increase = current_count - last_count
    
    print(f"   Previous count: {last_count}")
    print(f"   Current count: {current_count}")
    print(f"   Increase: {actual_increase}")
    
    return current_count