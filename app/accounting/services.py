import math
from app.shared.enums import VariableObjetivo, Frequency
from app.accounting.schemas import (
    ProblemaInteresSimple,
    ProblemaInteresCompuesto,
    ProblemaDescuentoBancario
)

class AccountingService:
    
    def _get_frecuencia_anual(self, freq: Frequency) -> int:
        """Retorna cuántos periodos caben en un año (m)"""
        mapa = {
            Frequency.ANUAL: 1, Frequency.SEMESTRAL: 2, Frequency.CUATRIMESTRAL: 3,
            Frequency.TRIMESTRAL: 4, Frequency.BIMESTRAL: 6, Frequency.MENSUAL: 12,
            Frequency.QUINCENAL: 24, Frequency.SEMANAL: 52, Frequency.DIARIO: 360
        }
        return mapa.get(freq, 1)

    def _normalizar_tasa(self, tasa_obj, frecuencia_capitalizacion: Frequency = None) -> float:
        """Convierte tasa a efectiva del periodo."""
        if not tasa_obj: return 0.0
        i = tasa_obj.valor
        if tasa_obj.es_nominal:
            cap = tasa_obj.capitalizacion or frecuencia_capitalizacion
            m = self._get_frecuencia_anual(cap)
            return i / m
        return i

    def _get_meses_por_periodo(self, freq: Frequency) -> float:
        freq_anual = self._get_frecuencia_anual(freq)
        return 12 / freq_anual
    
    def _formatear_tiempo_humano(self, total_meses: float) -> str:
        """
        Convierte una cantidad de meses (ej. 22.2) a texto legible:
        "1 año, 10 meses, 6 días"
        Asume año comercial de 360 días (mes de 30 días).
        """
        if total_meses < 0: return "Tiempo negativo (?)"
        
        # 1. Calcular Años
        anios = int(total_meses // 12)
        resto_meses = total_meses % 12
        
        # 2. Calcular Meses
        meses = int(resto_meses)
        fraccion_mes = resto_meses - meses
        
        # 3. Calcular Días (Comercial: 30 días por mes)
        dias = round(fraccion_mes * 30)
        
        partes = []
        if anios > 0: partes.append(f"{anios} año(s)")
        if meses > 0: partes.append(f"{meses} mes(es)")
        if dias > 0: partes.append(f"{dias} día(s)")
        
        return ", ".join(partes) if partes else "0 días"

    # --- SOLUCIONADOR INTERÉS SIMPLE ---
    def resolver_interes_simple(self, p: ProblemaInteresSimple) -> dict:
        resultados = {}
        C = p.capital
        M = p.monto_futuro
        I = p.interes_ganado
        t_meses = p.tiempo_meses
        
        # Inferencia inicial
        if I is None and M is not None and C is not None: I = M - C
        if C is None and M is not None and I is not None: C = M - I
        if M is None and C is not None and I is not None: M = C + I

        # Preparación Dimensional
        i_tasa = None
        n_periodos = None
        unidad_tiempo = "Mensual"

        if p.tasa:
            i_tasa = p.tasa.valor
            freq_tasa = p.tasa.periodo or Frequency.ANUAL
            unidad_tiempo = freq_tasa.value.title()
            if t_meses is not None:
                duracion_periodo = self._get_meses_por_periodo(freq_tasa)
                n_periodos = t_meses / duracion_periodo
        elif t_meses is not None:
             n_periodos = t_meses

        try:
            target = p.incognita
            
            # --- BLOQUE DE CÁLCULO (Encuentra la pieza que falta) ---
            if target == VariableObjetivo.TASA:
                if I is not None and C is not None and t_meses is not None:
                    if C * t_meses == 0: raise ValueError("División por cero")
                    
                    if p.periodo_tasa_solicitada:
                        freq_obj = p.periodo_tasa_solicitada
                        nombre_per = freq_obj.value.title()
                        duracion = self._get_meses_por_periodo(freq_obj)
                        n_calc = t_meses / duracion
                    else:
                        freq_obj = Frequency.MENSUAL
                        nombre_per = "Mensual"
                        n_calc = t_meses 

                    i_calc = I / (C * n_calc)
                    
                    resultados["tasa_calculada"] = {
                        "valor": i_calc,
                        "etiqueta": f"{round(i_calc*100, 4)}% {nombre_per}",
                        "anual": i_calc * self._get_frecuencia_anual(freq_obj)
                    }
                    resultados["formula"] = "i = I / (C * n)"
                    i_tasa = i_calc 

            elif target == VariableObjetivo.TIEMPO:
                if I is not None and C is not None and i_tasa is not None:
                    n_calc = I / (C * i_tasa)
                    duracion_periodo = self._get_meses_por_periodo(p.tasa.periodo or Frequency.ANUAL)
                    t_meses_calc = n_calc * duracion_periodo
                    
                    resultados["tiempo_calculado"] = {
                        "n": round(n_calc, 4),
                        "unidad": unidad_tiempo,
                        "texto_humano": self._formatear_tiempo_humano(t_meses_calc)
                    }
                    resultados["formula"] = "n = I / (C * i)"
                    n_periodos = n_calc
                    t_meses = t_meses_calc

            elif target == VariableObjetivo.CAPITAL:
                if M is not None and i_tasa is not None and n_periodos is not None:
                    res = M / (1 + (i_tasa * n_periodos))
                    resultados["formula"] = "C = M / (1 + i*n)"
                elif I is not None and i_tasa is not None and n_periodos is not None:
                    res = I / (i_tasa * n_periodos)
                    resultados["formula"] = "C = I / (i*n)"
                else:
                    return {"error": "Faltan datos para calcular Capital"}
                C = res

            elif target == VariableObjetivo.MONTO:
                if C is not None and i_tasa is not None and n_periodos is not None:
                    res = C * (1 + (i_tasa * n_periodos))
                    resultados["formula"] = "M = C * (1 + i*n)"
                else:
                    return {"error": "Faltan datos para calcular Monto"}
                M = res
            
            elif target == VariableObjetivo.INTERES:
                if C is not None and i_tasa is not None and n_periodos is not None:
                    res = C * i_tasa * n_periodos
                    resultados["formula"] = "I = C * i * n"
                else:
                    return {"error": "Faltan datos para calcular Interés"}
                I = res

            # --- BLOQUE DE CONSOLIDACIÓN (Rellenar huecos C-M-I) ---
            if I is None and M is not None and C is not None: I = M - C
            if M is None and C is not None and I is not None: M = C + I
            if C is None and M is not None and I is not None: C = M - I

            # --- CÁLCULO DE VARIABLES DE TASA Y TIEMPO (r, i, t, n) ---
            
            # 1. Definir la Frecuencia Base (m)
            # Si se usó una tasa en el cálculo, esa define la frecuencia.
            # Si no (porque se calculó desde cero), asumimos la solicitada o Mensual.
            if p.tasa:
                freq_obj = p.tasa.periodo or Frequency.ANUAL
            elif p.periodo_tasa_solicitada:
                freq_obj = p.periodo_tasa_solicitada
            else:
                freq_obj = Frequency.MENSUAL # Default
            
            nombre_periodo = freq_obj.value.title()
            m = self._get_frecuencia_anual(freq_obj) # Frecuencia anual

            # 2. Obtener i (Tasa del Periodo) y r (Tasa Nominal Anual)
            val_i = i_tasa if i_tasa is not None else 0.0
            val_r = val_i * m # r = i * m

            # 3. Obtener n (Periodos) y t (Tiempo cronológico)
            val_n = n_periodos if n_periodos is not None else 0.0
            # Si tenemos t_meses (cronológico), lo usamos. Si no, lo derivamos de n.
            if t_meses:
                val_t_texto = self._formatear_tiempo_humano(t_meses)
            else:
                # Reconstruir tiempo cronológico desde n
                meses_totales = val_n * (12 / m)
                val_t_texto = self._formatear_tiempo_humano(meses_totales)

            # Construimos el "Resumen Financiero Completo"
            resultados["resumen"] = {
                "variables_monetarias": {
                    "C": C,
                    "M": M,
                    "I": I
                },
                "variables_tasa": {
                    "r": val_r, # Nominal Anual
                    "i": val_i, # Efectiva Periodo
                    "freq": nombre_periodo
                },
                "variables_tiempo": {
                    "t_legible": val_t_texto,
                    "n": val_n,
                    "unidad_n": nombre_periodo
                }
            }

        except Exception as e:
            return {"error": f"Error matemático: {str(e)}"}

        return resultados

    # --- SOLUCIONADOR INTERÉS COMPUESTO (Mantenemos el anterior) ---
    def resolver_interes_compuesto(self, p: ProblemaInteresCompuesto) -> dict:
        resultados = {}
        C = p.capital
        M = p.monto_futuro
        t_meses = p.tiempo_meses
        m_anual = self._get_frecuencia_anual(p.capitalizacion)
        
        # n = total periodos
        n = None
        if t_meses is not None:
            meses_por_periodo = 12 / m_anual
            n = t_meses / meses_por_periodo

        # i = tasa efectiva periodo
        i = self._normalizar_tasa(p.tasa, p.capitalizacion)

        if p.incognita == VariableObjetivo.MONTO:
            res = C * math.pow(1 + i, n)
            resultados["formula"] = "M = C * (1 + i)^n"
            resultados["resultado"] = round(res, 2)
            
        elif p.incognita == VariableObjetivo.CAPITAL:
            res = M / math.pow(1 + i, n)
            resultados["formula"] = "C = M / (1 + i)^n"
            resultados["resultado"] = round(res, 2)

        return resultados

    def solve(self, problema_dto) -> dict:
        tipo = problema_dto.tipo
        if tipo == "interes_compuesto":
            return self.resolver_interes_compuesto(problema_dto)
        elif tipo == "interes_simple":
            return self.resolver_interes_simple(problema_dto)
        elif tipo == "descuento_bancario":
            return {"error": "Lógica de descuento aún no implementada"}
        else:
            return {"error": "Tipo de problema no soportado"}

accounting_service = AccountingService()
