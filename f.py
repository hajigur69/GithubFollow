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

def get_followers_count(headers):
    """Get current follower count from authenticated user's profile"""
    url = "https://api.github.com/user"
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
    print(f"   Current count:  {current_count}")
    print(f"   Expected gain:  +{expected_increase}")
    print(f"   Actual gain:    +{actual_increase}")
    print("-"*70)
    
    if actual_increase >= expected_increase:
        print(f"   ✅ PASSED: Followers increased by {actual_increase}!")
    elif actual_increase > 0:
        print(f"   ⚠️  PARTIAL: Only {actual_increase} of {expected_increase} followers added")
        print(f"   💡 This may be due to:")
        print(f"      • Some users don't auto-follow back")
        print(f"      • Mutual follow takes time to reflect")
        print(f"      • API delay in updating counts")
    else:
        print(f"   ❌ FAILED: No follower increase detected")
        print(f"   💡 Possible reasons:")
        print(f"      • Follows are not being reciprocated")
        print(f"      • Account may have restrictions")
        print(f"      • API data needs time to update")
    
    print("="*70 + "\n")
    
    return current_count

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

        # Get initial follower count
        print("\n📊 Getting initial follower count...")
        initial_followers = get_followers_count(headers)
        if initial_followers is not None:
            print(f"✅ Starting with {initial_followers} followers\n")
        else:
            print("⚠️  Could not retrieve initial follower count\n")
            initial_followers = 0
        
        last_follower_count = initial_followers
        follow_count_since_check = 0

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
                current_time = time.time()
                wait_seconds = max(reset_time - current_time, 0) + 60  # Add 1 minute buffer
                
                print(f"\n⚠️ API limit reached. Reset at: {reset_dt}")
                print(f"⏰ Auto-waiting for {int(wait_seconds/60)} minutes before resuming...")
                print("💡 You can press Ctrl+C to stop the script if needed.")
                
                try:
                    countdown(int(wait_seconds))
                    print("✅ Rate limit reset! Resuming follows...\n")
                    continue  # Retry the same user
                except KeyboardInterrupt:
                    print("\n\n⚠️ Wait interrupted by user. Exiting...")
                    sys.exit(0)

            if resp.status_code == 204:
                print("Success!")
                follow_count_since_check += 1
            elif resp.status_code == 404:
                print("User not found.")
            elif resp.status_code == 403:
                reset_dt = datetime.datetime.fromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S')
                current_time = time.time()
                wait_seconds = max(reset_time - current_time, 0) + 60  # Add 1 minute buffer
                
                # If no reset time or unreasonable, default to 30 minutes
                if wait_seconds <= 0 or wait_seconds > 7200:  # max 2 hours
                    wait_seconds = 1800  # 30 minutes default
                
                print(f"⚠️ Forbidden (rate limited). Reset at: {reset_dt}")
                print(f"⏰ Auto-waiting for {int(wait_seconds/60)} minutes before resuming...")
                print("💡 You can press Ctrl+C to stop the script if needed.")
                
                try:
                    countdown(int(wait_seconds))
                    print("✅ Rate limit reset! Resuming follows...\n")
                    continue  # Retry the same user
                except KeyboardInterrupt:
                    print("\n\n⚠️ Wait interrupted by user. Exiting...")
                    sys.exit(0)
            elif resp.status_code == 401:
                print("Unauthorized. Check your ACCESS_TOKEN.")
                sys.exit(1)
            else:
                print(f"Failed with status code {resp.status_code}.")

            # Perform spot check every 10 successful follows
            if follow_count_since_check >= 10:
                time.sleep(2)  # Wait a bit for API to update
                last_follower_count = spot_check_followers(headers, follow_count_since_check, last_follower_count)
                follow_count_since_check = 0
                
                # Pause for 3 seconds before continuing
                countdown(3)

            idx += 1
            time.sleep(1/2)

        # Final spot check if there are remaining follows
        if follow_count_since_check > 0:
            print("\n📊 Performing final spot check...")
            time.sleep(2)
            last_follower_count = spot_check_followers(headers, follow_count_since_check, last_follower_count)
        
        # Summary
        print("\n" + "="*70)
        print("   🎉 FOLLOW SESSION COMPLETE")
        print("="*70)
        print(f"   Total users processed: {total}")
        print(f"   Starting followers:    {initial_followers}")
        print(f"   Ending followers:      {last_follower_count}")
        print(f"   Net gain:              +{last_follower_count - initial_followers}")
        print("="*70 + "\n")

    except KeyboardInterrupt:
        print("\nInterrupted by user, exiting.")
        sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
