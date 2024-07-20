
# NEXT fixbug in to_front_of by creating new function in python_wizard
# 


from typing import *
import pandas as pd
import polars as pl
import datatable as dt
import pandas as pd
from typing import Union, List
import numpy as np
from inspect_py import Scalar, Scalar_Numpy, Scalar_BuiltIn
# Define my own types

def swap_col(df: Union[pd.DataFrame], 
             col1:str, 
             col2:str,
             inplace: bool = True) -> Union[pd.DataFrame, None]:
    
    import python_wizard.pw_list as pwl
    # not tested
    """
    Swapp column of df

    """
    # TOADD_01: find the most similar column name

    cols = [col1,col2]

    if isinstance(df,pd.DataFrame):
        # Ensure all specified columns exist in the DataFrame
        non_existent = set(cols) - set(df.columns)
        if non_existent:
            raise ValueError(f"Columns {non_existent} do not exist in the DataFrame")
        

        
        # Create the new column order
        new_order = pwl.swap_item(list(df.columns), col1, col2)
        
        if inplace:
            # Reorder the columns in-place
            df.sort_index(axis=1, key=lambda x: pd.Index([new_order.index(c) if c in new_order else len(df.columns) for c in x]), inplace=True)
            return None
        else:
            # Create a new DataFrame with the new order
            return df.reindex(columns=new_order)
# def swap_col(df, col1, col2):
    # not sure if this works
#     """Swap two columns in a DataFrame."""
#     column_list = list(df.columns)
#     col1_index, col2_index = column_list.index(col1), column_list.index(col2)
    
#     # Swap the positions in the column list
#     column_list[col2_index], column_list[col1_index] = column_list[col1_index], column_list[col2_index]
    
#     # Reorder the DataFrame according to the new column list
#     return df[column_list]
        
def to_first_col(df: pd.DataFrame, cols: Union[str, List[str]], inplace: bool = True) -> Union[pd.DataFrame, None]:
    # 1 shot from Claude 3.5, July 6, 24
    """
    Reorder the columns of a dataframe by moving some columns to the front while preserving dtypes.

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
    >>> to_first_col(df, 'C')
    >>> df
       C  A  B
    0  7  1  4
    1  8  2  5
    2  9  3  6
    >>> result = to_first_col(df, ['B', 'C'], inplace=False)
    >>> result
       B  C  A
    0  4  7  1
    1  5  8  2
    2  6  9  3
    """
    
    # Convert cols to a list if it is a string
    if isinstance(cols, str):
        cols = [cols]
    
    # Ensure all specified columns exist in the DataFrame
    non_existent = set(cols) - set(df.columns)
    if non_existent:
        raise ValueError(f"Columns {non_existent} do not exist in the DataFrame")
    
    # Create a list of the remaining columns
    cols_remain = [x for x in df.columns if x not in cols]
    
    # Create the new column order
    new_order = cols + cols_remain
    
    if inplace:
        # Reorder the columns in-place
        df.sort_index(axis=1, key=lambda x: pd.Index([new_order.index(c) if c in new_order else len(df.columns) for c in x]), inplace=True)
        return None
    else:
        # Create a new DataFrame with the new order
        return df.reindex(columns=new_order)

def to_first_col(df: pd.DataFrame, cols: Union[str, List[str]], inplace: bool = True) -> Union[pd.DataFrame, None]:
    # 1 shot from Claude 3.5, July 6, 24
    """
    Reorder the columns of a dataframe by moving some columns to the front while preserving dtypes.

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
    >>> to_first_col(df, 'C')
    >>> df
       C  A  B
    0  7  1  4
    1  8  2  5
    2  9  3  6
    >>> result = to_first_col(df, ['B', 'C'], inplace=False)
    >>> result
       B  C  A
    0  4  7  1
    1  5  8  2
    2  6  9  3
    """
    
    # Convert cols to a list if it is a string
    if isinstance(cols, str):
        cols = [cols]
    
    # Ensure all specified columns exist in the DataFrame
    non_existent = set(cols) - set(df.columns)
    if non_existent:
        raise ValueError(f"Columns {non_existent} do not exist in the DataFrame")
    
    # Create a list of the remaining columns
    cols_remain = [x for x in df.columns if x not in cols]
    
    # Create the new column order
    new_order = cols + cols_remain
    
    if inplace:
        # Reorder the columns in-place
        df.sort_index(axis=1, key=lambda x: pd.Index([new_order.index(c) if c in new_order else len(df.columns) for c in x]), inplace=True)
        return None
    else:
        # Create a new DataFrame with the new order
        return df.reindex(columns=new_order)


def to_last_col(df: pd.DataFrame, cols: Union[str, List[str]], inplace: bool = True) -> Union[pd.DataFrame, None]:
    # 1 shot from Claude 3.5, July 6, 24
    """
    Reorder the columns of a dataframe by moving some columns to the front while preserving dtypes.

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
    >>> to_first_col(df, 'C')
    >>> df
       C  A  B
    0  7  1  4
    1  8  2  5
    2  9  3  6
    >>> result = to_first_col(df, ['B', 'C'], inplace=False)
    >>> result
       B  C  A
    0  4  7  1
    1  5  8  2
    2  6  9  3
    """
    
    # Convert cols to a list if it is a string
    if isinstance(cols, str):
        cols = [cols]
    
    # Ensure all specified columns exist in the DataFrame
    non_existent = set(cols) - set(df.columns)
    if non_existent:
        raise ValueError(f"Columns {non_existent} do not exist in the DataFrame")
    
    # Create a list of the remaining columns
    cols_remain = [x for x in df.columns if x not in cols]
    
    # Create the new column order
    new_order = cols_remain + cols
    
    if inplace:
        # Reorder the columns in-place
        df.sort_index(axis=1, key=lambda x: pd.Index([new_order.index(c) if c in new_order else len(df.columns) for c in x]), inplace=True)
        return None
    else:
        # Create a new DataFrame with the new order
        return df.reindex(columns=new_order)
    

def to_front_of(df: pd.DataFrame, col_ref: Union[str, int], cols_to_move: Union[str, List[str]], inplace: bool = True) -> Union[pd.DataFrame, None]:
    import python_wizard as pw
    import python_wizard.pw_list as pwl
    # it works now :>
    # seems to work now with the help of pwl.to_front_of

    # hard for ChatGPT 4o& Claude 3.5 as of July 6, 24


    """
    Move specified columns in front of a reference column in a dataframe while preserving dtypes.

    Parameters
    ----------
    df : pandas.DataFrame
        The dataframe to reorder.
    col_ref : str or int
        The reference column name or index in front of which the columns will be moved.
    cols_to_move : str or list of str
        The column name or names to move.
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
    >>> to_front_of(df, 'B', 'C')
    >>> df
       A  C  B
    0  1  7  4
    1  2  8  5
    2  3  9  6
    >>> result = to_front_of(df, 0, ['B', 'C'], inplace=False)
    >>> result
       B  C  A
    0  4  7  1
    1  5  8  2
    2  6  9  3
    """
    
    # Convert cols_to_move to a list if it is a string
    if isinstance(cols_to_move, str):
        cols_to_move_in = [cols_to_move]
    else:
        cols_to_move_in = list(cols_to_move)


    # Create the new column order
    new_order = pwl.to_front_of(list(df.columns), col_ref, cols_to_move_in)

    if inplace:
        # Reorder the columns in-place
        df.sort_index(axis=1, key=lambda x: pd.Index([new_order.index(c) if c in new_order else len(df.columns) for c in x]), inplace=True)
        return None
    else:
        # Create a new DataFrame with the new order
        return df.reindex(columns=new_order)
    
def to_back_of(df: pd.DataFrame, col_ref: Union[str, int], cols_to_move: Union[str, List[str]], inplace: bool = True) -> Union[pd.DataFrame, None]:
    # not tested
    """
    Move specified column(s) to the back of a DataFrame, positioning them after a reference column.

    This function rearranges the columns of a DataFrame, moving the specified column(s) to a position
    immediately after the reference column. If multiple columns are specified to be moved, they will
    maintain their relative order.

    Parameters:
    -----------
    df : pd.DataFrame
        The input DataFrame whose columns are to be rearranged.
    
    col_ref : Union[str, int]
        The reference column. The columns to be moved will be placed immediately after this column.
        Can be either a column name (string) or column index (integer).
    
    cols_to_move : Union[str, List[str]]
        The column(s) to be moved. Can be either a single column name (string) or a list of column names.
    
    inplace : bool, default True
        If True, modifies the DataFrame in-place and returns None.
        If False, returns a new DataFrame with rearranged columns.

    Returns:
    --------
    Union[pd.DataFrame, None]
        If inplace=True, returns None after modifying the input DataFrame in-place.
        If inplace=False, returns a new DataFrame with the rearranged columns.

    Raises:
    -------
    ValueError
        If col_ref or any of cols_to_move are not present in the DataFrame.

    Notes:
    ------
    - This function uses the `python_wizard` and `python_wizard.pw_list` modules.
    - The implementation relies on the `pwl.to_back_of` function to determine the new column order.
    - When inplace=True, the function uses DataFrame's sort_index method with a custom key function
      to reorder the columns efficiently.

    Examples:
    ---------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9], 'D': [10, 11, 12]})
    >>> to_back_of(df, 'B', ['A', 'C'])
    >>> print(df.columns)
    Index(['B', 'D', 'A', 'C'], dtype='object')

    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6], 'C': [7, 8, 9], 'D': [10, 11, 12]})
    >>> new_df = to_back_of(df, 'B', 'A', inplace=False)
    >>> print(new_df.columns)
    Index(['B', 'C', 'D', 'A'], dtype='object')
    """

    import python_wizard.pw_list as pwl
    # not done 
    # seems to work now with the help of pwl.to_front_of
    # still doesn't work when 

    # From ChatGPT 4o as of July 6, 24
    # hard for 
    
    # Convert cols_to_move to a list if it is a string
    if isinstance(cols_to_move, str):
        cols_to_move_in = [cols_to_move]
    else:
        cols_to_move_in = list(cols_to_move)


    # Create the new column order
    new_order = pwl.to_back_of(list(df.columns), col_ref, cols_to_move_in)

    if inplace:
        # Reorder the columns in-place
        df.sort_index(axis=1, key=lambda x: pd.Index([new_order.index(c) if c in new_order else len(df.columns) for c in x]), inplace=True)
        return None
    else:
        # Create a new DataFrame with the new order
        return df.reindex(columns=new_order)

