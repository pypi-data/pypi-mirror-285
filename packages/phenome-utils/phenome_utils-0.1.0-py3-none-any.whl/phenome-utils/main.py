import os
import glob
import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt

def sum_and_sort_columns(df, plot_histogram=False):
    """
    Sum the numerical columns of a DataFrame, remove columns with a sum of zero,
    and sort the columns in descending order based on their sum. Optionally, plot a histogram of the non-zero column sums.

    Parameters:
    - df (DataFrame): The input DataFrame.
    - plot_histogram (bool): Whether to plot a histogram of the non-zero column sums. Defaults to False.

    Returns:
    - DataFrame: A DataFrame with columns sorted in descending order based on their sum, zero-sum columns removed, and non-numeric columns preserved as the first columns.
    """

    # Separate non-numeric columns
    non_numeric_cols = df.select_dtypes(exclude=['number']).columns.tolist()

    # Sum each numeric column
    col_sums = df.sum(numeric_only=True)

    # Filter out columns with a sum of zero
    non_zero_cols = col_sums[col_sums != 0].index.tolist()
    non_zero_sums = col_sums[col_sums != 0].values

    # Sort numeric columns by sum in descending order
    sorted_cols = col_sums.sort_values(ascending=False).index.tolist()

    # Filter and sort the DataFrame columns
    sorted_df = df[sorted_cols]
    sorted_df = sorted_df.loc[:, non_zero_cols]

    # Add non-numeric columns to the beginning of the sorted DataFrame
    sorted_df = pd.concat([df[non_numeric_cols], sorted_df], axis=1)

    # Plot histogram if requested
    if plot_histogram:
        plt.hist(non_zero_sums, bins=30, edgecolor='k', alpha=0.7)
        plt.title('Distribution of Non-Zero Column Sums')
        plt.xlabel('Sum')
        plt.ylabel('Number of Columns')
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)
        plt.show()

    return sorted_df


def binary_threshold_matrix_by_col(df, lower_threshold=1, upper_threshold=99,
                                   second_df=None, decimal_proportion_threshold=0.1,
                                   filter_column=None):
    """
    Convert a DataFrame's numerical columns to a binary matrix based on percentile thresholds
    and filter based on a second DataFrame.

    Parameters:
    - df (DataFrame): The input DataFrame.
    - lower_threshold (int, optional): The lower percentile threshold. Defaults to 1.
    - upper_threshold (int, optional): The upper percentile threshold. Defaults to 99.
    - second_df (DataFrame, optional): A second DataFrame with 'subcategory' and 'decimal_proportion' columns.
    - decimal_proportion_threshold (float, optional): Threshold for filtering the second DataFrame. Defaults to 0.1.
    - filter_column (str, optional): Column name in the original DataFrame to filter based on 'subcategory' from the second DataFrame.

    Returns:
    - DataFrame: A binary matrix where numerical column values outside the thresholds are 1 and within the thresholds are 0. Object columns are preserved.
    """

    # Copy the DataFrame to avoid modifying the original
    binary_df = df.copy()

    # Iterate over columns
    for col in df.columns:
        if df[col].dtype == 'O':  # If column is of object type, skip
            continue

        # Calculate percentiles
        lower_val = df[col].quantile(lower_threshold / 100.0)
        upper_val = df[col].quantile(upper_threshold / 100.0)

        # Convert to binary based on thresholds
        binary_df[col] = ((df[col] < lower_val) | (
            df[col] > upper_val)).astype(int)

    # Filter based on the second DataFrame if provided
    if second_df is not None and filter_column:
        # Filter the second DataFrame based on decimal_proportion_threshold
        valid_subcategories = second_df[second_df['decimal_proportion']
                                        > decimal_proportion_threshold]['subcategory']

        # Filter the binary matrix based on the valid subcategories
        binary_df = binary_df[binary_df[filter_column].isin(
            valid_subcategories)]

    return binary_df


def binary_threshold_matrix_by_row(df, lower_threshold=1, upper_threshold=99,
                                   second_df=None, decimal_proportion_threshold=0.1,
                                   filter_column=None):
    """
    Convert a DataFrame's numerical rows to a binary matrix based on percentile thresholds
    and filter based on a second DataFrame.

    Parameters:
    - df (DataFrame): The input DataFrame.
    - lower_threshold (int, optional): The lower percentile threshold. Defaults to 1.
    - upper_threshold (int, optional): The upper percentile threshold. Defaults to 99.
    - second_df (DataFrame, optional): A second DataFrame with 'subcategory' and 'decimal_proportion' columns.
    - decimal_proportion_threshold (float, optional): Threshold for filtering the second DataFrame. Defaults to 0.1.
    - filter_column (str, optional): Column name in the original DataFrame to filter based on 'subcategory' from the second DataFrame.

    Returns:
    - DataFrame: A binary matrix where numerical row values outside the thresholds are 1 and within the thresholds are 0. Object columns are preserved.
    """

    def threshold_row(row):
        # Calculate percentiles for the numeric values in the row
        numeric_values = row[row.apply(
            lambda x: np.isreal(x) and not np.isnan(x))]
        lower_val = numeric_values.quantile(lower_threshold / 100.0)
        upper_val = numeric_values.quantile(upper_threshold / 100.0)

        # Convert numeric values to binary based on thresholds
        binary_row = ((numeric_values < lower_val) |
                      (numeric_values > upper_val)).astype(int)

        # Update the original row with the binary values
        row.update(binary_row)
        return row

    # Apply the threshold function to each row
    binary_df = df.apply(threshold_row, axis=1)

    # Convert only the numeric columns to integers
    numeric_cols = binary_df.select_dtypes(include=[np.number]).columns
    binary_df[numeric_cols] = binary_df[numeric_cols].fillna(0).astype(int)

    # Filter based on the second DataFrame if provided
    if second_df is not None and filter_column:
        # Filter the second DataFrame based on decimal_proportion_threshold
        valid_subcategories = second_df[second_df['decimal_proportion']
                                        > decimal_proportion_threshold]['subcategory']

        # Filter the binary matrix based on the valid subcategories
        binary_df = binary_df[binary_df[filter_column].isin(
            valid_subcategories)]

    return binary_df


def concatenate_csvs_in_directory(root_dir, filter_string=None, file_extension="csv", csv_filename=None):
    """
    Concatenate CSV files from a root directory and its subdirectories.

    Parameters:
    - root_dir (str): The root directory to start the search.
    - filter_string (str, optional): A string that must be in the filename to be included. Defaults to None.
    - file_extension (str, optional): The file extension to search for. Defaults to "csv".
    - csv_filename (str, optional): The filename to save the concatenated CSV. If not provided, returns the DataFrame.

    Returns:
    - DataFrame or None: A concatenated DataFrame of all the CSVs if csv_filename is not provided. Otherwise, saves the DataFrame and returns None.
    """

    # List to store DataFrames
    dfs = []

    # Walk through the directory
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check file extension and filter string
            if filename.endswith(file_extension) and (not filter_string or filter_string in filename):
                file_path = os.path.join(dirpath, filename)
                dfs.append(pd.read_csv(file_path))

    # Concatenate all DataFrames
    concatenated_df = pd.concat(dfs, ignore_index=True)

    # Rename "Unnamed: 0" column to "category"
    if "Unnamed: 0" in concatenated_df.columns:
        concatenated_df.rename(
            columns={"Unnamed: 0": "category"}, inplace=True)

    # Save to CSV if filename is provided
    if csv_filename:
        concatenated_df.to_csv(csv_filename, index=False)
        return None

    return concatenated_df


def aggregate_function(x, numeric_method='median', substitute=np.nan):
    """
    General-purpose aggregation function.

    Parameters:
    - x (pd.Series): Input series
    - numeric_method (str, optional): Method to aggregate numeric data. Supports 'median', 'mean', and 'mode'. Default is 'median'.
    - substitute (any, optional): Value to substitute when all values are NaN or mode is empty. Default is np.nan.

    Returns:
    - Aggregated value
    """
    if pd.api.types.is_numeric_dtype(x):
        if x.isnull().all():
            return substitute
        if numeric_method == 'mean':
            return x.mean()
        elif numeric_method == 'median':
            return x.median()
        elif numeric_method == 'mode':
            return x.mode()[0] if not x.mode().empty else substitute
        else:
            raise ValueError(f"Unsupported numeric_method: {numeric_method}")
    elif pd.api.types.is_object_dtype(x) or pd.api.types.is_string_dtype(x) or pd.api.types.is_categorical_dtype(x):
        return '|'.join(x.astype(str))
    else:
        return x.mode()[0] if not x.mode().empty else substitute


def aggregate_duplicates(df, group_columns, numeric_method='median', substitute=np.nan):
    """
    Aggregates duplicates in a dataframe based on specified grouping columns and a chosen aggregation method for numeric types.

    Parameters:
    - df (pd.DataFrame): Input dataframe
    - group_columns (list): List of column names to group by
    - numeric_method (str, optional): Method to aggregate numeric data. Supports 'median', 'mean', and 'mode'. Default is 'median'.
    - substitute (any, optional): Value to substitute when all values are NaN or mode is empty. Default is np.nan.

    Returns:
    - pd.DataFrame: Dataframe with aggregated duplicates
    """

    # return df.groupby(group_columns).agg(lambda x: aggregate_function(x, numeric_method, substitute)).reset_index()

    aggregated_df = df.groupby(group_columns).agg(
        lambda x: aggregate_function(x, numeric_method, substitute))

    # Check for group columns before resetting index
    for col in group_columns:
        if col in aggregated_df.columns:
            aggregated_df.drop(col, axis=1, inplace=True)

    return aggregated_df.reset_index()


def generate_subcategories(df, columns, col_separator='_', val_separator=' ', missing_val='NA'):
    """
    Generate subcategories by combining values from specified columns.

    Parameters:
    - df (pd.DataFrame): The input dataframe.
    - columns (list): List of columns to generate subcategories from.
    - col_separator (str, optional): Separator to use between column names for new columns. Defaults to '_'.
    - val_separator (str, optional): Separator to use between values when combining. Defaults to ' '.
    - missing_val (str, optional): Value to replace missing data in specified columns. Defaults to 'NA'.

    Returns:
    - pd.DataFrame: DataFrame with new subcategory columns.
    - list: List of all column names (original + generated).
    """

    # Handle missing values in specified columns
    for col in columns:
        if df[col].dtype.name == 'category':
            df[col] = df[col].cat.add_categories([missing_val])
    df[columns] = df[columns].fillna(missing_val)

    # Validate that specified columns are categorical
    for col in columns:
        if df[col].dtype not in ['object', 'category']:
            raise ValueError(f"Column {col} is not categorical.")

    # Calculate and print the total number of new subcategory combinations
    total_combinations = sum(
        [len(list(itertools.combinations(columns, i))) for i in range(1, len(columns) + 1)]) - len(columns)
    print(f"Expected number of subcategories: {total_combinations}")

    # Generate new subcategory columns
    new_columns = []
    for i in range(1, len(columns) + 1):
        for subset in itertools.combinations(columns, i):
            new_col_name = col_separator.join(subset)
            df[new_col_name] = df[list(subset)].apply(
                lambda x: val_separator.join(x.dropna().astype(str)), axis=1)
            new_columns.append(new_col_name)

    # Combine original and new column names
    all_columns = columns + new_columns

    return df, all_columns


def generate_subcategories_with_proportions(df, columns, solo_columns=[], col_separator='_', val_separator=' ', missing_val='NA', overall_category_name='overall'):
    """
    Generate subcategories by combining values from specified columns.

    Parameters:
    - df (pd.DataFrame): The input dataframe.
    - columns (list): List of columns to generate subcategories from.
    - solo_columns (list): List of columns to be considered on their own.
    - col_separator (str, optional): Separator to use between column names for new columns. Defaults to '_'.
    - val_separator (str, optional): Separator to use between values when combining. Defaults to ' '.
    - missing_val (str, optional): Value to replace missing data in specified columns. Defaults to 'NA'.
    - overall_category_name (str, optional): Name for the overall category. Defaults to 'overall'.

    Returns:
    - pd.DataFrame: DataFrame with new subcategory columns.
    - list: List of all column names (original + generated).
    - pd.DataFrame: DataFrame with subcategory and its decimal proportion.
    """

    # Combine original and new column names
    all_columns = columns + solo_columns

    # Handle missing values in specified columns
    for col in all_columns:
        if df[col].dtype.name == 'category':
            df[col] = df[col].cat.add_categories([missing_val])
    df[all_columns] = df[all_columns].fillna(missing_val)

    # Validate that specified columns are categorical
    for col in all_columns:
        if df[col].dtype not in ['object', 'category']:
            raise ValueError(f"Column {col} is not categorical.")

    # Generate new subcategory columns
    new_columns = []
    for i in range(1, len(columns) + 1):
        for subset in itertools.combinations(columns, i):
            if any(col in subset for col in solo_columns) and len(subset) > 1:
                continue
            new_col_name = col_separator.join(subset)
            df[new_col_name] = df[list(subset)].apply(
                lambda x: val_separator.join(x.astype(str)), axis=1)
            new_columns.append(new_col_name)
            #print(f"New column created: {new_col_name}") # add this line

    # Combine original and new column names
    all_columns += new_columns

    # Create a DataFrame with subcategory and its decimal proportion
    proportions = []
    for col in all_columns:
        value_counts = df[col].value_counts()
        normalized_value_counts = value_counts / len(df)
        for subcategory, proportion in normalized_value_counts.items():
            count = value_counts[subcategory]
            proportions.append((subcategory, proportion, count))

    proportions_df = pd.DataFrame(
        proportions, columns=['subcategory', 'decimal_proportion', 'subcohort_n'])

    # Convert subcohort_n to int
    proportions_df['subcohort_n'] = proportions_df['subcohort_n'].astype(int)

    # Add the overall category with a proportion of 1
    overall_row = pd.DataFrame([[overall_category_name, 1, len(df)]], columns=[
                               'subcategory', 'decimal_proportion', 'subcohort_n'])
    proportions_df = pd.concat(
        [overall_row, proportions_df], ignore_index=True)
    
    #print("generate_subcategories_with_proportions")
    #print(df.columns)

    return df, all_columns, proportions_df


def bin_continuous(dataframe, column_name, bin_size=10, range_start=0):
    """
    Bins continuous data in a specified column of a dataframe.

    Parameters:
    - dataframe (pd.DataFrame): The input dataframe.
    - column_name (str): The name of the column containing continuous data to be binned.
    - bin_size (int, optional): The size of each bin. Default is 10.
    - range_start (int, optional): The starting value of the range for binning. Default is 0.

    Returns:
    - pd.DataFrame: The dataframe with an additional column for binned data.
    """

    # Determine the maximum value in the specified column and convert to integer
    max_value = int(dataframe[column_name].max())

    # Create bins based on the specified range and bin size
    bins = list(range(range_start, max_value + bin_size * 2, bin_size))  # Add one more bin

    # Generate labels for each bin
    labels = [f"{i}-{i+bin_size-1}" for i in bins[:-1]]

    # Create a new column in the dataframe with binned data
    dataframe[f"{column_name}_bin"] = pd.cut(
        dataframe[column_name], bins=bins, labels=labels, right=False, include_lowest=True)

    return dataframe


def load_latest_yyyymmdd_file(directory, base_filename, file_extension, na_values=None):
    """
    Load the latest file from the specified directory based on its date.

    Args:
        directory (str): Path to the directory containing the files.
        base_filename (str): Base name of the file.
        file_extension (str): File extension including the dot (e.g., '.csv').

    Returns:
        pd.DataFrame: The loaded data.

    Example usage:
        df = load_latest_yyyymmdd_file("/procedure/arivale_spoke_kg/src/mapping/metabolome_mapping/", "metabolome_mapping_MERGED_", ".csv")
        print(df.head())
    """

    # Ensure directory path ends with a slash
    if not directory.endswith('/'):
        directory += '/'

    # List all matching files
    if "." in file_extension:
        pattern = f"{directory}{base_filename}*{file_extension}"
    else:
        pattern = f"{directory}{base_filename}*.{file_extension}"
    files = glob.glob(pattern)

    # Check if files list is empty
    if not files:
        raise ValueError("No files found matching the pattern.")

    # Sort files by date in the filename to get the latest
    latest_file = sorted(files, key=lambda x: os.path.basename(
        x).split('_')[-1].replace(file_extension, ''), reverse=True)[0]

    return pd.read_csv(latest_file, na_values=na_values)


def remove_rows_with_na_threshold(df, stringified_ids, threshold=0.5, save_starting_df=False):
    """
    Removes rows from the dataframe that have a fraction of NA values greater than the specified threshold.

    Parameters:
    - df (pd.DataFrame): The input dataframe.
    - stringified_ids (list): List of column names to consider for NA value calculation.
    - threshold (float, optional): The fraction of NA values for a row to be removed. Default is 0.5.

    Returns:
    - pd.DataFrame: The dataframe with rows removed based on the threshold.
    """

    # Save the initial dataframe to a CSV file
    if save_starting_df:
        df.to_csv('starting_df.csv', index=False)

    # Filter stringified_ids to only include columns that are in df
    valid_columns = [col for col in stringified_ids if col in df.columns]

    # Calculate fraction of NA values for each row considering only the valid columns
    na_fractions = df[valid_columns].isnull().mean(axis=1)

    # Determine rows that have a fraction of NA values greater than the threshold
    rows_to_remove = df[na_fractions > threshold]

    # Print the count of rows removed of total rows
    print(f"Removed {len(rows_to_remove)} rows out of {len(df)} total rows.")

    # Print the highest fraction of NA values found
    highest_na_fraction = na_fractions.max()
    print(
        f"The highest fraction of NA values in a row is {highest_na_fraction:.2f}.")

    # Drop the rows and return the dataframe
    return df.drop(rows_to_remove.index)


def impute_na_in_columns(df, method='median'):
    """
    Imputes NA values in columns with either the minimum or median value of the column.

    Parameters:
    - df (pd.DataFrame): The input dataframe.
    - method (str, optional): Method for imputation. Either 'min' or 'median'. Default is 'median'.

    Returns:
    - pd.DataFrame: The dataframe with NA values imputed.
    """

    # Normalize data types for mixed-type columns
    df = df.infer_objects()

    # Save and temporarily remove identifier columns
    identifiers = {}
    for id_col in ['public_client_id', 'sample_id', 'Chip_ID_CAM', 'Chip_ID_CRE', 'Chip_ID_CVD2', 'Chip_ID_CVD3', 'Chip_ID_DEV', "Chip_ID_IRE", "Chip_ID_MET", "Chip_ID_NEU1", "Chip_ID_NEX", "Chip_ID_ODA", "Chip_ID_ONC2", "Chip_ID_ONC3", "Chip_ID_INF", "month", "weekday", "season"]:
        if id_col in df.columns:
            identifiers[id_col] = df[id_col].copy()
            df.drop(columns=[id_col], inplace=True)

    # Validate method argument
    if method not in ['min', 'median']:
        raise ValueError("Method must be either 'min' or 'median'")

    def impute_column(col):
        col_numeric = pd.to_numeric(col, errors='coerce')
        if col_numeric.isnull().all():
            return col
        if method == 'min':
            return col_numeric.fillna(col_numeric.min())
        elif method == 'median':
            return col_numeric.fillna(col_numeric.median())
    imputed_dataframe = df.apply(impute_column, axis=0)

    # Add identifier columns back to the dataframe
    for id_col, col_data in identifiers.items():
        imputed_dataframe[id_col] = col_data

    return imputed_dataframe

# Example usage:
# df = pd.DataFrame({"A": [1, 2, np.nan, 4], "B": [5, np.nan, 7, 8]})
# imputed_df = impute_na_in_columns(df, method='random_forest')
