"""
_summary_
"""

from typing import Optional

from pydantic import ConfigDict

from behavysis_core.data_models.pydantic_base_model import PydanticBaseModel


class VidMetadata(PydanticBaseModel):
    """_summary_"""

    model_config = ConfigDict(extra="forbid")

    fps: Optional[float] | str = None
    width_px: Optional[int] | str = None
    height_px: Optional[int] | str = None
    total_frames: Optional[int] | str = None
