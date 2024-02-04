from abc import ABCMeta, abstractproperty
from browser import Browser

class PoshmarkPage(ABCMeta):
    _base_url = "https://poshmark.com"
    share_news = f"{_base_url}/news/share"
    
    def __init__(self, browser: Browser):
        self.browser = browser
        
    @abstractproperty
    def _path(self)->str:
        pass
    
    @property
    def _page_url(self)->str:
        return f"{self._base_url}/{self._path}"
    
    def go(self):
        page = self.__class__.__name__
        if not self.browser.already_on_page(page):
            self.browser.get(self._page_url)
            self.browser.set_current_page(page)
        
    def scroll_to_top(self):
        self.browser.scroll_to_top()
