# tests/test_ph_utils.py
import sys
import os
import unittest
import pandas as pd
import numpy as np

print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

try:
    import ph_utils
    print("ph_utils imported successfully")
    print("ph_utils location:", ph_utils.__file__)
    print("ph_utils contents:", dir(ph_utils))
except ImportError as e:
    print("Import error:", str(e))

from ph_utils import (
    aggregate_function,
    sum_and_sort_columns,
    binary_threshold_matrix_by_col,
    binary_threshold_matrix_by_row,
    aggregate_duplicates,
    bin_continuous,
    impute_na_in_columns,
    concatenate_csvs_in_directory,
    generate_subcategories,
    generate_subcategories_with_proportions,
    load_latest_yyyymmdd_file,
    remove_rows_with_na_threshold
)

class TestPhUtils(unittest.TestCase):
    def test_sum_and_sort_columns(self):
        # Test case from test_main.py
        df = pd.DataFrame({
            'A': [1, 2, 3],
            'B': [0, 0, 0],
            'C': [4, 5, 6],
            'D': ['x', 'y', 'z']
        })
        result = sum_and_sort_columns(df)
        expected = pd.DataFrame({
            'D': ['x', 'y', 'z'],
            'A': [1, 2, 3],
            'C': [4, 5, 6]
        })
        pd.testing.assert_frame_equal(result.sort_index().reset_index(drop=True), expected.sort_index().reset_index(drop=True))

    def test_sum_and_sort_columns_with_nan(self):
        df = pd.DataFrame({
            'A': [1, 2, np.nan],
            'B': [0, 0, 0],
            'C': [4, 5, 6],
            'D': ['x', 'y', 'z']
        })
        result = sum_and_sort_columns(df)
        expected = pd.DataFrame({
            'D': ['x', 'y', 'z'],
            'A': [1, 2, np.nan],
            'C': [4, 5, 6]
        })
        pd.testing.assert_frame_equal(result.sort_values(by='D').reset_index(drop=True), 
                                    expected.sort_values(by='D').reset_index(drop=True))

    def test_binary_threshold_matrix_by_col(self):
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['a', 'b', 'c', 'd', 'e']
        })
        result = binary_threshold_matrix_by_col(df, lower_threshold=20, upper_threshold=80)
        expected = pd.DataFrame({
            'A': [1, 0, 0, 0, 1],
            'B': [1, 0, 0, 0, 1],
            'C': ['a', 'b', 'c', 'd', 'e']
        })
        pd.testing.assert_frame_equal(result.sort_values(by='age').reset_index(drop=True), 
                                      expected.sort_values(by='age').reset_index(drop=True))

    def test_binary_threshold_matrix_by_col(self):
        df = pd.DataFrame({
            'A': [1, 2, 3, 4, 5],
            'B': [10, 20, 30, 40, 50],
            'C': ['a', 'b', 'c', 'd', 'e']
        })
        result = binary_threshold_matrix_by_col(df, lower_threshold=20, upper_threshold=80)
        expected = pd.DataFrame({
            'A': [1, 0, 0, 0, 1],
            'B': [1, 0, 0, 0, 1],
            'C': ['a', 'b', 'c', 'd', 'e']
        })
        pd.testing.assert_frame_equal(result.sort_values(by='A').reset_index(drop=True), 
                                    expected.sort_values(by='A').reset_index(drop=True))

    def test_aggregate_duplicates(self):
        df = pd.DataFrame({
            'group': ['A', 'A', 'B', 'B', 'C'],
            'value1': [1, 2, 3, 4, 5],
            'value2': [10, 20, 30, 40, 50]
        })
        result = aggregate_duplicates(df, group_columns=['group'], numeric_method='mean')
        expected = pd.DataFrame({
            'group': ['A', 'B', 'C'],
            'value1': [1.5, 3.5, 5.0],
            'value2': [15.0, 35.0, 50.0]
        })
        pd.testing.assert_frame_equal(result.sort_values(by='group').reset_index(drop=True), 
                                    expected.sort_values(by='group').reset_index(drop=True))

    def test_bin_continuous(self):
        df = pd.DataFrame({
            'age': [25, 30, 35, 40, 45, 50, 55, 60]
        })
        result = bin_continuous(df, 'age', bin_size=10, range_start=20)
        expected = pd.DataFrame({
            'age': [25, 30, 35, 40, 45, 50, 55, 60],
            'age_bin': pd.Categorical(['20-29', '30-39', '30-39', '40-49', '40-49', '50-59', '50-59', '60-69'], 
                                    categories=['20-29', '30-39', '40-49', '50-59', '60-69'], ordered=True)
        })
        pd.testing.assert_frame_equal(result.sort_values(by='age').reset_index(drop=True), 
                                    expected.sort_values(by='age').reset_index(drop=True))

    def test_impute_na_in_columns(self):
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4],
            'B': [5, np.nan, 7, 8],
            'C': ['x', 'y', 'z', np.nan]
        })
        result = impute_na_in_columns(df, method='median')
        expected = pd.DataFrame({
            'A': [1.0, 2.0, 2.0, 4.0],
            'B': [5.0, 7.0, 7.0, 8.0],
            'C': ['x', 'y', 'z', np.nan]
        })
        pd.testing.assert_frame_equal(result.sort_values(by='A').reset_index(drop=True), 
                                      expected.sort_values(by='A').reset_index(drop=True))

    def test_concatenate_csvs_in_directory(self):
        # Create sample CSV files
        df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        df1.to_csv('test1.csv', index=False)
        df2.to_csv('test2.csv', index=False)

        # Call the function
        result = concatenate_csvs_in_directory('.', file_extension='csv')

        # Check if the result is correct
        expected = pd.concat([df1, df2], ignore_index=True)
        pd.testing.assert_frame_equal(result.sort_values(by='A').reset_index(drop=True), 
                                      expected.sort_values(by='A').reset_index(drop=True))

        # Clean up
        os.remove('test1.csv')
        os.remove('test2.csv')

    def test_aggregate_function(self):
        series = pd.Series([1, 2, 3, 4, 5])
        result = aggregate_function(series, numeric_method='mean')
        self.assertEqual(result, 3)

        series = pd.Series([1, 2, 3, 4, 5])
        result = aggregate_function(series, numeric_method='median')
        self.assertEqual(result, 3)

        series = pd.Series(['a', 'b', 'c'])
        result = aggregate_function(series)
        self.assertEqual(result, 'a|b|c')

    def test_generate_subcategories(self):
        df = pd.DataFrame({
            'A': ['foo', 'bar', 'baz'],
            'B': ['one', 'two', 'three']
        })
        result_df, all_columns = generate_subcategories(df, ['A', 'B'])
        expected_columns = ['A', 'B', 'A_B']
        self.assertEqual(set(all_columns), set(expected_columns))
        self.assertIn('A_B', result_df.columns)

    def test_generate_subcategories_with_proportions(self):
        df = pd.DataFrame({
            'A': ['foo', 'bar', 'baz'],
            'B': ['one', 'two', 'three']
        })
        result_df, all_columns, proportions_df = generate_subcategories_with_proportions(df, ['A', 'B'])
        expected_columns = ['A', 'B', 'A_B']
        self.assertEqual(set(all_columns), set(expected_columns))
        self.assertIn('A_B', result_df.columns)
        self.assertIn('subcategory', proportions_df.columns)
        self.assertIn('decimal_proportion', proportions_df.columns)

    def test_load_latest_yyyymmdd_file(self):
        # Create sample CSV files with dates in the filenames
        df1 = pd.DataFrame({'A': [1, 2]})
        df2 = pd.DataFrame({'A': [3, 4]})
        df1.to_csv('test_20230101.csv', index=False)
        df2.to_csv('test_20230201.csv', index=False)

        # Call the function
        result = load_latest_yyyymmdd_file('.', 'test_', '.csv')

        # Check if the result is correct
        pd.testing.assert_frame_equal(result, df2)

        # Clean up
        os.remove('test_20230101.csv')
        os.remove('test_20230201.csv')

    def test_remove_rows_with_na_threshold(self):
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4],
            'B': [np.nan, 2, 3, 4],
            'C': [1, 2, 3, np.nan]
        })
        result = remove_rows_with_na_threshold(df, ['A', 'B', 'C'], threshold=0.5)
        expected = pd.DataFrame({
            'A': [1, 2, np.nan, 4],
            'B': [np.nan, 2, 3, 4],
            'C': [1, 2, 3, np.nan]
        })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)
        # Create sample CSV files
        df1 = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        df2 = pd.DataFrame({'A': [5, 6], 'B': [7, 8]})
        df1.to_csv('test1.csv', index=False)
        df2.to_csv('test2.csv', index=False)

        # Call the function
        result = concatenate_csvs_in_directory('.', file_extension='csv')

        # Check if the result is correct
        expected = pd.concat([df1, df2], ignore_index=True)
        pd.testing.assert_frame_equal(result, expected)

        # Clean up
        os.remove('test1.csv')
        os.remove('test2.csv')

    def test_generate_subcategories(self):
        df = pd.DataFrame({
            'A': ['foo', 'bar', 'baz'],
            'B': ['one', 'two', 'three']
        })
        result_df, all_columns = generate_subcategories(df, ['A', 'B'])
        expected_columns = ['A', 'B', 'A_B']
        self.assertEqual(set(all_columns), set(expected_columns))
        self.assertIn('A_B', result_df.columns)

    def test_generate_subcategories_with_proportions(self):
        df = pd.DataFrame({
            'A': ['foo', 'bar', 'baz'],
            'B': ['one', 'two', 'three']
        })
        result_df, all_columns, proportions_df = generate_subcategories_with_proportions(df, ['A', 'B'])
        expected_columns = ['A', 'B', 'A_B']
        self.assertEqual(set(all_columns), set(expected_columns))
        self.assertIn('A_B', result_df.columns)
        self.assertIn('subcategory', proportions_df.columns)
        self.assertIn('decimal_proportion', proportions_df.columns)

    def test_load_latest_yyyymmdd_file(self):
        # Create sample CSV files with dates in the filenames
        df1 = pd.DataFrame({'A': [1, 2]})
        df2 = pd.DataFrame({'A': [3, 4]})
        df1.to_csv('test_20230101.csv', index=False)
        df2.to_csv('test_20230201.csv', index=False)

        # Call the function
        result = load_latest_yyyymmdd_file('.', 'test_', '.csv')

        # Check if the result is correct
        pd.testing.assert_frame_equal(result, df2)

        # Clean up
        os.remove('test_20230101.csv')
        os.remove('test_20230201.csv')

    def test_remove_rows_with_na_threshold(self):
        df = pd.DataFrame({
            'A': [1, 2, np.nan, 4],
            'B': [np.nan, 2, 3, 4],
            'C': [1, 2, 3, np.nan]
        })
        result = remove_rows_with_na_threshold(df, ['A', 'B', 'C'], threshold=0.5)
        expected = pd.DataFrame({
            'A': [1, 2, np.nan, 4],
            'B': [np.nan, 2, 3, 4],
            'C': [1, 2, 3, np.nan]
        })
        pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

if __name__ == '__main__':
    unittest.main()
