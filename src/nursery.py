import random, time
from datetime import datetime, timedelta
from poshmark import Poshmark


class Posh_Nursery:
    def __init__(self, username, password, slowMode = False, debug = False, checkCaptcha = True, toShareClosetsFromFile = False, timeToWait = 3600, maintainOrder = False, shareBack = False):
        self.timeToWait = timeToWait
        self.poshmark = Poshmark(username, password, slowMode, debug, checkCaptcha, toShareClosetsFromFile, maintainOrder, shareBack)
        self.driver.minimize_window()
   

    def quit(self):   
      self.poshmark.quit()
   
    def getRandomSec(self):
      return random.randrange(1, 5, 1)

    def share(self):
        self.poshmark.share()
        print("Shared closet, will share again in " + str(self.timeToWait/60) + " mins at " + str(datetime.now() + timedelta(seconds=self.timeToWait))) 
        time.sleep(self.timeToWait)
        
    def login(self):
        self.poshmark.login()
        





   


   


   
