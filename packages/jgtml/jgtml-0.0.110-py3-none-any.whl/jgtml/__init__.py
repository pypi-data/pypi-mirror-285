# jgtml
__version__ = "0.0.110"
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import mfihelper2 as mfih

from jtc import (
    calculate_target_variable_min_max as calc_target_from_df,
    pto_target_calculation as calc_target_to_file,
    readMXFile as read
)

from jplt import (an_biv_plt2ds as plot_an_biv_plt2ds, an_bivariate_plot00 as plot_an_bivariate_plot00)

import jdash as jdb

# from jgtpy import JGTPDS as pds,JGTADS as ads,JGTPDSP as pds

def __init__():
    """
    Initialize the jgtml module.
    """
    pass
