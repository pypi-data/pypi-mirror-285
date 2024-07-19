"""
Utility functions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import mode

from behavysis_core.constants import BehavCN, BehavColumns, BehavIN
from behavysis_core.data_models.bouts import Bouts
from behavysis_core.mixins.df_io_mixin import DFIOMixin

# TODO

class BehavMixin:
    """_summary_"""

    @staticmethod
    def vect_2_bouts(vect: np.ndarray | pd.Series) -> pd.DataFrame:
        """
        Will return a dataframe with the start and stop indexes of each contiguous set of
        positive values (i.e. a bout).

        Parameters
        ----------
        vect : np.ndarray | pd.Series
            Expects a vector of booleans

        Returns
        -------
        pd.DataFrame
            _description_
        """
        offset = 0
        if isinstance(vect, pd.Series):
            if vect.shape[0] > 0:
                offset = vect.index[0]
        # Getting stop and start indexes of each bout
        z = np.concatenate(([0], vect, [0]))
        start = np.flatnonzero(~z[:-1] & z[1:])
        stop = np.flatnonzero(z[:-1] & ~z[1:]) - 1
        bouts_ls = np.column_stack((start, stop)) + offset
        # Making dataframe
        bouts_df = pd.DataFrame(bouts_ls, columns=["start", "stop"])
        bouts_df["dur"] = bouts_df["stop"] - bouts_df["start"] + 1
        return bouts_df

    @staticmethod
    def frames_2_bouts(frames_df: pd.DataFrame) -> Bouts:
        """
        Frames df to bouts model object.
        """
        bouts_ls = []
        # For each behaviour
        for behav in frames_df.columns.unique(BehavCN.BEHAVIOURS.value):
            # Getting start-stop of each bout
            start_stop_df = BehavMixin.vect_2_bouts(frames_df[(behav, "pred")])
            # For each bout (i.e. start-stop pair)
            for _, row in start_stop_df.iterrows():
                # Getting only the frames in the current bout
                bout_frames_df = frames_df.loc[row["start"] : row["stop"]]
                # Preparing to make Bout model object
                bout_dict = {
                    "start": row["start"],
                    "stop": row["stop"],
                    "behaviour": behav,
                    "actual": int(
                        mode(bout_frames_df[(behav, BehavColumns.ACTUAL.value)]).mode
                    ),
                    "user_defined": {},
                }
                # Getting the mode value for the bout (actual, and specific user_behavs)
                for outcome, values in bout_frames_df[behav].items():
                    if outcome not in DFIOMixin.enum_to_list(BehavColumns):
                        bout_dict["user_defined"][str(outcome)] = int(mode(values).mode)
                # Making the Bout model object and appending to bouts_ls
                bouts_ls.append(bout_dict)
        # Making and return the Bouts model object
        return Bouts(
            start=frames_df.index[0], stop=frames_df.index[-1] + 1, bouts=bouts_ls
        )

    @staticmethod
    def include_outcome_behavs(
        df: pd.DataFrame, behav_outcomes: dict[str, tuple[str]]
    ) -> pd.DataFrame:
        """
        Adding the user_behavs columns to the df for each behaviour.

        Expects `behav_outcomes` to be a dictionary with the behaviour str
        as the key and a tuple of specific behaviour strs as the value.
        """
        # Keeping the `actual`, `pred`, and all user_behavs columns
        out_df = BehavMixin.init_df(df.index)
        a = BehavColumns.ACTUAL.value
        p = BehavColumns.PRED.value
        for behav, user_behavs in behav_outcomes.items():
            # Adding pred column
            out_df[(behav, p)] = df[(behav, p)].values
            # Adding actual column
            # TODO: quick flip but make more explicit
            out_df[(behav, a)] = df[(behav, p)].values * -1
            # Adding user_behav columns
            for i in user_behavs:
                out_df[(behav, i)] = 0
        # Ordering by "behaviours" level
        out_df = out_df.sort_index(axis=1, level=BehavCN.BEHAVIOURS.value)
        # Returning the new df
        return out_df

    @staticmethod
    def bouts_2_frames(bouts: Bouts) -> pd.DataFrame:
        """
        Bouts model object to frames df.
        """
        # Making columns
        all_behavs = {}  # behav: user_behav_ls pairs
        for bout in bouts.bouts:
            if bout.behaviour not in all_behavs:
                all_behavs[bout.behaviour] = {
                    BehavColumns.PRED.value,
                    BehavColumns.ACTUAL.value,
                }
            all_behavs[bout.behaviour] |= set(bout.user_defined.keys())

        # construct ret_df with index from given start and stop, and all_behavs dict
        ret_df = BehavMixin.init_df(np.arange(bouts.start, bouts.stop))
        for behav, outcomes in all_behavs.items():
            for outcome in outcomes:
                ret_df[(behav, outcome)] = 0
        ret_df = ret_df.sort_index(axis=1)
        # Filling in all user_behavs columns for each behaviour
        for bout in bouts.bouts:
            bout_ret_df = ret_df.loc[bout.start : bout.stop]
            # Filling in predicted behaviour column
            bout_ret_df.loc[:, (bout.behaviour, BehavColumns.PRED.value)] = 1
            # Filling in actual behaviour column
            bout_ret_df.loc[:, (bout.behaviour, BehavColumns.ACTUAL.value)] = (
                bout.actual
            )
            # Filling in user_behavs columns
            for k, v in bout.user_defined.items():
                bout_ret_df.loc[:, (bout.behaviour, k)] = v
        # Returning frames df
        return ret_df

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
            index=pd.Index(frame_vect, name=DFIOMixin.enum_to_list(BehavIN)[0]),
            columns=pd.MultiIndex.from_tuples(
                (), names=DFIOMixin.enum_to_list(BehavCN)
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
        DFIOMixin.check_df_index_names(df, BehavIN)
        # Checking that the column levels are correct
        DFIOMixin.check_df_column_names(df, BehavCN)

    @staticmethod
    def read_feather(fp: str) -> pd.DataFrame:
        """
        Reading feather file.
        """
        # Reading
        df = DFIOMixin.read_feather(fp)
        # Checking
        BehavMixin.check_df(df)
        # Returning
        return df

    @staticmethod
    def update_behav(df: pd.DataFrame, behav_src: str, behav_dst: str) -> pd.DataFrame:
        """
        Update the behaviour column with the given outcome and value.
        """
        # Getting columns
        columns = df.columns.to_frame(index=False)
        # Updating the behaviour column
        columns[BehavCN.BEHAVIOURS.value] = columns[BehavCN.OUTCOMES.value].map(
            lambda x: behav_dst if x == behav_src else x
        )
        # Setting the new columns
        df.columns = pd.MultiIndex.from_frame(columns)
        # Returning
        return df

    @staticmethod
    def import_boris_tsv(fp: str, behavs_ls: list[str], start_frame: int, stop_frame: int) -> pd.DataFrame:
        """
        Importing Boris TSV file.
        """
        # Making df structure
        df = BehavMixin.init_df(np.arange(start_frame, stop_frame))
        # Reading in corresponding BORIS tsv file
        df_boris = pd.read_csv(fp, sep="\t")
        # Initialising new classification column based on BORIS filename and behaviour name
        # TODO: how to reconcile this with the behavs_ls?
        for behav in df_boris["Behavior"].unique():
            df[(behav, BehavColumns.ACTUAL.value)] = 0
            df[(behav, BehavColumns.PRED.value)] = 0
        for behav in behavs_ls:
            df[(behav, BehavColumns.ACTUAL.value)] = 0
            df[(behav, BehavColumns.PRED.value)] = 0
        # Setting the classification values from the BORIS file
        for ind, row in df_boris.iterrows():
            # Getting corresponding frame of this event point
            behav = row["Behavior"]
            frame = row["Image index"]
            status = row["Behavior type"]
            # Updating the classification in the scored df
            df.loc[frame:, (behav, BehavColumns.ACTUAL.value)] = status == "START"
            df.loc[frame:, (behav, BehavColumns.PRED.value)] = status == "START"
        # Setting dtype to int8
        df = df.astype(np.int8)
        return df
