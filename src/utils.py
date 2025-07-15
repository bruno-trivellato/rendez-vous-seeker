"""
Utilitários para o Monitor de Rendez-vous
"""
import time
import random
import logging
import os
import subprocess
from datetime import datetime
from typing import Optional
from .config import config


class Logger:
    """Logger customizado para o monitor"""
    
    def __init__(self, name: str = "RDVMonitor"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(config.logging.level.value)
        
        # Handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.logging.level.value)
        
        # Formato do log
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Adiciona handler se não existir
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
        
        # Handler para arquivo (se configurado)
        if config.logging.log_to_file:
            file_handler = logging.FileHandler(config.logging.log_file)
            file_handler.setLevel(config.logging.level.value)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log de informação"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log de erro"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Log de debug"""
        self.logger.debug(message)


class AntiDetectionUtils:
    """Utilitários para evitar detecção de bot"""
    
    def __init__(self):
        self.current_user_agent_index = 0
        self.request_count = 0
        self.session_start_time = time.time()
    
    def get_random_delay(self) -> float:
        """Retorna um delay aleatório entre min e max"""
        if not config.anti_detection.enable_random_delays:
            return 0
        
        return random.uniform(
            config.monitoring.min_random_delay,
            config.monitoring.max_random_delay
        )
    
    def get_next_user_agent(self) -> str:
        """Retorna o próximo user agent da lista (rotação)"""
        if not config.anti_detection.enable_user_agent_rotation:
            return config.chrome.user_agents[0] if config.chrome.user_agents else ""
        
        if config.chrome.user_agents:
            user_agent = config.chrome.user_agents[self.current_user_agent_index]
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(config.chrome.user_agents)
            return user_agent
        return ""
    
    def should_rotate_session(self) -> bool:
        """Verifica se deve rotacionar a sessão"""
        if not config.anti_detection.enable_session_rotation:
            return False
        
        self.request_count += 1
        return (
            self.request_count % config.anti_detection.session_rotation_interval == 0 or
            time.time() - self.session_start_time > 3600  # 1 hora
        )
    
    def reset_session(self):
        """Reseta contadores da sessão"""
        self.request_count = 0
        self.session_start_time = time.time()


class TimeUtils:
    """Utilitários relacionados a tempo"""
    
    @staticmethod
    def get_timestamp() -> str:
        """Retorna timestamp formatado"""
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formata duração em segundos para string legível"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class HashUtils:
    """Utilitários para hash e comparação de conteúdo"""
    
    @staticmethod
    def normalize_content(content: str) -> str:
        """Normaliza conteúdo removendo elementos dinâmicos"""
        import re
        
        # Remove timestamps
        content = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', content)
        content = re.sub(r'\d{4}-\d{2}-\d{2}', '', content)
        
        # Remove IDs dinâmicos
        content = re.sub(r'id="[^"]*"', '', content)
        content = re.sub(r'data-[^=]*="[^"]*"', '', content)
        
        # Remove espaços extras
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    @staticmethod
    def calculate_similarity(hash1: str, hash2: str) -> float:
        """Calcula similaridade entre dois hashes"""
        if hash1 == hash2:
            return 1.0
        
        # Implementação simples - pode ser melhorada
        return 0.0


class NotificationUtils:
    """Utilitários para notificações"""
    
    @staticmethod
    def play_sound():
        """Toca um som de notificação"""
        try:
            # Tenta diferentes comandos de som baseado no sistema
            if os.name == 'posix':  # macOS/Linux
                # Tenta afplay (macOS)
                subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], 
                             capture_output=True, timeout=5)
            else:  # Windows
                # Tenta PowerShell para tocar som
                subprocess.run(['powershell', '-c', '[console]::beep(800,500)'], 
                             capture_output=True, timeout=5)
        except Exception as e:
            logger.debug(f"⚠️  Não foi possível tocar som: {e}")
    
    @staticmethod
    def show_notification(title: str, message: str):
        """Mostra notificação do sistema"""
        try:
            if os.name == 'posix':  # macOS/Linux
                subprocess.run(['osascript', '-e', 
                              f'display notification "{message}" with title "{title}"'], 
                             capture_output=True, timeout=5)
            else:  # Windows
                subprocess.run(['powershell', '-c', 
                              f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; $template = \'<toast><visual><binding template="ToastText01"><text id="1">{message}</text></binding></visual></toast>\'; $xml = New-Object Windows.Data.Xml.Dom.XmlDocument; $xml.LoadXml($template); $toast = New-Object Windows.UI.Notifications.ToastNotification $xml; [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{title}").Show($toast);'], 
                             capture_output=True, timeout=10)
        except Exception as e:
            logger.debug(f"⚠️  Não foi possível mostrar notificação: {e}")


# Instâncias globais
logger = Logger()
anti_detection = AntiDetectionUtils()
time_utils = TimeUtils()
hash_utils = HashUtils()
notification_utils = NotificationUtils() 