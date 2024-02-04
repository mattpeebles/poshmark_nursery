import os
import sys
from closet_page import ClosetBase
from src.browser import Browser
from src.pages.my_stats_page import MyStats
from src.utils import is_debug


class MyCloset(ClosetBase):
    def __init__(self, browser: Browser):
        username = os.getenv("POSH_USERNAME")
        super().__init__(browser, username)
    
    def _is_mine(self) -> bool:
        return True

    def _share_impl(self, order_file: str | None, slowly: bool):
        while 1:
            stats_page = MyStats(self.browser)
            stats_page.go()
            closet_size_from_stats_page = stats_page.get_closet_size()
            self.go()
            scroll = True
            num_times_to_scroll = 4
            count = 0
            while scroll:
                self.scroll()
                self.get_share_buttons()
                print("Available items in the closet: {}".format(self.closet_size))
                if closet_size_from_stats_page <= self.closet_size:
                    scroll = False
                else:
                    # check closet size from the stats page after trying scrolling 4 times and the size still don't add up
                    # this is for the case where something gets sold between the time it last checked the stats page and going to the closet
                    if count >= num_times_to_scroll:
                        stats_page.go()
                        closet_size_from_stats_page = stats_page.get_closet_size()
                        if closet_size_from_stats_page <= self.closet_size:
                            print("Closet size matches now")
                            scroll = False
                        else:
                            print(
                                "Closet size doesn't match on stats page of "
                                + str(closet_size_from_stats_page)
                                + ". Scrolling from begining..."
                            )
                            self.go()
                            scroll = True
                    else:
                        print(
                            "Closet size doesn't match on stats page of "
                            + str(closet_size_from_stats_page)
                            + ". Scroll more..."
                        )
                        scroll = True
                count += 1

            self.scroll_to_top()
            self.get_item_names()
            if order_file:
                print("Keeping closet order based on " + self.order_text_file)
                self.arrange_closet_items_for_sharing(order_file)
            self.share_all_items(slowly)
            self._clears_and_resets()

    def share_in_text_file_order(self, order_text_file: str, slowly: bool):
        """shares in order of the text file"""
        self._share_impl(order_text_file, slowly)
    
    def share(self, slowly: bool):
        self._share_impl(slowly)
        """shares in closet order"""

    def read_in_closet_order(self):
        self.closetOrder = [line.rstrip("\n") for line in open(self.order_text_file)]
        for n, sortedItem in enumerate(self.closetOrder):
            self.closetOrderDict[sortedItem] = n


    def arrange_closet_items_for_sharing(self, order_file: str):
        self.read_in_closet_order()
        self.update_order_file(order_file)
        if self.hasUpdate:
            self.closetOrderDict = {}
            self.read_in_closet_order()
            print(f"Updated {order_file}")
        if is_debug():
            print(self.closetOrderDict)
        self.orderedShareButtons = [None] * self.closet_size
        for itemName, item in zip(self.item_names, self.share_buttons):
            self.orderedShareButtons[self.closetOrderDict[itemName]] = item
        count = 0
        for button in self.orderedShareButtons:
            if button == None:
                print(str(count) + " is None. Something went wrong. Exiting")
                self.quit()
                sys.exit()
            count += 1

    def update_order_file(self, order_file: str):
        for itemName in reversed(self.item_names):
            # append to begining of order file
            if not self.check_item_in_order_text_file(itemName):
                self.hasUpdate = True
                print(itemName + " not in order text file")
                print("Adding " + itemName)
                with open(order_file, "r") as f:
                    lines = f.readlines()
                with open(order_file, "w") as f:
                    f.write(itemName + "\n")
                    for line in lines:
                        item = line.strip("\n")
                        if item != itemName:
                            f.write(line)

        for closetOrderItem in self.closetOrderDict.keys():
            if not self.check_item_in_closet(closetOrderItem):
                self.hasUpdate = True
                # delete from order file
                print(closetOrderItem + " is not in closet anymore")
                print("Deleting " + closetOrderItem)
                with open(order_file, "r") as f:
                    lines = f.readlines()
                with open(order_file, "w") as f:
                    for line in lines:
                        item = line.strip("\n")
                        if item != closetOrderItem:
                            f.write(line)

    def check_item_in_order_text_file(self, item):
        return item in self.closetOrderDict.keys()

    def check_item_in_closet(self, item):
        return item in self.item_names
