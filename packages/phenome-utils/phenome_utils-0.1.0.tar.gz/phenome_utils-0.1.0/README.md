# 📚 Python Script Documentation for `main.py`

Welcome to the documentation for the `main.py` file. This file contains a series of utility functions designed to manipulate, transform, and analyze pandas DataFrames. The main modules used in this script are pandas, numpy, itertools, and matplotlib.

## 📑 Index

1. [sum_and_sort_columns](#1-sum_and_sort_columns)
2. [binary_threshold_matrix_by_col](#2-binary_threshold_matrix_by_col)
3. [binary_threshold_matrix_by_row](#3-binary_threshold_matrix_by_row)
4. [concatenate_csvs_in_directory](#4-concatenate_csvs_in_directory)
5. [aggregate_function](#5-aggregate_function)
6. [aggregate_duplicates](#6-aggregate_duplicates)
7. [generate_subcategories](#7-generate_subcategories)
8. [generate_subcategories_with_proportions](#8-generate_subcategories_with_proportions)
9. [bin_continuous](#9-bin_continuous)
10. [load_latest_yyyymmdd_file](#10-load_latest_yyyymmdd_file)
11. [remove_rows_with_na_threshold](#11-remove_rows_with_na_threshold)
12. [impute_na_in_columns](#12-impute_na_in_columns)

---

## 1. `sum_and_sort_columns`

### Description

Sum the numerical columns of a DataFrame, remove columns with a sum of zero, and sort the columns in descending order based on their sum. Optionally, plot a histogram of the non-zero column sums.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `df`            | `DataFrame`   | The input DataFrame.                                             |
| `plot_histogram`| `bool`        | Whether to plot a histogram of the non-zero column sums. Defaults to False. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `DataFrame`   | A DataFrame with columns sorted in descending order based on their sum, zero-sum columns removed, and non-numeric columns preserved as the first columns. |

### Example Usage

```python
# Example code demonstrating usage
sorted_df = sum_and_sort_columns(df, plot_histogram=True)
```

### 📊 Visualization

If `plot_histogram` is set to True, a histogram of the non-zero column sums will be displayed.

---

## 2. `binary_threshold_matrix_by_col`

### Description

Convert a DataFrame's numerical columns to a binary matrix based on percentile thresholds and filter based on a second DataFrame.

### Parameters

| Parameter                     | Type          | Description                                                      |
|-------------------------------|---------------|------------------------------------------------------------------|
| `df`                          | `DataFrame`   | The input DataFrame.                                             |
| `lower_threshold`             | `int`         | The lower percentile threshold. Defaults to 1.                   |
| `upper_threshold`             | `int`         | The upper percentile threshold. Defaults to 99.                  |
| `second_df`                   | `DataFrame`   | A second DataFrame with 'subcategory' and 'decimal_proportion' columns. |
| `decimal_proportion_threshold`| `float`       | Threshold for filtering the second DataFrame. Defaults to 0.1.   |
| `filter_column`               | `str`         | Column name in the original DataFrame to filter based on 'subcategory' from the second DataFrame. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `DataFrame`   | A binary matrix where numerical column values outside the thresholds are 1 and within the thresholds are 0. Object columns are preserved. |

### Example Usage

```python
# Example code demonstrating usage
binary_df = binary_threshold_matrix_by_col(df, lower_threshold=5, upper_threshold=95, second_df=second_df, filter_column='category')
```

---

## 3. `binary_threshold_matrix_by_row`

### Description

Convert a DataFrame's numerical rows to a binary matrix based on percentile thresholds and filter based on a second DataFrame.

### Parameters

| Parameter                     | Type          | Description                                                      |
|-------------------------------|---------------|------------------------------------------------------------------|
| `df`                          | `DataFrame`   | The input DataFrame.                                             |
| `lower_threshold`             | `int`         | The lower percentile threshold. Defaults to 1.                   |
| `upper_threshold`             | `int`         | The upper percentile threshold. Defaults to 99.                  |
| `second_df`                   | `DataFrame`   | A second DataFrame with 'subcategory' and 'decimal_proportion' columns. |
| `decimal_proportion_threshold`| `float`       | Threshold for filtering the second DataFrame. Defaults to 0.1.   |
| `filter_column`               | `str`         | Column name in the original DataFrame to filter based on 'subcategory' from the second DataFrame. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `DataFrame`   | A binary matrix where numerical row values outside the thresholds are 1 and within the thresholds are 0. Object columns are preserved. |

### Example Usage

```python
# Example code demonstrating usage
binary_df = binary_threshold_matrix_by_row(df, lower_threshold=5, upper_threshold=95, second_df=second_df, filter_column='category')
```

---

## 4. `concatenate_csvs_in_directory`

### Description

Concatenate CSV files from a root directory and its subdirectories.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `root_dir`      | `str`         | The root directory to start the search.                          |
| `filter_string` | `str`         | A string that must be in the filename to be included. Defaults to None. |
| `file_extension`| `str`         | The file extension to search for. Defaults to "csv".             |
| `csv_filename`  | `str`         | The filename to save the concatenated CSV. If not provided, returns the DataFrame. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `DataFrame` or `None` | A concatenated DataFrame of all the CSVs if `csv_filename` is not provided. Otherwise, saves the DataFrame and returns None. |

### Example Usage

```python
# Example code demonstrating usage
concatenated_df = concatenate_csvs_in_directory('/path/to/directory', filter_string='data', csv_filename='output.csv')
```

---

## 5. `aggregate_function`

### Description

General-purpose aggregation function.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `x`             | `pd.Series`   | Input series                                                     |
| `numeric_method`| `str`         | Method to aggregate numeric data. Supports 'median', 'mean', and 'mode'. Default is 'median'. |
| `substitute`    | `any`         | Value to substitute when all values are NaN or mode is empty. Default is np.nan. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `any`         | Aggregated value                                                 |

### Example Usage

```python
# Example code demonstrating usage
aggregated_value = aggregate_function(pd.Series([1, 2, 3, np.nan]), numeric_method='mean')
```

---

## 6. `aggregate_duplicates`

### Description

Aggregates duplicates in a dataframe based on specified grouping columns and a chosen aggregation method for numeric types.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `df`            | `pd.DataFrame`| Input dataframe                                                  |
| `group_columns` | `list`        | List of column names to group by                                 |
| `numeric_method`| `str`         | Method to aggregate numeric data. Supports 'median', 'mean', and 'mode'. Default is 'median'. |
| `substitute`    | `any`         | Value to substitute when all values are NaN or mode is empty. Default is np.nan. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| Dataframe with aggregated duplicates                             |

### Example Usage

```python
# Example code demonstrating usage
aggregated_df = aggregate_duplicates(df, group_columns=['category'], numeric_method='mean')
```

---

## 7. `generate_subcategories`

### Description

Generate subcategories by combining values from specified columns.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `df`            | `pd.DataFrame`| The input dataframe.                                             |
| `columns`       | `list`        | List of columns to generate subcategories from.                  |
| `col_separator` | `str`         | Separator to use between column names for new columns. Defaults to '_'. |
| `val_separator` | `str`         | Separator to use between values when combining. Defaults to ' '. |
| `missing_val`   | `str`         | Value to replace missing data in specified columns. Defaults to 'NA'. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| DataFrame with new subcategory columns.                          |
| `list`        | List of all column names (original + generated).                 |

### Example Usage

```python
# Example code demonstrating usage
df, all_columns = generate_subcategories(df, columns=['col1', 'col2'])
```

---

## 8. `generate_subcategories_with_proportions`

### Description

Generate subcategories by combining values from specified columns and calculate their proportions.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `df`            | `pd.DataFrame`| The input dataframe.                                             |
| `columns`       | `list`        | List of columns to generate subcategories from.                  |
| `solo_columns`  | `list`        | List of columns to be considered on their own.                   |
| `col_separator` | `str`         | Separator to use between column names for new columns. Defaults to '_'. |
| `val_separator` | `str`         | Separator to use between values when combining. Defaults to ' '. |
| `missing_val`   | `str`         | Value to replace missing data in specified columns. Defaults to 'NA'. |
| `overall_category_name` | `str` | Name for the overall category. Defaults to 'overall'.            |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| DataFrame with new subcategory columns.                          |
| `list`        | List of all column names (original + generated).                 |
| `pd.DataFrame`| DataFrame with subcategory and its decimal proportion.           |

### Example Usage

```python
# Example code demonstrating usage
df, all_columns, proportions_df = generate_subcategories_with_proportions(df, columns=['col1', 'col2'], solo_columns=['col3'])
```

---

## 9. `bin_continuous`

### Description

Bins continuous data in a specified column of a dataframe.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `dataframe`     | `pd.DataFrame`| The input dataframe.                                             |
| `column_name`   | `str`         | The name of the column containing continuous data to be binned.  |
| `bin_size`      | `int`         | The size of each bin. Default is 10.                             |
| `range_start`   | `int`         | The starting value of the range for binning. Default is 0.       |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| The dataframe with an additional column for binned data.         |

### Example Usage

```python
# Example code demonstrating usage
binned_df = bin_continuous(df, column_name='age', bin_size=5)
```

---

## 10. `load_latest_yyyymmdd_file`

### Description

Load the latest file from the specified directory based on its date.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `directory`     | `str`         | Path to the directory containing the files.                      |
| `base_filename` | `str`         | Base name of the file.                                           |
| `file_extension`| `str`         | File extension including the dot (e.g., '.csv').                 |
| `na_values`     | `list or dict`| Additional strings to recognize as NA/NaN.                       |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| The loaded data.                                                 |

### Example Usage

```python
# Example code demonstrating usage
df = load_latest_yyyymmdd_file("/path/to/directory", "data_", ".csv")
print(df.head())
```

---

## 11. `remove_rows_with_na_threshold`

### Description

Removes rows from the dataframe that have a fraction of NA values greater than the specified threshold.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `df`            | `pd.DataFrame`| The input dataframe.                                             |
| `stringified_ids`| `list`       | List of column names to consider for NA value calculation.       |
| `threshold`     | `float`       | The fraction of NA values for a row to be removed. Default is 0.5. |
| `save_starting_df`| `bool`      | Whether to save the initial dataframe to a CSV file. Default is False. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| The dataframe with rows removed based on the threshold.          |

### Example Usage

```python
# Example code demonstrating usage
cleaned_df = remove_rows_with_na_threshold(df, stringified_ids=['col1', 'col2'], threshold=0.3)
```

---

## 12. `impute_na_in_columns`

### Description

Imputes NA values in columns with either the minimum or median value of the column.

### Parameters

| Parameter       | Type          | Description                                                      |
|-----------------|---------------|------------------------------------------------------------------|
| `df`            | `pd.DataFrame`| The input dataframe.                                             |
| `method`        | `str`         | Method for imputation. Either 'min' or 'median'. Default is 'median'. |

### Returns

| Type          | Description                                                      |
|---------------|------------------------------------------------------------------|
| `pd.DataFrame`| The dataframe with NA values imputed.                            |

### Example Usage

```python
# Example code demonstrating usage
imputed_df = impute_na_in_columns(df, method='median')
```

---

Each function is meticulously crafted to handle specific tasks related to data manipulation, transformation, and analysis. This documentation provides a comprehensive understanding of the capabilities and usage of each function within the `main.py` script. Happy coding! 🎉
</source>
# ph_utils

ph_utils is a Python package that provides utility functions for data manipulation and analysis, particularly focused on working with pandas DataFrames.

## Features

- Sum and sort DataFrame columns
- Generate binary threshold matrices
- Concatenate CSV files from directories
- Aggregate duplicates in DataFrames
- Generate subcategories from DataFrame columns
- Bin continuous data
- Load latest files based on date in filename
- Remove rows with NA values above a threshold
- Impute NA values in DataFrame columns

## Installation

You can install ph_utils using pip:

```
pip install ph_utils
```

## Usage

Here are some examples of how to use ph_utils:

```python
import pandas as pd
from ph_utils import sum_and_sort_columns, binary_threshold_matrix_by_col, aggregate_duplicates

# Example 1: Sum and sort columns
df = pd.DataFrame({
    'A': [1, 2, 3],
    'B': [0, 0, 0],
    'C': [4, 5, 6],
    'D': ['x', 'y', 'z']
})
result = sum_and_sort_columns(df)
print(result)

# Example 2: Create a binary threshold matrix
binary_df = binary_threshold_matrix_by_col(df, lower_threshold=25, upper_threshold=75)
print(binary_df)

# Example 3: Aggregate duplicates
aggregated_df = aggregate_duplicates(df, group_columns=['D'], numeric_method='mean')
print(aggregated_df)
```

For more detailed information on each function, please refer to the function docstrings in the source code.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
