"""
Page handlers for the monitor
"""
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from ...utils import logger
from ...page_detector import PageType
from .captcha_handler import CaptchaHandler
from .availability_handler import AvailabilityHandler


class PageHandlers:
    """Handles different page types"""
    
    @staticmethod
    def handle_blocked_page(driver: WebDriver, timestamp: str, page_info: dict, driver_manager) -> None:
        """Handles blocked page"""
        logger.warning(f"🚫 [{timestamp}] BLOCKED! {page_info['description']}")
        logger.warning(f"📋 Reason: {page_info.get('blocked_reason', 'Not specified')}")
        
        # Log detailed blocked page analysis
        driver_manager.log_blocked_page_content()
        
        logger.info("⏳ Waiting before next attempt...")
        logger.info("⏳ Waiting 30 seconds due to BLOCKED page...")
        time.sleep(30)  # Wait longer if blocked
    
    @staticmethod
    def handle_maintenance_page(timestamp: str, page_info: dict) -> None:
        """Handles maintenance page"""
        logger.warning(f"🔧 [{timestamp}] MAINTENANCE! {page_info['description']}")
        logger.info("⏳ Waiting before next attempt...")
        logger.info("⏳ Waiting 60 seconds due to MAINTENANCE...")
        time.sleep(60)  # Wait longer if in maintenance
    
    @staticmethod
    def handle_error_page(timestamp: str, page_info: dict) -> None:
        """Handles error page"""
        logger.error(f"❌ [{timestamp}] ERROR! {page_info['description']}")
        logger.info("⏳ Waiting before next attempt...")
        logger.info("⏳ Waiting 45 seconds due to ERROR...")
        time.sleep(45)  # Wait longer if error
    
    @staticmethod
    def handle_loading_page(timestamp: str, page_info: dict) -> None:
        """Handles loading page"""
        logger.info(f"⏳ [{timestamp}] Loading... {page_info['description']}")
        logger.info("⏳ Waiting 5 seconds due to LOADING...")
        time.sleep(5)  # Wait a bit more if loading
    
    @staticmethod
    def handle_initial_page(driver: WebDriver, timestamp: str) -> bool:
        """Handles initial page - tries to click 'Prendre un rendez-vous' button"""
        logger.info(f"🏠 [{timestamp}] Back to initial page - need to navigate again")
        logger.info("🔘 Action: Attempting to click 'Prendre un rendez-vous' button...")
        
        if PageHandlers._click_prendre_rdv_button(driver):
            logger.info("🔘 Successfully clicked 'Prendre un rendez-vous'")
            return True
        else:
            logger.warning("⚠️  Could not find 'Prendre un rendez-vous' button")
            logger.info("🔄 Will retry on next check...")
            return False
    
    @staticmethod
    def handle_navigation_complete(timestamp: str, page_info: dict) -> None:
        """Handles when navigation is complete"""
        logger.info(f"📄 [{timestamp}] Navigated to appointment page - {page_info['description']}")
        logger.info("✅ Action: Transitioning to monitoring state...")
        logger.info("✅ Starting availability monitoring...")
    
    @staticmethod
    def _click_prendre_rdv_button(driver: WebDriver) -> bool:
        """Tries to click the 'Prendre un rendez-vous' button"""
        try:
            logger.info("🔍 Looking for 'Prendre un rendez-vous' button...")
            
            # Specific selectors for the exact button
            specific_selectors = [
                "a[href='/rdvpref/reservation/demarche/3720/cgu/']",
                "a.bg-primary[href*='cgu']",
                "a.q-btn[href*='cgu']",
                "a[href*='cgu']"
            ]
            
            # Try specific selectors first
            for selector in specific_selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    element_text = element.text.lower().strip()
                    if "prendre un rendez-vous" in element_text:
                        logger.info(f"🔘 Found specific button: '{element.text}' with selector: {selector}")
                        
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        logger.info("⏳ Waiting 0.5 seconds after scrolling to element...")
                        time.sleep(0.5)
                        
                        # Click the element
                        logger.info("🔘 Attempting to click...")
                        element.click()
                        logger.info("⏳ Waiting 3 seconds after clicking...")
                        time.sleep(3)  # Wait for navigation
                        
                        logger.info("✅ Button clicked successfully")
                        return True
            
            # Fallback to general search
            logger.info("🔍 Specific button not found, trying general search...")
            
            # Get all clickable elements
            all_elements = []
            
            # Try different selectors for the button
            selectors = [
                "a[href*='prendre']",
                "a[href*='rdv']", 
                "a[href*='rendez-vous']",
                "button[onclick*='prendre']",
                "button[onclick*='rdv']",
                "a",
                "button",
                "input[type='submit']",
                "input[type='button']"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                all_elements.extend(elements)
                logger.info(f"🔍 Found {len(elements)} elements with selector: {selector}")
            
            # Remove duplicates
            unique_elements = []
            seen_texts = set()
            for element in all_elements:
                try:
                    element_text = element.text.lower().strip()
                    if element_text and element_text not in seen_texts:
                        unique_elements.append(element)
                        seen_texts.add(element_text)
                except:
                    continue
            
            logger.info(f"🔍 Total unique elements found: {len(unique_elements)}")
            
            # Log all element texts for debugging
            for i, element in enumerate(unique_elements[:10]):  # Log first 10
                try:
                    text = element.text.strip()
                    if text:
                        logger.info(f"🔍 Element {i+1}: '{text}'")
                except:
                    continue
            
            # Look for the button
            for element in unique_elements:
                try:
                    element_text = element.text.lower().strip()
                    if any(keyword in element_text for keyword in [
                        "prendre un rendez-vous",
                        "prendre rendez-vous", 
                        "prendre rdv",
                        "prendre un rdv",
                        "rendez-vous",
                        "rdv"
                    ]):
                        logger.info(f"🔘 Found button: '{element.text}'")
                        
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        logger.info("⏳ Waiting 0.5 seconds after scrolling to element...")
                        time.sleep(0.5)
                        
                        # Click the element
                        logger.info("🔘 Attempting to click...")
                        element.click()
                        logger.info("⏳ Waiting 3 seconds after clicking...")
                        time.sleep(3)  # Wait for navigation
                        
                        logger.info("✅ Button clicked successfully")
                        return True
                except Exception as e:
                    logger.warning(f"⚠️  Error with element '{element.text}': {e}")
                    continue
            
            logger.warning("❌ 'Prendre un rendez-vous' button not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error clicking 'Prendre un rendez-vous' button: {e}")
            return False 