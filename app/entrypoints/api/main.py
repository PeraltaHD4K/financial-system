from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

# Importamos nuestros motores
from app.llm_engine import llm_service
from app.llm_schema_registry import ExtraccionFinanciera
from app.accounting.services import accounting_service
from app.negotiation.services import negotiation_service

app = FastAPI(
    title="Financial AI System",
    description="API para análisis y renegociación financiera.",
    version="1.0.0"
)

class UserRequest(BaseModel):
    text: str

@app.post("/analyze")
async def analyze_financial_problem(request: UserRequest) -> Dict[str, Any]:
    """
    Recibe un texto financiero, lo procesa y devuelve la Ficha Técnica estructurada.
    """
    try:
        system_prompt = """
        Eres un experto actuario. Extrae datos para problemas de:
        1. Interés Simple/Compuesto (Capital, Monto, Tasa, Tiempo).
        2. Renegociación de Deudas (Deudas viejas, Pagos nuevos, Fecha Focal).
        
        IMPORTANTE:
        - Si el usuario pide tasa 'trimestral', 'mensual', etc., ponlo en 'periodo_tasa_solicitada'.
        - Normaliza tiempos a meses.
        """
        
        extraccion = llm_service.extract_data(
            system_prompt=system_prompt,
            user_text=request.text,
            schema=ExtraccionFinanciera
        )
        
        problem_data = extraccion.problema
        problem_type = problem_data.tipo
        
        calc_result = {}

        if problem_type == "renegociacion_deuda":
            calc_result = negotiation_service.resolver_ecuacion_valor(problem_data)
            
        elif problem_type in ["interes_simple", "interes_compuesto"]:
            calc_result = accounting_service.solve(problem_data)
            
        else:
            return {
                "status": "warning",
                "message": f"Tipo de problema '{problem_type}' detectado pero no soportado por el motor matemático.",
                "analysis": extraccion.razonamiento
            }

        # Manejo de Errores Matemáticos
        if "error" in calc_result:
            raise HTTPException(status_code=400, detail=calc_result["error"])

        # RESPUESTA JSON ESTANDARIZADA
        return {
            "status": "success",
            "metadata": {
                "type": problem_type,
                "reasoning": extraccion.razonamiento,
                "model_used": llm_service.model
            },
            "financial_data": calc_result
        }

    except Exception as e:
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def home():
    return {"msg": "Financial System API is Running 🚀"}
