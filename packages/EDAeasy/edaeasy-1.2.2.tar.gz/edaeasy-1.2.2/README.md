# EDAeasy 😀
The package for quick exploratory data analysis


## Instalation 

`pip install EDAeasy`

## Usage
The **dataframe_summary** function have relative simple summary of the columns of your dataframe
for quick look at tabular data

    Generate a summary DataFrame of the input DataFrame 'dataframe'.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The input DataFrame for which the summary needs to be generated.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing summary information for each column in 'df':
        - Type: Data type of the column.
        - Min: Minimum value in the column.
        - Max: Maximum value in the column.
        - Nan %: Percentage of NaN values in the column.
        - # Unique Values: Total number of unique values in the column.
        - Unique values: List of unique values in the column.

    Example
    -------
    >>> data = {
            'age': ['[40-50)', '[60-70)', '[70-80)'],
            'time_in_hospital': [8, 3, 5],
            'n_lab_procedures': [72, 34, 45],
            ...
        }
    >>> dataframe = pd.DataFrame(data)
    >>> result = dataframe_summary(df)
    >>> print(result)
               Type       Min        Max  Nan %  # Unique Values                                  Unique values
    Variables                                                                                                              
    age       object   [40-50)    [90-100)    0.0        3      ['[70-80)', '[50-60)', '[60-70)', '[40-50)', '[80-90)', ...
    time_in_hospital  int64    1           14    0.0        3        [8, 3, 5]
    n_lab_procedures  int64    1          113    0.0        3        [72, 34, 45]
    ...

    Note
    ----
    The function uses vectorized operations to improve performance and memory usage.
