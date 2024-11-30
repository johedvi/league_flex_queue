
import requests
import time
from urllib.parse import urlencode

class RateLimiter:
    def __init__(self, max_requests, period):
        self.max_requests = max_requests  # Maximum requests allowed
        self.period = period  # Time period in seconds
        self.requests = []
    
    def wait(self):
        current_time = time.time()
        # Remove requests that are outside the period
        self.requests = [req_time for req_time in self.requests if req_time > current_time - self.period]
        if len(self.requests) >= self.max_requests:
            # Calculate the time to wait
            sleep_time = self.period - (current_time - self.requests[0])
            print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds.")
            time.sleep(sleep_time)
            # After sleeping, remove the oldest request
            self.requests.pop(0)
        # Record the new request
        self.requests.append(time.time())

    