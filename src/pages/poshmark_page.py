from abc import ABC, abstractproperty
from src.browser import Browser

class PoshmarkPage(ABC):
    _base_url = "https://poshmark.com"
    
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
        if not self.browser.is_already_on_page(page):
            self.browser.get(self._page_url)
            self.browser.set_current_page(page)
        
    def scroll_to_top(self):
        self.browser.scroll_to_top()
