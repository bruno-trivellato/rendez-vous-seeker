"""
Core monitor class for the Rendez-vous system
"""
import time
import signal
import sys
from typing import Optional

from ..config import config
from ..utils import logger, anti_detection, time_utils
from ..driver_manager import DriverManager
from ..page_detector import page_detector, PageType

from .states import MonitorState
from .utils import DelayManager, PageUtils
from .handlers import CaptchaHandler, AvailabilityHandler, PageHandlers


class RDVMonitor:
    """Main monitor to detect appointment availability"""
    
    def __init__(self):
        self.driver_manager = DriverManager()
        self.running = True
        self.check_count = 0
        self.start_time = time.time()
        self.state = MonitorState.MONITORING  # Start directly in monitoring state
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
            self._log_startup_info()
            
            # Initialize the driver
            driver = self._initialize_driver()
            if driver is None:
                return
            
            # Load the initial page
            self._load_initial_page(driver)
            
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
    
    def _log_startup_info(self):
        """Logs startup information"""
        logger.info("🚀 Starting Rendez-vous monitor...")
        logger.info(f"📍 URL: {config.monitoring.url}")
        logger.info(f"⏱️  Base interval: {config.monitoring.base_interval} seconds")
        logger.info(f"🎯 Anti-detection: {'Enabled' if config.anti_detection.enable_random_delays else 'Disabled'}")
        logger.debug(f"🔧 User agents count: {len(config.chrome.user_agents) if config.chrome.user_agents else 0}")
        logger.debug(f"🔧 Session rotation interval: {config.anti_detection.session_rotation_interval}")
        logger.info("🛑 Press Ctrl+C to stop\n")
    
    def _initialize_driver(self) -> Optional[object]:
        """Initializes the Chrome driver"""
        logger.debug("🔧 Setting up ChromeDriver...")
        self.driver_manager.setup_driver()
        driver = self.driver_manager.get_driver()
        
        if driver is None:
            logger.error("❌ Failed to initialize driver")
            return None
        
        logger.debug("✅ ChromeDriver initialized successfully")
        return driver
    
    def _load_initial_page(self, driver):
        """Loads the initial page"""
        logger.info("🌐 Loading initial page asynchronously...")
        PageUtils.load_page_async(driver, config.monitoring.url, self.driver_manager)
        
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
        
        logger.info("✅ Page loaded initially")
    
    def _monitoring_loop(self, driver):
        """Main monitoring loop with state management"""
        while self.running:
            try:
                self._log_loop_start()
                
                # Handle session rotation
                driver = self._handle_session_rotation(driver)
                
                # Handle page refresh
                self._handle_page_refresh(driver)
                
                # Process current page
                if driver is not None:
                    self._process_current_page(driver)
                
                # Apply appropriate delay
                self._apply_delay()
                
            except Exception as e:
                logger.error(f"❌ Error during monitoring: {e}")
                if self.state != MonitorState.CAPTCHA_WAIT:
                    DelayManager.smart_delay()
    
    def _log_loop_start(self):
        """Logs the start of each monitoring loop iteration"""
        logger.debug(f"🔄 Starting check #{self.check_count + 1} (State: {self.state.value})")
        if self.state == MonitorState.CAPTCHA_WAIT:
            logger.info(f"🔐 CAPTCHA_WAIT: Check #{self.check_count + 1} - Waiting for manual captcha input...")
            logger.info(f"🔐 CAPTCHA_WAIT: Current state confirmed: {self.state.value}")
    
    def _handle_session_rotation(self, driver):
        """Handles session rotation if needed"""
        if self.state != MonitorState.CAPTCHA_WAIT and anti_detection.should_rotate_session():
            logger.info("🔄 Rotating session for security...")
            logger.debug(f"📊 Request count: {anti_detection.request_count}")
            self.driver_manager.rotate_session()
            driver = self.driver_manager.get_driver()
            if driver is None:
                logger.error("❌ Failed to get driver after rotation")
                return driver
            logger.debug("🌐 Loading page after session rotation...")
            driver.get(self.initial_page_url)
            self.state = MonitorState.INITIAL
        return driver
    
    def _handle_page_refresh(self, driver):
        """Handles page refresh if needed"""
        if driver is not None and self.state != MonitorState.CAPTCHA_WAIT and self.state != MonitorState.AVAILABLE:
            logger.debug("🔄 Refreshing page...")
            PageUtils.refresh_page_fast(driver)
            
            # Log request details after refresh
            self.driver_manager.log_request_details()
    
    def _process_current_page(self, driver):
        """Processes the current page"""
        page_info = page_detector.get_page_info(driver)
        page_type = page_info["type"]
        page_title = page_info.get('title', 'Unknown')
        
        # Check if CAPTCHA was completed
        if self.state == MonitorState.CAPTCHA_WAIT and page_type != PageType.CAPTCHA:
            CaptchaHandler.handle_captcha_completed(time_utils.get_timestamp(), page_type.value)
            self.state = MonitorState.MONITORING
            self.check_count = 0  # Reset check count for better tracking after captcha
        
        logger.info(f"📄 Page: {page_type.value} - '{page_title}'")
        logger.info(f"🔄 Current state: {self.state.value}")
        
        self.check_count += 1
        timestamp = time_utils.get_timestamp()
        
        # Handle different page types
        self._handle_page_type(driver, page_type, page_info, page_title, timestamp)
    
    def _handle_page_type(self, driver, page_type, page_info, page_title, timestamp):
        """Handles different page types"""
        if page_type == PageType.BLOCKED:
            PageHandlers.handle_blocked_page(driver, timestamp, page_info, self.driver_manager)
        elif page_type == PageType.MAINTENANCE:
            PageHandlers.handle_maintenance_page(timestamp, page_info)
        elif page_type == PageType.ERROR:
            PageHandlers.handle_error_page(timestamp, page_info)
        elif page_type == PageType.LOADING:
            PageHandlers.handle_loading_page(timestamp, page_info)
        elif page_type == PageType.CAPTCHA:
            self._handle_captcha_page(driver, timestamp, page_info)
        elif page_type == PageType.INITIAL:
            self._handle_initial_page(driver, timestamp)
        elif page_type == PageType.AVAILABLE:
            self._handle_available_page(driver, timestamp, page_info, page_title)
        elif page_type == PageType.UNAVAILABLE:
            self._handle_unavailable_page(driver, timestamp, page_info, page_title)
        else:  # UNKNOWN or others
            logger.warning(f"❓ [{timestamp}] Unknown page: {page_info['description']}")
            logger.info(f"📄 Title: {page_info['title']}")
            logger.info(f"🔗 URL: {page_info['url']}")
    
    def _handle_captcha_page(self, driver, timestamp, page_info):
        """Handles captcha page"""
        if self.state != MonitorState.CAPTCHA_WAIT:
            CaptchaHandler.handle_captcha_detected(driver, timestamp, self.check_count, page_info)
            self.state = MonitorState.CAPTCHA_WAIT
        else:
            CaptchaHandler.handle_captcha_waiting(timestamp, self.check_count)
    
    def _handle_initial_page(self, driver, timestamp):
        """Handles initial page"""
        if PageHandlers.handle_initial_page(driver, timestamp):
            self.state = MonitorState.NAVIGATING
    
    def _handle_available_page(self, driver, timestamp, page_info, page_title):
        """Handles available page"""
        if self.state == MonitorState.MONITORING:
            AvailabilityHandler.handle_availability_detected(timestamp, self.check_count, page_info)
            self.state = MonitorState.AVAILABLE
        elif self.state == MonitorState.AVAILABLE:
            AvailabilityHandler.handle_availability_reminder(timestamp, self.check_count)
            
            # Check if we're still on the appointment page and slots are still available
            if "choisissez votre créneau" in page_title.lower():
                is_available, _ = AvailabilityHandler.check_availability(driver)
                if not is_available:
                    AvailabilityHandler.handle_availability_lost(timestamp)
                    self.state = MonitorState.MONITORING
        else:
            logger.info(f"🎉 [{timestamp}] Available slots detected but not in monitoring state")
    
    def _handle_unavailable_page(self, driver, timestamp, page_info, page_title):
        """Handles unavailable page"""
        if self.state == MonitorState.MONITORING:
            # Check if this is the appointment page and look for available slots
            if "choisissez votre créneau" in page_title.lower():
                is_available, _ = AvailabilityHandler.handle_appointment_page_check(driver, timestamp, self.check_count)
                if is_available:
                    self.state = MonitorState.AVAILABLE
                else:
                    if config.logging.show_check_count:
                        logger.info(f"[{timestamp}] Check #{self.check_count} - No available slots")
                    else:
                        logger.info(f"[{timestamp}] No available slots")
            else:
                # Regular unavailable page
                if config.logging.show_check_count:
                    logger.info(f"[{timestamp}] Check #{self.check_count} - {page_info['description']}")
                else:
                    logger.info(f"[{timestamp}] {page_info['description']}")
        elif self.state == MonitorState.NAVIGATING:
            PageHandlers.handle_navigation_complete(timestamp, page_info)
            self.state = MonitorState.MONITORING
        else:
            logger.info(f"📄 [{timestamp}] {page_info['description']}")
    
    def _apply_delay(self):
        """Applies appropriate delay based on current state"""
        if self.state == MonitorState.CAPTCHA_WAIT:
            DelayManager.captcha_wait_delay()
        elif self.state == MonitorState.AVAILABLE:
            DelayManager.available_slots_delay()
        else:
            DelayManager.smart_delay()
    
    def get_stats(self) -> dict:
        """Returns monitoring statistics"""
        uptime = time.time() - self.start_time
        return {
            "check_count": self.check_count,
            "uptime": time_utils.format_duration(uptime),
            "checks_per_minute": self.check_count / (uptime / 60) if uptime > 0 else 0,
            "current_state": self.state.value
        } 