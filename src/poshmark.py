import datetime
from enum import Enum
import pdb
from browser import Browser
import sys
from spinner import Spinner
import time
from selenium.common.exceptions import TimeoutException
from pages import LoginPage


class PoshmarkPageElements(Enum):
    STATS = "((//div[@class='stats-container__border stats__content'])[1]//h1[@class='posh-stats__value'])[1]"
    LOGIN = "//input[@name='userHandle']"
    PASSWORD = "//input[@name='password']"
    FIRST_SHARE = "//i[@class='icon share-gray-large']"
    SOCIAL_BAR = "//div[@class='social-action-bar tile__social-actions']"
    ITEM_NAME = "//a[@class='tile__title tc--b']"
    SECOND_SHARE = "//i[@class='icon pm-logo-white']"
    SHARE_MODAL_TITLE = "//h5[@class='modal__title']"
    CAPTCHA_MODAL_TITLE = "//h5[@class='modal__title']"
    CAPTCHA_CLOSE_BUTTON = (
        "//button[@class='btn btn--close modal__close-btn simple-modal-close']"
    )
    CLOSET_NAME = "//p[@class='wb--ww tc--g']//a"  # used for sharing back
    FOLLOW_BUTTON = "//button[@class='al--right btn follow__btn m--l--2 m--r--1 btn--primary']"  # used to follow


class Poshmark:
    def __init__(
        self,
        username,
        password,
        slowMode=False,
        debug=False,
        checkCaptcha=True,
        toShareClosetsFromFile=False,
        maintainOrder=False,
        shareBack=False,
    ):
        self.browser = Browser()
        self.username = username
        self.password = password
        self.numItemsToShareFromOtherClosets = 8

        if maintainOrder:
            self.orderTextFile = "order.txt"
        else:
            self.orderTextFile = ""
        self.closetsToShareFile = "closetsToShare.txt"
        self.availableUrl = self.get_closet_available_url(self.username)
        self.hasUpdate = (
            False  # used when preserving closet order to keep track of newly added item
        )
        self.closetSize = 0
        self.shareButtons = []
        self.orderedShareButtons = []
        self.itemNameElements = []
        self.itemNames = []
        self.closetOrder = []
        self.closetOrderDict = {}
        self.closetSharedBack = []
        self.checkCaptcha = checkCaptcha
        self.toShareClosetsFromFile = toShareClosetsFromFile
        self.debug = debug
        self.shareBack = shareBack
        self.slowMode = slowMode

    def clears_and_resets(self, sharingMine=True):
        if sharingMine:
            self.hasUpdate = False
            self.orderedShareButtons = []
            self.closetOrder = []
            self.closetOrderDict = {}
        self.closetSize = 0
        self.shareButtons = []
        self.itemNameElements = []
        self.itemNames = []

    def login(self):
        spinner = Spinner(f"Logging in Poshmark as {self.username}...")
        spinner.start()
        login_page = LoginPage(self.browser)
        login_page.go()
        login_page.login()
        spinner.stop("Logged into poshmark")


    def get_closet_available_url(self, username):
        availableUrl = "{}/{}{}".format(
            self.closetUrl, username, "?availability=available"
        )
        return availableUrl

    def scrollCloset(self):
        lastHeight = self.browser.execute_script("return document.body.scrollHeight")
        scrollMore = True
        print("Scrolling")
        while scrollMore:
            self.browser.switch_to.window(self.browser.current_window_handle)
            self.browser.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(self.scrollWaitTime)
            newHeight = self.browser.execute_script("return document.body.scrollHeight")
            if newHeight == lastHeight:
                scrollMore = False
            lastHeight = newHeight

    def readInClosetOrder(self):
        self.closetOrder = [line.rstrip("\n") for line in open(self.orderTextFile)]
        for n, sortedItem in enumerate(self.closetOrder):
            self.closetOrderDict[sortedItem] = n

    def getShareButtons(self, shareAFew=False):
        self.shareButtons = self.browser.find_elements(self.firstShareXPath)
        self.closetSize = len(self.shareButtons)
        if shareAFew and self.closetSize > self.numItemsToShareFromOtherClosets:
            for _ in range(0, self.closetSize - self.numItemsToShareFromOtherClosets):
                self.shareButtons.pop()

    def clickFirstShareButton(self, shareButton):
        self.clickAButton(shareButton)
        if self.debug:
            print("      Clicked 1st share")
        self.waitTillModalPopsUp(self.shareModalTitleXPath)
        if self.slowMode:
            time.sleep(self.getRandomSec())

    def waitTillShareModalIsGone(self, shareModal):
        try:
            self.browser.wait_until_element_off_screen(shareModal)
        except TimeoutException as e:
            print(
                "Timed out while waiting for share modal to disappear..clicking second share again"
            )
            print(e)
            return False
        return True

    def closeCaptchaPopUp(self):
        try:
            captchaXButton = self.browser.find_element_by_xpath(self.captchaXButtonXPath)
            self.clickAButton(captchaXButton)
        except Exception as e:
            print(
                "      Exception occured while closing captcha pop up, exiting: "
                + str(e)
            )

    def retrySharingAnItem(self, firstShareButton):
        self.closeCaptchaPopUp()
        self.clickFirstShareButton(firstShareButton)
        shareToFollowers = self.browser.wait_till_clickable("xpath", self.secondShareXPath)
        shared = False
        while not shared:
            self.clickAButton(shareToFollowers)
            if self.debug:
                print("     Retrying sharing an item before captcha")
            if self.waitTillShareModalIsGone(shareToFollowers):
                shared = True

    def checkForCaptcha(self, modalTitleXPath):
        modalTitle = ""
        try:
            modalTitle = self.browser.find_element_by_xpath(modalTitleXPath).text
        except Exception as e:
            if self.debug:
                print("      No modal, no captcha")
        if modalTitle:
            if modalTitle == "Share this listing":
                if self.debug:
                    print("      No captcha")
            elif (
                modalTitle == "Oh the HUMAN-ity. Check the box if you're a real person."
            ):
                print("      Captcha detected, please solve")
                return True
            else:
                print("      Modal title: " + modalTitle)
        return False

    def checkAndWaitForCaptchaSolve(self, firstShareButton):
        if self.checkForCaptcha(self.captchaModalTitleXPath):
            self.browser.open_window()
            pdb.set_trace()
            self.browser.minimize_window()
            self.retrySharingAnItem(firstShareButton)
            self.checkAndWaitForCaptchaSolve(firstShareButton)

    def clickSecondShareButton(self, firstShareButton):
        shareToFollowers = self.browser.wait_till_clickable("xpath", self.secondShareXPath)
        if not shareToFollowers:
            print("time out exception occured clicking second share button")
            pdb.set_trace()
        shared = False
        while not shared:
            self.clickAButton(shareToFollowers)
            if self.debug:
                print("      Clicked 2nd share")
            if self.waitTillShareModalIsGone(shareToFollowers):
                shared = True

        if self.checkCaptcha:
            self.checkAndWaitForCaptchaSolve(firstShareButton)

        self.browser.wait_till_clickable("xpath", self.socialBarXPath)

        if self.slowMode:
            time.sleep(self.getRandomSec())

    def shareCloset(self, orderList, shareButtonsList):
        closet_size = len(orderList)
        self.update_loading_bar(0, closet_size)
        for idx, (itemName, shareButton) in enumerate(
            zip(reversed(orderList), reversed(shareButtonsList))
        ):
            if self.debug:
                print("   Sharing " + itemName)
            self.clickFirstShareButton(shareButton)
            self.clickSecondShareButton(shareButton)
            self.update_loading_bar(idx + 1, closet_size)

    def shareAllItems(
        self, sharingMine=True
    ):  # default is sharing all items from own closet
        self.browser.minimize_window()
        if self.slowMode:
            time.sleep(3)
        now = datetime.now()
        print("Current date and time: " + now.strftime("%Y-%m-%d %H:%M:%S"))
        if sharingMine:
            if self.orderTextFile:
                print("Sharing to order given by order.txt...")
                self.shareCloset(self.closetOrder, self.orderedShareButtons)
            else:
                print("No ordered text given, sharing in current closet order...")
                self.shareCloset(self.itemNames, self.shareButtons)
        else:
            self.shareCloset(self.itemNames, self.shareButtons)

    def getClosetSizeFromStatsPage(self):
        self.browser.get(self.closetStatsUrl)
        availableStats = None
        while not availableStats:
            availableStats = self.waitForAnElementByXPath(
                self.statsXPath, "available stats"
            ).text
        if self.debug:
            print("Available items from stats = " + str(availableStats))
        return int(availableStats)

    def share(self):
        if self.toShareClosetsFromFile:
            self.shareClosetsFromFile()
        else:
            while 1:
                closetSizeFromStatsPage = self.getClosetSizeFromStatsPage()
                self.browser.get(self.availableUrl)
                scroll = True
                numTimesToScroll = 4
                count = 0
                while scroll:
                    self.scrollCloset()
                    self.getShareButtons()
                    print("Available items in the closet: {}".format(self.closetSize))
                    if closetSizeFromStatsPage <= self.closetSize:
                        scroll = False
                    else:
                        # check closet size from the stats page after trying scrolling 4 times and the size still don't add up
                        # this is for the case where something gets sold between the time it last checked the stats page and going to the closet
                        if count >= numTimesToScroll:
                            closetSizeFromStatsPage = self.getClosetSizeFromStatsPage()
                            if closetSizeFromStatsPage <= self.closetSize:
                                print("Closet size matches now")
                                scroll = False
                            else:
                                print(
                                    "Closet size doesn't match on stats page of "
                                    + str(closetSizeFromStatsPage)
                                    + ". Scrolling from begining..."
                                )
                                self.browser.get(self.availableUrl)
                                scroll = True
                        else:
                            print(
                                "Closet size doesn't match on stats page of "
                                + str(closetSizeFromStatsPage)
                                + ". Scroll more..."
                            )
                            scroll = True
                    count += 1
                self.scrollToTop()
                self.getItemNames()
                if self.orderTextFile:
                    print("Keeping closet order based on " + self.orderTextFile)
                    self.arrangeClosetItemsForSharing()
                self.shareAllItems()
                self.clears_and_resets()

                if self.shareBack:
                    self.shareBackAndFollowOtherClosets()

    def shareAnotherCloset(
        self, closetName, sharingAFew=False
    ):  # default is sharing all items from another closet
        sharingMine = False
        closetUrl = self.get_closet_available_url(closetName)
        self.browser.get(closetUrl)
        if not sharingAFew:
            self.scrollCloset()
        self.getShareButtons(sharingAFew)
        if not sharingAFew:
            self.scrollToTop()
        self.getItemNames(sharingAFew)
        print("Available items in the closet: " + str(len(self.shareButtons)))
        self.shareAllItems(sharingMine)
        self.clears_and_resets(sharingMine)

    def followACloset(self, closetName=""):
        if closetName:
            closetUrl = self.get_closet_available_url(closetName)
            self.browser.get(closetUrl)
        followButton = self.browser.wait_till_clickable("xpath", self.followButtonXPath, 1)
        if followButton:
            print("following this closet")
            self.clickAButton(followButton)
        else:
            print("already following")

    def shareBackAndFollowOtherClosets(self):
        """when given no param, it follows the closet on the page that's currently loaded"""
        print("sharing back")
        sharingAFew = True
        self.browser.get(self.shareNewsUrl)
        self.scrollPageANumTimes()
        self.waitForAnElementByXPath(self.closetNameXPath, "closetNameXPath")
        closetNames = self.browser.find_elements(self.closetNameXPath)
        closetNamesSet = set()
        for n in closetNames:
            closetNamesSet.add(n.text)
        print(closetNamesSet)

        for closet in closetNamesSet:
            if closet not in self.closetSharedBack:
                print("sharing " + closet)
                self.shareAnotherCloset(closet, sharingAFew)
                self.closetSharedBack.append(closet)
                self.followACloset()

    def checkItemInOrderTextFile(self, item):
        if item in self.closetOrderDict.keys():
            return True
        else:
            return False

    def checkItemInCloset(self, item):
        if item in self.itemNames:
            return True
        else:
            return False

    def updateOrderFile(self):
        for itemName in reversed(self.itemNames):
            # append to begining of order file
            if not self.checkItemInOrderTextFile(itemName):
                self.hasUpdate = True
                print(itemName + " not in order text file")
                print("Adding " + itemName)
                with open(self.orderTextFile, "r") as f:
                    lines = f.readlines()
                with open(self.orderTextFile, "w") as f:
                    f.write(itemName + "\n")
                    for line in lines:
                        item = line.strip("\n")
                        if item != itemName:
                            f.write(line)

        for closetOrderItem in self.closetOrderDict.keys():
            if not self.checkItemInCloset(closetOrderItem):
                self.hasUpdate = True
                # delete from order file
                print(closetOrderItem + " is not in closet anymore")
                print("Deleting " + closetOrderItem)
                with open(self.orderTextFile, "r") as f:
                    lines = f.readlines()
                with open(self.orderTextFile, "w") as f:
                    for line in lines:
                        item = line.strip("\n")
                        if item != closetOrderItem:
                            f.write(line)

    def arrangeClosetItemsForSharing(self):
        self.readInClosetOrder()
        self.updateOrderFile()
        if self.hasUpdate:
            self.closetOrderDict = {}
            self.readInClosetOrder()
            print("Updated order.txt")
        if self.debug:
            print(self.closetOrderDict)
        self.orderedShareButtons = [None] * self.closetSize
        for itemName, item in zip(self.itemNames, self.shareButtons):
            self.orderedShareButtons[self.closetOrderDict[itemName]] = item
        count = 0
        for button in self.orderedShareButtons:
            if button == None:
                print(str(count) + " is None. Something went wrong. Exiting")
                self.quit()
                sys.exit()
            count += 1

    def getAndPrintItemNames(self):
        for count, itemName in enumerate(self.itemNameElements):
            itemNameTxt = itemName.text
            self.itemNames.append(itemNameTxt)
            if self.debug:
                print(str(count) + ": " + itemNameTxt)

    def getItemNames(self, shareAFew=False):
        self.itemNameElements = self.browser.find_elements(self.itemNameXPath)
        if shareAFew:
            closetSize = len(self.itemNameElements)
            if closetSize > self.numItemsToShareFromOtherClosets:
                for i in range(0, closetSize - self.numItemsToShareFromOtherClosets):
                    self.itemNameElements.pop()
        self.getAndPrintItemNames()

    def getClosetsToShareFromFile(self):
        self.closetsToShare = []
        with open(self.closetsToShareFile, "r") as f:
            lines = f.readlines()
            for line in lines:
                closetName = line.strip()
                if closetName:
                    self.closetsToShare.append(closetName)
        numClosets = len(self.closetsToShare)
        if numClosets == 0:
            print("No closets given in the file")
        return numClosets

    def shareClosetsFromFile(self):
        if self.getClosetsToShareFromFile():
            for closet in self.closetsToShare:
                print("Sharing " + closet)
                closetAvailableUrl = self.get_closet_available_url(closet)
                self.shareAnotherCloset(closetAvailableUrl)

    def update_loading_bar(self, current_iteration, iterations):
        progress = current_iteration / iterations
        bar_length = 40
        bar = (
            "["
            + "=" * int(bar_length * progress)
            + " " * (bar_length - int(bar_length * progress))
            + "]"
        )
        status = f"{current_iteration} out of {iterations} items"
        sys.stdout.write(f"\r{bar} {int(progress * 100)}% {status}")
        sys.stdout.flush()
