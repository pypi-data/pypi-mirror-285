
import pandas as pd
from jgtpy import JGTCDSSvc as svc
from jgtutils import jgtpov as jpov

from mlutils import drop_columns_if_exists, dropna_volume_in_dataframe
from mlconstants import TTF_NOT_NEEDED_COLUMNS_LIST, default_columns_to_get_from_higher_tf,TTF_DTYPE_DEFINITION

import os
from mlutils import get_basedir,get_outfile_fullpath
from mldatahelper import get_ttf_outfile_fullpath,write_patternname_columns_list,read_patternname_columns_list


def make_htf_created_columns_array(workset,t,columns_list_from_higher_tf=None):
    if columns_list_from_higher_tf is None:
      columns_list_from_higher_tf = default_columns_to_get_from_higher_tf
    created_columns=[]
    for c in columns_list_from_higher_tf:
      for k in workset:
        if not c in created_columns: 
          created_columns.append(c)
        new_col_name = c+"_"+k
        if k != t:
          if not new_col_name in created_columns: 
            created_columns.append(new_col_name)
    return created_columns

def read_ttf_csv(i, t, use_full=False,force_refresh=False,midfix="ttf")->pd.DataFrame:
    if force_refresh:
        return create_ttf_csv(i, t, use_full,use_fresh=True,force_read=False)
    output_filename=get_ttf_outfile_fullpath(i,t,use_full,midfix=midfix)
    if not os.path.exists(output_filename):
        print("   Non existent, Creating TTF: ", output_filename)
        print("WARN::#@STCIssue In case of Specific pattern, it wont be able to read it, we could extend get data defining the PATTERNNAME and the COLUMNS it contains, therefore it could create the TTF patterns and read it.... ")
        return create_ttf_csv(i, t, use_full,force_read=True)
    else:
        print("   Read TTF: ", output_filename)
        
        return pd.read_csv(output_filename, index_col=0,dtype=TTF_DTYPE_DEFINITION)
  
def read_ttf_csv_selection(i, t, use_full=False,suffix="_sel",midfix="ttf"):
    output_filename_sel=get_ttf_outfile_fullpath(i,t,use_full,suffix=suffix,midfix=midfix)
    return pd.read_csv(output_filename_sel, index_col=0)

def _upgrade_ttf_depending_data(i, t, use_full=False, use_fresh=True, quotescount=-1,dropna=True,quiet=True):
  try:
    if not quiet:
      print("Upgrading/Refreshing the Depending Data before creating the TTF")
    svc.get_higher_cdf_datasets(i, t, use_full=use_full, use_fresh=use_fresh, quotescount=quotescount, quiet=True, force_read=False)
  except:
    print("Error in _upgrade_ttf_depending_data")
    raise Exception("Error in _upgrade_ttf_depending_data")


def create_ttf_csv(i, t, use_full=False, use_fresh=True, quotescount=-1,force_read=False,dropna=True,quiet=True,columns_list_from_higher_tf=None,not_needed_columns=None,dropna_volume=True,midfix="ttf",also_output_sel_csv=False)->pd.DataFrame:
  if not_needed_columns is None:
    not_needed_columns = TTF_NOT_NEEDED_COLUMNS_LIST
  if columns_list_from_higher_tf is None:
    columns_list_from_higher_tf = default_columns_to_get_from_higher_tf
  #print("Columns List from Higher TF:",columns_list_from_higher_tf)
  
  povs = jpov.get_higher_tf_array(t)
  if not quiet:
    print(f"Povs:",povs)
  
  if use_fresh:
    print("create_ttf_csv::Calling ::_upgrade_ttf_depending_data")
    _upgrade_ttf_depending_data(i, t, use_full=use_full, use_fresh=True,quiet=quiet)
    use_fresh=False
    force_read=True #@STCissue Unclear if that force read the CDS or the TTF (ITS the CDS)
    
  workset = svc.get_higher_cdf_datasets(i, t, use_full=use_full, use_fresh=use_fresh, quotescount=quotescount, quiet=True, force_read=force_read)
  #Get the dataframe for the current timeframe
  df:pd.DataFrame=workset[t]
  
  created_columns = make_htf_created_columns_array(workset, t, columns_list_from_higher_tf)
  
  write_patternname_columns_list(i,t,use_full,created_columns,midfix=midfix)
  
  if dropna_volume:
    df=dropna_volume_in_dataframe(df)
  
  # for key_tf, v in workset.items():
  #   if key_tf != t:
  #     # Ensure 'v' is sorted by index to use merge_asof
  #     #v_sorted = v.sort_index()
  #     for col in columns_list_from_higher_tf:
  #       new_col_name = f"{col}_{key_tf}"
        
  #       # Prepare a temporary DataFrame with just the index and the column of interest
  #       temp_df = pd.DataFrame(v[col])
  #       #temp_df.reset_index(inplace=True)
        
  #       # Use merge_asof to merge 'df' with 'temp_df' based on the closest index values
  #       merged_df = pd.merge_asof(df, temp_df, on='index', direction='backward')
        
  #       # Set the new column in 'df' with the merged values
  #       df[new_col_name] = merged_df[col]
  # count=0
  # for key_tf, v in workset.items():
  #   if key_tf!=t:
      
  #     for col in columns_list_from_higher_tf:
      
  #       new_col_name:str = col+"_"+key_tf
  #       df[new_col_name]=None

  #       for ii, row in df.iterrows():
  #         count+=1
  #         #get the date of the current row (the index)
  #         date = ii
  #         #print(k)
  #         data:pd.DataFrame = v[v.index <= date]
  #         if not data.empty:
  #           data = data.iloc[-1]
  #           #print(count,"::ii:",ii," ::data:",data[col]," ::new_col_name:",new_col_name)
  #           df.at[ii,new_col_name]=data[col]
  # Pre-allocate new columns with None (or np.nan for numerical data)
  for col in columns_list_from_higher_tf:
    for key_tf in workset:
      if key_tf != t:
        new_col_name = f"{col}_{key_tf}"
        df[new_col_name] = None
  count = 0
  for key_tf, v in workset.items():
    if key_tf != t:
      v_sorted = v.sort_index()  # Ensure data is sorted for efficient access
      for col in columns_list_from_higher_tf:
        new_col_name = f"{col}_{key_tf}"
        for ii in df.index:
          count += 1
          date = ii
          # Limit the data to those less than or equal to the current date
          data = v_sorted[v_sorted.index <= date]
          if not data.empty:
              latest_data = data.iloc[-1]  # Get the latest data point
              df.at[ii, new_col_name] = latest_data[col]

  print("Total count of operations:",count)
  columns_we_want_to_keep_to_view=created_columns
  
  if also_output_sel_csv:
    ttf_sel=df[columns_we_want_to_keep_to_view].copy()
  
  #save basedir is $JGTPY_DATA/ttf is not use_full, if use_full save basedir is $JGTPY_DATA_FULL/ttf
  
  output_filename=get_ttf_outfile_fullpath(i,t,use_full,midfix=midfix)
  if also_output_sel_csv:
    output_filename_sel=get_ttf_outfile_fullpath(i,t,use_full,suffix="_sel",midfix=midfix)
  
  if dropna:
    df.dropna(inplace=True)
  
  drop_columns_if_exists(df,not_needed_columns)
  df.to_csv(output_filename, index=True)
  
  if also_output_sel_csv:
    ttf_sel.to_csv(output_filename_sel, index=True)
    print(f"    TTF Output sel :'{output_filename_sel}'")
  print(f"    TTF Output full:'{output_filename}'")
  return df
