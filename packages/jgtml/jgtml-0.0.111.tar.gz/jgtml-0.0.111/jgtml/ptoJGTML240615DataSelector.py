import os
from jgtutils.jgtconstants import (HIGH, LOW, JAW, TEETH, LIPS, TJAW, TTEETH, TLIPS, BJAW, BTEETH, BLIPS, FDB_TARGET, VECTOR_AO_FDB_COUNT, FDBS, VECTOR_AO_FDBS_COUNT, FDBB, VECTOR_AO_FDBB_COUNT)
from ptodata2406dConfNRequest import JGTML240615Config, JGTML240615Request

class JGTML240615DataSelector:
  def __init__(self, config, request):
    self.config = config
    self.request = request
    self.sel_columns_base = [HIGH, LOW, JAW, TEETH, LIPS]
    self.sel_columns_tide_alligator = [TJAW, TTEETH, TLIPS]
    self.sel_columns_big_alligator = [BJAW, BTEETH, BLIPS]
    self.sel_columns_common = self._select_columns()

  def _select_columns(self):
    # Select columns according to Flags (big alligator and tide alligator)
    sel_columns = self.sel_columns_base
    if self.config.balligator_flag:
      sel_columns += self.sel_columns_big_alligator
    if self.config.talligator_flag:
      sel_columns += self.sel_columns_tide_alligator
    sel_columns += [FDB_TARGET, VECTOR_AO_FDB_COUNT]
    return sel_columns

  def get_columns_for_bs(self):
    # Adjust columns based on buy/sell flag
    if self.request.bs == "S":
      return self.sel_columns_common + [FDBS, VECTOR_AO_FDBS_COUNT]
    elif self.request.bs == "B":
      return self.sel_columns_common + [FDBB, VECTOR_AO_FDBB_COUNT]
    else:
      return self.sel_columns_common

# Example usage
config = JGTML240615Config()
request = JGTML240615Request(bs=os.getenv("bs", "S"))  # Assuming bs is part of the environment
data_selector = JGTML240615DataSelector(config, request)
selected_columns = data_selector.get_columns_for_bs()