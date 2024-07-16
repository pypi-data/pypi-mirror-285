
import argparse
# import pandas as pd
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtutils import jgtcommon

import mlclicommon


def _parse_args():
  sparser=mlclicommon.new_child_parser("A CLI for the jgtml project to test structuring arg parsing","xcliarg_test","We are testing parent and child parsers")
  
  args=mlclicommon.parse_args(sparser)
  return args
  

def main():
  args = _parse_args()
  
if __name__ == "__main__":
  main()


