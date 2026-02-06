from pydantic import BaseModel, Field
from typing import Optional, Literal
from app.shared.enums import ProblemType, VariableObjetivo, Frequency
from app.shared.schemas import TasaInteres

class ProblemaInteresSimple(BaseModel):
    tipo: Literal[ProblemType.INTERES_SIMPLE]
    capital: Optional[float] = Field(None, description="Capital inicial o Valor Presente")
    monto_futuro: Optional[float] = Field(None, description="Monto final o Valor Futuro")
    interes_ganado: Optional[float] = Field(None, description="Importe monetario del interés (I)")
    tasa: Optional[TasaInteres] = None
    tiempo_meses: Optional[float] = None
    incognita: VariableObjetivo
    periodo_tasa_solicitada: Optional[Frequency] = Field(None, description="Si el usuario pide explícitamente la tasa en un periodo (ej. trimestral, semestral)")

class ProblemaDescuentoBancario(BaseModel):
    tipo: Literal[ProblemType.DESCUENTO_BANCARIO]
    valor_nominal: Optional[float] = Field(None, description="Valor al vencimiento (M)")
    valor_recibido: Optional[float] = Field(None, description="Valor efectivo o descontado (C)")
    descuento_importe: Optional[float] = Field(None, description="Monto del descuento (D)")
    tasa_descuento: Optional[TasaInteres] = None
    tiempo_meses: Optional[float] = None
    incognita: VariableObjetivo

class ProblemaInteresCompuesto(BaseModel):
    tipo: Literal[ProblemType.INTERES_COMPUESTO]
    capital: Optional[float] = None
    monto_futuro: Optional[float] = None
    tasa: Optional[TasaInteres] = None
    tiempo_meses: Optional[float] = None
    capitalizacion: Frequency = Field(..., description="Frecuencia de conversión/capitalización")
    incognita: VariableObjetivo
