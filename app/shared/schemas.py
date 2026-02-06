from pydantic import BaseModel, Field
from typing import Optional
from .enums import Frequency

class TasaInteres(BaseModel):
    valor: float = Field(..., description="El valor decimal de la tasa (ej. 0.15 para 15%)")
    periodo: Frequency = Field(default=Frequency.ANUAL, description="Periodo de la tasa (ej. anual, mensual)")
    es_nominal: bool = Field(default=False, description="True si es Tasa Nominal (j), False si es efectiva")
    capitalizacion: Optional[Frequency] = Field(None, description="Solo si es nominal: frecuencia de capitalización")
    