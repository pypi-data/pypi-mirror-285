import os
#considering the above classes JGTML240615Config and JGTML240615Request, abstract the business component logics 

class JGTML240615Config:
  def __init__(self):
    self.use_env = os.getenv("JGTENV", "0")
    self.force_regenerate_mxfiles = self._env_bool("force_regenerate_mxfiles", False)
    self.mfi_flag = True
    self.balligator_flag = True
    self.talligator_flag = True
    self.regenerate_cds = self._env_bool("regenerate_cds", False)
    self.use_fresh = self._env_bool("use_fresh", True)
    self.quiet = self._env_bool("quiet", False)
    self.output_path_default = "/b/Dropbox/jgt"
    self.output_subdir = "drop"
    self.result_file_basename_default = "jgtml_obsds_240515_SIGNALS.result"
    self.jgtdroot = os.getenv("jgtdroot", self.output_path_default)

  def _env_bool(self, env_var, default):
    return os.getenv(env_var, str(default)).lower() in ["true", "1", "yes"]

class JGTML240615Request:
  def __init__(self, instrument='SPX500', timeframe='D1', bs='S'):
    self.instrument = os.getenv("i", instrument)
    self.timeframe = os.getenv("t", timeframe)
    self.bs = os.getenv("bs", bs)  # Buy/Sell flag

  @staticmethod
  def from_env():
    return JGTML240615Request(
      instrument=os.getenv("i", 'SPX500'),
      timeframe=os.getenv("t", 'D1'),
      bs=os.getenv("bs", 'S')
    )
    
    