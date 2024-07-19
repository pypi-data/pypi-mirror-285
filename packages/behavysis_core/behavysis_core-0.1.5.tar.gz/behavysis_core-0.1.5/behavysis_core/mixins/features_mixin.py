"""
Utility functions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from behavysis_core.constants import FeaturesCN, FeaturesIN, IndivColumns
from behavysis_core.mixins.df_io_mixin import DFIOMixin


class FeaturesMixin:
    """__summary__"""

    @staticmethod
    def check_bpts_exist(df: pd.DataFrame, bodyparts: list) -> None:
        """
        _summary_

        Parameters
        ----------
        df : pd.DataFrame
            _description_
        bodyparts : list
            _description_

        Raises
        ------
        ValueError
            _description_
        """
        # Checking that the bodyparts are all valid:
        bodyparts_exist = np.isin(bodyparts, df.columns.unique("bodyparts"))
        if not bodyparts_exist.all():
            msg = (
                "Some bodyparts in the config file are missing from the csv file.\n"
                + "They are:\n"
            )
            for bp in np.array(bodyparts)[~bodyparts_exist]:
                msg += f"    - {bp}\n"
            raise ValueError(msg)

    @staticmethod
    def get_headings(df: pd.DataFrame) -> tuple[list[str], list[str]]:
        """
        Returns a tuple of the individuals (animals, not "single"), and tuple of the multi-animal
        bodyparts.

        Parameters
        ----------
        df : pd.DataFrame
            Keypoints pd.DataFrame.

        Returns
        -------
        tuple[list[str], list[str]]
            `(indivs_ls, bpts_ls)` tuples. It is recommended to unpack these vals.
        """
        # Getting column MultiIndex
        columns = df.columns
        # Filtering out any single and processing columns
        for i in [IndivColumns.PROCESS.value, IndivColumns.SINGLE.value]:
            if i in columns.unique("individuals"):
                columns = columns.drop(i, level="individuals")
        # Getting individuals list
        indivs = columns.unique("individuals").to_list()
        # Getting bodyparts list
        bpts = columns.unique("bodyparts").to_list()
        return indivs, bpts

    @staticmethod
    def init_df(frame_vect: pd.Series | pd.Index) -> pd.DataFrame:
        """
        Returning a frame-by-frame analysis_df with the frame number (according to original video)
        as the MultiIndex index, relative to the first element of frame_vect.
        Note that that the frame number can thus begin on a non-zero number.

        Parameters
        ----------
        frame_vect : pd.Series | pd.Index
            _description_

        Returns
        -------
        pd.DataFrame
            _description_
        """
        return pd.DataFrame(
            index=pd.Index(frame_vect, name=DFIOMixin.enum_to_list(FeaturesIN)[0]),
            columns=pd.MultiIndex.from_tuples(
                (), names=DFIOMixin.enum_to_list(FeaturesCN)
            ),
        )

    @staticmethod
    def check_df(df: pd.DataFrame) -> None:
        """
        Checks whether the dataframe is in the correct format for the keypoints functions.

        Checks that:

        - There are no null values.
        - The column levels are correct.
        - The index levels are correct.
        """
        # Checking for null values
        assert not df.isnull().values.any(), "The dataframe contains null values. Be sure to run interpolate_points first."
        # Checking that the index levels are correct
        DFIOMixin.check_df_index_names(df, FeaturesIN)
        # Checking that the column levels are correct
        DFIOMixin.check_df_column_names(df, FeaturesCN)

    @staticmethod
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        # Reading
        df = DFIOMixin.read_feather(fp)
        # Checking
        FeaturesMixin.check_df(df)
        # Returning
        return df
