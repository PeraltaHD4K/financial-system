from app.llm_engine import llm_service, Config
from app.llm_schema_registry import ExtraccionFinanciera
from app.accounting.services import accounting_service
from app.negotiation.services import negotiation_service # <--- IMPORTAR NUEVO

# TEXTO COMPLEJO DE RENEGOCIACIÓN
TEXTO_PRUEBA = """
Contamos con 3 deudas, 1 de 100000 pesos con vencimiento en 2 meses, 250000 en 1 mes, 500000 en 6 meses.
Las cuales se van a renegociar, el banco acepta con las siguientes condiciones:
- Tasa de renegociacion del 19% con capuitalizacion mensual.
- Un primer pago hoy por 50000 pesos.
- El segundo pago en un año por el 50% del valor del tercer pago el cual sera en 2 años.
(Anual)
"""

SYSTEM_PROMPT = """
Eres un experto actuario financiero.
Analiza el texto y extrae una estructura JSON válida.
- Si es renegociación, identifica deudas originales y pagos propuestos.
- Si hay pagos iguales desconocidos, modelalos como incógnitas (proporcion_incognita=1.0).
- Normaliza tasas y tiempos.
- REGLA DE FECHA FOCAL: Si el usuario NO especifica explícitamente una "fecha focal", 
  debes establecer 'fecha_focal_mes' en 0.0 (El momento actual).
"""

def main():
    print(f"🚀 Iniciando Sistema Financiero Avanzado")
    print(f"🧠 Cerebro: {Config.PROVIDER.upper()} | 🧮 Motor: Python Math")
    print("-" * 60)

    try:
        # FASE 1: EXTRACCIÓN
        print("1️⃣  Analizando el problema...")
        extraccion = llm_service.extract_data(
            system_prompt=SYSTEM_PROMPT,
            user_text=TEXTO_PRUEBA,
            schema=ExtraccionFinanciera
        )
        print(f"   > Tipo detectado: {extraccion.problema.tipo}")
        print(f"   > Razonamiento: {extraccion.razonamiento}")

        # FASE 2: ORQUESTACIÓN Y CÁLCULO
        print("\n2️⃣  Ejecutando matemática financiera...")
        
        tipo = extraccion.problema.tipo
        
        if tipo == "renegociacion_deuda":
            resultado = negotiation_service.resolver_ecuacion_valor(extraccion.problema)
            tech = resultado["analisis_tecnico"]
            balance = resultado["balance_ecuacion"]
            
            print("\n✅ SOLUCIÓN DE RENEGOCIACIÓN:")
            print(f"   💰 DEUDA TOTAL HOY: ${resultado['valor_presente_deudas']:,.2f}")
            print(f"   💎 PAGO REQUERIDO (X): ${resultado['valor_x']:,.2f}")
            
            print("\n   --- 📋 Desglose Individual (Valuación en Fecha Focal) ---")
            print(f"   Tasa usada: {tech['tasa_base_usada']}% ({tech['frecuencia']})")
            
            print("\n   [DEUDAS ORIGINALES]")
            for d in tech['desglose_deudas']:
                # AQUÍ ESTÁ EL DATO QUE PEDISTE: d['monto_en_ff']
                flecha = "🔻" if d['n_periodos_capitalizacion'] < 0 else "🔺"
                print(f"   • Deuda de ${d['monto_original']:,.2f} (Vence Mes {d['mes_origen']})")
                print(f"     {flecha} Se mueve {d['n_periodos_capitalizacion']} periodos -> Vale HOY: ${d['monto_en_ff']:,.2f}")

            print("\n   [NUEVA PROPUESTA DE PAGO]")
            for p in tech['desglose_pagos']:
                if p['tipo'] == "CONOCIDO":
                    flecha = "🔻" if p['n_periodos'] < 0 else "🔺"
                    print(f"   • Pago Fijo de ${p['monto_origen']:,.2f} (Mes {p['mes']})")
                    print(f"     {flecha} Se mueve {p['n_periodos']} periodos -> Vale HOY: ${p['valor_ff']:,.2f}")
                else:
                    # Calculamos el valor monetario real de X para mostrarlo
                    valor_real_x_ff = p['factor_ff'] * resultado['valor_x']
                    flecha = "🔻" if p['n_periodos'] < 0 else "🔺"
                    print(f"   • Pago Incógnita (X) (Mes {p['mes']})")
                    print(f"     {flecha} Factor {p['factor_ff']} * X -> Aporta HOY: ${valor_real_x_ff:,.2f}")

            print("\n   --- ⚖️ Comprobación Final ---")
            print(f"   Sumatoria Deudas (Hoy):    ${balance['total_deudas_ff']:,.2f}")
            print(f"   Sumatoria Propuesta (Hoy): ${balance['total_propuesta_ff']:,.2f}")
            print(f"   Diferencia:                {balance['diferencia']}")
            
        elif tipo in ["interes_simple", "interes_compuesto", "descuento_bancario"]:
            resultado = accounting_service.solve(extraccion.problema)
            
            if "error" in resultado:
                print(f"\n❌ ERROR MATEMÁTICO: {resultado['error']}")
            else:
                res = resultado.get("resumen", {})
                mon = res.get("variables_monetarias", {})
                tas = res.get("variables_tasa", {})
                tie = res.get("variables_tiempo", {})
                
                print("\n✅ FICHA TÉCNICA DE LA OPERACIÓN (Interés Simple):")
                print(f"   ──────────────────────────────────────────")
                print(f"   💵 [C] Capital Inicial:      $ {mon.get('C', 0):,.2f}")
                print(f"   📈 [I] Interés Ganado:       $ {mon.get('I', 0):,.2f}")
                print(f"   💰 [M] Monto Final:          $ {mon.get('M', 0):,.2f}")
                print(f"   ──────────────────────────────────────────")
                print(f"   📊 [r] Tasa Nominal:         {tas.get('r', 0)*100:.2f}% Anual")
                print(f"   📉 [i] Tasa Periodo:         {tas.get('i', 0)*100:.4f}% ({tas.get('freq')})")
                print(f"   ──────────────────────────────────────────")
                print(f"   📅 [t] Plazo Real:           {tie.get('t_legible')}")
                print(f"   🧮 [n] N° Periodos:          {tie.get('n', 0):.4f} periodos ({tas.get('freq')})")
                
                print(f"\n   🔎 Fórmula Despeje: {resultado.get('formula')}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
