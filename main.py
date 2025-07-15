#!/usr/bin/env python3
"""
Rendez-vous Monitor - Boulogne-Billancourt
Automated system to monitor appointment availability at the city hall
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.monitor import RDVMonitor
from src.utils import logger


def main():
    """Main function"""
    print("=" * 60)
    print("🎯 RENDEZ-VOUS MONITOR - BOULOGNE-BILLANCOURT")
    print("=" * 60)
    
    try:
        # Start the monitor
        monitor = RDVMonitor()
        monitor.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Monitor interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 