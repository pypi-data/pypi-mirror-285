from typing import *
import pandas as pd
import dataframe_short.utils_ds as ds 


def add_prefix_num(df:Union[pd.DataFrame],
                   col:str,
                   start_index:int = 1,
                   increment:int = 1, # not implemented
                   ) -> pd.Series:
    n_rows = df.shape[0]
    
    digit_rows = len(str(n_rows))
   
    df_copy = ds.by_col(df,col)
    
    df_copy.reset_index(drop=True, inplace=True)
    df_copy.index += start_index

    out_series = df_copy.index.map(lambda x: f"{str(x).zfill(digit_rows)}") + "_" + df_copy[col]

    return out_series


def check_levels(df_left: pd.DataFrame, df_right: pd.DataFrame, cols: Dict[str, str], ignore_dtype: bool = False) -> pd.DataFrame:

    # Solo from Claude3
    """
    Compare levels of specified columns between two DataFrames.

    Parameters
    ----------
    df_left : pd.DataFrame
        The left DataFrame for comparison.
    df_right : pd.DataFrame
        The right DataFrame for comparison.
    cols : Dict[str, str]
        A dictionary mapping column names from df_left to df_right.
    ignore_dtype : bool, optional
        If True, treat numeric values as equivalent regardless of their specific data type.
        For example, '2' (str), 2.0 (float), and 2 (int) will be considered the same.
        Default is False.

    Returns
    -------
    pd.DataFrame
        A DataFrame with columns:
        - left_col: name of the column in df_left
        - right_col: name of the column in df_right
        - left_only: levels present only in df_left
        - right_only: levels present only in df_right
        - both: levels present in both DataFrames

    Examples
    --------
    >>> df1 = pd.DataFrame({'A': [1, '2', 3], 'B': ['a', 'b', 'c']})
    >>> df2 = pd.DataFrame({'X': [2.0, 3, 4], 'Y': ['b', 'c', 'd']})
    >>> cols_map = {'A': 'X', 'B': 'Y'}
    >>> check_levels(df1, df2, cols_map, ignore_dtype=True)
       left_col right_col left_only right_only     both
    0         A         X        [1]        [4]  [2, 3]
    1         B         Y        [a]        [d]  [b, c]
    """
    def normalize(value: Union[str, int, float]) -> Union[str, float]:
        if ignore_dtype:
            try:
                return float(value)
            except ValueError:
                return str(value).lower()
        return value

    results = []

    for left_col, right_col in cols.items():
        left_levels = set(map(normalize, df_left[left_col].unique()))
        right_levels = set(map(normalize, df_right[right_col].unique()))

        left_only = list(left_levels - right_levels)
        right_only = list(right_levels - left_levels)
        both = list(left_levels & right_levels)

        # Convert back to original types for consistency in output
        left_only = [v if not ignore_dtype else df_left[left_col].dtype.type(v) for v in left_only]
        right_only = [v if not ignore_dtype else df_right[right_col].dtype.type(v) for v in right_only]
        both = [v if not ignore_dtype else df_left[left_col].dtype.type(v) for v in both]

        results.append({
            'left_col': left_col,
            'right_col': right_col,
            'left_only': left_only,
            'right_only': right_only,
            'both': both
        })

    return pd.DataFrame(results)