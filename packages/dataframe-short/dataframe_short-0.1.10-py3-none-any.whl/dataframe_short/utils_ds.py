# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 10:53:08 2023

@author: Heng2020
"""

import pandas as pd
import numpy as np
from itertools import product
from collections import defaultdict
import sys
from typing import *
import py_string_tool as pst
################################################## Immigrated Jun 15 2024 #################################################
import dataframe_short.move_column as mc
import pandas as pd
from typing import Union, Dict

import pandas as pd
from typing import Dict, List


def display_nice_df(df, display_height=300):

    """
    main reason I create this is to display the row with the scrolling
    display_height: is the height of diplayed cells
    """
    from IPython.display import display, HTML
    if isinstance(df, pd.Series):
        df_in = df.to_frame()
        html = f"""
        <div style="max-height: {display_height}px; overflow-y: scroll;">
            {df_in.to_html()}
        </div>
        """
        display(HTML(html))
    else:
        html = f"""
        <div style="max-height: {display_height}px; overflow-y: scroll;">
            {df.to_html()}
        </div>
        """
        display(HTML(html))


def dtype(df: pd.DataFrame, return_as_dict: bool = False) -> Union[pd.DataFrame, Dict[str, str]]:
    # plan to have no test case

    """
    Get the data types of columns in a DataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        The input DataFrame.
    return_as_dict : bool, default False
        If True, return the result as a dictionary.

    Returns
    -------
    pandas.DataFrame or dict
        A DataFrame with columns ['column', 'dtype'] if return_as_dict is False.
        A dictionary with column names as keys and dtypes as values if return_as_dict is True.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c'], 'C': [1.1, 2.2, 3.3]})
    >>> dtype(df)
       column   dtype
    0      A    int64
    1      B   object
    2      C  float64

    >>> dtype(df, return_as_dict=True)
    {'A': 'int64', 'B': 'object', 'C': 'float64'}
    """
    result = pd.DataFrame({
        'column': df.columns,
        'dtype': df.dtypes.astype(str)
    })
    
    if return_as_dict:
        return dict(zip(result['column'], result['dtype']))
    else:
        return result

def value_counts(df:pd.DataFrame,dropna:bool = False) -> pd.DataFrame:
    """
    {'count','count_prop'}
    """
    df_count = pd.concat([df.value_counts(dropna= dropna),df.value_counts(normalize=True,dropna=dropna)], axis = 1)
    df_count.columns = ['count','count_prop']
    return df_count

def percentile_values(pd_series, percentile_from=0.75, percentile_to=1, increment = 0.01) -> pd.DataFrame:
    import pandas as pd
    import numpy as np
    # medium tested via pd. 1.1.3
    """
    Calculate percentiles for a given Pandas Series.

    Args:
        pd_series (pd.Series): The input Pandas Series.
        percentile_from (float, optional): Starting percentile (default is 0.75).
        percentile_to (float, optional): Ending percentile(inclusive) (default is 1.0).

    Returns:
        pd.DataFrame: A DataFrame with columns 'percentile' and 'value'.
    """
    percentile_list = np.arange(percentile_from,percentile_to + increment ,increment)      
    # Calculate the specified percentiles
    percentiles = pd_series.quantile(percentile_list)

    # Create a DataFrame with the results
    result_df = pd.DataFrame({
        'percentile': percentile_list,
        'value': percentiles.values
    })

    return result_df

def constrict_levels(df, allowed_levels):
    # from Claude
    for col, levels_dict in allowed_levels.items():
        level_set = set(levels_dict['levels'])
        replaced_by = levels_dict.get('replaced_by')
        
        if replaced_by is None:
            invalid_rows = df.loc[~df[col].isin(level_set)]
            if not invalid_rows.empty:
                print(f"Removing rows for column {col} with invalid levels:")
                for idx, row in invalid_rows.iterrows():
                    print(f"Row Index: {idx}, Invalid Level: {row[col]}")
                df.drop(invalid_rows.index, inplace=True)
        else:
            df.loc[~df[col].isin(level_set), col] = replaced_by


def mixed_type_cols(df):
    mixed_columns_list = []
    for column in df.columns:
        dtype = pd.api.types.infer_dtype(df[column])
        if 'mix' in dtype:
            mixed_columns_list.append(column)
    return mixed_columns_list

#-------------------------------------------- Immigrated Jun 15 2024 ------------------------------------------------------------------------------
def rename_col_by_index(df, index, new_name, inplace=True):
    """
    medium tested
    Rename a column in a DataFrame based on its index (this can handle repeated name)

    Parameters:
    df (pd.DataFrame): The DataFrame whose column you want to rename.
    index (int): The index of the column to rename.
    new_name (str): The new name for the column.
    inplace (bool): If True, modifies the DataFrame in place (default is True).

    Returns:
    pd.DataFrame or None: The DataFrame with the renamed column if inplace is False, otherwise None.
    """
    # Ensure the index is within the valid range
    if not 0 <= index < len(df.columns):
        raise IndexError("Column index out of range.")
    
    # Copy df if not inplace
    if not inplace:
        df = df.copy()
    
    # Set new column name
    df.columns = df.columns[:index].tolist() + [new_name] + df.columns[index+1:].tolist()
    
    if not inplace:
        return df


def index_aligned_append(df1, df2, col_name):
    # it works: medium tested
    import pandas as pd
    """
    Appends rows from df2 to df1 based on a specific column (col_name).
    And readjust the index in each episode via (col_name)
    
    Inspired by BigBang theory script
    
    The objective of this function is to align the index so that every starting episode
    should start with index 1 of Portuguese and English
    
    Parameters:
    - df1: DataFrame, the main DataFrame to which df2 will be appended
    - df2: DataFrame, the DataFrame to append to df1
    - col_name: str, the name of the column based on which the append will be done
    
    Returns:
    - merged_df: DataFrame, the merged DataFrame
    """
    # Find the starting indices for each unique value in the col_name column in both DataFrames
    df1_start_indices = df1.groupby(col_name).head(1).index.tolist()
    df2_start_indices = df2.groupby(col_name).head(1).index.tolist()
    
    # Initialize an empty DataFrame to store the merged data
    merged_df = pd.DataFrame()

    # Loop through the unique values to merge df1 and df2 based on the col_name column
    for df1_idx, df2_idx in zip(df1_start_indices, df2_start_indices):
        df1_value = df1.loc[df1_idx, col_name]
        df2_value = df2.loc[df2_idx, col_name]
        
        if df1_value == df2_value:
            # Extract df1 rows for this value
            if df1_idx == df1_start_indices[-1]:
                df1_rows = df1.loc[df1_idx:]
            else:
                next_df1_idx = df1_start_indices[df1_start_indices.index(df1_idx) + 1]
                df1_rows = df1.loc[df1_idx:next_df1_idx - 1]
            
            # Extract df2 rows for this value
            if df2_idx == df2_start_indices[-1]:
                df2_rows = df2.loc[df2_idx:]
            else:
                next_df2_idx = df2_start_indices[df2_start_indices.index(df2_idx) + 1]
                df2_rows = df2.loc[df2_idx:next_df2_idx - 1]
            
            df1_rows = df1_rows.reset_index(drop = True)
            df2_rows = df2_rows.reset_index(drop = True)
            # Append df2 rows to df1 rows for this value
            merged_rows = pd.concat([df1_rows, df2_rows],axis=1)
            
            # Append the merged rows to the final DataFrame
            merged_df = pd.concat([merged_df, merged_rows])

    return merged_df


def combine_files_to_df(
        folder_path,
        extract_pattern = None,
        filename_col_name = 'filename',

        ):
    import pandas as pd
    import re
    import os

    import sys
    import os_toolkit as ost

    
    if not os.path.isdir(folder_path):
        print("This is not the correct folder path")
        return False


    path_list = ost.get_full_filename(folder_path,extension=[".xlsx",".csv"])
    out_df = pd.DataFrame()
    
    for i, curr_path in enumerate(path_list):
        curr_df = pd.read_excel(curr_path)
        filename = ost.extract_filename(curr_path,with_extension=False)

        if extract_pattern is None:
            name_filter = filename
        else:
            name_filter = re.search(extract_pattern, filename).group()
        # curr_df.columns.values[0] = 'NoSentence'
        curr_df[filename_col_name] = name_filter
        mc.to_first_col(curr_df, filename_col_name)
        out_df = pd.concat([out_df,curr_df])

    return out_df



def xlookup(df_main, df_lookup, lookup_col, key_col, return_col, inplace=True):
    # v02 => raise Exception
    """
    Perform an XLOOKUP-like operation on DataFrames.

    Parameters:
        df_main (pd.DataFrame): Main DataFrame.
        df_lookup (pd.DataFrame): Lookup DataFrame.
        lookup_col (str or list[str]): Column(s) in df_main to use for lookup.
        key_col (str): Column in df_lookup to match with lookup_col.
        return_col (str or list[str]): Column(s) in df_lookup to return.
        inplace (bool, optional): If True, modifies df_main in-place. Otherwise, returns a new DataFrame. Default is True.

    Returns:
        pd.DataFrame: Modified df_main if inplace=True, otherwise a new DataFrame.
    """
    # Ensure lookup_col is a list
    import pandas as pd
    if not isinstance(lookup_col, list):
        lookup_col = [lookup_col]

    # Merge DataFrames
    merged_df = pd.merge(df_main, df_lookup, left_on=lookup_col, right_on=key_col, how='left')
    
    df_main_cols = list(df_main.columns)
    # Keep only the specified return columns
    if isinstance(return_col, str):
        return_col = [return_col]  # Convert single column name to list

    if inplace:
        for col in return_col:
            if df_main.shape[0] != merged_df.shape[0]:
                raise Exception(f"Please drop duplicate in df_main first. The original n_rows of df_main is {df_main.shape[0]}, but became {merged_df.shape[0]} after merging ")
            else:
                df_main[col] = merged_df[col]
        return df_main
    else:
        return merged_df[return_col + df_main_cols] 

def sum_all(df,value_col,exclude = None, inplace = False, dropna = False):
    """ This will sum the value_col grouped by other_column """

    test01 = df.groupby(['aPol_CalYear'])[['exposure','claim_count','total_paid']].sum()
    if exclude is None:
        exclude = []

    other_column = list(df.columns.difference(value_col))
    groupby_col = [x for x in other_column if x not in exclude ]
    df_drop = df[groupby_col + value_col]
    df_agg = df_drop.groupby(groupby_col, dropna = dropna)[value_col].sum().reset_index()


    test02 = df_agg.groupby(['aPol_CalYear'], dropna = False)[['exposure','claim_count','total_paid']].sum()
    if inplace: 
        df = df_agg
        return df
    else:
        return df_agg

def count_freq(df, groupby_col, value_col):
    """
    Count the frequency of values in a column and return a dataframe.

    This function creates dummy variables for the values in the value_col
    column of the input dataframe df, and then groups by the groupby_col
    column and sums the dummy variables. The result is a dataframe with
    the groupby_col as the index and the n_ prefixed value_col values as
    the columns.

    Parameters
    ----------
    df : DataFrame
        The input dataframe.
    groupby_col : str
        The name of the column to group by.
    value_col : str
        The name of the column to count the frequency of values.

    Returns
    -------
    DataFrame
        The output dataframe with the frequency counts.

    Examples
    --------
    >>> df = pd.DataFrame({
            "Policy No": ["A123", "A123", "B456", "B456", "C789"],
            "Transaction Type": ["New Policy", "Cancel", "Endorsement", "Endorsement", "Renewal"]
        })
    >>> pd_count_freq(df, "Policy No", "Transaction Type")
           n_Cancel  n_Endorsement  n_New Policy  n_Renewal
    Policy No
    A123          1              0             1          0
    B456          0              2             0          0
    C789          0              0             0          1 
    """

    # not tested yet
    # Create dummy variables for the value column
    df_in = df[[groupby_col,value_col]]
    
    df_dummies = pd.get_dummies(df_in[value_col])
    
    # Concatenate the dummy variables with the original dataframe
    df_in = pd.concat([df_in, df_dummies], axis=1)
    
    # Group by the groupby column and sum the dummy variables
    df_result = df_in.groupby(groupby_col).sum()
    
    # Rename the columns with n_ prefix
    df_result = df_result.rename(columns=lambda x: "n_" + x)
    df_result = df_result.reset_index()
    
    
    # Return the output dataframe
    return df_result



def write_excel(list_dfs, excel_name, sheet_name = None):
    # little tested
    # from openpyxl.writer.excel import ExcelWriter
    writer = pd.ExcelWriter(excel_name, engine='openpyxl')
    for n, df in enumerate(list_dfs):
        if isinstance(sheet_name,list):
            df.to_excel(writer, sheet_name = sheet_name[n])
        else:
            df.to_excel(writer,'sheet%s' % n)
    writer.save()

def common_col(df1,df2):
    common_col = [x for x in list(df1.columns) if x in list(df2.columns) ]
    return common_col

def get_col(df,start_with = "",end_with ="", contain = "", case_sensitive=False, print_col=True):

# this is from print_col 
# !!! TODO start_with, end_with, contain is list
# add 2 logic options

    cols = list(df.columns)
    
    if start_with != "":
        if case_sensitive:
            cols = [x for x in cols if x.startswith(start_with) ]
        else:
            cols = [x for x in cols if x.lower().startswith(start_with.lower()) ]
        
    
    if end_with != "":
        if case_sensitive:
            cols = [x for x in cols if x.endswith(end_with) ]
        else:
            cols = [x for x in cols if x.lower().endswith(end_with.lower()) ]
    
    if contain != "":
        if case_sensitive:
            cols = [x for x in cols if contain in x]
        else:
            cols = [x for x in cols if contain.lower() in x.lower()]
    
    cols.sort()

    if print_col:
        for col in cols:
            print(col)

    return cols


def merge2(left, 
             right, 
             how='inner', 
             on=None, 
             left_on=None, 
             right_on=None,
             keep = "left"):
    
    def func_keep(val1,val2,keep ="left"):
        if pd.isna(val1):
            if pd.isna(val2):
                return np.nan
            else: 
                return val2
        else:
            if pd.isna(val2):
                if val1 == "New":
                    # print("")
                    pass
                return val1
            else: 
                # both have values
                if keep == "left":
                    return val1
                else:
                    return val2

#keep this because logic is easier to read
    # pd_get_col
    
    if (on is None) and (on is None) and (on is None):
        # todo next 
        # this will be the auto merge functionality given that left&right has the same column name
        pass
    
    df_merged = pd.merge(left,right,how,on,left_on,right_on)
    # if keep == "left":
    #     df_merged = pd.merge(left,right,how,on,left_on,right_on,suffixes=('', '_remove'))
    # elif keep == "right":
    #     df_merged = pd.merge(left,right,how,on,left_on,right_on,suffixes=('_remove', ''))
    
    x_col = get_col(df_merged,end_with = "_x",print_col=False)
    
    xy_col = list(zip(get_col(df_merged,end_with = "_x",print_col=False),get_col(df_merged,end_with = "_y",print_col=False) ))

    for x_col, y_col in xy_col:
        col_name = x_col.split("_")[0]
        df_merged[col_name] = df_merged.apply(lambda row: func_keep(row[x_col],row[y_col],keep), axis = 1)
        
        # df_merged = df_merged.sort_index(axis=1)
        
        df_merged.drop(x_col,inplace=True, axis=1)
        df_merged.drop(y_col,inplace=True, axis=1)


        
    # df_merged.drop([i for i in df_merged.columns if 'remove' in i],
    #            axis=1, inplace=True)
    return df_merged


def merge(left, 
             right, 
             how='inner', 
             on=None, 
             left_on=None, 
             right_on=None,
             keep = "left"):

    # use this instead of pd_merge2
    # this function is much faster bc of vectorizated
    """ 

    will not work properly if name of columns contain _x
    need more sophisticated logic

    """
    # vectorized version
    
    if (on is None) and (on is None) and (on is None):
        # todo next 
        # this will be the auto merge functionality given that left&right has the same column name
        pass
    
    df_merged = pd.merge(left,right,how,on,left_on,right_on)
    # if keep == "left":
    #     df_merged = pd.merge(left,right,how,on,left_on,right_on,suffixes=('', '_remove'))
    # elif keep == "right":
    #     df_merged = pd.merge(left,right,how,on,left_on,right_on,suffixes=('_remove', ''))
    
    x_col_list = get_col(df_merged,end_with = "_x",print_col=False)
    y_col_list = get_col(df_merged,end_with = "_y",print_col=False)
    
    xy_col_list = x_col_list + y_col_list
    
    xy_col = list(zip(get_col(df_merged,end_with = "_x",print_col=False),get_col(df_merged,end_with = "_y",print_col=False) ))

    for x_col, y_col in xy_col:
        col_name = x_col.split("_x")[0]
        
        if col_name == "Effective Date":
            # for debug
            print("")
        
        conditions = [
            df_merged[x_col].isna() & df_merged[y_col].isna(), # both are null
            df_merged[x_col].isna() & ~df_merged[y_col].isna(), # only x is null
            ~df_merged[x_col].isna() & df_merged[y_col].isna(), # only y is null
            ~df_merged[x_col].isna() & ~df_merged[y_col].isna() & (keep == 'left'), # both have values and keep left
            ~df_merged[x_col].isna() & ~df_merged[y_col].isna() & (keep == 'right') # both have values and keep right
        ]
        
        choices = [
            np.nan, # return nan if both are null
            df_merged[y_col], # return y if only x is null
            df_merged[x_col], # return x if only y is null
            df_merged[x_col], # return x if both have values and keep left
            df_merged[y_col] # return y if both have values and keep right
        ]
        df_merged[col_name] = np.select(conditions, choices)
        
        # df_merged = df_merged.sort_index(axis=1)
        
        # df_merged.drop(x_col,inplace=True, axis=1)
        # df_merged.drop(y_col,inplace=True, axis=1)
    
    df_merged.drop(columns = xy_col_list, inplace=True)


        
    # df_merged.drop([i for i in df_merged.columns if 'remove' in i],
    #            axis=1, inplace=True)
    return df_merged




def check_col_exist(df:Union[pd.DataFrame], columns:List[str]) -> List[Tuple[str, bool]]:

    """
    check if the columns in columns are in df.columns
    """

    # Create an empty list to store the tuples
    result = []
    
    # Loop through the columns list
    for col in columns:
        # Check if the column is in df.columns using the isin() method
        # This will return a boolean Series with one element
        # Use the any() method to get the boolean value of that element
        is_in = df.columns.isin([col]).any()
        
        # Append a tuple of the column name and the boolean value to the result list
        result.append((col, is_in))
    
    # Return the result list
    return result



def unique_element(df, include=None, 
               exclude=None, 
               sort_by='n_elements',
               ascending=True,
               list_ascending = True
               ):
    # little tested
    """
    This function returns a dataframe with information about the categorical columns of another dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe to analyze.
    include : list, optional
        A list of column names to include in the analysis. If None, all columns are included. Default is None.
    exclude : list, optional
        A list of column names to exclude from the analysis. If None, no columns are excluded. Default is None.
    cut_off : int, optional
        The maximum number of unique values in a column to be considered as categorical. Default is 15.
    sort_by : str, optional
        The column name to sort the output dataframe by. It can be either 'col_name' or 'n_elements'. Default is 'n_elements'.

    Returns
    -------
    out_df : pd.DataFrame
        The output dataframe with three columns: 'col_name', 'n_elements', and 'elements'.
        'col_name' is the name of the categorical column.
        'n_elements' is the number of unique values in the column.
        'elements' is a list of the unique values in the column.
    """
    # Check the input arguments
    if include is not None and exclude is not None:
        raise ValueError("Cannot specify both include and exclude")
    if exclude is not None:
        df_ = df.drop(exclude, axis=1)
        
    else:
        if include is not None:
            df_ = df[include]
        else:
            # both include and exclude is None
            df_ = df.copy()
    if sort_by not in ['col_name', 'n_elements']:
        raise ValueError("Invalid value for sort_by")

    # Initialize the output dataframe
    out_df = pd.DataFrame(columns=['col_name', 'n_elements', 'elements'])

    # Loop over the columns of the input dataframe
    for col in df_.columns:
       
        curr_type = df_[col].dtype.name
        try:
            n_elements = df_[col].nunique()
            # ! TOFIX
            # sort might give an error at col: 'fClm_LargeLossIndicator'
            # elements = sorted(list(df_[col].unique()),reverse = not list_ascending )
            
            elements = list(df_[col].unique())
            # Append the information to the output dataframe
            df_temp = pd.DataFrame({'col_name': [col], 'n_elements': [n_elements]})
            
            last_row = out_df.shape[0]
            
            out_df = pd.concat([out_df, df_temp], axis=0, ignore_index=True)
            
            out_df.at[last_row,'elements'] = elements
        except:
            print(f"'{col}' has an error ")
        
        
    # Sort the output dataframe by the specified column
    out_df = out_df.sort_values(by=sort_by, ascending=False)
    
    out_df = out_df.reset_index(drop=True)

    # Return the output dataframe
    return out_df





def cat_report(df, include=None, 
               exclude=None, 
               cut_off:int =1000, 
               sort_by='n_elements',
               ascending=True,
               list_ascending = True,
               exclude_num_cols = True,
               ):
    # little tested
    # v02 => change .append to .concat

    # Added feature exclude_num_cols
    """
    This function returns a dataframe with information about the categorical columns of another dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe to analyze.
    include : list, optional
        A list of column names to include in the analysis. If None, all columns are included. Default is None.
    exclude : list, optional
        A list of column names to exclude from the analysis. If None, no columns are excluded. Default is None.
    cut_off : int, optional
        The maximum number of unique values in a column to be considered as categorical. Default is 15.
    sort_by : str, optional
        The column name to sort the output dataframe by. It can be either 'col_name' or 'n_elements'. Default is 'n_elements'.
    exclude_num_cols: bool, optional
        If False, I would also include numerical columns 
    Returns
    -------
    out_df : pd.DataFrame
        The output dataframe with three columns: 'col_name', 'n_elements', and 'elements'.
        'col_name' is the name of the categorical column.
        'n_elements' is the number of unique values in the column.
        'elements' is a list of the unique values in the column.
    """
    # Check the input arguments
    if include is not None and exclude is not None:
        raise ValueError("Cannot specify both include and exclude")
        
    if exclude is not None:
        df_ = df.drop(exclude, axis=1)
        
    else:
        if include is not None:
            df_ = df[include]
        else:
            # both include and exclude is None
            df_ = df.copy()
    if sort_by not in ['col_name', 'n_elements']:
        raise ValueError("Invalid value for sort_by")

    # Initialize the output dataframe
    out_df = pd.DataFrame(columns=['col_name', 'n_elements', 'elements'])

    # Loop over the columns of the input dataframe
    for col in df_.columns:
        # Check if the column is categorical
        curr_type = df_[col].dtype.name

        
        if exclude_num_cols:
            if df_[col].dtype.name in ['object', 'category'] and df[col].nunique() <= cut_off:
                # Get the number and list of unique values
                n_elements = df_[col].nunique()
                elements = sorted(list(df_[col].unique()),reverse = not list_ascending )
                # Append the information to the output dataframe
                # out_df = out_df.append({'col_name': col, 'n_elements': n_elements, 'elements': elements}, ignore_index=True)
                out_df = pd.concat([out_df, pd.DataFrame({'col_name': [col], 'n_elements': [n_elements], 'elements': [elements]})], ignore_index=True)
        
        # include numerical columns
        else:
            if df[col].nunique() <= cut_off:
                n_elements = df_[col].nunique()
                elements = sorted(list(df_[col].unique()),reverse = not list_ascending )
                # Append the information to the output dataframe
                # out_df = out_df.append({'col_name': col, 'n_elements': n_elements, 'elements': elements}, ignore_index=True)
                out_df = pd.concat([out_df, pd.DataFrame({'col_name': [col], 'n_elements': [n_elements], 'elements': [elements]})], ignore_index=True)



    # Sort the output dataframe by the specified column
    out_df = out_df.sort_values(by=sort_by, ascending=False)
    
    out_df = out_df.reset_index(drop=True)

    # Return the output dataframe
    return out_df

def reorder_dict(df,col,begin_with = None,end_with = None):
    
    """
    This function returns a dataframe with information about the categorical columns of another dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe to analyze.
    col : list
        A list of column names to include in the analysis. If None, all columns are included. Default is None.
    begin_with : list
        A list of levels to that is string put it first. Default is None.
    end_with : list
        A list of levels to that is string put it last. Default is None.

    Returns
    -------
    out_dict : dictionary
    """
    import python_wizard as pw
    df_temp = df[col]
    order_df = unique_element(df_temp)
    order_df['element_sorted'] = order_df['elements'].apply(lambda x: pw.custom_sort(x,begin_with,end_with))
    out_dict = dict(zip(order_df['col_name'], order_df['element_sorted']))
    return out_dict

def reorder(df,col,begin_with = None,end_with = None):
    mapping_dict = reorder_dict(df,col,begin_with,end_with)
    
    for col, new_order in mapping_dict.items():
        df[col] = df[col].cat.reorder_categories(new_order)
    
    return df


def print_shape(df):
    # originally from lib01
    # but upgraded
    # medium tested
    import pandas as pd
    if isinstance(df, pd.DataFrame):
        print("The shape ({:,} * {:,})".format(*df.shape))
    # to support when df.shape is an input
    elif isinstance(df, tuple):
        print("The shape ({:,} * {:,})".format(*df))

def duplicate_col(df):
    # Get the column names of the DataFrame
    col_names = df.columns
    
    # Create an empty list to store the duplicated column names
    dup_cols = []
    
    # Loop through the column names and check if there are duplicates
    for i in range(len(col_names)):
        # Get the current column name
        col = col_names[i]
        
        # Check if the current column name is already in the dup_cols list
        if col in dup_cols:
            # If yes, skip it and continue to the next column name
            continue
        
        # Check if the current column name appears more than once in the col_names list
        if col_names.tolist().count(col) > 1:
            # If yes, add it to the dup_cols list
            dup_cols.append(col)
    
    # Check if the dup_cols list is empty or not
    if len(dup_cols) == 0:
        # If empty, print a message and return False
        print("There's no duplicated columns")
        return False
    else:
        # If not empty, return the dup_cols list
        return dup_cols



# -------------------------------------------------- imported from work Mar 17, 2024 ------------------------------------------------------






def value_index(df, value):
    """
    Searches for a specific value in the DataFrame using a vectorized approach
    and returns a new DataFrame with the row and column indices where the value
    is found.

    Parameters:
    - df: The input pandas DataFrame to search.
    - value: The value to search for in the DataFrame.

    Returns:
    - out_df: A pandas DataFrame with columns ('row_index', 'col_index') indicating
              the locations of the value. Row and column names are returned if available,
              otherwise integer indices are used.
    """
    # Create a boolean mask where the condition matches
    mask = df == value

    # Find row and column indices where the mask is True
    row_indices, col_indices = np.where(mask)

    # Convert indices to row and column labels if available
    row_labels = df.index[row_indices].tolist()
    col_labels = df.columns[col_indices].tolist()

    # Construct the output DataFrame
    out_df = pd.DataFrame({
        'row_index': row_labels,
        'col_index': col_labels
    })

    return out_df

def count_null(df):
    # Get the number of null values in each column
    null_counts = df.isnull().sum()
    # Get the total number of rows in the DataFrame
    total_rows = df.shape[0]
    # Compute the proportion of null values in each column
    null_proportions = null_counts / total_rows
    # Create a dictionary mapping column names to null proportions
    result = dict(zip(df.columns, null_proportions))
    return result

def common_element(series_1,series_2):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 08_VocabList\VocatList_func01.py"

    """
    series_1 

    Parameters
    ----------
    series_1 : pd.Series
        should be something like df1['x1']
    series_2 : TYPE
        DESCRIPTION.

    Returns
    -------
    common_elements : list

    """
    common_elements = list(set(series_1).intersection(series_2))
    return common_elements


def is_same(df1,df2):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 08_VocabList\VocatList_func01.py"
    
    """ check if each row is the same or not regardless of their row index?
    
    """
    sorted_df1 = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)
    sorted_df2 = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
    
    # Check if the sorted DataFrames are exactly the same
    are_rows_identical = sorted_df1.equals(sorted_df2)
    
    return are_rows_identical

# def read_excel(filepath,sheet_name = 0, header = 1):
#     # this function is designed to read to pd.df that allow me to open the workbook
#     # at the same time
#     # medium tested
#     import xlwings as xw
    
#     if header is None:
#         header = False
        
#     wb = xw.Book(filepath)
#     sheet = wb.sheets[sheet_name]
    
#     # Find the used range
#     used_range = sheet.used_range
    
#     # Convert the used range to a Pandas DataFrame
#     df = used_range.options(pd.DataFrame, header=header, index=False).value
    
#     return df


def read_excel(filepath, sheet_name=1, header_row=1, start_row=None, end_row=None) -> pd.DataFrame:
    import pandas as pd
    import xlwings as xw
    import numpy as np
    # Hard for both Cluade3 & GPT4
    # medium tested
    # took about 1.5 hr(include testing)

    # took about 1 just to get the index right

    """
    
    Read an Excel file into a Pandas DataFrame.

    Args:
        filepath (str): Path to the Excel file.
        sheet_name (int or str, optional): Name or index of the sheet to read. Default is 0.
        header_row (int or None, optional): Row number to use as the column names. If None, no header row is used. Default is 1.
        start_row (int or None, optional): Row number to start reading data. If None, start from the beginning. Default is None.
        end_row (int or None, optional): Row number to stop reading data. If None, read until the end. Default is None.

    Returns:
        Tuple containing:
            - pandas.DataFrame: The data read from the Excel file.
            - pandas.Series: The header row as a Series.
    """
    wb = xw.Book(filepath)
    
    if isinstance(sheet_name,int):
        sheet = wb.sheets[sheet_name-1]
    elif isinstance(sheet_name,str):
        sheet = wb.sheets[sheet_name]

    used_range = sheet.used_range
    first_used_row = used_range[0].row

    # header_row is False or None
    if header_row in [False,None] :
        header = False
    elif header_row in [1]:
        header = 1
    else:
        header = header_row - first_used_row +1
    
    # Convert the used range to a Pandas DataFrame
    if header in [None,False,1]:
        df_read_ori = used_range.options(pd.DataFrame, header=header, index=False).value
    else:
        df_read_ori = used_range.options(pd.DataFrame, header=False, index=False).value
    
    
    if header_row in [1] and start_row in [None] :
        return df_read_ori
    # Get the header row as a Series
    header_row_df = df_read_ori.iloc[[header_row - first_used_row]]

    # Slice the DataFrame based on start_row and end_row
    if start_row is None:
        start_row_in = 0
    elif header in [1]:
        # Adjust for 0-based indexing and header row and used_range
        # test2
        start_row_in = start_row - first_used_row -1
    else:
        # test4
        start_row_in = start_row - first_used_row 
    
    
    if end_row is None:
        df_info = df_read_ori.iloc[start_row_in:, :]
        
    elif header in [1]:
        end_row_in = end_row - 1 - first_used_row 
        df_info = df_read_ori.iloc[start_row_in:end_row_in+1, :]
    
    else:
        # Adjust for 0-based indexing and header row and used_range
        end_row_in = end_row - 1 - first_used_row 
        df_info = df_read_ori.iloc[start_row_in:end_row_in+1+first_used_row, :]
    
    if header:
        df_info = df_info.reset_index(drop=True)
        if header in [1]:
            return df_info
    
    # Combine the header row and data into a single DataFrame
    out_df = pd.concat([header_row_df, df_info], ignore_index=True)
    out_df.columns = out_df.iloc[0]
    out_df = out_df[1:]
    out_df.reset_index(drop=True, inplace=True)
    try:
        out_df.columns.name = None
    except:
        pass
    return out_df


def regex_index(df,regex, column):
    # from C:/Users/Heng2020/OneDrive/Python NLP/NLP 07_Sentence Alignment
    # middle tested by read_movie_script
    
    # used by: pd_split_into_dict_df
    
    """
    

    Parameters
    ----------
    df : pd.DataFrame
        DESCRIPTION.
    regex : str
        use raw string to specify the regex.
    column : str, int
        DESCRIPTION.

    Returns
    -------
    list[int]
        find the row that has this specific index.

    """
    import pandas as pd
    import re
    
    if isinstance(column, int):
        select_column = df.iloc[:,column]
    elif isinstance(column, str):
        select_column = df[[column]]
    else:
        return "column can only be str or int"
    
    def regex_identifier(value):
        return bool(re.match(regex, str(value)))
    
    boolean_df = select_column.apply(regex_identifier)
    
    
    ans_index = boolean_df[boolean_df].index.tolist()
    
    if len(ans_index) == 1:
        ans_index = ans_index[0]
    
    return ans_index

def split_into_dict_df(df,regex = None, regex_column = None, index_list = None,add_prefix_index = False):
    # from C:/Users/Heng2020/OneDrive/Python NLP/NLP 07_Sentence Alignment
    # middle tested by read_movie_script
    # if index_list is supplied then ignore regex, regex_column
    
    # dependency: pd_split_into_dict_df, pd_regex_index
    from collections import OrderedDict
    df_dict = OrderedDict()

    # split using header
    if (regex is None) and (regex_column is None) and (index_list is None):
        # imported from C:/Users/Heng2020/OneDrive/D_Code/Python/Python NLP/NLP 02/NLP_2024/NLP 11_Local_TTS
        index_list_used = df.index[df.iloc[:, 1:].isnull().all(axis=1) & df.iloc[:, 0].notnull()].tolist()

        # Use the values of the first column as keys and the slices between the found indices as dictionary values
        n_dict = len(index_list_used)
        i = 1
        for start, end in zip(index_list_used, index_list_used[1:] + [None]):  # Adding None to handle till the end of the DataFrame
            format_num = pst.format_index_num(i, n_dict)
            if add_prefix_index:
                key = format_num + "_" + df.iloc[start, 0]  # The key is the value in the first column
            else:
                key = df.iloc[start, 0]
            # Slice the DataFrame from the current index to the next one in the list
            each_df = df.iloc[start+1:end].reset_index(drop=True)
            each_df = each_df.dropna(how='all')
            
            df_dict[key] = each_df
            i += 1
    else:
        if index_list is None:
            index_list_used = regex_index(df,regex,regex_column)
        else:
            index_list_used = [x for x in index_list]
        
        
        start_index = 0
        
        temp_df : pd.DataFrame
        
        for end_index in index_list_used:
            # Slice the dataframe for each episode
            temp_df = df.iloc[start_index:end_index, :]

            if not temp_df.empty:
                # Get the episode identifier from the first row
                episode_identifier = temp_df.iloc[0, 0]
                temp_df = temp_df.reset_index(drop=True)
                temp_df = temp_df.drop(0)
                # Store the dataframe in the dictionary
                df_dict[episode_identifier] = temp_df

            start_index = end_index
        
    return df_dict

def by_col(df:Union[pd.DataFrame], cols:Union[List,int,str]):

    """
    slice the dataFrame refer to by str or int
    """

    # from C:/Users/Heng2020/OneDrive/Python NLP/NLP 07_Sentence Alignment
    # middle tested by read_movie_script
    # 
    
    if isinstance(cols, (str,int,float)):
        column_list = [cols]
    else:
        column_list = [x for x in cols]
    
    col_index = []
    
    for col in column_list:
        if isinstance(col, str):
            col_index.append(df.columns.get_loc(col))
        elif isinstance(col, (int,float)):
            col_index.append(int(col))
    
    out_df = df.iloc[:,col_index]
    return out_df


def num_to_cat(data,num_to_cat_col):
    if type(num_to_cat_col) == str:
        data[num_to_cat_col] = data[num_to_cat_col].astype(str)
    else:
        for col_name in num_to_cat_col:
            data[col_name] = data[col_name].astype(str)
    return data

def num_to_cat02(data,num_to_cat_col):
    # change to category instead of str()
    # this also convert column(object) to category
    if type(num_to_cat_col) == str:
        data[num_to_cat_col] = data[num_to_cat_col].astype("category")
    else:
        for col_name in num_to_cat_col:
            data[col_name] = data[col_name].astype("category")
            
        obj_cols = data.select_dtypes(include=['object']).columns
        data[obj_cols] = data[obj_cols].astype('category')
    return data

def drop_column(data, drop_col):
    """
    it will not throw an error when there's no column in data.columns
    """
    for col in drop_col:
        if col in data.columns:
            data.drop(col, axis=1, inplace=True)
        else:
            print(f"This column doesn't exist:  '{col}' ")
    
    return data


def cat_col(data):
    cat_cols = data.select_dtypes(include=['object','category']).columns.tolist()
    return cat_cols

def num_col(data):
    num_cols = data.select_dtypes(include=np.number).columns.tolist()
    return num_cols

def select_col(data,used_col,drop_col):
    pass
    
def create_dummy(data,exclude=None):
    # Get the list of categorical and object columns
    categorical_cols = data.select_dtypes(include=['category', 'object']).columns
    # remove element(usually y_name in Index object)
    categorical_cols = categorical_cols[categorical_cols !=exclude]

    # Create dummy variables for each categorical column with drop_first=True
    dummy_variables = pd.get_dummies(data[categorical_cols], drop_first=True)
    
    # Concatenate the dummy variables with the original DataFrame
    data_with_dummies = pd.concat([data, dummy_variables], axis=1)
    
    # Drop the original categorical columns
    data_with_dummies.drop(categorical_cols, axis=1, inplace=True)
    
    return data_with_dummies

def combination(dict_in):
    # Get all combinations of values for each key in the dictionary
    combinations = product(*dict_in.values())
    
    # Create a list of dictionaries with all combinations of key-value pairs
    list_of_dicts = [dict(zip(dict_in.keys(), combo)) for combo in combinations]
    
    # Convert the list of dictionaries to a pandas DataFrame
    pd_combinations = pd.DataFrame(list_of_dicts)
    
    return pd_combinations

def cat_combi(pd_in):

    cat_dict = defaultdict(list)

    for col in pd_in.columns:
        if pd_in[col].dtype == 'object':
            for elem in pd_in[col].unique():
                cat_dict[col].append(elem)

    cat_combi = combination(cat_dict)
    return cat_combi

def num_combi(pd_in,n_sample = 30):
    num_dict = defaultdict(list)
    # n_sample = # of sample to generate
    numeric_cols = pd_in.select_dtypes(include=['number']).columns.tolist()
    num = 30
    for col in numeric_cols:
        min_val = pd_in[col].min()
        max_val = pd_in[col].max()
        out_list = np.linspace(start = min_val, stop = max_val,num=num)
        num_dict[col] = list(out_list)
    num_combi = combination(num_dict)
    return num_combi
def make_testing_val(pd_in,n_sample = 30):
    # n_sample = # of sample generate for each of numeric columns
    cat_combi_val = cat_combi_val(pd_in)
    num_combi_val = num_combi_val(pd_in,n_sample)
    
    out_df = _merge_df(cat_combi_val,num_combi_val)
    return out_df

def _merge_df(df1, df2):
    # not sure what it does
    """
    Merge two dataframes into all combinations from every row of df1 to every row of df2.
    """
    result = pd.merge(df1.assign(key=1), df2.assign(key=1), on='key').drop('key', axis=1)
    return result

# def model_values(xgb_pipeline,X,y_name=""):
#     # In case y_name="" means that X doesn't have the y values already
    
#     if y_name != "":
#         X_NO_y = X.drop(y_name,axis=1)
#     else:
#         X_NO_y = X
#     test_val = make_testing_val(X_NO_y)
#     model_val = xgb_predict_append(xgb_pipeline, test_val)
#     return model_val