import time
from datetime import datetime, timedelta
from src.poshmark import Poshmark
from src.constants import ONE_HOUR_IN_SECONDS



class Posh_Nursery:
    def __init__(
        self,
        slow_mode=False,
        share_closets_from_file=False,
        time_to_wait_seconds=ONE_HOUR_IN_SECONDS,
        maintain_order=False,
        share_back=False,
    ):
        self.timeToWait = time_to_wait_seconds
        self.poshmark = Poshmark(
            slow_mode, share_closets_from_file, maintain_order, share_back
        )

    def quit(self):
        self.poshmark.quit()

    def share(self):
        self.poshmark.share()
        print(
            "Shared closet, will share again in "
            + str(self.timeToWait / 60)
            + " mins at "
            + str(datetime.now() + timedelta(seconds=self.timeToWait))
        )
        time.sleep(self.timeToWait)

    def login(self):
        self.poshmark.login()
