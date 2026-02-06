import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
    MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    @staticmethod
    def validate():
        if Config.PROVIDER == "openai" and not Config.OPENAI_API_KEY:
            raise ValueError("Error: Configurado 'openai' pero falta OPENAI_API_KEY en .env")
        
        if Config.PROVIDER == "gemini" and not Config.GEMINI_API_KEY:
            raise ValueError("Error: Configurado 'gemini' pero falta GEMINI_API_KEY en .env")

# Validar al importar
Config.validate()
