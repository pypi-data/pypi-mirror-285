"""
_summary_
"""

import os
from typing import Optional

import matplotlib.pyplot as plt
from pydantic import BaseModel, ConfigDict, field_validator

from behavysis_core.constants import KeypointsCN
from behavysis_core.data_models.pydantic_base_model import PydanticBaseModel
from behavysis_core.data_models.vid_metadata import VidMetadata
from behavysis_core.mixins.df_io_mixin import DFIOMixin


class ConfigsFormatVid(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    width_px: Optional[int | str] = None
    height_px: Optional[int | str] = None
    fps: Optional[float | str] = None
    start_sec: Optional[float | str] = None
    stop_sec: Optional[float | str] = None


class ConfigsRunDLC(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    model_fp: str = os.path.join(".")  # FilePath


class ConfigsCalculateParams(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="allow")


class ConfigsPreprocess(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="allow")


class ConfigsExtractFeatures(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    individuals: list[str] | str = ["mouse1marked", "mouse2unmarked"]
    bodyparts: list[str] | str = [
        "LeftEar",
        "RightEar",
        "Nose",
        "BodyCentre",
        "LeftFlankMid",
        "RightFlankMid",
        "TailBase1",
        "TailTip4",
    ]


class ConfigsClassifyBehav(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    model_fp: str = os.path.join(".")  # FilePath
    pcutoff: float | str | None = None
    min_window_frames: int | str = 1
    user_behavs: list[str] | str = []


class ConfigsAnalyse(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="allow")

    bins_sec: list[int] | str = [30, 60, 120]
    custom_bins_sec: list[int] | str = [60, 120, 300, 600]


class ConfigsEvalKeypointsPlot(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    bodyparts: list[str] | str = [
        "LeftEar",
        "RightEar",
        "Nose",
        "BodyCentre",
        "LeftFlankMid",
        "RightFlankMid",
        "TailBase1",
        "TailTip4",
    ]


class ConfigsEvalVid(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    funcs: list[str] | str = ["keypoints"]
    pcutoff: float | str = 0.8
    colour_level: str = "individuals"
    radius: int | str = 3
    cmap: str = "rainbow"

    @field_validator("cmap")
    @classmethod
    def validate_cmap(cls, v):
        """_summary_"""
        return PydanticBaseModel.validate_attr_closed_set(v, plt.colormaps())

    @field_validator("colour_level")
    @classmethod
    def validate_colour_level(cls, v):
        """_summary_"""
        vals = DFIOMixin.enum_to_list(KeypointsCN)
        return PydanticBaseModel.validate_attr_closed_set(v, vals)


class ConfigsEvaluate(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    keypoints_plot: ConfigsEvalKeypointsPlot = ConfigsEvalKeypointsPlot()
    eval_vid: ConfigsEvalVid = ConfigsEvalVid()


class ConfigsUser(BaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    format_vid: ConfigsFormatVid = ConfigsFormatVid()
    run_dlc: ConfigsRunDLC = ConfigsRunDLC()
    calculate_params: ConfigsCalculateParams = ConfigsCalculateParams()
    preprocess: ConfigsPreprocess = ConfigsPreprocess()
    extract_features: ConfigsExtractFeatures = ConfigsExtractFeatures()
    classify_behaviours: list[ConfigsClassifyBehav] = list()
    analyse: ConfigsAnalyse = ConfigsAnalyse()
    evaluate: ConfigsEvaluate = ConfigsEvaluate()


class ConfigsAuto(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    raw_vid: VidMetadata = VidMetadata()
    formatted_vid: VidMetadata = VidMetadata()

    px_per_mm: Optional[float] = None
    start_frame: Optional[int] = None
    stop_frame: Optional[int] = None
    exp_dur_frames: Optional[int] = None


class ConfigsRef(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="allow")


class ExperimentConfigs(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    user: ConfigsUser = ConfigsUser()
    auto: ConfigsAuto = ConfigsAuto()
    ref: ConfigsRef = ConfigsRef()

    def get_ref(self, val: str):
        """
        If the val is in the reference format, then
        return reference value of the val if it exists in the reference store.
        Otherwise, return the val itself.
        """
        # Check if the value is in the reference format
        if isinstance(val, str) and val.startswith("--"):
            # Remove the '--' from the val
            val = val[2:]
            # Check if the value exists in the reference store
            assert hasattr(
                self.ref, val
            ), f"Value '{val}' can't be found in the configs reference section."
            # Return the reference value
            return getattr(self.ref, val)
        # Return the value itself
        return val
