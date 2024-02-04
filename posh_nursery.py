import os, argparse
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
from src import nursery
from src.constants import ONE_HOUR_IN_SECONDS
from src.utils import set_debug

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
         "--share-closets-from-file",
         action="store_true",
         help="Share closets from closetsToShare.txt (optional).",
         default=False
      )
      parser.add_argument(
         "--wait-time",
         type=int,
         default=ONE_HOUR_IN_SECONDS,
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
      set_debug(args.debug)

      posh_nursery = nursery.Posh_Nursery(
         slow_mode=args.slow_mode,
         share_closets_from_file=args.share_closets_from_file,
         time_to_wait_seconds=args.wait_time,
         maintain_order=args.maintain_order,
         share_back=args.share_back
      )
      posh_nursery.login()
      posh_nursery.share()
      posh_nursery.quit()

if __name__ == "__main__":
    main()
