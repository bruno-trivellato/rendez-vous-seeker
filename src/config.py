"""
Centralized configuration for the Rendez-vous Monitor
"""
import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Available log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class ChromeConfig:
    """Chrome configuration"""
    window_size: str = "1920,1080"
    disable_images: bool = True
    user_agents: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.user_agents is None:
            self.user_agents = [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ]


@dataclass
class MonitoringConfig:
    """Monitoring configuration"""
    url: str = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/3720/"
    target_url: str = "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/3720/creneau/"
    base_interval: int = 20  # seconds
    min_random_delay: int = 5  # seconds
    max_random_delay: int = 10  # seconds
    max_retries: int = 3
    timeout: int = 30


@dataclass
class DetectionConfig:
    """Detection configuration"""
    availability_indicators: Optional[List[str]] = None
    change_threshold: float = 0.1  # minimum change percentage to consider relevant
    
    def __post_init__(self):
        if self.availability_indicators is None:
            self.availability_indicators = [
                "disponible", "available", "libre", "free",
                "réserver", "reserve", "choisir", "select",
                "creneau", "slot", "rendez-vous", "appointment",
                "horaire", "schedule", "placer", "place"
            ]


@dataclass
class AntiDetectionConfig:
    """Anti-detection configuration"""
    enable_random_delays: bool = True
    enable_user_agent_rotation: bool = True
    enable_headers_rotation: bool = True
    enable_session_rotation: bool = True
    session_rotation_interval: int = 50  # rotation every N requests
    max_requests_per_session: int = 100
    
    # Extra headers to appear more human-like
    additional_headers: Optional[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.additional_headers is None:
            self.additional_headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Cache-Control": "max-age=0"
            }


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: LogLevel = LogLevel.INFO
    show_timestamps: bool = True
    show_check_count: bool = True
    log_to_file: bool = False
    log_file: str = "rdv_monitor.log"


class Config:
    """Main system configuration"""
    
    def __init__(self):
        self.chrome = ChromeConfig()
        self.monitoring = MonitoringConfig()
        self.detection = DetectionConfig()
        self.anti_detection = AntiDetectionConfig()
        self.logging = LoggingConfig()
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create configuration from environment variables"""
        config = cls()
        
        # Allow overriding configurations via env vars
        rdv_url = os.getenv("RDV_URL")
        if rdv_url is not None:
            config.monitoring.url = rdv_url
        
        rdv_interval = os.getenv("RDV_INTERVAL")
        if rdv_interval is not None:
            config.monitoring.base_interval = int(rdv_interval)
        
        rdv_log_level = os.getenv("RDV_LOG_LEVEL")
        if rdv_log_level is not None:
            config.logging.level = LogLevel(rdv_log_level)
        
        return config


# Global configuration instance
config = Config.from_env() 