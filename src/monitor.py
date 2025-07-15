"""
Main monitor for the Rendez-vous system
"""
import time
import signal
import sys
import hashlib
from typing import Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .config import config
from .utils import logger, anti_detection, time_utils, hash_utils, notification_utils
from .driver_manager import DriverManager
from .page_detector import page_detector, PageType


class RDVMonitor:
    """Main monitor to detect appointment availability"""
    
    def __init__(self):
        self.driver_manager = DriverManager()
        self.running = True
        self.last_page_hash: Optional[str] = None
        self.check_count = 0
        self.start_time = time.time()
        
        # Configure signal handler to stop gracefully
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler for Ctrl+C and SIGTERM"""
        logger.info("\n🛑 Stopping the monitor...")
        self.running = False
        self.driver_manager.quit()
        sys.exit(0)
    
    def start(self):
        """Starts the monitoring"""
        try:
            logger.info("🚀 Starting Rendez-vous monitor...")
            logger.info(f"📍 URL: {config.monitoring.url}")
            logger.info(f"⏱️  Base interval: {config.monitoring.base_interval} seconds")
            logger.info(f"🎯 Anti-detection: {'Enabled' if config.anti_detection.enable_random_delays else 'Disabled'}")
            logger.info("🛑 Press Ctrl+C to stop\n")
            
            # Initialize the driver
            self.driver_manager.setup_driver()
            driver = self.driver_manager.get_driver()
            
            if driver is None:
                logger.error("❌ Failed to initialize driver")
                return
            
            # Load the initial page
            driver.get(config.monitoring.url)
            time.sleep(3)  # Wait for initial loading
            
            # First check
            self.last_page_hash = self._get_page_hash(driver)
            logger.info("✅ Page loaded initially")
            
            # Main monitoring loop
            self._monitoring_loop(driver)
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
        finally:
            self.driver_manager.quit()
    
    def _monitoring_loop(self, driver):
        """Main monitoring loop"""
        while self.running:
            try:
                # Check if session should be rotated
                if anti_detection.should_rotate_session():
                    logger.info("🔄 Rotating session for security...")
                    self.driver_manager.rotate_session()
                    driver = self.driver_manager.get_driver()
                    if driver is None:
                        logger.error("❌ Failed to get driver after rotation")
                        continue
                    driver.get(config.monitoring.url)
                
                # Page refresh
                if driver is not None:
                    driver.refresh()
                    time.sleep(2)  # Wait for loading
                
                # Detect current page type
                if driver is not None:
                    page_info = page_detector.get_page_info(driver)
                    page_type = page_info["type"]
                    
                    # Generate hash of new page
                    current_hash = self._get_page_hash(driver)
                    self.check_count += 1
                    
                    timestamp = time_utils.get_timestamp()
                    
                    # Log based on page type
                    if page_type == PageType.BLOCKED:
                        logger.warning(f"🚫 [{timestamp}] BLOCKED! {page_info['description']}")
                        logger.warning(f"📋 Reason: {page_info.get('blocked_reason', 'Not specified')}")
                        logger.info("⏳ Waiting before next attempt...")
                        time.sleep(30)  # Wait longer if blocked
                        continue
                        
                    elif page_type == PageType.MAINTENANCE:
                        logger.warning(f"🔧 [{timestamp}] MAINTENANCE! {page_info['description']}")
                        logger.info("⏳ Waiting before next attempt...")
                        time.sleep(60)  # Wait longer if in maintenance
                        continue
                        
                    elif page_type == PageType.ERROR:
                        logger.error(f"❌ [{timestamp}] ERROR! {page_info['description']}")
                        logger.info("⏳ Waiting before next attempt...")
                        time.sleep(45)  # Wait longer if error
                        continue
                        
                    elif page_type == PageType.LOADING:
                        logger.info(f"⏳ [{timestamp}] Loading... {page_info['description']}")
                        time.sleep(5)  # Wait a bit more if loading
                        continue
                        
                    elif page_type == PageType.CAPTCHA:
                        logger.warning(f"\n🔐 [{timestamp}] CAPTCHA DETECTED! (Check #{self.check_count})")
                        logger.warning(f"📝 {page_info['description']}")
                        
                        # Sound and visual notification
                        notification_utils.play_sound()
                        notification_utils.show_notification(
                            "RDV Monitor - CAPTCHA", 
                            "Manual intervention required! Type the captcha."
                        )
                        
                        logger.info("🔐 Type the captcha manually and press Enter to continue...")
                        input("Press Enter when you finish the captcha...")
                        continue
                        
                    elif page_type == PageType.INITIAL:
                        logger.info(f"\n🏠 [{timestamp}] INITIAL PAGE DETECTED! (Check #{self.check_count})")
                        logger.info(f"📝 {page_info['description']}")
                        
                        # Try to click the "Prendre un rendez-vous" button
                        try:
                            from selenium.webdriver.common.by import By
                            buttons = driver.find_elements(By.TAG_NAME, "a")
                            for button in buttons:
                                if "prendre un rendez-vous" in button.text.lower():
                                    logger.info("🔘 Clicking on 'Prendre un rendez-vous'...")
                                    button.click()
                                    time.sleep(3)  # Wait for loading
                                    break
                            else:
                                logger.warning("⚠️  'Prendre un rendez-vous' button not found")
                        except Exception as e:
                            logger.error(f"❌ Error clicking button: {e}")
                        
                        continue
                        
                    elif page_type == PageType.AVAILABLE:
                        logger.info(f"\n🎉 [{timestamp}] AVAILABLE SLOTS! (Check #{self.check_count})")
                        logger.info(f"📝 Details: {page_info['description']}")
                        
                        # Sound and visual notification
                        notification_utils.play_sound()
                        notification_utils.show_notification(
                            "RDV Monitor - AVAILABLE SLOTS!", 
                            "Open the browser to schedule!"
                        )
                        
                        # Show availability details
                        availability_details = page_info.get('availability_details', {})
                        if availability_details.get('buttons'):
                            logger.info(f"🔘 Buttons: {', '.join(availability_details['buttons'])}")
                        if availability_details.get('links'):
                            logger.info(f"🔗 Links: {', '.join(availability_details['links'])}")
                        
                        logger.info("🔗 Open the browser manually to schedule!")
                        
                        # Keep the page open for the user
                        input("\nPress Enter to continue monitoring or Ctrl+C to stop...")
                        
                    elif page_type == PageType.UNAVAILABLE:
                        if current_hash != self.last_page_hash:
                            logger.info(f"\n🔄 [{timestamp}] CHANGE DETECTED! (Check #{self.check_count})")
                            logger.info(f"ℹ️  {page_info['description']}")
                            self.last_page_hash = current_hash
                        else:
                            if config.logging.show_check_count:
                                logger.info(f"[{timestamp}] Check #{self.check_count} - {page_info['description']}")
                            else:
                                logger.info(f"[{timestamp}] {page_info['description']}")
                                
                    else:  # UNKNOWN or others
                        logger.warning(f"❓ [{timestamp}] Unknown page: {page_info['description']}")
                        logger.info(f"📄 Title: {page_info['title']}")
                        logger.info(f"🔗 URL: {page_info['url']}")
                
                # Delay before next check
                self._smart_delay()
                
            except Exception as e:
                logger.error(f"❌ Error during monitoring: {e}")
                self._smart_delay()
    
    def _get_page_hash(self, driver) -> Optional[str]:
        """Generates a hash of the page content to detect changes"""
        try:
            if driver is None:
                return None
                
            # Wait for the page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get the HTML of the page
            page_source = driver.page_source
            
            # Normalize content
            normalized_content = hash_utils.normalize_content(page_source)
            
            # Remove scripts and dynamic elements
            soup = BeautifulSoup(normalized_content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Remove attributes that change frequently
            for tag in soup.find_all(True):
                for attr in ['data-reactid', 'data-testid', 'id']:
                    if tag.has_attr(attr):
                        del tag[attr]
            
            # Generate hash of clean content
            content = str(soup)
            return hashlib.md5(content.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Error generating page hash: {e}")
            return None
    
    def _check_availability(self, driver) -> Tuple[bool, str]:
        """Checks if there are available slots on the page"""
        try:
            if driver is None:
                return False, "Driver not available"
                
            page_text = driver.page_source.lower()
            
            # Check for appointment buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                button_text = button.text.lower()
                if config.detection.availability_indicators and any(indicator in button_text for indicator in config.detection.availability_indicators):
                    return True, f"Button found: {button.text}"
            
            # Check for appointment links
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.lower()
                if config.detection.availability_indicators and any(indicator in link_text for indicator in config.detection.availability_indicators):
                    return True, f"Link found: {link.text}"
            
            # Check for availability messages in text
            if config.detection.availability_indicators:
                for indicator in config.detection.availability_indicators:
                    if indicator in page_text:
                        return True, f"Indicator found: {indicator}"
            
            return False, "No available slots detected"
            
        except Exception as e:
            logger.error(f"❌ Error checking availability: {e}")
            return False, f"Error: {e}"
    
    def _smart_delay(self):
        """Implements intelligent delay with anti-detection"""
        if config.anti_detection.enable_random_delays:
            delay = anti_detection.get_random_delay()
            logger.debug(f"⏳ Random delay: {delay:.1f}s")
            time.sleep(delay)
        else:
            time.sleep(config.monitoring.base_interval)
    
    def get_stats(self) -> dict:
        """Returns monitoring statistics"""
        uptime = time.time() - self.start_time
        return {
            "check_count": self.check_count,
            "uptime": time_utils.format_duration(uptime),
            "checks_per_minute": self.check_count / (uptime / 60) if uptime > 0 else 0
        } 