import chardet
import pandas as pd
import numpy as np
from fs import open_fs
import csv
import warnings


def remove_duplicate_columns(df):
    """
    Warns and removes duplicate columns from a DataFrame
    """
    duplicated_cols = df.columns[df.columns.duplicated()]

    # Drop duplicate columns if any are found
    if len(duplicated_cols) > 0:
        warnings.warn(f"Duplicate columns found: {duplicated_cols}")
        df.drop(columns=duplicated_cols, inplace=True)

    return df


def write_csv(df, fs, filename, index=False, buffer_size=1024 * 1024):
    df = remove_duplicate_columns(df)
    with fs.open(filename, "w") as stream:  # Open in binary write mode ('wb')
        writer = csv.writer(stream)  # Create a CSV writer using the stream
        writer.writerow(df.columns)
        
        data = df.to_records(index=False).tolist()

        writer.writerows(data)


def open_location(path):
    return open_fs(path)


def open_file(fs, file):
    """
    Opens a file within a pyfilesystem
    """
    # Check file encoding
    encoding = check_encoding(fs, file)
    # Open the CSV file using the FS URL
    with fs.open(file, "rb") as f:
        # Read the file content into a pandas DataFrame
        df = pd.read_csv(f, encoding=encoding)
    df = drop_blank_columns(df)
    return df


def fillna_key_columns(df, columns):
    """
    Fill missing values in categorical columns with -1
    """
    for column in columns:
        df[column] = df[column].fillna(-1)
    return df


def fillna_date_columns(df, columns):
    """
    Fill missing values in date columns with 2999-12-31
    """
    for column in columns:
        df[column] = df[column].fillna("2999-12-31")
    return df


def fillna_cat_columns(df, columns):
    """
    Fill missing values in categorical columns with Unknown
    """
    for column in columns:
        df[column] = df[column].fillna("Unknown")
    return df


def fillna_num_columns(df, columns):
    """
    Fill missing values in number columns with None
    """
    for column in columns:
        df[column] = df[column].fillna(np.nan).replace([np.nan], [None])
    return df


def add_nan_row(df):
    """
    Add a lookup for other tables with missing key values
    """
    nan_col = {col: None for col in df.columns}
    df.loc[len(df)] = nan_col
    return df


def generate_dim(data, filename, fs):
    write_csv(pd.DataFrame(data), fs, filename, False)


def check_encoding(fs, file_path):
    """
    Check encoding of a file
    """
    file = fs.open(file_path, "rb")

    bytes_data = file.read()  # Read as bytes
    result = chardet.detect(bytes_data)  # Detect encoding on bytes
    return result["encoding"]


def drop_blank_columns(df):
    unnamed_columns = [
        col for col in df.columns if "Unnamed" in col
    ]
    df = df.drop(columns=unnamed_columns)
    return df