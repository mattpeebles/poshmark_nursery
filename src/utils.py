import os
import random
import sys

def get_random_sec():
    return random.randrange(1, 5, 1)

def set_debug(debug: bool):
    os.environ['DEBUG'] = str(debug)
    
def is_debug()->bool:
    return os.environ.get('DEBUG', "false").lower() == "true"

# todo: move to own class
def update_loading_bar(self, current_iteration, iterations):
    progress = current_iteration / iterations
    bar_length = 40
    bar = (
        "["
        + "=" * int(bar_length * progress)
        + " " * (bar_length - int(bar_length * progress))
        + "]"
    )
    status = f"{current_iteration} out of {iterations} items"
    sys.stdout.write(f"\r{bar} {int(progress * 100)}% {status}")
    sys.stdout.flush()
