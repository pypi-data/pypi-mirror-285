"""
Common functions for various cli of the jgtml project

- instrument/timeframe arguments
- force_refresh
- columns_list_from_higher_tf
- bars_amount_V2_arguments
- use_fresh_argument
- dropna_volume_argument
- drop_bid_ask
- columns_to_keep
- columns_to_drop
- lag_period
- total_lagging_periods
- patternname

"""


import argparse
from jgtutils import jgtcommon

def create_parent_jgtcommon_parser(description:str,prog:str,epilog:str)->argparse.ArgumentParser:
  parser=argparse.ArgumentParser(add_help=False)
    #jgtcommon.new_parser(description,prog,epilog)
  parser.add_help=False
  parser=jgtcommon.add_instrument_timeframe_arguments(parser)
  parser=jgtcommon.add_use_fresh_argument(parser)
  parser=jgtcommon.add_bars_amount_V2_arguments(parser)
  return parser

def new_child_parser(description:str,prog:str,epilog:str)->argparse.ArgumentParser:
  parent_parser:argparse.ArgumentParser=create_parent_jgtcommon_parser(description,prog,epilog)
  parser = argparse.ArgumentParser(description=description,prog=prog+"-child",epilog=epilog)
  #parser.add_subparsers(dest='command',type[])
  
  # parser=jgtcommon.add_instrument_timeframe_arguments(parser)
  # parser=jgtcommon.add_use_fresh_argument(parser)
  # parser=jgtcommon.add_bars_amount_V2_arguments(parser)
  return parser



def parse_args(parser:argparse.ArgumentParser)->argparse.Namespace:
  #args:argparse.Namespace=jgtcommon.parse_args(parser)
  args=parser.parse_args()
  #raise "Not Implemented Fully.  #@STCIssue Parent Parser not implemented and understood"
  return args


