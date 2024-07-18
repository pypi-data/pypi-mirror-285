"""
This submodule contains the classes that define the different campaigns that
can be run.
"""

from .glitcher_gui import GlitcherGUI
from .target_gui import TargetGUI
from .skip_campaign import SkipCampaign
from .verify_pin_campaign import VerifyPinCampaign
from .skip_max_attempts_campaign import SkipMaxAttemptsCampaign
from .pfa_campaign import PfaCampaign

__all__ = [
    "GlitcherGUI",
    "TargetGUI",
    "SkipCampaign",
    "VerifyPinCampaign",
    "SkipMaxAttemptsCampaign",
    "PfaCampaign",
]
