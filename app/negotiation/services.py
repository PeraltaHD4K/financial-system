import math
from app.negotiation.schemas import ProblemaRenegociacion
from app.shared.enums import Frequency

class NegotiationService:
    
    def _get_frecuencia_anual(self, freq: Frequency) -> int:
        mapa = {
            Frequency.ANUAL: 1, Frequency.SEMESTRAL: 2, Frequency.CUATRIMESTRAL: 3,
            Frequency.TRIMESTRAL: 4, Frequency.BIMESTRAL: 6, Frequency.MENSUAL: 12,
            Frequency.QUINCENAL: 24, Frequency.SEMANAL: 52, Frequency.DIARIO: 360
        }
        return mapa.get(freq, 1)

    def _get_tasa_mensual_efectiva(self, tasa_obj) -> float:
        i_base = tasa_obj.valor
        if tasa_obj.es_nominal:
            freq_cap = self._get_frecuencia_anual(tasa_obj.capitalizacion)
            i_periodo = i_base / freq_cap
            meses_por_periodo = 12 / freq_cap
            return math.pow(1 + i_periodo, 1 / meses_por_periodo) - 1
        else:
            freq_tasa = self._get_frecuencia_anual(tasa_obj.periodo)
            meses_duracion = 12 / freq_tasa
            return math.pow(1 + i_base, 1 / meses_duracion) - 1

    def resolver_ecuacion_valor(self, problema: ProblemaRenegociacion) -> dict:
        # 1. MOTOR INTERNO (Estandarizado a Mensual)
        tasa_mensual = self._get_tasa_mensual_efectiva(problema.tasa_referencia)
        ff = problema.fecha_focal_mes 
        
        # --- ANALISIS VISUAL (Tasa nativa para reporte) ---
        datos_visuales = {}
        if problema.tasa_referencia.es_nominal:
            freq_cap_nombre = problema.tasa_referencia.capitalizacion
            m = self._get_frecuencia_anual(freq_cap_nombre)
            i_periodo = problema.tasa_referencia.valor / m 
            datos_visuales = {
                "frecuencia_base": freq_cap_nombre,
                "m_anual": m,
                "i_periodo": round(i_periodo * 100, 4),
                "mensaje": f"Tasa {freq_cap_nombre} del {round(i_periodo*100, 4)}%"
            }
        else:
            datos_visuales = {
                "frecuencia_base": "mensual (efectiva)",
                "m_anual": 12,
                "i_periodo": round(tasa_mensual * 100, 4),
                "mensaje": f"Tasa Efectiva Mensual del {round(tasa_mensual*100, 4)}%"
            }

        # 2. Calcular Valor Presente TOTAL (Deuda Hoy)
        valor_presente_total = 0.0
        for d in problema.deudas_originales:
            vp = d.monto / math.pow(1 + tasa_mensual, d.vencimiento_meses)
            valor_presente_total += vp

        # 3. Mover Deudas a Fecha Focal (Lado A)
        suma_deudas_ff = 0.0
        detalles_deudas = []
        factor_conv_periodos = datos_visuales["m_anual"] / 12

        for d in problema.deudas_originales:
            n_meses = ff - d.vencimiento_meses
            factor = math.pow(1 + tasa_mensual, n_meses)
            valor_en_ff = d.monto * factor
            suma_deudas_ff += valor_en_ff
            
            n_periodos_cap = n_meses * factor_conv_periodos
            detalles_deudas.append({
                "monto_original": d.monto,
                "mes_origen": d.vencimiento_meses,
                "n_periodos_capitalizacion": round(n_periodos_cap, 4),
                "monto_en_ff": round(valor_en_ff, 2)
            })

        # 4. Mover Pagos a Fecha Focal (Lado B)
        suma_pagos_conocidos_ff = 0.0
        factor_total_x = 0.0
        detalles_pagos = []

        for p in problema.pagos_propuestos:
            n_meses = ff - p.mes
            factor_tiempo = math.pow(1 + tasa_mensual, n_meses)
            n_periodos_cap = n_meses * factor_conv_periodos

            if p.monto is not None:
                valor_pago = p.monto * factor_tiempo
                suma_pagos_conocidos_ff += valor_pago
                detalles_pagos.append({
                    "tipo": "CONOCIDO",
                    "monto_origen": p.monto,
                    "mes": p.mes,
                    "n_periodos": round(n_periodos_cap, 4),
                    "valor_ff": round(valor_pago, 2)
                })
            
            elif p.proporcion_incognita is not None:
                coef_en_ff = p.proporcion_incognita * factor_tiempo
                factor_total_x += coef_en_ff
                detalles_pagos.append({
                    "tipo": "INCOGNITA",
                    "proporcion": p.proporcion_incognita,
                    "mes": p.mes,
                    "n_periodos": round(n_periodos_cap, 4),
                    "factor_ff": round(coef_en_ff, 4)
                })

        # 5. Despejar X
        if factor_total_x == 0:
            return {"error": "No hay incógnita X que despejar."}
            
        valor_x = (suma_deudas_ff - suma_pagos_conocidos_ff) / factor_total_x
        valor_propuesta_ff = suma_pagos_conocidos_ff + (factor_total_x * valor_x)

        return {
            "valor_presente_deudas": round(valor_presente_total, 2),
            "valor_x": round(valor_x, 2),
            "balance_ecuacion": {
                "total_deudas_ff": round(suma_deudas_ff, 2),
                "total_propuesta_ff": round(valor_propuesta_ff, 2),
                "diferencia": round(suma_deudas_ff - valor_propuesta_ff, 4)
            },
            "analisis_tecnico": {
                "tasa_base_usada": datos_visuales["i_periodo"],
                "frecuencia": datos_visuales["frecuencia_base"],
                "desglose_deudas": detalles_deudas,
                "desglose_pagos": detalles_pagos
            }
        }

negotiation_service = NegotiationService()
