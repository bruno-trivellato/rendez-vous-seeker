"""
Delay utilities for the monitor
"""
import time
from typing import Optional

from ...config import config
from ...utils import logger, anti_detection


class DelayManager:
    """Manages different types of delays for the monitor"""
    
    @staticmethod
    def smart_delay() -> None:
        """Implements intelligent delay with anti-detection"""
        if config.anti_detection.enable_random_delays:
            delay = anti_detection.get_random_delay()
            logger.info(f"⏳ Random delay: {delay:.1f} seconds")
            time.sleep(delay)
        else:
            logger.info(f"⏳ Fixed delay: {config.monitoring.base_interval} seconds")
            time.sleep(config.monitoring.base_interval)
    
    @staticmethod
    def captcha_wait_delay() -> None:
        """Short delay when waiting for captcha input"""
        logger.info("⏳ CAPTCHA_WAIT: Short delay (1s) while waiting for manual captcha input...")
        time.sleep(1)
        logger.info("✅ CAPTCHA_WAIT: Delay completed, checking again...")
    
    @staticmethod
    def available_slots_delay() -> None:
        """Delay when slots are available"""
        logger.info("⏳ Short delay (30s) while slots are available...")
        time.sleep(30)
    
    @staticmethod
    def blocked_page_delay() -> None:
        """Delay when page is blocked"""
        logger.info("⏳ Waiting 30 seconds due to BLOCKED page...")
        time.sleep(30)
    
    @staticmethod
    def maintenance_delay() -> None:
        """Delay when page is in maintenance"""
        logger.info("⏳ Waiting 60 seconds due to MAINTENANCE...")
        time.sleep(60)
    
    @staticmethod
    def error_delay() -> None:
        """Delay when there's an error"""
        logger.info("⏳ Waiting 45 seconds due to ERROR...")
        time.sleep(45)
    
    @staticmethod
    def loading_delay() -> None:
        """Delay when page is loading"""
        logger.info("⏳ Waiting 5 seconds due to LOADING...")
        time.sleep(5) 