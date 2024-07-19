"""
_summary_
"""

from enum import Enum

####################################################################################################
# PIPELINE FOLDERS
####################################################################################################


class Folders(Enum):
    """Enum for the pipeline folders."""

    CONFIGS = "0_configs"
    RAW_VID = "1_raw_vid"
    FORMATTED_VID = "2_formatted_vid"
    DLC = "3_dlc"
    PREPROCESSED = "4_preprocessed"
    FEATURES_EXTRACTED = "5_features_extracted"
    PREDICTED_BEHAVS = "6_predicted_behavs"
    SCORED_BEHAVS = "7_scored_behavs"


FILE_EXTS = {
    Folders.CONFIGS: ".json",
    Folders.RAW_VID: ".mp4",
    Folders.FORMATTED_VID: ".mp4",
    Folders.DLC: ".feather",
    Folders.PREPROCESSED: ".feather",
    Folders.FEATURES_EXTRACTED: ".feather",
    Folders.PREDICTED_BEHAVS: ".feather",
    Folders.SCORED_BEHAVS: ".feather",
}

ANALYSIS_DIR = "8_analysis"
DIAGNOSTICS_DIR = "0_diagnostics"
EVALUATE_DIR = "9_evaluate"
TEMP_DIR = ".temp"

####################################################################################################
# KEYPOINTS DATAFRAME CONSTANTS
####################################################################################################


class FramesIN(Enum):
    """Enum for the index in frame-by-frame dataframe."""

    FRAME = "frame"


class KeypointsCN(Enum):
    """Enum for the columns in the keypoints dataframe."""

    ("scorer", "individuals", "bodyparts", "coords")

    SCORER = "scorer"
    INDIVIDUALS = "individuals"
    BODYPARTS = "bodyparts"
    COORDS = "coords"


class Coords(Enum):
    """Enum for the coordinates in the keypoints dataframe."""

    X = "x"
    Y = "y"
    LIKELIHOOD = "likelihood"


KeypointsIN = FramesIN

DLC_HDF_KEY = "data"


class IndivColumns(Enum):
    """Enum for the individuals level in the columns of the keypoints dataframe."""

    SINGLE = "single"
    PROCESS = "processed"  # TODO: remove this


####################################################################################################
# EXTRACTED FEATURES DATAFRAME CONSTANTS
####################################################################################################


class FeaturesCN(Enum):
    """Enum for the columns in the extracted features dataframe."""

    FEATURES = "features"


FeaturesIN = FramesIN

####################################################################################################
# BEHAVIOUR DATAFRAME CONSTANTS
####################################################################################################


class BehavCN(Enum):
    """Enum for the columns in the behaviour dataframe."""

    BEHAVIOURS = "behaviours"
    OUTCOMES = "outcomes"


BehavIN = FramesIN


class BehavColumns(Enum):
    """Enum for the columns in the behaviour dataframe."""

    PROB = "prob"
    PRED = "pred"
    ACTUAL = "actual"


####################################################################################################
# ANALYSIS DATAFRAME CONSTANTS
####################################################################################################


class AnalysisCN(Enum):
    """Enum for the columns in the analysis dataframe."""

    INDIVIDUALS = "individuals"
    MEASURES = "measures"


AnalysisIN = FramesIN


class AggAnalysisCN(Enum):
    """Enum for the columns in the aggregated analysis dataframe."""

    INDIVIDUALS = "individuals"
    MEASURES = "measures"
    AGGS = "aggs"


AggAnalysisIN = FramesIN

####################################################################################################
# DIAGNOSTICS CONSTANTS
####################################################################################################

DIAGNOSTICS_SUCCESS_MESSAGES = (
    "Success! Success! Success!!",
    "Done and DONE!!",
    "Yay! Completed!",
    "This process was completed. Good on you :)",
    "Thumbs up!",
    "Woohoo!!!",
    "Phenomenal!",
    ":) :) :) :) :)",
    "Go you!",
    "You are doing awesome!",
    "You got this!",
    "You're doing great!",
    "Sending good vibes.",
    "I believe in you!",
    "You're a champion!",
    "No task too tall :) :)",
    "A job done well, and a well done job!",
    "Top job!",
)

STR_DIV = "".ljust(50, "-")


####################################################################################################
# PLOT CONSTANTS
####################################################################################################

PLOT_STYLE = "whitegrid"
PLOT_DPI = 75
