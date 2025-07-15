"""
Main monitor for the Rendez-vous system
"""
import time
import signal
import sys
import hashlib
from enum import Enum
from typing import Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .config import config
from .utils import logger, anti_detection, time_utils, hash_utils, notification_utils
from .driver_manager import DriverManager
from .page_detector import page_detector, PageType


class MonitorState(Enum):
    """States of the monitoring process"""
    INITIAL = "initial"
    NAVIGATING = "navigating"
    CAPTCHA_WAIT = "captcha_wait"
    MONITORING = "monitoring"
    AVAILABLE = "available"


class RDVMonitor:
    """Main monitor to detect appointment availability"""
    
    def __init__(self):
        self.driver_manager = DriverManager()
        self.running = True
        self.last_page_hash: Optional[str] = None
        self.check_count = 0
        self.start_time = time.time()
        self.state = MonitorState.INITIAL
        self.initial_page_url = config.monitoring.url
        
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
            logger.debug(f"🔧 User agents count: {len(config.chrome.user_agents) if config.chrome.user_agents else 0}")
            logger.debug(f"🔧 Session rotation interval: {config.anti_detection.session_rotation_interval}")
            logger.info("🛑 Press Ctrl+C to stop\n")
            
            # Initialize the driver
            logger.debug("🔧 Setting up ChromeDriver...")
            self.driver_manager.setup_driver()
            driver = self.driver_manager.get_driver()
            
            if driver is None:
                logger.error("❌ Failed to initialize driver")
                return
            
            logger.debug("✅ ChromeDriver initialized successfully")
            
            # Load the initial page
            logger.debug(f"🌐 Loading initial page: {config.monitoring.url}")
            driver.get(config.monitoring.url)
            logger.debug("⏳ Waiting for page to load...")
            time.sleep(3)  # Wait for initial loading
            
            # Log detailed request/response information
            self.driver_manager.log_request_details()
            
            # Log page information
            try:
                current_url = driver.current_url
                page_title = driver.title
                logger.debug(f"📄 Current URL: {current_url}")
                logger.debug(f"📄 Page title: {page_title}")
            except Exception as e:
                logger.warning(f"⚠️  Could not get page info: {e}")
            
            # First check
            logger.debug("🔍 Generating initial page hash...")
            self.last_page_hash = self._get_page_hash(driver)
            if self.last_page_hash:
                logger.debug(f"🔍 Initial page hash: {self.last_page_hash[:16]}...")
            
            logger.info("✅ Page loaded initially")
            
            # Main monitoring loop
            logger.debug("🔄 Starting main monitoring loop...")
            self._monitoring_loop(driver)
            
        except Exception as e:
            logger.error(f"❌ Fatal error: {e}")
            import traceback
            logger.debug(f"📋 Full traceback: {traceback.format_exc()}")
        finally:
            logger.debug("🛑 Cleaning up...")
            self.driver_manager.quit()
    
    def _monitoring_loop(self, driver):
        """Main monitoring loop with state management"""
        while self.running:
            try:
                logger.debug(f"🔄 Starting check #{self.check_count + 1} (State: {self.state.value})")
                
                # Check if session should be rotated (only during monitoring, not during captcha wait)
                if self.state != MonitorState.CAPTCHA_WAIT and anti_detection.should_rotate_session():
                    logger.info("🔄 Rotating session for security...")
                    logger.debug(f"📊 Request count: {anti_detection.request_count}")
                    self.driver_manager.rotate_session()
                    driver = self.driver_manager.get_driver()
                    if driver is None:
                        logger.error("❌ Failed to get driver after rotation")
                        continue
                    logger.debug("🌐 Loading page after session rotation...")
                    driver.get(self.initial_page_url)
                    self.state = MonitorState.INITIAL
                
                # Page refresh (only if not waiting for captcha)
                if driver is not None and self.state != MonitorState.CAPTCHA_WAIT:
                    logger.debug("🔄 Refreshing page...")
                    driver.refresh()
                    logger.debug("⏳ Waiting for page refresh...")
                    time.sleep(2)  # Wait for loading
                    
                    # Log request details after refresh
                    self.driver_manager.log_request_details()
                
                # Detect current page type
                if driver is not None:
                    logger.debug("🔍 Detecting page type...")
                    page_info = page_detector.get_page_info(driver)
                    page_type = page_info["type"]
                    logger.debug(f"📄 Page type detected: {page_type.value}")
                    logger.debug(f"📄 Page title: {page_info.get('title', 'Unknown')}")
                    logger.debug(f"📄 Page URL: {page_info.get('url', 'Unknown')}")
                    
                    # Generate hash of new page
                    logger.debug("🔍 Generating page hash...")
                    current_hash = self._get_page_hash(driver)
                    self.check_count += 1
                    
                    if current_hash:
                        logger.debug(f"🔍 Current page hash: {current_hash[:16]}...")
                        if self.last_page_hash:
                            logger.debug(f"🔍 Previous page hash: {self.last_page_hash[:16]}...")
                            hash_changed = current_hash != self.last_page_hash
                            logger.debug(f"🔍 Hash changed: {hash_changed}")
                    
                    timestamp = time_utils.get_timestamp()
                    
                    # Handle different page types based on current state
                    if page_type == PageType.BLOCKED:
                        logger.warning(f"🚫 [{timestamp}] BLOCKED! {page_info['description']}")
                        logger.warning(f"📋 Reason: {page_info.get('blocked_reason', 'Not specified')}")
                        
                        # Log detailed blocked page analysis
                        self.driver_manager.log_blocked_page_content()
                        
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
                        if self.state != MonitorState.CAPTCHA_WAIT:
                            logger.warning(f"\n🔐 [{timestamp}] CAPTCHA DETECTED! (Check #{self.check_count})")
                            logger.warning(f"📝 {page_info['description']}")
                            
                            # Sound and visual notification
                            notification_utils.play_sound()
                            notification_utils.show_notification(
                                "RDV Monitor - CAPTCHA", 
                                "Manual intervention required! Type the captcha."
                            )
                            
                            self.state = MonitorState.CAPTCHA_WAIT
                            logger.info("🔐 Type the captcha manually and press Enter to continue...")
                            input("Press Enter when you finish the captcha...")
                            
                            # After captcha, transition to monitoring state
                            self.state = MonitorState.MONITORING
                            logger.info("✅ Captcha completed! Starting availability monitoring...")
                        else:
                            logger.info(f"⏳ [{timestamp}] Waiting for captcha completion...")
                        
                        continue
                        
                    elif page_type == PageType.INITIAL:
                        if self.state == MonitorState.INITIAL:
                            logger.info(f"\n🏠 [{timestamp}] INITIAL PAGE DETECTED! (Check #{self.check_count})")
                            logger.info(f"📝 {page_info['description']}")
                            
                            # Try to click the "Prendre un rendez-vous" button
                            if self._click_prendre_rdv_button(driver):
                                self.state = MonitorState.NAVIGATING
                                logger.info("🔘 Successfully clicked 'Prendre un rendez-vous'")
                                logger.info("⏳ Navigating to appointment page...")
                            else:
                                logger.warning("⚠️  Could not find 'Prendre un rendez-vous' button")
                                logger.info("🔄 Will retry on next check...")
                        else:
                            logger.info(f"🏠 [{timestamp}] Back to initial page - retrying navigation...")
                            if self._click_prendre_rdv_button(driver):
                                self.state = MonitorState.NAVIGATING
                                logger.info("🔘 Successfully clicked 'Prendre un rendez-vous'")
                        
                        continue
                        
                    elif page_type == PageType.AVAILABLE:
                        if self.state == MonitorState.MONITORING:
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
                            
                            self.state = MonitorState.AVAILABLE
                            
                            # Keep the page open for the user
                            input("\nPress Enter to continue monitoring or Ctrl+C to stop...")
                            self.state = MonitorState.MONITORING  # Resume monitoring
                        else:
                            logger.info(f"🎉 [{timestamp}] Available slots detected but not in monitoring state")
                        
                    elif page_type == PageType.UNAVAILABLE:
                        if self.state == MonitorState.MONITORING:
                            if current_hash != self.last_page_hash:
                                logger.info(f"\n🔄 [{timestamp}] CHANGE DETECTED! (Check #{self.check_count})")
                                logger.info(f"ℹ️  {page_info['description']}")
                                self.last_page_hash = current_hash
                            else:
                                if config.logging.show_check_count:
                                    logger.info(f"[{timestamp}] Check #{self.check_count} - {page_info['description']}")
                                else:
                                    logger.info(f"[{timestamp}] {page_info['description']}")
                        elif self.state == MonitorState.NAVIGATING:
                            logger.info(f"📄 [{timestamp}] Navigated to appointment page - {page_info['description']}")
                            self.state = MonitorState.MONITORING
                            logger.info("✅ Starting availability monitoring...")
                        else:
                            logger.info(f"📄 [{timestamp}] {page_info['description']}")
                                
                    else:  # UNKNOWN or others
                        logger.warning(f"❓ [{timestamp}] Unknown page: {page_info['description']}")
                        logger.info(f"📄 Title: {page_info['title']}")
                        logger.info(f"🔗 URL: {page_info['url']}")
                
                # Delay before next check (only if not waiting for captcha)
                if self.state != MonitorState.CAPTCHA_WAIT:
                    self._smart_delay()
                else:
                    time.sleep(1)  # Short delay when waiting for captcha
                
            except Exception as e:
                logger.error(f"❌ Error during monitoring: {e}")
                if self.state != MonitorState.CAPTCHA_WAIT:
                    self._smart_delay()
    
    def _get_page_hash(self, driver) -> Optional[str]:
        """Generates a hash of the page content to detect changes"""
        try:
            if driver is None:
                logger.debug("❌ Driver is None, cannot generate hash")
                return None
                
            # Wait for the page to load
            logger.debug("⏳ Waiting for page body to load...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Get the HTML of the page
            logger.debug("📄 Getting page source...")
            page_source = driver.page_source
            logger.debug(f"📄 Page source length: {len(page_source)} characters")
            
            # Normalize content
            logger.debug("🔧 Normalizing content...")
            normalized_content = hash_utils.normalize_content(page_source)
            logger.debug(f"🔧 Normalized content length: {len(normalized_content)} characters")
            
            # Remove scripts and dynamic elements
            logger.debug("🧹 Cleaning HTML content...")
            soup = BeautifulSoup(normalized_content, 'html.parser')
            
            # Remove scripts and styles
            scripts_removed = len(soup(["script", "style"]))
            for script in soup(["script", "style"]):
                script.decompose()
            logger.debug(f"🧹 Removed {scripts_removed} script/style elements")
            
            # Remove attributes that change frequently
            attrs_removed = 0
            for tag in soup.find_all(True):
                for attr in ['data-reactid', 'data-testid', 'id']:
                    if tag.has_attr(attr):
                        del tag[attr]
                        attrs_removed += 1
            logger.debug(f"🧹 Removed {attrs_removed} dynamic attributes")
            
            # Generate hash of clean content
            content = str(soup)
            hash_result = hashlib.md5(content.encode()).hexdigest()
            logger.debug(f"🔍 Generated hash: {hash_result[:16]}...")
            return hash_result
            
        except Exception as e:
            logger.error(f"❌ Error generating page hash: {e}")
            import traceback
            logger.debug(f"📋 Hash generation traceback: {traceback.format_exc()}")
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
    
    def _click_prendre_rdv_button(self, driver) -> bool:
        """Tries to click the 'Prendre un rendez-vous' button"""
        try:
            logger.debug("🔍 Looking for 'Prendre un rendez-vous' button...")
            
            # Try different selectors for the button
            selectors = [
                "a[href*='prendre']",
                "a[href*='rdv']", 
                "a[href*='rendez-vous']",
                "button[onclick*='prendre']",
                "button[onclick*='rdv']",
                "a",
                "button"
            ]
            
            for selector in selectors:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
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
                        logger.debug(f"🔘 Clicking element with selector: {selector}")
                        
                        # Scroll to element
                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                        time.sleep(0.5)
                        
                        # Click the element
                        element.click()
                        time.sleep(3)  # Wait for navigation
                        
                        logger.debug("✅ Button clicked successfully")
                        return True
            
            logger.debug("❌ 'Prendre un rendez-vous' button not found")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error clicking 'Prendre un rendez-vous' button: {e}")
            return False
    
    def get_stats(self) -> dict:
        """Returns monitoring statistics"""
        uptime = time.time() - self.start_time
        return {
            "check_count": self.check_count,
            "uptime": time_utils.format_duration(uptime),
            "checks_per_minute": self.check_count / (uptime / 60) if uptime > 0 else 0,
            "current_state": self.state.value
        } 