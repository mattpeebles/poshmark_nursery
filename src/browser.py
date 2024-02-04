from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
import random, time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class Browser:
    _current_page: str | None
    
    def __init__(self):
        self.chrome_options = Options()
        # self.chrome_options.add_argument("--headless")
        # self.chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.time_out_secs = 10
        self.scroll_wait_time = 5
        self.num_times_to_scroll = 5
        self._current_page = None

    def is_already_on_page(self, page: str)->bool:
        return page == self._current_page

    def set_current_page(self, page: str):
        self._current_page = page

    def quit(self):
        self.driver.quit()

    def get(self, url: str):
        """points browser to the url """
        self.driver.get(url)

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

    def wait_till_clickable(self, find_by_id_or_path: str, id_or_path, time_out_secs=10) -> (WebElement | bool):
        clickable_element = False
        if find_by_id_or_path == "id":
            try:
                clickable_element = WebDriverWait(self.driver, time_out_secs).until(
                    EC.element_to_be_clickable((By.ID, id_or_path))
                )
            except TimeoutException as e:
                print(
                    "Timed out at locating element by "
                    + find_by_id_or_path
                    + " at "
                    + str(id_or_path)
                    + ": "
                    + str(e)
                )
                return False
        else:
            try:
                clickable_element = WebDriverWait(self.driver, time_out_secs).until(
                    EC.element_to_be_clickable((By.XPATH, id_or_path))
                )
            except TimeoutException as e:
                print(
                    "Timed out at locating element by "
                    + find_by_id_or_path
                    + " at "
                    + str(id_or_path)
                    + ": "
                    + str(e)
                )
                return False
        
        return clickable_element

    def wait_for_an_element_by_xpath(self, xpath, elementName) -> (WebElement | bool):
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

    def click(self, button: WebElement):
        try:
            self.driver.execute_script("arguments.click();", button)
        except Exception as e:
            print("clicking button failed: " + str(e))

    def wait_till_modal_appears(self, xpath):
        modal_pops_up = False
        while not modal_pops_up:
            modal_pops_up = self.wait_for_an_element_by_xpath(xpath, "modal")

    def scroll_page(self):
        """will scroll the current page self.num_times_to_scroll times"""
        for _ in range(0, self.num_times_to_scroll):
            self.driver.switch_to.window(self.driver.current_window_handle)
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(self.scroll_wait_time)
