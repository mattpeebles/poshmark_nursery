from src.pages.poshmark_page import PoshmarkPage
from src.utils import is_debug

class MyStats(PoshmarkPage):
    STATS = "((//div[@class='stats-container__border stats__content'])[1]//h1[@class='posh-stats__value'])[1]"

    @property
    def _path(self):
        return "users/self/closet_stats"
    
    def get_closet_size(self)->int:
        available_stats = None
        while not available_stats:
            available_stats = self.browser.wait_for_an_element_by_xpath(
                self.STATS, "available stats"
            ).text
        if is_debug():
            print("Available items from stats = " + str(available_stats))
        return int(available_stats)
