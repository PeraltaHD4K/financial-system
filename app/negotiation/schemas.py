from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from app.shared.enums import ProblemType
from app.shared.schemas import TasaInteres

class Deuda(BaseModel):
    monto: float
    vencimiento_meses: float = Field(..., description="Meses hasta el vencimiento desde la fecha focal. Negativo si ya venció.")

class Pago(BaseModel):
    monto: Optional[float] = Field(None, description="Monto del pago. None si es la incógnita 'x'")
    mes: float = Field(..., description="Momento del pago en meses")
    proporcion_incognita: Optional[float] = Field(None, description="Si el pago es '2x', esto sería 2.0")

class ProblemaRenegociacion(BaseModel):
    tipo: Literal[ProblemType.RENEGOCIACION_DEUDA]
    deudas_originales: List[Deuda]
    pagos_propuestos: List[Pago]
    tasa_referencia: TasaInteres
    fecha_focal_mes: float = Field(default=0.0, description="Fecha donde se igualan deudas y pagos")
    incognita: Literal["valor_pago_x"] = "valor_pago_x"
    