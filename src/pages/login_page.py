from poshmark_page import PoshmarkPage
import sys
import pdb

class LoginPage(PoshmarkPage):
    def _path():
        return "login"
    
    def login(self, username: str, password: str):
        self._enter_username(username)
        self._enter_and_submit_password(password)
        if self.debug:
            print(self.browser.title)
        
        try:
            self.browser.wait_until_page_is("Feed")
        except Exception as e:
            print("ERROR: logging error{}".format(e))
            print("Please solve captcha and then type 'c' or 'continue'")
            self.browser.switch_to.window(self.browser.current_window_handle)
            pdb.set_trace()
            self.browser.minimize_window()
    def _enter_username(self, username: str):
        user_name_element = self._get_login_element("login_form_username_email", PoshmarkPageElements.LOGIN)
        if not user_name_element:
            print("Username element not obtained from page, exiting...")
            self.quit()
            sys.exit()
        self.enterTxtSlowly(user_name_element, username)

    def _enter_and_submit_password(self, password: str):
        password_element = self._get_login_element("login_form_password", self.passwordXPath)
        if not password_element:
            print("Password element not obtained from page, exiting...")
            self.quit()
            sys.exit()
        self.enterTxtSlowly(password_element, password)
        password_element.submit()
        
    def _get_login_element(self, elementID, elementXPath):
        element = self.browser.wait_till_clickable("id", elementID)
        if not element:
            print("Time out at locating ID: " + elementID)
            element = self.browser.wait_till_clickable("xpath", elementXPath)
            if not element:
                print("Timed out again with xpath")
                print(
                    "Please manually enter username/password, then type 'c' or 'continue'"
                )
                pdb.set_trace()
        return element
