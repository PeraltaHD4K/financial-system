import openai
import instructor
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from pydantic import BaseModel
from typing import Type, TypeVar
from app.config import Config

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class LLMEngine:
    def __init__(self):
        self.provider = Config.PROVIDER
        self.model = Config.MODEL_NAME
        
        if self.provider == "gemini":
            self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        elif self.provider == "openai":
            self.client = instructor.from_openai(
                openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            )

    @retry(
        retry=retry_if_exception_type(ClientError),
        stop=stop_after_attempt(4),
        
        wait=wait_exponential(multiplier=2, min=30, max=120),
        
        before_sleep=lambda retry_state: print(f"Alerta de Tráfico (429). Esperando {retry_state.next_action.sleep}s para intentar otra vez...")
    )
    def extract_data(self, system_prompt: str, user_text: str, schema: Type[T]) -> T:
        """
        Función agnóstica para extraer datos estructurados con reintentos automáticos.
        """
        if self.provider == "gemini":
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_text,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        response_mime_type='application/json',
                        response_schema=schema
                    )
                )
                return response.parsed
                
            except Exception as e:
                raise e

        elif self.provider == "openai":
            return self.client.chat.completions.create(
                model=self.model,
                response_model=schema,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ]
            )

llm_service = LLMEngine()
