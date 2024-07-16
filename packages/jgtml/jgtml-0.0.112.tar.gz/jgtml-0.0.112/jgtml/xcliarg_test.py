
import argparse
# import pandas as pd
import os
import sys

from jgtutils import jgtcommon

class CustomAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # Implement your custom logic here
        # You can access the parsed arguments using the namespace object
        
        # For example, if you want to print the parsed arguments:
        print(namespace.instrument)
        print(namespace.timeframe)
        
        print("values:", values)
        
        # You can also modify the parsed arguments or perform any other actions
        # based on the values passed to the custom action
        
        # Set the modified values back to the namespace object if needed
        #setattr(namespace, self.dest, values)


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


def create_parent_parser():
    """Creates a parent parser with common arguments."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--verbose", action="store_true", help="Increase output verbosity.")
    parser=jgtcommon.add_instrument_timeframe_arguments(parser)
    return parser

def create_child_parser():
    """Creates a child parser with specific arguments."""
    parser = argparse.ArgumentParser(parents=[create_parent_parser()])
    #parser.add_argument("input_file", help="The input file to process.")
    #parser.add_argument("--output_file", help="The output file to write results to.")
    parser.add_argument('-cation', '--flag_with_custom_action', action=CustomAction, help='Has an action attached to it', nargs='+')
    
    return parser

def main():
    """Parses arguments and runs the program."""
    parser = create_child_parser()
    args = parser.parse_args()

    # Process the input file and write results to the output file.
    # ...

if __name__ == "__main__":
    main()