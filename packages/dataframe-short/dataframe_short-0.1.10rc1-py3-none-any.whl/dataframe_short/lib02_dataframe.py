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

# from lib01_xgb import *
# import string_01 as pst
import py_string_tool as pst

def indexAlignedAppend(df1, df2, col_name):
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
        pd_move_col_front(curr_df, filename_col_name)
        out_df = pd.concat([out_df,curr_df])

    return out_df


# ########################################## imported from work Mar 17, 2024 #######################################################################
def df_to_str_decimal(df,cols,decimal_place = 1, inplace = True, except_level = []):
    # based on pd = 2.1.0
    # Next: add except_level
    from pandas.api.types import is_numeric_dtype

    if isinstance(cols,list):
        except_level_in = list(cols)
    else:
        except_level_in = [except_level]

    if isinstance(cols,list):
        cols_in = list(cols)
    else:
        cols_in = [cols]
    
    for col in cols_in:
        if is_numeric_dtype(df[col]):
            df[col] = df[col].apply(lambda row: f"{row:.{decimal_place}f}")
        # df[col] = df[col].apply(lambda row: f"{row:.{decimal_place}f}" if row not in except_level, axis = 1)


def df_XLookup(df_main, df_lookup, lookup_col, key_col, return_col, inplace=True):
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
    if not isinstance(lookup_col, list):
        lookup_col = [lookup_col]

    # Merge DataFrames
    merged_df = pd.merge(df_main, df_lookup, left_on=lookup_col, right_on=key_col, how='left')

    # Keep only the specified return columns
    if isinstance(return_col, str):
        return_col = [return_col]  # Convert single column name to list

    if inplace:
        for col in return_col:
            df_main[col] = merged_df[col]
        return df_main
    else:
        return merged_df[return_col]

def pd_shape(df):
    # originally from lib01
    # but upgraded
    # medium tested
    import pandas as pd
    if isinstance(df, pd.DataFrame):
        print("The shape ({:,} * {:,})".format(*df.shape))
    # to support when df.shape is an input
    elif isinstance(df, tuple):
        print("The shape ({:,} * {:,})".format(*df))


def pd_to_datetime(df,cols = None,inplace=True, print_col = True):
    # little tested
    # required: pd_get_col
    """
    Convert columns of a DataFrame to datetime dtype.

    This function uses the pd.to_datetime() function to convert the columns
    of a DataFrame that contain date-like values to datetime dtype. It can
    either modify the original DataFrame or return a new one.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to convert.
    cols : list-like, optional
        The list of column names or positions to convert. If None, the function
        will use the pd_get_col() function to find the columns that contain
        'date' in their names. Default None.
    inplace : bool, optional
        Whether to modify the original DataFrame or return a new one. If True,
        the original DataFrame will be modified and nothing will be returned.
        If False, a new DataFrame will be returned and the original one will
        be unchanged. Default True.

    Returns
    -------
    pandas.DataFrame or None
        A new DataFrame with the converted columns, or None if inplace is True.

    Examples
    --------
    >>> df = pd.DataFrame({'date': ['2020-01-01', '2020-01-02'],
                           'value': [1, 2]})
    >>> df
            date  value
    0 2020-01-01      1
    1 2020-01-02      2
    >>> pd_to_datetime(df)
    >>> df
          date  value
    0 2020-01-01      1
    1 2020-01-02      2
    >>> df.dtypes
    date     datetime64[ns]
    value             int64
    dtype: object
    >>> pd_to_datetime(df, cols=['value'], inplace=False)
          date      value
    0 2020-01-01 1970-01-01
    1 2020-01-02 1970-01-02
    """

    import pandas as pd

    if cols is None:
        cols = pd_get_col(df,contain='date',print_col=print_col)

    
    out_df = pd.DataFrame()
    
    if not inplace:
        out_df = df.copy()
    
    for col in cols:
        if inplace:
            df[col] = pd.to_datetime(df[col]) 
        else:
            out_df[col] = pd.to_datetime(out_df[col]) 
    
    if not inplace:
        return out_df

def df_sum_all(df,value_col,exclude = None, inplace = False, dropna = False):
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

def pd_count_freq(df, groupby_col, value_col):
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

def pd_common_col(df1,df2):
    common_col = [x for x in list(df1.columns) if x in list(df2.columns) ]
    return common_col

def pd_get_col(df,start_with = "",end_with ="", contain = "", case_sensitive=False, print_col=True):

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


def pd_merge2(left, 
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
    
    x_col = pd_get_col(df_merged,end_with = "_x",print_col=False)
    
    xy_col = list(zip(pd_get_col(df_merged,end_with = "_x",print_col=False),pd_get_col(df_merged,end_with = "_y",print_col=False) ))

    for x_col, y_col in xy_col:
        col_name = x_col.split("_")[0]
        df_merged[col_name] = df_merged.apply(lambda row: func_keep(row[x_col],row[y_col],keep), axis = 1)
        
        # df_merged = df_merged.sort_index(axis=1)
        
        df_merged.drop(x_col,inplace=True, axis=1)
        df_merged.drop(y_col,inplace=True, axis=1)


        
    # df_merged.drop([i for i in df_merged.columns if 'remove' in i],
    #            axis=1, inplace=True)
    return df_merged


def pd_merge(left, 
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
    
    x_col_list = pd_get_col(df_merged,end_with = "_x",print_col=False)
    y_col_list = pd_get_col(df_merged,end_with = "_y",print_col=False)
    
    xy_col_list = x_col_list + y_col_list
    
    xy_col = list(zip(pd_get_col(df_merged,end_with = "_x",print_col=False),pd_get_col(df_merged,end_with = "_y",print_col=False) ))

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


def pd_to_num(df,cols,num_type = "int64",inplace = True,fill_na = 0):
    # fill_na has to be 0 for it to work properly ----> need more investigation
    
    # it seems to work even when it's already number
    # must import
    from pandas.api.types import is_object_dtype
    if isinstance(cols, str):
        # convert to list
        cols_ = [cols]
    else:
        cols_ = [x for x in cols]
        
    if isinstance(cols_, list):
        for col in cols_:
            if is_object_dtype(df[col]):
                try:
                    df[col] = df[col].str.replace("," ,  "")
                    if fill_na is not False: 
                        df[col] = df[col].fillna(fill_na)
                    # df[col] = df[col].astype(num_type)
                    df[col] = pd.to_numeric(df[col],errors='coerce')
                except Exception as e:
                    e_str = str(e)
                    print(e_str)
                    print(f"'{col}' has an error")

    else:
        pass

def pd_move_col_front(df, cols, inplace=True):
    """
    old code
    # based on pd version == 2.1.3
    
    Reorder the columns of a dataframe by moving some columns to the front.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to reorder.
    cols : str or list of str
        The column name or names to move to the front.
    inplace : bool, optional
        Whether to modify the original dataframe or return a new one. Default is True.

    Returns
    -------
    pandas.DataFrame or None
        The reordered dataframe if inplace is False, otherwise None.

    Examples
    --------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
    >>> df
       A  B  C
    0  1  4  7
    1  2  5  8
    2  3  6  9

    >>> pd_move_col_front(df, 'C')
    >>> df
       C  A  B
    0  7  1  4
    1  8  2  5
    2  9  3  6

    >>> pd_move_col_front(df, ['B', 'C'], inplace=False)
       B  C  A
    0  4  7  1
    1  5  8  2
    """
    
    # Convert cols to a list if it is a string
    if isinstance(cols, str):
        cols = [cols]

    # Create a list of the remaining columns
    cols_remain = [x for x in df.columns if x not in cols]

    # Reorder the columns by concatenating the two lists
    df_new = df[cols + cols_remain]

    # Modify the original dataframe or return a new one depending on inplace parameter
    if inplace:
        df.columns = df_new.columns
        df[:] = df_new
        # return None
    else:
        return df_new

# def pd_move_col_front(df, cols, inplace=True):
#     """
#     from Claude 3(solo)
#     # based on pd version == 2.1.3

#     Reorder the columns of a dataframe by moving some columns to the front.

#     Parameters
#     ----------
#     df : pandas.DataFrame
#         The dataframe to reorder.
#     cols : str or list of str
#         The column name or names to move to the front.
#     inplace : bool, optional
#         Whether to modify the original dataframe or return a new one. Default is True.

#     Returns
#     -------
#     pandas.DataFrame or None
#         The reordered dataframe if inplace is False, otherwise None.

#     Examples
#     --------
#     >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9]})
#     >>> df
#        A  B  C
#     0  1  4  7
#     1  2  5  8
#     2  3  6  9

#     >>> pd_move_col_front(df, 'C')
#     >>> df
#        C  A  B
#     0  7  1  4
#     1  8  2  5
#     2  9  3  6

#     >>> pd_move_col_front(df, ['B', 'C'], inplace=False)
#        B  C  A
#     0  4  7  1
#     1  5  8  2
#     2  6  9  3
#     """
#     # Convert cols to a list if it is a string
#     if isinstance(cols, str):
#         cols = [cols]

#     # Create a list of the remaining columns
#     cols_remain = [x for x in df.columns if x not in cols]

#     # Get the original data types of the columns
#     dtypes = {col: df[col].dtypes for col in df.columns}

#     # Reorder the columns by concatenating the two lists
#     df_new = df[cols + cols_remain]

#     # Modify the original dataframe or return a new one depending on inplace parameter
#     if inplace:
#         # Replace the data in the original DataFrame with the reordered data
#         df[:] = df_new

#         # Restore the original data types of the columns
#         for col in df.columns:
#             df[col] = df[col].astype(dtypes[col])
#         # return None
#     else:
#         return df_new



def pd_check_col(df, columns):
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

def custom_sort(lst, begin_with, end_with,ascending=True, string_last = True):
    import re
    # medium tested
    
    # what if there's no begin_with or end_with?

    # cover when begin_with is string
    # cover when end_with is string
    
    sort_by = []
    
    have_begin = []
    have_end = []
    
    large_num = 2*len(lst)
    count = 0
    # ['m.>30', 'b.-30to-20', 'a.<-30', 'l.21to30', 'd.-14to-10', 'j.11to15', 'i.6to10', 'h.1to5', 'e.-9to-5', 'f.-4to-1', 'c.-19to-15', 'g.0', 'k.16to20']
    # check only first element
    if isinstance(lst[0], str):
        match = re.search(r'[a-zA-Z]\.', lst[0])
    else:
        # If it's a number 
        match = False
    
    if match:
        sorted_list = sorted(lst,reverse=not ascending)
        return sorted_list
    for val in lst:
        try:
            num = float(val)
            sort_by.append(num)
        except ValueError:
            num_02 = val.split(" ")[0]
            num_03 = pst.St_GetNum(num_02)
            
            # string case
            if val in begin_with:
                order_index = -large_num + begin_with.index(val)
                sort_by.append(order_index)
                
            elif val in end_with:
                order_index = large_num + begin_with.index(val)
                sort_by.append(order_index)
                
            else:
                if num_03 is False:
                    
                    # if val not in either begin_with nor end_with
                    if string_last:
                        # put string at the end
                        order_index = large_num + count
                        count += 1
                    else:
                        # put string at the beginning
                        order_index = -large_num + count
                        count += 1
                    sort_by.append(order_index)
                else:
                    sort_by.append(num_03)
                
                    
                    
    # sort_by.sort(reverse = not ascending)

                    
    
    sorted_list = [x for x, y in sorted(zip(lst, sort_by), key=lambda pair: pair[1])]
    # print(sorted_list01)
    return sorted_list


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


def emblem_base(df, value_col="exposure", choose="max"):
    # medium tested
    """
    For each column except for value_col, sum value_col grouped by the unique elements of each column.
    Then, depending on the choose parameter, create a dictionary with the key being that column name and the value being the element with the highest or lowest sum of value_col.

    Parameters
    ----------
    df : pd.DataFrame
        The input data frame.
    value_col : str, optional
        The name of the column that contains the values to be summed. The default is "exposure".
    choose : str, optional
        The option to select the element with the highest or lowest sum of value_col. The default is "max".

    Returns
    -------
    dictt : dict
        The output dictionary with the column names as keys and the selected elements as values.

    Examples
    --------
    >>> df = pd.DataFrame({'country': ['USA', 'USA', 'Canada', 'Canada', 'Mexico', 'Mexico'],
                           'gender': ['M', 'F', 'M', 'F', 'M', 'F'],
                           'exposure': [100, 200, 300, 400, 500, 600]})
    >>> emblem_base(df)
    {'country': 'Mexico', 'gender': 'F'}
    >>> emblem_base(df, choose='min')
    {'country': 'USA', 'gender': 'M'}
    """
    
    # create an empty dictionary to store the results
    dictt = {}
    
    # loop through each column except for value_col
    for col in df.columns:
        if col != value_col:
            # group by the column and sum the value_col
            grouped = df.groupby(col)[value_col].sum()
            # depending on the choose parameter, select the element with the highest or lowest sum
            if choose == "max":
                element = grouped.idxmax()
            elif choose == "min":
                element = grouped.idxmin()
            else:
                raise ValueError("Invalid choose parameter. It must be either 'max' or 'min'.")
            # add the column name and the element to the dictionary
            dictt[col] = element
    
    # return the dictionary
    return dictt




def cat_report(df, include=None, 
               exclude=None, 
               cut_off=15, 
               sort_by='n_elements',
               ascending=True,
               list_ascending = True
               ):
    # little tested
    # v02 => change .append to .concat
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
        # Check if the column is categorical
        curr_type = df_[col].dtype.name
        if df_[col].dtype.name in ['object', 'category'] and df[col].nunique() <= cut_off:
            # Get the number and list of unique values
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

    df_temp = df[col]
    order_df = unique_element(df_temp)
    order_df['element_sorted'] = order_df['elements'].apply(lambda x: custom_sort(x,begin_with,end_with))
    out_dict = dict(zip(order_df['col_name'], order_df['element_sorted']))
    return out_dict

def pd_reorder(df,col,begin_with = None,end_with = None):
    mapping_dict = reorder_dict(df,col,begin_with,end_with)
    
    for col, new_order in mapping_dict.items():
        df[col] = df[col].cat.reorder_categories(new_order)
    
    return df


def pd_shape(df):
    print("The shape ({:,} * {:,})".format(*df.shape))


def pd_duplicate_col(df):
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


def pd_to_str(df,cols = None,inplace = True,fill_na = False):
    # if cols is None convert all columns to string
    if cols is None:
        cols_ = list(df.columns)
    elif isinstance(cols, str):
        # convert to list
        cols_ = [cols]
    else:
        cols_ = [x for x in cols]
        
    if isinstance(cols_, list):
        for col in cols_:
            df[col] = df[col].astype(str)
    else:
        pass

# -------------------------------------------------- imported from work Mar 17, 2024 ------------------------------------------------------



def swap_columns(df, col1, col2):
    """Swap two columns in a DataFrame."""
    column_list = list(df.columns)
    col1_index, col2_index = column_list.index(col1), column_list.index(col2)
    
    # Swap the positions in the column list
    column_list[col2_index], column_list[col1_index] = column_list[col1_index], column_list[col2_index]
    
    # Reorder the DataFrame according to the new column list
    return df[column_list]


def df_value_index(df, value):
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

def pd_common_elements(series_1,series_2):
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


def pd_is_same(df1,df2):
    # imported from "C:\Users\Heng2020\OneDrive\Python NLP\NLP 08_VocabList\VocatList_func01.py"
    
    """ check if each row is the same or not regardless of their row index?
    
    """
    sorted_df1 = df1.sort_values(by=df1.columns.tolist()).reset_index(drop=True)
    sorted_df2 = df2.sort_values(by=df2.columns.tolist()).reset_index(drop=True)
    
    # Check if the sorted DataFrames are exactly the same
    are_rows_identical = sorted_df1.equals(sorted_df2)
    
    return are_rows_identical

# def pd_read_excel(filepath,sheet_name = 0, header = 1):
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


def pd_read_excel(filepath, sheet_name=0, header_row=1, start_row=None, end_row=None):
    import pandas as pd
    import xlwings as xw
    # Hard for both Cluade3 & GPT4
    # medium tested
    # took about 1.5 hr(include testing)
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
    # header_row is False or None
    if header_row in [False,None] :
        header = False
    else:
        header = 1

    wb = xw.Book(filepath)
    sheet = wb.sheets[sheet_name]

    used_range = sheet.used_range

    # Convert the used range to a Pandas DataFrame
    df_read_ori = used_range.options(pd.DataFrame, header=header, index=False).value

    # Get the header row as a Series
    header_row_df = df_read_ori.iloc[[header_row - 2]]

    # Slice the DataFrame based on start_row and end_row
    if start_row is None:
        start_row_in = 0
    else:
        start_row_in = start_row -2 # Adjust for 0-based indexing and header row

    if end_row is None:
        df_info = df_read_ori.iloc[start_row_in:, :]
    else:
        end_row_in = end_row - 1  # Adjust for 0-based indexing
        df_info = df_read_ori.iloc[start_row_in:end_row_in, :]

    # Combine the header row and data into a single DataFrame
    out_df = pd.concat([header_row_df, df_info], ignore_index=True)
    out_df.columns = out_df.iloc[0]
    out_df = out_df[1:]
    out_df.reset_index(drop=True, inplace=True)

    return out_df


def pd_regex_index(df,regex, column):
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

def pd_split_into_dict_df(df,regex = None, regex_column = None, index_list = None):
    # from C:/Users/Heng2020/OneDrive/Python NLP/NLP 07_Sentence Alignment
    # middle tested by read_movie_script
    # if index_list is supplied then ignore regex, regex_column
    
    # dependency: pd_split_into_dict_df, pd_regex_index


    if index_list is None:
        index_list_used = pd_regex_index(df,regex,regex_column)
    else:
        index_list_used = [x for x in index_list]
    
    df_dict = {}
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

def pd_by_column(df, columns):
    # from C:/Users/Heng2020/OneDrive/Python NLP/NLP 07_Sentence Alignment
    # middle tested by read_movie_script
    # slice the dataFrame refer to by str or int
    
    if isinstance(columns, (str,int,float)):
        column_list = [columns]
    else:
        column_list = [x for x in columns]
    
    col_index = []
    
    for col in column_list:
        if isinstance(col, str):
            col_index.append(df.columns.get_loc[col])
        elif isinstance(col, (int,float)):
            col_index.append(int(col))
    
    out_df = df.iloc[:,col_index]
    return out_df


def pd_num_to_cat(data,num_to_cat_col):
    if type(num_to_cat_col) == str:
        data[num_to_cat_col] = data[num_to_cat_col].astype(str)
    else:
        for col_name in num_to_cat_col:
            data[col_name] = data[col_name].astype(str)
    return data

def pd_num_to_cat02(data,num_to_cat_col):
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

def pd_drop_column(data, drop_col):
    for col in drop_col:
        if col in data.columns:
            data.drop(col, axis=1, inplace=True)
        else:
            print(f"This column doesn't exist:  '{col}' ")
    
    return data


def pd_cat_column(data):
    cat_cols = data.select_dtypes(include=['object','category']).columns.tolist()
    return cat_cols

def pd_num_column(data):
    num_cols = data.select_dtypes(include=np.number).columns.tolist()
    return num_cols

def pd_select_column(data,used_col,drop_col):
    pass
    
def pd_to_category(data):
    object_cols = data.select_dtypes(include=['object']).columns
    data[object_cols] = data[object_cols].astype('category')
    return data

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

def pd_combination(dict_in):
    # Get all combinations of values for each key in the dictionary
    combinations = product(*dict_in.values())
    
    # Create a list of dictionaries with all combinations of key-value pairs
    list_of_dicts = [dict(zip(dict_in.keys(), combo)) for combo in combinations]
    
    # Convert the list of dictionaries to a pandas DataFrame
    pd_combinations = pd.DataFrame(list_of_dicts)
    
    return pd_combinations

def pd_cat_combi(pd_in):

    cat_dict = defaultdict(list)

    for col in pd_in.columns:
        if pd_in[col].dtype == 'object':
            for elem in pd_in[col].unique():
                cat_dict[col].append(elem)

    cat_combi = pd_combination(cat_dict)
    return cat_combi

def pd_num_combi(pd_in,n_sample = 30):
    num_dict = defaultdict(list)
    # n_sample = # of sample to generate
    numeric_cols = pd_in.select_dtypes(include=['number']).columns.tolist()
    num = 30
    for col in numeric_cols:
        min_val = pd_in[col].min()
        max_val = pd_in[col].max()
        out_list = np.linspace(start = min_val, stop = max_val,num=num)
        num_dict[col] = list(out_list)
    num_combi = pd_combination(num_dict)
    return num_combi
def make_testing_val(pd_in,n_sample = 30):
    # n_sample = # of sample generate for each of numeric columns
    cat_combi = pd_cat_combi(pd_in)
    num_combi = pd_num_combi(pd_in,n_sample)
    
    out_df = _merge_df(cat_combi,num_combi)
    return out_df

def _merge_df(df1, df2):
    # not sure what it does
    """
    Merge two dataframes into all combinations from every row of df1 to every row of df2.
    """
    result = pd.merge(df1.assign(key=1), df2.assign(key=1), on='key').drop('key', axis=1)
    return result

def model_values(xgb_pipeline,X,y_name=""):
    # In case y_name="" means that X doesn't have the y values already
    
    if y_name != "":
        X_NO_y = X.drop(y_name,axis=1)
    else:
        X_NO_y = X
    test_val = make_testing_val(X_NO_y)
    model_val = xgb_predict_append(xgb_pipeline, test_val)
    return model_val