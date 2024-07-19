"""
Utility functions.
"""

from __future__ import annotations

import os
from typing import Callable, Optional

import numpy as np
import pandas as pd

from behavysis_core.constants import DIAGNOSTICS_SUCCESS_MESSAGES


class DiagnosticsMixin:
    """__summary__"""

    @staticmethod
    def success_msg() -> str:
        """
        Return a random positive message :)
        """
        return np.random.choice(DIAGNOSTICS_SUCCESS_MESSAGES)

    @staticmethod
    def warning_msg(func: Optional[Callable] = None):
        """
        Return a warning message for the given function.
        """
        if not func:
            # Getting the name of the calling function
            func_name = "func"
        else:
            func_name = func.__name__
        return (
            "WARNING: Output file already exists - not overwriting file.\n"
            + f"To overwrite, specify `{func_name}(..., overwrite=True)`.\n"
        )

    @staticmethod
    def read_diagnostics(fp):
        """
        __summary__
        """
        return pd.read_csv()

    @staticmethod
    def load_diagnostics(fp: str) -> pd.DataFrame:
        """
        Reads the data from the diagnostics file with the given name.
        """
        return pd.read_csv(fp, index_col=0).sort_index()

    @staticmethod
    def save_diagnostics(df: pd.DataFrame, fp: str) -> None:
        """
        Writes the given data to a diagnostics file with the given name.
        """
        # Making a folder if it does not exist
        os.makedirs(os.path.split(fp)[0], exist_ok=True)
        # Writing diagnostics file
        df.to_csv(fp)
