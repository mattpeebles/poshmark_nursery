from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
import random, time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Browser:
    def __init__(self):
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")
        # self.chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.time_out_secs = 10
        self.scroll_wait_time = 5
        self.num_times_to_scroll = 5

    def quit(self):
        self.driver.quit()

    def get(self, url: str):
        """points browser to the url """
        self.browser.get(url)

    def minimize_window(self):
        self.driver.minimize_window()
        
    def open_window(self):
        """opens window on desktop"""
        self.browser.switch_to.window(self.browser.current_window_handle)

    def wait_until_page_is(self, page_title: str):
        self.wait_until(EC.title_contains(page_title))

    def wait_until_element_off_screen(self, element):
        WebDriverWait(self.driver, self.time_out_secs).until(
            EC.invisibility_of_element_located(element)
        )

    def wait_until(self, condition):
        WebDriverWait(self.driver, self.time_out_secs).until(condition)

    def find_elements(self, xpath: str):
        return self.driver.find_elements(By.XPATH, xpath)

    def wait_till_clickable(self, findByIdOrPath, idOrPath, timeOutSecs=10):
        clickableElement = False
        if findByIdOrPath == "id":
            try:
                clickableElement = WebDriverWait(self.driver, timeOutSecs).until(
                    EC.element_to_be_clickable((By.ID, idOrPath))
                )
            except TimeoutException as e:
                print(
                    "Timed out at locating element by "
                    + findByIdOrPath
                    + " at "
                    + str(idOrPath)
                    + ": "
                    + str(e)
                )
                return False
        else:
            try:
                clickableElement = WebDriverWait(self.driver, timeOutSecs).until(
                    EC.element_to_be_clickable((By.XPATH, idOrPath))
                )
            except TimeoutException as e:
                print(
                    "Timed out at locating element by "
                    + findByIdOrPath
                    + " at "
                    + str(idOrPath)
                    + ": "
                    + str(e)
                )
                return False
        return clickableElement

    def wait_for_an_element_by_xpath(self, xpath, elementName):
        try:
            element = WebDriverWait(self.driver, self.time_out_secs).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
        except TimeoutException as e:
            print(
                "Timed out while waiting for "
                + elementName
                + " to pop up..waiting again"
            )
            print(e)
            return False
        return element

    def enter_text_slowly(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.random())

    def scroll_to_top(self):
        self.driver.switch_to.window(self.driver.current_window_handle)
        self.driver.execute_script("window.scrollTo(0, 0);")

    def click(self, button):
        try:
            self.driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            print("clicking button failed: " + str(e))

    def waitTillModalPopsUp(self, xpath):
        modalPopsUp = False
        while not modalPopsUp:
            modalPopsUp = self.wait_for_an_element_by_xpath(xpath, "modal")

    def scroll_page(self):
        """will scroll the current page self.num_times_to_scroll times"""
        for _ in range(0, self.num_times_to_scroll):
            self.driver.switch_to.window(self.driver.current_window_handle)
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(self.scroll_wait_time)
