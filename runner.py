import time
from tasks import log_something

if __name__ == "__main__":
    while True:
        log_something.delay()
        time.sleep(5)
