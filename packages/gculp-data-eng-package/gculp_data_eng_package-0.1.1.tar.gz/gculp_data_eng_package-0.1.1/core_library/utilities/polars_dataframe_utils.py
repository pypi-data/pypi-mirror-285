"""
Utilities for working with polars dataframes
"""
from datetime import datetime
from typing import Dict, List, Optional, Union

import polars as pl
from polars.type_aliases import FrameInitTypes

from core_library.utilities.misc_utils import hash_func, setup_console_logger
from core_library.utilities.text_utils import cols_text_to_standard

mds_logger = setup_console_logger()


def pl_create_df(data: FrameInitTypes, schema: Optional[Dict] = None) -> pl.DataFrame:
    """Create a Polars Dataframe

    :param data: Data to create DF
    :type data: FrameInitTypes
    :param schema: Schema dictionary for the polars dataframe
    :type schema: Dict
    :return: Polars Dataframe
    :rtype: pl.DataFrame
    """
    mds_logger.info("Converting to dataframe")
    df = pl.DataFrame(data=data, schema=schema)
    return df


def pl_df_cols_to_standard(df: pl.DataFrame, upper: bool = True):
    """Convert polars dataframe columns to standard used"""
    mds_logger.info("Converting dataframe cols to standard")
    for col in df.columns:
        new_col = cols_text_to_standard(col, upper=upper)
        df = df.rename({col: new_col})

    return df


def pl_concat_dfs(list_of_dfs: List[pl.DataFrame], **kwargs) -> pl.DataFrame:
    """
    Helpful function to take in a list of dataframes and concatenate them

    :param list_of_dfs: List of dataframes
    :type list_of_dfs: List[pl.DataFrame]
    :return: One dataframe
    :rtype: pl.DataFrame
    """

    result_df = pl.concat(items=list_of_dfs, **kwargs)

    return result_df


def pl_aggregate_column(
    df: pl.DataFrame, column_name: str, agg_type: str
) -> Union[int, str, datetime, None]:
    """
    Aggregate a single column and get back one record as a native python type

    :param df: Dataframe to aggregate
    :type df: pl.DataFrame
    :param column_name: Column to aggregate
    :type column_name: str
    :param agg_type: type of aggregation to use
    :type agg_type: str
    :return: Result from dataframe in native python type
    :rtype: Union[int, str, datetime, None]
    """
    result = None

    if df.is_empty():
        mds_logger.info("Empty Dataframe")
        return result

    if agg_type == "max":
        result = df.select(pl.col(column_name)).max()[column_name][0]
    elif agg_type == "min":
        result = df.select(pl.col(column_name)).min()[column_name][0]

    return result


def pl_log_dataframe(
    df: pl.DataFrame,
    n_rows: int = 3,
    order_by: Optional[str] = None,
    ascending: Optional[bool] = None,
    only_cols: Optional[bool] = False,
) -> None:
    """
    Log a dataframe helpful for viewing at different stages

    :param df: Polars dataframe to log
    :type df: pl.DataFrame
    :param n_rows: Number of records to show
    :type n_rows: int
    :param order_by: If you want to order the dataframe, defaults to None
    :type order_by: Optional[str], optional
    :param ascending: Sort order if passing in order_by col, defaults to None
    :type ascending: Optional[bool], optional
    """
    # TODO: Implement this functionality
    if (order_by and not ascending) or (ascending and not order_by):
        Exception("order_by and ascending arguments are both required")

    if only_cols:
        mds_logger.info(f"DF Columns: {df.columns}")
        return None

    mds_logger.info("Dataframe Preview:")
    # TODO: If there are a lot of columns it is weird

    mds_logger.info(df)
    return None


def pl_check_empty_df(df: pl.DataFrame) -> bool:
    """
    Check if a dataframe is empty

    :param df: Input dataframe
    :type df: pl.DataFrame
    :return: True if empty
    :rtype: bool
    """
    if df.is_empty():
        mds_logger.info("Dataframe is emtpy")
        return True
    return False


def pl_concat_str(
    df: pl.DataFrame, cols: Union[List[str], str], alias: str, ignore_nulls: bool = True
) -> pl.DataFrame:
    """
    Concatenate columns together

    :param df: Input Dataframe
    :type df: pl.DataFrame
    :param cols: Columns to concatenate together
    :type cols: Union[List[str], str]
    :param alias: Output column name
    :type alias: str
    :param ignore_nulls: If false nulls will returrn nulls, defaults to True
    :type ignore_nulls: bool, optional
    :return: Output Dataframe
    :rtype: pl.DataFrame
    """
    df = df.with_columns(pl.concat_str(cols, ignore_nulls=ignore_nulls).alias(alias))
    return df


def pl_hash_func(
    df: pl.DataFrame,
    cols: Union[str, List],
    alias: str = "KEY_HASH",
    drop_concat_col: bool = False,
) -> pl.DataFrame:
    """
    Dataframe hash a list of cols - will automatically concat them together if multiple

    :param df: Dataframe to hash
    :type df: pl.DataFrame
    :param cols: Cols to hash
    :type cols: Union[str, List]
    :param alias: New column name, defaults to 'KEY_HASH'
    :type alias: str, optional
    :return: Hashed Dataframe
    :rtype: pl.DataFrame
    """
    df = pl_concat_str(df, cols=cols, alias="KEY_CONCAT")

    df = df.with_columns(pl.col("KEY_CONCAT").map_elements(hash_func).alias(alias))

    if drop_concat_col:
        df = df.drop("KEY_CONCAT")

    return df


def pl_add_standard_cols(df: pl.DataFrame, hash_cols: List[str]) -> pl.DataFrame:
    """
    Adds standard cols to a dataframe on ingestions

    :param df: Dataframe to add cols to
    :type df: pl.DataFrame
    :param hash_cols: What columns to hash
    :type hash_cols: List[str]
    :return: Standard Dataframe
    :rtype: pl.DataFrame
    """
    mds_logger.info("Adding hash cols and ingestion time to dataframe")

    # Add a hash column of the unique keys
    df = pl_hash_func(df, hash_cols)

    # Add an ETL timestamp column
    df = df.with_columns(INGESTION_DATE_TIME=datetime.now())

    return df
