#!/usr/bin/env python3
"""
Monitor de Rendez-vous - Boulogne-Billancourt
Sistema automatizado para monitorar disponibilidade de horários na prefeitura
"""

import sys
import os

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.monitor import RDVMonitor
from src.utils import logger


def main():
    """Função principal"""
    print("=" * 60)
    print("🎯 MONITOR DE RENDEZ-VOUS - BOULOGNE-BILLANCOURT")
    print("=" * 60)
    
    try:
        # Inicia o monitor
        monitor = RDVMonitor()
        monitor.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Monitor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 