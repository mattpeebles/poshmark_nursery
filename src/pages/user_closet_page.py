from src.pages.closet_page_base import ClosetBase

class Closet(ClosetBase):
    FOLLOW_BUTTON = "//button[@class='al--right btn follow__btn m--l--2 m--r--1 btn--primary']"  # used to follow

    def _is_mine(self)->bool:
        return False

    def follow(self):
        self.go()
        follow_button = self.browser.wait_till_clickable("xpath", self.FOLLOW_BUTTON, 1)
        if follow_button:
            print("following this closet")
            self.browser.click(follow_button)
        else:
            print("already following")
            
            
    def _share_impl(self, sharing_a_few: bool, slowly: bool):
        self.go()
        if not sharing_a_few:
            self.scroll()
        self.get_share_buttons(sharing_a_few)
        
        if not sharing_a_few:
            self.scroll_to_top()
        
        self.get_item_names(sharing_a_few)
        print("Available items in the closet: " + str(len(self.share_buttons)))
        self.share_all_items()
        self._clears_and_resets()
        
    def share(self, slowly: bool):
        self._share_impl(False, slowly)
        
    def share_a_few(self, slowly: bool):
        self._share_impl(True, slowly)
        