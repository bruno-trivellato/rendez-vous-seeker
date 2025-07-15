"""
Monitor states for the Rendez-vous system
"""
from enum import Enum


class MonitorState(Enum):
    """States of the monitoring process"""
    INITIAL = "initial"
    NAVIGATING = "navigating"
    CAPTCHA_WAIT = "captcha_wait"
    MONITORING = "monitoring"
    AVAILABLE = "available" 