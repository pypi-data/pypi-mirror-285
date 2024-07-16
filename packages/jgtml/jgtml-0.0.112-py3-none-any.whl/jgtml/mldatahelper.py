
"""
Here we would have common data functions such as : write_patternname_columns_list and read_patternname_columns_list

Therefore: 
 * ttfcli would  
"""
import pandas as pd
from mlutils import get_basedir,get_outfile_fullpath
from mlconstants import TTF_NOT_NEEDED_COLUMNS_LIST, default_columns_to_get_from_higher_tf,TTF_DTYPE_DEFINITION

#ttf


def get_ttf_outfile_fullpath(i,t,use_full=True,suffix="",ns="ttf",pn="ttf"):
  return get_outfile_fullpath(i,t,use_full,ns,pn=pn,suffix=suffix)


def write_patternname_columns_list(i,t,use_full=True,columns_list_from_higher_tf=None,pn="ttf",ns="ttf",suffix="_columns"):
  if columns_list_from_higher_tf is None:
    columns_list_from_higher_tf = default_columns_to_get_from_higher_tf
  output_filename=get_ttf_outfile_fullpath(i,t,use_full,suffix=suffix,pn=pn,ns=ns)
  with open(output_filename, 'w') as f:
    for item in columns_list_from_higher_tf:
      f.write("%s\n" % item)
  print(f"    Pattern:{pn} Output columns :'{output_filename}'")
  return output_filename

def read_patternname_columns_list(i,t,use_full=True,pn="ttf",ns="ttf",suffix="_columns")->list:
  output_filename=get_ttf_outfile_fullpath(i,t,use_full,suffix=suffix,pn=pn,ns=ns)
  with open(output_filename, 'r') as f:
    columns_list_from_higher_tf = f.readlines()
  columns_list_from_higher_tf = [x.strip() for x in columns_list_from_higher_tf]
  return columns_list_from_higher_tf

def create_filebase_from_patternname(i,t,pn="ttf")->str:
  ifn=i.replace("/","-")
  output_filename = f"{ifn}_{t}_{pn}"
  return output_filename.replace("__","_")

def create_filensbase_from_patternname(i,t,pn="ttf",ns="ttf")->str:
  filebase=create_filebase_from_patternname(i,t,pn)
  return f"{ns}/{filebase}"


#@STCIssue Future Generic we would use for other patterns (ex.  targets/mx)
def read_pattern_raw(i, t,pn,ns, use_full=True)->pd.DataFrame:

  outfile_fullpath=get_outfile_fullpath(i,t,use_full,ns,pn=pn)
  df=pd.read_csv(outfile_fullpath, index_col=0,dtype=TTF_DTYPE_DEFINITION)
  return df


def read_ttf_pattern_raw(i, t, use_full=True,pn="ttf",ns="ttf")->pd.DataFrame:
  ttf_outfile_fullpath=get_ttf_outfile_fullpath(i,t,pn=pn,ns=ns,use_full=use_full)
  df=pd.read_csv(ttf_outfile_fullpath, index_col=0,dtype=TTF_DTYPE_DEFINITION)
  return df
  

def read_ttf_feature_columns_only_from_pattern(i, t, use_full=True,pn="ttf",ns="ttf"):
  df=read_ttf_pattern_raw(i, t, use_full=use_full,pn=pn,ns=ns)
  pattern_columns_list:list=read_patternname_columns_list(i,t,pn=pn,ns=ns)
  #keep only the columns from the list
  df=df[pattern_columns_list]
  return df


MLF_NS = "mlf"

def write_mlf_pattern_lagging_columns_list(i, t, use_full=True, pn="ttf", lagging_columns=None):
  write_patternname_columns_list(i,t,use_full,lagging_columns,pn=pn,ns=MLF_NS)

def read_mlf_pattern_lagging_columns_list(i, t, use_full=True, pn="ttf"):
  lagging_columns=read_patternname_columns_list(i,t,use_full,pn=pn,ns=MLF_NS)
  return lagging_columns

def read_mlf_pattern_raw(i, t, use_full=True,pn="ttf"):
  df=read_ttf_pattern_raw(i, t, use_full=use_full,pn=pn,ns=MLF_NS)
  return df


def read_mlf_for_pattern(i, t, use_full=True,pn="ttf"):
  df=read_ttf_pattern_raw(i, t, use_full=use_full,pn=pn,ns=MLF_NS)
  return df

def read_mlf_feature_columns_only_from_pattern(i, t, use_full=True,pn="ttf"):
  df=read_mlf_for_pattern(i, t, use_full=use_full,pn=pn)
  lagging_columns_list:list=read_mlf_pattern_lagging_columns_list(i,t,pn=pn,use_full=use_full)
  #keep only the columns from the list
  df=df[lagging_columns_list]
  return df
