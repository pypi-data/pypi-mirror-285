import argparse
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


from ptottf import create_ttf_csv # type: ignore

import os

def main():
  parser = argparse.ArgumentParser(description="Create ttf CSV file")
  parser.add_argument("-i", "--instrument", required=True, help="Instrument name")
  parser.add_argument("-t", "--timeframe", required=True, help="Timeframe (e.g., D1, H4)")
  parser.add_argument("-uf", "--full", action="store_true", help="Use full dataset")
  parser.add_argument("-new", "--fresh", action="store_true", help="Use fresh data")
  parser.add_argument("-fr", "--force_read", action="store_true", help="Force to read CDS (should increase speed but relies on existing data)")
  parser.add_argument("-c", "--quotescount", type=int, default=-1, help="Number of quotes to retrieve (default: 333)")
  #columns_list_from_higher_tf
  parser.add_argument("-clh", "--columns_list_from_higher_tf", nargs='+', help="List of columns to get from higher TF", default=None)
  #@STCGoal Future Proto where Sub-Patterns are created from TTF with their corresponding Columns list and mayby Lags
  #patternname
  parser.add_argument("-pn", "--patternname", help="Pattern Name", default="ttf")
  
  args = parser.parse_args()
  columns_list_from_higher_tf = args.columns_list_from_higher_tf if args.columns_list_from_higher_tf else None
  
  #print("Columns List from Higher TF:",columns_list_from_higher_tf)
  
  create_ttf_csv(args.instrument, args.timeframe, args.full if args.full else False, True if args.fresh else False, args.quotescount, args.force_read, columns_list_from_higher_tf=columns_list_from_higher_tf, midfix=args.patternname)

if __name__ == "__main__":
  main()
  