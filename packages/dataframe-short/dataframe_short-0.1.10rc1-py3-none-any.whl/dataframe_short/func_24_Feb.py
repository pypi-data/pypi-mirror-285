import pandas as pd
# v02 => import read_dict_from_csv, write_dict_as_csv

def read_dict_from_csv(file_path):
    import csv
    """
    Reads a CSV file and returns a dictionary.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        dict: The dictionary containing the data from the CSV file.
    """
    out_dict = dict()
    with open(file_path) as file:
        reader = csv.reader(file)
        for row in reader:
            out_dict[row[0]] = float(row[1])
    return out_dict

def write_dict_as_csv(saved_dict,file_name,folder_path):
    # tested
    import csv
    if ".csv" in file_name:
        saved_dict_path = folder_path + "/" + file_name
    else:
        saved_dict_path = folder_path + "/" + file_name + ".csv"


    with open(saved_dict_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for key, value in saved_dict.items():
            writer.writerow([key, value])

def closest_value(df: pd.DataFrame, column_name: str, lookup_value: float) -> pd.Series:
    """
    Find the row in a DataFrame where the value in a specified column
    is closest to a given lookup value.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to search.
    column_name : str
        The name of the column in the DataFrame to compare the lookup_value against.
    lookup_value : float
        The value to find the closest match for in the specified column.

    Returns
    -------
    pd.Series
        A pandas Series object representing the row in the DataFrame where
        the column's value is closest to the lookup_value. If the DataFrame
        is empty or the column does not exist, an empty Series is returned.

    Examples
    --------
    >>> data = {'x1': [2.5, 2.6, 3.0, 2.4, 2.565, 2.575], 'x2': ['A', 'B', 'C', 'D', 'E', 'F']}
    >>> df = pd.DataFrame(data)
    >>> closest_value(df, 'x1', 2.568)
    x1    2.565
    x2        E
    Name: 4, dtype: object
    """
    if column_name not in df.columns:
        # Return an empty Series if the column does not exist
        return pd.Series(dtype='object')

    try:
        # Compute the absolute difference and find the index of the smallest difference
        closest_index = (df[column_name] - lookup_value).abs().idxmin()
        # Return the row with the closest value
        return df.loc[closest_index]
    except ValueError:
        # Return an empty Series if the DataFrame is empty or another error occurs
        return pd.Series(dtype='object')

# Example usage
if __name__ == "__main__":
    data = {'x1': [2.5, 2.6, 3.0, 2.4, 2.565, 2.575], 'x2': ['A', 'B', 'C', 'D', 'E', 'F']}
    df = pd.DataFrame(data)
    print(closest_value(df, 'x1', 2.568))
