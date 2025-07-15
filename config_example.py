"""
Exemplo de configuração personalizada para o Monitor de Rendez-vous
Copie este arquivo para config.py e ajuste conforme suas necessidades
"""

# Configurações de monitoramento
MONITORING_CONFIG = {
    "url": "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/3720/creneau/",
    "base_interval": 15,  # segundos (mais discreto)
    "min_random_delay": 5,  # segundos
    "max_random_delay": 12,  # segundos
    "max_retries": 3,
    "timeout": 30
}

# Configurações anti-detecção
ANTI_DETECTION_CONFIG = {
    "enable_random_delays": True,
    "enable_user_agent_rotation": True,
    "enable_headers_rotation": True,
    "enable_session_rotation": True,
    "session_rotation_interval": 30,  # rotação mais frequente
    "max_requests_per_session": 50
}

# Indicadores de disponibilidade personalizados
AVAILABILITY_INDICATORS = [
    "disponible", "available", "libre", "free",
    "réserver", "reserve", "choisir", "select",
    "creneau", "slot", "rendez-vous", "appointment",
    "horaire", "schedule", "placer", "place",
    # Adicione mais palavras-chave específicas do site
    "prendre rendez-vous", "book appointment"
]

# Configurações de logging
LOGGING_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "show_timestamps": True,
    "show_check_count": False,  # Menos verbose
    "log_to_file": True,
    "log_file": "rdv_monitor.log"
}

# User agents adicionais (mais diversidade)
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

# Headers adicionais para parecer mais humano
ADDITIONAL_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"'
} 