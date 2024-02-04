from src.browser import Browser
from spinner import Spinner
from src.pages import LoginPage, MyCloset, ShareNews, Closet

class Poshmark:
    def __init__(
        self,
        slow_mode=False,
        share_closets_from_file=False,
        maintain_order=False,
        share_back=False,
    ):
        self.browser = Browser()
        self.maintain_order = maintain_order
        self.closets_to_share_file = "closetsToShare.txt"
        self.share_closets_from_file = share_closets_from_file
        self.share_back = share_back
        self.slow_mode = slow_mode
        self.closet_shared_back = []

    def login(self):
        login_page = LoginPage(self.browser)
        spinner = Spinner(f"Logging in Poshmark as {login_page.username}...")
        spinner.start()
        login_page.go()
        login_page.login()
        spinner.stop("Logged into poshmark")

    def share(self):
        if self.share_closets_from_file:
            self.share_closets_from_file()
        else:
            my_closet = MyCloset(self.browser)
            if self.maintain_order:
                my_closet.share_in_text_file_order("order.txt", self.slow_mode)
            else:
                my_closet.share(self.slow_mode)

            if self.share_back:
                self.share_back_and_follow_other_closets()

    def share_another_closet(
        self, closet: Closet, sharing_a_few=False
    ):
        """Shares items from another users closet

            Arguments:
                closet_name - the closet to share \n
                sharing_a_few - if true, will only share a limited number of items otherwise, will share all
            
        """
        closet.share_a_few(self.slow_mode) if sharing_a_few else closet.share(self.slow_mode)

    def share_back_and_follow_other_closets(self):
        """when given no param, it follows the closet on the page that's currently loaded"""
        print("sharing back")
        share_a_few = True
        share_news = ShareNews(self.browser)
        share_news.go()
        closet_names = share_news.get_closet_names()
        for closet_name in closet_names:
            if closet_name not in self.closet_shared_back:
                print("sharing " + closet_name)
                closet = Closet(self.browser, closet_name)
                self.share_another_closet(closet, share_a_few)
                self.closet_shared_back.append(closet_name)
                closet.follow()

    def get_closets_to_share_from_file(self)->list[str]:
        closets_to_share = []
        with open(self.closets_to_share_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                closet_name = line.strip()
                if closet_name:
                    closets_to_share.append(closet_name)
        if not closets_to_share:
            print("No closets given in the file")
        return closets_to_share

    def share_closets_from_file(self):
        if (closets_to_share := self.get_closets_to_share_from_file()):
            for closet in closets_to_share:
                print("Sharing " + closet)
                self.share_another_closet(closet)
