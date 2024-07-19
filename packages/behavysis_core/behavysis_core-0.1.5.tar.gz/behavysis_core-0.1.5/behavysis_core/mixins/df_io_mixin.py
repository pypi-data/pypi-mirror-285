"""
Utility functions.
"""

from __future__ import annotations

import functools
import os
from enum import EnumType
from typing import Callable

import numpy as np
import pandas as pd

from behavysis_core.constants import DLC_HDF_KEY, KeypointsCN


class DFIOMixin:
    """__summary"""

    ###############################################################################################
    # DF Read/Write functions
    ###############################################################################################

    @staticmethod
    def __read_decorator(
        func: Callable[[str], pd.DataFrame],
    ) -> Callable[[str], pd.DataFrame]:
        """A decorator to catch errors when reading in a file."""

        @functools.wraps(func)
        def wrapper(fp: str):
            # Reading the file and sorting by index
            return func(fp).sort_index()

        return wrapper

    @staticmethod
    def __write_decorator(
        func: Callable[[pd.DataFrame, str], None],
    ) -> Callable[[pd.DataFrame, str], None]:
        """A decorator to catch errors when writing to a file."""

        @functools.wraps(func)
        def wrapper(df, fp: str):
            # Making the directory if it doesn't exist
            os.makedirs(os.path.split(fp)[0], exist_ok=True)
            # Writing the file
            return func(df, fp)

        return wrapper

    @staticmethod
    @__read_decorator
    def read_dlc_csv(fp: str) -> pd.DataFrame:
        """
        Reading DLC csv file.
        """
        col_levels = DFIOMixin.enum_to_list(KeypointsCN)
        return pd.read_csv(fp, header=np.arange(len(col_levels)).tolist(), index_col=0)

    @staticmethod
    @__write_decorator
    def write_dlc_csv(df: pd.DataFrame, fp: str) -> None:
        """
        Writing DLC dataframe to csv file.
        """
        df.to_csv(fp)

    @staticmethod
    @__read_decorator
    def read_h5(fp: str) -> pd.DataFrame:
        """
        Reading h5 file.
        """
        return pd.DataFrame(pd.read_hdf(fp, key=DLC_HDF_KEY, mode="r"))

    @staticmethod
    @__write_decorator
    def write_h5(df: pd.DataFrame, fp: str) -> None:
        """
        Writing dataframe h5 file.
        """
        df.to_hdf(fp, key=DLC_HDF_KEY, mode="w")

    @staticmethod
    @__read_decorator
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        return pd.read_feather(fp)

    @staticmethod
    @__write_decorator
    def write_feather(df: pd.Series | pd.DataFrame, fp: str) -> None:
        """
        Writing dataframe feather file.
        """
        df.to_feather(fp)

    ###############################################################################################
    # DF init functions
    ###############################################################################################

    @staticmethod
    def init_df(frame_vect: pd.Series | pd.Index) -> pd.DataFrame:
        """__summary__"""
        return pd.DataFrame(index=frame_vect)

    ###############################################################################################
    # DF Check functions
    ###############################################################################################

    @staticmethod
    def check_df(df: pd.DataFrame) -> None:
        """__summary__"""
        assert isinstance(df, pd.DataFrame), "The dataframe is not a pandas DataFrame."

    @staticmethod
    def check_df_index_names(
        df: pd.DataFrame, levels: EnumType | tuple[str] | str
    ) -> None:
        """__summary__"""
        # Converting `levels` to a tuple
        if isinstance(levels, EnumType):  # If Enum
            levels = DFIOMixin.enum_to_list(levels)
        elif isinstance(levels, str):  # If str
            levels = (levels,)
        assert (
            df.index.names == levels
        ), f"The index level is incorrect. Expected {levels} but got {df.index.name}."

    @staticmethod
    def check_df_column_names(
        df: pd.DataFrame, levels: EnumType | tuple[str] | str
    ) -> None:
        """__summary__"""
        # Converting `levels` to a tuple
        if isinstance(levels, EnumType):  # If Enum
            levels = DFIOMixin.enum_to_list(levels)
        elif isinstance(levels, str):  # If str
            levels = (levels,)
        assert (
            df.columns.names == levels
        ), f"The column level is incorrect. Expected {levels} but got {df.columns.name}."

    @staticmethod
    def enum_to_list(my_enum: EnumType) -> list[str]:
        """
        Useful helper function to convert an Enum to a list of its values.
        Used in `check_df` and `init_df` functions.
        """
        return [i.value for i in my_enum]
