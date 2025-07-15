"""
Captcha handler for the monitor
"""
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from ...utils import logger, notification_utils


class CaptchaHandler:
    """Handles captcha-related operations"""
    
    @staticmethod
    def check_captcha_image(driver: WebDriver) -> None:
        """Checks and extracts captcha image information"""
        try:
            logger.info("🔍 Checking captcha image...")
            
            # Look for captcha elements
            captcha_elements = driver.find_elements(By.CSS_SELECTOR, ".captcha img")
            if captcha_elements:
                logger.info(f"🔍 Found {len(captcha_elements)} captcha image(s)")
                
                for i, img in enumerate(captcha_elements):
                    try:
                        src = img.get_attribute("src")
                        if src:
                            if src.startswith("data:image"):
                                logger.info(f"🔍 Captcha image {i+1}: Base64 image found (length: {len(src)} chars)")
                                # Extract just the beginning to see if it's valid
                                if len(src) > 100:
                                    logger.info(f"🔍 Base64 starts with: {src[:100]}...")
                                else:
                                    logger.warning(f"⚠️  Base64 seems too short: {src}")
                            else:
                                logger.info(f"🔍 Captcha image {i+1}: URL image - {src}")
                        else:
                            logger.warning(f"⚠️  Captcha image {i+1}: No src attribute")
                    except Exception as e:
                        logger.warning(f"⚠️  Error checking captcha image {i+1}: {e}")
            else:
                logger.warning("⚠️  No captcha images found with .captcha img selector")
                
                # Try alternative selectors
                alt_selectors = ["img[src*='captcha']", "img[src*='data:image']", ".captcha", "img"]
                for selector in alt_selectors:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        logger.info(f"🔍 Found {len(elements)} elements with selector '{selector}'")
                        for elem in elements[:3]:  # Check first 3
                            try:
                                src = elem.get_attribute("src")
                                if src and "data:image" in src:
                                    logger.info(f"🔍 Found base64 image with selector '{selector}': {src[:50]}...")
                            except:
                                continue
                        break
                        
        except Exception as e:
            logger.error(f"❌ Error checking captcha image: {e}")
    
    @staticmethod
    def handle_captcha_detected(driver: WebDriver, timestamp: str, check_count: int, page_info: dict) -> None:
        """Handles when captcha is detected"""
        logger.warning(f"\n🔐 [{timestamp}] CAPTCHA DETECTED! (Check #{check_count})")
        logger.warning(f"📝 {page_info['description']}")
        logger.info("🔐 Action: Stopping refresh, waiting for manual captcha input...")
        
        # Try to extract captcha image info
        CaptchaHandler.check_captcha_image(driver)
        
        # Sound and visual notification (custom captcha sound)
        notification_utils.play_sound(1, "captcha")
        notification_utils.show_notification(
            "RDV Monitor - CAPTCHA", 
            "Manual intervention required! Type the captcha."
        )
        
        logger.info("🔐 Type the captcha manually - system will detect when completed...")
    
    @staticmethod
    def handle_captcha_waiting(timestamp: str, check_count: int) -> None:
        """Handles when waiting for captcha completion"""
        logger.info(f"⏳ [{timestamp}] CAPTCHA_WAIT: Still waiting for captcha completion... (Check #{check_count})")
    
    @staticmethod
    def handle_captcha_completed(timestamp: str, page_type: str) -> None:
        """Handles when captcha is completed"""
        logger.info(f"✅ [{timestamp}] CAPTCHA completed! Detected page change to: {page_type}")
        logger.info("✅ Resuming normal monitoring...") 