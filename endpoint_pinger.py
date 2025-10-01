import time
import requests
from datetime import datetime
from pathlib import Path

LINKS_FILE = "links.txt"
LOG_FILE = "ping_log.txt"

def load_links():
    """Read links from the links.txt file (ignores empty lines)."""
    path = Path(LINKS_FILE)
    if not path.exists():
        print(f"Error: {LINKS_FILE} not found.")
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def clear_log_on_saturday():
    """Clear the log file every Saturday."""
    if datetime.now().weekday() == 5:  # Saturday = 5 (Monday = 0)
        with open(LOG_FILE, "w") as f:
            f.write(f"--- Log cleared on {datetime.now().strftime('%Y-%m-%d')} ---\n")
        print("✅ Log file cleared (Saturday).")

def ping_links():
    ping_number = 1
    while True:
        now = datetime.now()

        # Check if within allowed time window (10 AM to 7 PM)
        if 0 <= now.hour < 19:
            clear_log_on_saturday()

            links = load_links()
            if not links:
                print("No links found in links.txt. Add some URLs.")
                time.sleep(30)
                continue

            with open(LOG_FILE, "a") as log:
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                header = f"\n--- Ping #{ping_number} at {timestamp} ---\n"
                log.write(header)
                print(header, end="")

                for link in links:
                    try:
                        start_time = time.time()
                        response = requests.get(link, timeout=10)
                        elapsed_ms = round((time.time() - start_time) * 1000, 2)

                        # Parse JSON if available
                        try:
                            data = response.json()
                            message_field = data.get("message", "No message in response")
                        except ValueError:
                            message_field = "Response not JSON"

                        message = f"{link} -> {response.status_code} | {elapsed_ms} ms | {message_field}"
                    except requests.RequestException as e:
                        message = f"{link} -> ERROR: {e}"

                    print(message)
                    log.write(message + "\n")

            ping_number += 1
        else:
            print(f"⏸ Outside working hours (10 AM - 7 PM). Current time: {now.strftime('%H:%M:%S')}")

        time.sleep(30)

if __name__ == "__main__":
    ping_links()
