from enum import Enum

class Frequency(str, Enum):
    DIARIO = "diario"
    SEMANAL = "semanal"
    QUINCENAL = "quincenal"
    MENSUAL = "mensual"
    BIMESTRAL = "bimestral"
    TRIMESTRAL = "trimestral"
    CUATRIMESTRAL = "cuatrimestral"
    SEMESTRAL = "semestral"
    ANUAL = "anual"

class ProblemType(str, Enum):
    INTERES_SIMPLE = "interes_simple"
    INTERES_COMPUESTO = "interes_compuesto"
    DESCUENTO_BANCARIO = "descuento_bancario"
    RENEGOCIACION_DEUDA = "renegociacion_deuda"
    DESCONOCIDO = "desconocido"

class VariableObjetivo(str, Enum):
    CAPITAL = "capital"       # C
    MONTO = "monto"           # M
    TASA = "tasa"             # i
    TIEMPO = "tiempo"         # t
    INTERES = "interes"       # I
    DESCUENTO = "descuento"   # D
    VALOR_NOMINAL = "valor_nominal" # Vn
    