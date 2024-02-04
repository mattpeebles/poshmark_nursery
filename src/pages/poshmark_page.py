from abc import ABCMeta, abstractproperty
from browser import Browser

class PoshmarkPage(ABCMeta):
    _base_url = "https://poshmark.com"
    closet = f"{_base_url}/closet"
    share_news = f"{_base_url}/news/share"
    closet_stats = f"{_base_url}/users/self/closet_stats"
    
    def __init__(self, browser: Browser):
        self.browser = browser
        
    @abstractproperty
    def _path(self)->str:
        pass
    
    def _page_url(self)->str:
        return f"{self._base_url}/{self._path}"
    
    def go(self):
        self.browser.get(self.loginUrl)
