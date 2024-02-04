import os, argparse
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from src import nursery

load_dotenv()

def checkBooleanInput(val):
   if val in ('y', 'yes', 't', 'true', '1'):
      return True, True
   elif val in ('n', 'no', 'f', 'false', '0'):
      return True, False
   else:
      return False, False

def main():
      parser = argparse.ArgumentParser(description="Poshmark Nursery")

      parser.add_argument(
         "--slow-mode",
         action="store_true",
         help="Enable slow mode (optional).",
         default=False
      )
      parser.add_argument(
         "--debug",
         action="store_true",
         help="Enable debug mode (optional).",
         default=False
      )
      parser.add_argument(
         "--check-captcha",
         action="store_true",
         help="Check for captcha (optional).",
         default=True
      )
      parser.add_argument(
         "--share-closets-from-file",
         action="store_true",
         help="Share closets from closetsToShare.txt (optional).",
         default=False
      )
      parser.add_argument(
         "--wait-time",
         type=int,
         default=3600,
         help="Number of seconds to wait after one round of sharing. Default is 3600.",
      )
      parser.add_argument(
         "--maintain-order",
         action="store_true",
         help="Maintain closet order based on an order file (optional).",
         default=False
      )
      parser.add_argument(
         "--share-back",
         action="store_true",
         help="Share back (optional).",
         default=False
      )

      args = parser.parse_args()
      username = os.getenv("POSH_USERNAME")
      password = os.getenv("POSH_PASSWORD")    
      posh_nursery = nursery.Posh_Nursery(
         username,
         password,
         args.slow_mode,
         args.debug,
         args.check_captcha,
         args.share_closets_from_file,
         args.wait_time,
         args.maintain_order,
         args.share_back
      )
      posh_nursery.login()
      posh_nursery.share()
      posh_nursery.quit()

if __name__ == "__main__":
    main()
