from src.pages.poshmark_page import PoshmarkPage

class ShareNews(PoshmarkPage):
    CLOSET_NAME = "//p[@class='wb--ww tc--g']//a"  # used for sharing back
    
    @property
    def _path(self):
        return "news/share"
    
    def get_closet_names(self)->list[str]:
        self.browser.scroll_page()
        self.browser.wait_for_an_element_by_xpath(self.CLOSET_NAME, "closetNameXPath")
        closet_names = self.browser.find_elements(self.CLOSET_NAME)
        closet_names_set = set()
        for n in closet_names:
            closet_names_set.add(n.text)
        print(closet_names_set)
        return list(closet_names_set)