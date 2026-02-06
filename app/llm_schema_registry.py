from pydantic import BaseModel, Field
from typing import Union
from app.accounting.schemas import (
    ProblemaInteresSimple, 
    ProblemaDescuentoBancario, 
    ProblemaInteresCompuesto
)
from app.negotiation.schemas import ProblemaRenegociacion

class ExtraccionFinanciera(BaseModel):
    razonamiento: str = Field(..., description="Explica paso a paso qué datos identificaste y por qué eliges este modelo.")
    problema: Union[
        ProblemaInteresSimple, 
        ProblemaDescuentoBancario, 
        ProblemaInteresCompuesto, 
        ProblemaRenegociacion
    ] = Field(..., description="El objeto del problema financiero identificado")
    