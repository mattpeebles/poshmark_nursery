from abc import ABC, abstractmethod, abstractproperty
import datetime
import pdb
import time
from src.pages.poshmark_page import PoshmarkPage
from src.browser import Browser
from src.utils import get_random_sec, is_debug, update_loading_bar
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement

class ClosetBase(PoshmarkPage, ABC):
    FIRST_SHARE = "//i[@class='icon share-gray-large']"
    SECOND_SHARE = "//i[@class='icon pm-logo-white']"
    SHARE_MODAL_TITLE = "//h5[@class='modal__title']"
    CAPTCHA_CLOSE_BUTTON = (
        "//button[@class='btn btn--close modal__close-btn simple-modal-close']"
    )
    SOCIAL_BAR = "//div[@class='social-action-bar tile__social-actions']"
    CAPTCHA_MODAL_TITLE = "//h5[@class='modal__title']"
    ITEM_NAME = "//a[@class='tile__title tc--b']"

    
    def __init__(self, browser: Browser, closet_name: str):
        super().__init__(browser)
        self.has_update = (
            False  # used when preserving closet order to keep track of newly added item
        )
        self.closet_name = closet_name
        self.closet_size = 0
        self.share_buttons = []
        self.ordered_share_buttons = []
        self.item_name_elements = []
        self.item_names = []
        self.closet_order = []
        self.closet_order_dict = {}
        self.num_items_to_share_from_other_closets = 8
    
    @property
    def _path(self)->str:
        return f"closet/{self.closet_name}?availability=available"
    
    @abstractproperty
    def _is_mine(self)->bool:
        pass
    
    def _clears_and_resets(self):
        if self._is_mine:
            self.has_update = False
            self.ordered_share_buttons = []
            self.closet_order = []
            self.closet_order_dict = {}
        
        self.closet_size = 0
        self.share_buttons = []
        self.item_name_elements = []
        self.item_names = []

    @abstractmethod
    def share(self, slowly: bool):
        """shares the closet"""
        pass
        
    def scroll(self):
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        scroll_more = True
        print("Scrolling")
        while scroll_more:
            self.browser.switch_to.window(self.browser.current_window_handle)
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(self.browser.scroll_wait_time)
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            scroll_more = new_height != last_height
            last_height = new_height

    def get_share_buttons(self, share_a_few=False):
        self.share_buttons = self.browser.find_elements(self.FIRST_SHARE)
        self.closet_size = len(self.share_buttons)
        if share_a_few and self.closet_size > self.num_items_to_share_from_other_closets:
            for _ in range(0, self.closet_size - self.num_items_to_share_from_other_closets):
                self.share_buttons.pop()

    def click_first_share_button(self, share_button: WebElement, slowly: bool):
        self.browser.click(share_button)
        if is_debug():
            print("      Clicked 1st share")
        self.browser.wait_till_modal_appears(self.SHARE_MODAL_TITLE)
        if slowly:
            time.sleep(get_random_sec())

    def wait_till_share_modal_is_gone(self, share_modal):
        try:
            self.browser.wait_until_element_off_screen(share_modal)
        except TimeoutException as e:
            print(
                "Timed out while waiting for share modal to disappear..clicking second share again"
            )
            print(e)
            return False
        return True
    
    def check_for_captcha(self, modal_title_x_path):
        modal_title = ""
        try:
            modal_title = self.browser.find_element_by_xpath(modal_title_x_path).text
        except Exception as e:
            if is_debug():
                print("      No modal, no captcha")
        if modal_title:
            if modal_title == "Share this listing":
                if is_debug():
                    print("      No captcha")
            elif (
                modal_title == "Oh the HUMAN-ity. Check the box if you're a real person."
            ):
                print("      Captcha detected, please solve")
                return True
            else:
                print("      Modal title: " + modal_title)
        return False

    
    def close_captcha_pop_up(self):
        try:
            captcha_x_button = self.browser.find_elements(self.CAPTCHA_CLOSE_BUTTON)[0]
            self.browser.click(captcha_x_button)
        except Exception as e:
            print(
                "      Exception occured while closing captcha pop up, exiting: "
                + str(e)
            )
            
    def retry_sharing_an_item(self, first_share_button: WebElement, slowly: bool):
        self.close_captcha_pop_up()
        self.click_first_share_button(first_share_button, slowly)
        share_to_followers_button = self.browser.wait_till_clickable("xpath", self.SECOND_SHARE)
        shared = False
        while not shared:
            self.browser.click(share_to_followers_button)
            if is_debug():
                print("     Retrying sharing an item before captcha")
            if self.wait_till_share_modal_is_gone(share_to_followers_button):
                shared = True
                
    def check_and_wait_for_captcha_solve(self, first_share_button: WebElement, slowly: bool):
        if self.check_for_captcha(self.CAPTCHA_MODAL_TITLE):
            self.browser.open_window()
            pdb.set_trace()
            self.browser.minimize_window()
            self.retry_sharing_an_item(first_share_button, slowly)
            self.check_and_wait_for_captcha_solve(first_share_button, slowly)

    def click_second_share_button(self, first_share_button: WebElement, slowly: bool):
        share_to_followers = self.browser.wait_till_clickable("xpath", self.SECOND_SHARE)
        if not share_to_followers:
            print("time out exception occured clicking second share button")
            pdb.set_trace()
        shared = False
        while not shared:
            self.browser.click(share_to_followers)
            if is_debug():
                print("      Clicked 2nd share")
            if self.wait_till_share_modal_is_gone(share_to_followers):
                shared = True

        self.check_and_wait_for_captcha_solve(first_share_button, slowly)
        self.browser.wait_till_clickable("xpath", self.SOCIAL_BAR)

        if slowly:
            time.sleep(self.getRandomSec())

    def share_closet(self, orderList, share_buttons_list: list[WebElement], slowly: bool):
        closet_size = len(orderList)
        update_loading_bar(0, closet_size)
        for idx, (item_name, share_button) in enumerate(
            zip(reversed(orderList), reversed(share_buttons_list))
        ):
            if is_debug():
                print("   Sharing " + item_name)
            self.click_first_share_button(share_button)
            self.click_second_share_button(share_button, slowly)
            update_loading_bar(idx + 1, closet_size)

    def share_all_items(
        self,
        slowly: bool
    ):
        self.browser.minimize_window()
        if slowly:
            time.sleep(3)
        now = datetime.now()
        print("Current date and time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        if self._is_mine:
            if self.order_text_file:
                print("Sharing to order given by order.txt...")
                self.share_closet(self.closet_order, self.ordered_share_buttons, slowly)
            else:
                print("No ordered text given, sharing in current closet order...")
                self.share_closet(self.item_names, self.share_buttons, slowly)
        else:
            self.share_closet(self.item_names, self.share_buttons, slowly)

    def get_and_print_item_names(self):
        for count, item_name in enumerate(self.item_name_elements):
            item_name_text = item_name.text
            self.item_names.append(item_name_text)
            if is_debug():
                print(str(count) + ": " + item_name_text)

    def get_item_names(self, shareAFew=False):
        self.item_name_elements = self.browser.find_elements(self.ITEM_NAME)
        if shareAFew:
            closetSize = len(self.item_name_elements)
            if closetSize > self.num_items_to_share_from_other_closets:
                for _ in range(0, closetSize - self.num_items_to_share_from_other_closets):
                    self.item_name_elements.pop()
        self.get_and_print_item_names()