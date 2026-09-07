# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'chatbot_support')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Configuración del LLM local (usamos un modelo open-source)
    MODEL_NAME = os.getenv('MODEL_NAME', 'microsoft/DialoGPT-medium')  # Cambia por tu modelo preferido
    USE_LOCAL_LLM = os.getenv('USE_LOCAL_LLM', 'True') == 'True'
    
    # Configuración para pruebas de seguridad
    MAX_RESPONSE_LENGTH = 500  # Para prevenir DoS
    ENABLE_LOGGING = True
    LOG_FILE = 'chatbot_audit.log'