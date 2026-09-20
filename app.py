import streamlit as st
import pandas as pd
import io
from datetime import date

st.set_page_config(
    page_title="Antes de invertir",
    page_icon="🧭",
    layout="wide"
)

# ============================================================
# ESTILOS
# ============================================================
st.markdown("""
<style>
.block-container {
    max-width: 1250px;
    padding-top: 1.7rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 1.4rem 1.6rem;
    border-radius: 16px;
    border: 1px solid #d9d9d9;
    margin-bottom: 1rem;
}
.notice {
    padding: 1rem 1.2rem;
    border-radius: 12px;
    background: #f5f7fa;
    border-left: 5px solid #667085;
    margin-bottom: 1.2rem;
}
.step {
    font-size: .95rem;
    opacity: .85;
}
.risk-note {
    padding: .8rem 1rem;
    border-radius: 10px;
    background: #f8f9fb;
    margin-bottom: .7rem;
}
.small {
    font-size: .88rem;
    opacity: .8;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================
PROBABILIDAD = {
    "Elegir...": 0,
    "1 · Muy poco probable": 1,
    "2 · Poco probable": 2,
    "3 · Posible": 3,
    "4 · Probable": 4,
    "5 · Muy probable / ya ocurre": 5,
}

IMPACTO = {
    "Elegir...": 0,
    "1 · Mínimo: se absorbe con la caja normal": 1,
    "2 · Bajo: requiere un ajuste menor": 2,
    "3 · Moderado: obliga a reprogramar gastos": 3,
    "4 · Alto: compromete liquidez o pagos": 4,
    "5 · Crítico: puede comprometer la continuidad": 5,
}

RESPONSABLES = [
    "Elegir...",
    "Propietario/a",
    "Administración",
    "Responsable financiero",
    "Encargado/a del proyecto",
    "Operaciones",
    "Otro",
]

FRECUENCIAS = [
    "Elegir...",
    "Semanal",
    "Quincenal",
    "Mensual",
    "Trimestral",
    "Por hito del proyecto",
]

ESTADOS = ["Pendiente", "En curso", "Controlado", "Revisar"]

RUBROS = [
    "Elegir...",
    "Panadería",
    "Gastronomía",
    "Supermercado / Minimercado",
    "Comercio",
    "Industria / Manufactura",
    "Taller / Servicios",
    "Construcción",
    "Otro",
]

TIPOS_INVERSION = [
    "Elegir...",
    "Compra de maquinaria o equipamiento",
    "Ampliación de capacidad productiva",
    "Apertura de un nuevo local / sucursal",
    "Incorporación de tecnología o software",
    "Mejora de infraestructura",
    "Nuevo producto o línea de negocio",
    "Otra",
]

OBJETIVOS = [
    "Elegir...",
    "Aumentar la capacidad de producción",
    "Reducir costos operativos",
    "Mejorar la productividad",
    "Mejorar la calidad del producto o servicio",
    "Reemplazar equipos obsoletos",
    "Incorporar tecnología / automatización",
    "Expandirse a otro mercado o zona",
    "Abrir un nuevo punto de venta",
    "Diversificar productos o servicios",
    "Mejorar seguridad y continuidad operativa",
    "Cumplir requisitos técnicos o regulatorios",
    "Otro",
]

FINANCIAMIENTO = [
    "Elegir...",
    "100% recursos propios",
    "Mixto (recursos propios + préstamo)",
    "100% préstamo / crédito",
    "Fondo / subsidio + recursos propios",
    "A definir",
    "Otro",
]

MONEDAS = [
    "UYU · Pesos uruguayos",
    "USD · Dólares estadounidenses",
]

# ============================================================
# RIESGOS BASE
# Enfoque principal: impacto financiero de una decisión de inversión.
# ============================================================
RIESGOS = {
    "R1": {
        "nombre": "Ingresos menores a los previstos",
        "factor": "Mercado",
        "pregunta_deteccion": "¿La inversión depende de que aumenten las ventas o ingresos para recuperar el dinero o cumplir nuevas obligaciones?",
        "disparadores": ["Sí", "No sé"],
        "causa": "Alta dependencia de ingresos futuros para sostener la inversión.",
        "evento": "Las ventas o ingresos adicionales resultan menores o llegan más tarde de lo previsto.",
        "consecuencia": "Menor recuperación de la inversión y mayor presión sobre la liquidez.",
        "tratamiento": "Definir un escenario conservador de ingresos y revisar si la empresa puede sostener gastos y obligaciones durante una recuperación más lenta.",
        "indicador": "Ingresos reales generados por la inversión vs. ingresos previstos.",
        "meta": "Revisar mensualmente el desvío y activar medidas si los ingresos reales quedan por debajo de lo previsto.",
        "frecuencia": "Mensual",
    },
    "R2": {
        "nombre": "Costos totales superiores a los presupuestados",
        "factor": "Financiero",
        "pregunta_deteccion": "¿Tenés identificados y presupuestados, además del precio de compra, los costos de instalación, obra, capacitación, mantenimiento inicial, energía, repuestos y otros gastos asociados?",
        "disparadores": ["No", "No sé"],
        "causa": "Presupuesto incompleto de la inversión.",
        "evento": "Aparecen costos no contemplados o mayores a los estimados.",
        "consecuencia": "Se requieren recursos adicionales, aumenta el endeudamiento o disminuye la liquidez.",
        "tratamiento": "Armar un presupuesto integral de la inversión, solicitar cotizaciones y reservar un margen para contingencias antes de comprometer todo el capital.",
        "indicador": "Desvío porcentual del costo real acumulado respecto del presupuesto total.",
        "meta": "Mantener el desvío dentro del margen de contingencia definido por la empresa.",
        "frecuencia": "Por hito del proyecto",
    },
    "R3": {
        "nombre": "Tensión de liquidez durante la inversión",
        "factor": "Financiero",
        "pregunta_deteccion": "Si la inversión demora en generar resultados, ¿la empresa podría seguir pagando sus gastos habituales y compromisos sin quedar sin efectivo?",
        "disparadores": ["No", "No sé"],
        "causa": "Margen de liquidez insuficiente durante la ejecución o puesta en marcha.",
        "evento": "La inversión tarda más de lo esperado en generar ingresos o aparecen egresos extraordinarios.",
        "consecuencia": "Dificultad para pagar obligaciones corrientes y sostener la operación.",
        "tratamiento": "Proyectar el flujo de caja durante la ejecución y definir una reserva mínima para cubrir gastos y obligaciones mientras la inversión todavía no genera el resultado esperado.",
        "indicador": "Meses de gastos y obligaciones que pueden cubrirse con la liquidez disponible.",
        "meta": "Definir y mantener el colchón de liquidez que la empresa considere necesario para el período de puesta en marcha.",
        "frecuencia": "Mensual",
    },
    "R4": {
        "nombre": "Dificultad para cumplir el financiamiento",
        "factor": "Financiero",
        "pregunta_deteccion": "¿La inversión se financiará total o parcialmente con préstamo, crédito o cuotas?",
        "disparadores": ["Sí"],
        "causa": "Incorporación de obligaciones financieras periódicas.",
        "evento": "En un período de menores ingresos o mayores costos, la empresa no dispone de fondos suficientes para pagar una cuota en fecha.",
        "consecuencia": "Atrasos, recargos y mayor presión sobre el flujo de caja.",
        "tratamiento": "Construir un calendario de cuotas, comparar cada vencimiento con el flujo de caja proyectado y actuar antes del vencimiento si aparece una brecha de pago.",
        "indicador": "Cuotas pagadas en fecha / total de cuotas vencidas.",
        "meta": "100% de las cuotas pagadas en fecha.",
        "frecuencia": "Mensual",
    },
    "R5": {
        "nombre": "Exposición al tipo de cambio",
        "factor": "Financiero / Mercado",
        "pregunta_deteccion": "¿La compra, deuda o cuotas están en dólares mientras la mayor parte de los ingresos de la empresa son en pesos?",
        "disparadores": ["Sí", "No sé"],
        "causa": "Descalce entre la moneda de los ingresos y la moneda de la obligación.",
        "evento": "El tipo de cambio se mueve de forma desfavorable.",
        "consecuencia": "Aumenta el costo en pesos de la inversión o de las obligaciones.",
        "tratamiento": "Identificar cuánto de la inversión queda expuesto a moneda extranjera, simular una suba del tipo de cambio y definir cómo cubrir esa diferencia sin afectar la operación.",
        "indicador": "Porcentaje de deuda u obligaciones de la inversión expresadas en moneda extranjera.",
        "meta": "Conocer y revisar la exposición antes de cada vencimiento relevante.",
        "frecuencia": "Mensual",
    },
    "R6": {
        "nombre": "Demora en habilitación o puesta en marcha",
        "factor": "Legal / Operativo",
        "pregunta_deteccion": "¿La inversión depende de habilitaciones, permisos, obras, instalaciones o trámites que todavía no están completamente resueltos?",
        "disparadores": ["Sí", "No sé"],
        "causa": "Dependencia de requisitos o hitos previos todavía pendientes.",
        "evento": "La habilitación, obra o instalación se demora más de lo previsto.",
        "consecuencia": "El capital queda inmovilizado y se retrasa la generación de ingresos.",
        "tratamiento": "Listar los requisitos e hitos críticos, verificar responsables y plazos, y evitar comprometer etapas irreversibles sin conocer el estado de las condiciones necesarias.",
        "indicador": "Hitos críticos completados / total de hitos críticos requeridos.",
        "meta": "100% de los requisitos críticos completados antes de la puesta en marcha.",
        "frecuencia": "Por hito del proyecto",
    },
    "R7": {
        "nombre": "Dependencia de proveedores, repuestos o técnicos",
        "factor": "Operativo / Abastecimiento",
        "pregunta_deteccion": "¿La inversión depende de un proveedor, repuesto, técnico o servicio especializado que sería difícil reemplazar rápidamente?",
        "disparadores": ["Sí", "No sé"],
        "causa": "Dependencia de un tercero crítico con pocas alternativas.",
        "evento": "El proveedor, repuesto o servicio técnico falla, demora o deja de estar disponible.",
        "consecuencia": "La inversión queda parcial o totalmente detenida y se generan pérdidas o costos adicionales.",
        "tratamiento": "Identificar al menos una alternativa viable para los insumos o servicios críticos y conocer tiempos de entrega, contacto y condiciones de reposición.",
        "indicador": "Cantidad de alternativas validadas para cada proveedor, repuesto o técnico crítico.",
        "meta": "Contar con al menos una alternativa viable para cada dependencia crítica identificada.",
        "frecuencia": "Trimestral",
    },
    "R8": {
        "nombre": "Interrupción por falla del activo incorporado",
        "factor": "Tecnológico / Operativo",
        "pregunta_deteccion": "¿La inversión incorpora una máquina, equipo o tecnología cuya falla podría detener una parte importante de la producción o del servicio?",
        "disparadores": ["Sí", "No sé"],
        "causa": "Alta dependencia operativa del nuevo activo.",
        "evento": "El equipo falla o queda fuera de servicio.",
        "consecuencia": "Se interrumpe la producción o el servicio y se pierden ingresos mientras se recupera la operación.",
        "tratamiento": "Definir mantenimiento preventivo, contacto de soporte, repuestos críticos y una alternativa temporal de operación ante una falla.",
        "indicador": "Horas de indisponibilidad del equipo por fallas no planificadas.",
        "meta": "Reducir al mínimo las horas de parada no planificada y revisar cada incidente relevante.",
        "frecuencia": "Mensual",
    },
}

# ============================================================
# FUNCIONES
# ============================================================
def clasificar(nivel):
    if nivel <= 0:
        return "Sin evaluar"
    if nivel <= 5:
        return "Bajo"
    if nivel <= 10:
        return "Medio"
    if nivel <= 15:
        return "Alto"
    return "Crítico"

def color_prioridad(prioridad):
    return {
        "Bajo": "#D9EAD3",
        "Medio": "#FFF2CC",
        "Alto": "#FCE5CD",
        "Crítico": "#F4CCCC",
        "Sin evaluar": "#EDEDED",
    }.get(prioridad, "#EDEDED")

def moneda_simbolo(moneda):
    return "$U" if moneda.startswith("UYU") else "US$"

def matriz_html(df):
    posiciones = {}
    for _, row in df.iterrows():
        if row["Probabilidad"] > 0 and row["Impacto"] > 0:
            posiciones.setdefault((int(row["Probabilidad"]), int(row["Impacto"])), []).append(row["Código"])

    html = """
    <div style="overflow-x:auto;">
    <table style="border-collapse:collapse; text-align:center; min-width:650px; width:100%;">
      <tr>
        <th style="padding:8px;border:1px solid #bbb;">Prob. \\ Impacto</th>
    """
    for i in range(1, 6):
        html += f'<th style="padding:8px;border:1px solid #bbb;">{i}</th>'
    html += "</tr>"

    for p in range(5, 0, -1):
        html += f'<tr><th style="padding:8px;border:1px solid #bbb;">{p}</th>'
        for imp in range(1, 6):
            nivel = p * imp
            prioridad = clasificar(nivel)
            color = color_prioridad(prioridad)
            codigos = "<br>".join(posiciones.get((p, imp), []))
            html += (
                f'<td style="height:64px;padding:6px;border:1px solid #bbb;'
                f'background:{color};font-weight:700;">{codigos}</td>'
            )
        html += "</tr>"
    html += "</table></div>"
    return html

def excel_bytes(datos_inversion, riesgos_df, plan_df):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        workbook = writer.book

        # Paleta
        navy = "#1F4E78"
        blue = "#D9EAF7"
        light = "#F7F9FC"
        border = "#D0D5DD"
        green = "#D9EAD3"
        yellow = "#FFF2CC"
        orange = "#FCE5CD"
        red = "#F4CCCC"

        fmt_title = workbook.add_format({
            "bold": True, "font_size": 18, "font_color": "white",
            "bg_color": navy, "align": "center", "valign": "vcenter"
        })
        fmt_section = workbook.add_format({
            "bold": True, "font_size": 12, "font_color": "white",
            "bg_color": navy, "align": "left", "valign": "vcenter"
        })
        fmt_label = workbook.add_format({
            "bold": True, "bg_color": blue, "border": 1, "border_color": border,
            "valign": "top"
        })
        fmt_value = workbook.add_format({
            "border": 1, "border_color": border, "text_wrap": True, "valign": "top"
        })
        fmt_header = workbook.add_format({
            "bold": True, "font_color": "white", "bg_color": navy,
            "border": 1, "border_color": border, "align": "center",
            "valign": "vcenter", "text_wrap": True
        })
        fmt_wrap = workbook.add_format({
            "border": 1, "border_color": border, "text_wrap": True, "valign": "top"
        })
        fmt_center = workbook.add_format({
            "border": 1, "border_color": border, "align": "center", "valign": "vcenter"
        })

        priority_formats = {
            "Bajo": workbook.add_format({"bg_color": green, "border": 1, "align": "center"}),
            "Medio": workbook.add_format({"bg_color": yellow, "border": 1, "align": "center"}),
            "Alto": workbook.add_format({"bg_color": orange, "border": 1, "align": "center"}),
            "Crítico": workbook.add_format({"bg_color": red, "bold": True, "border": 1, "align": "center"}),
        }

        # ---------------- RESUMEN ----------------
        ws = workbook.add_worksheet("Resumen")
        writer.sheets["Resumen"] = ws
        ws.hide_gridlines(2)
        ws.set_column("A:A", 25)
        ws.set_column("B:B", 42)
        ws.set_column("D:D", 24)
        ws.set_column("E:E", 18)

        ws.merge_range("A1:E2", "ANTES DE INVERTIR · AUTODIAGNÓSTICO DE RIESGOS", fmt_title)
        ws.set_row(0, 28)
        ws.write("A4", "Datos de la inversión", fmt_section)
        ws.merge_range("A4:B4", "Datos de la inversión", fmt_section)

        fila = 4
        for label, value in datos_inversion.items():
            ws.write(f"A{fila+1}", label, fmt_label)
            ws.write(f"B{fila+1}", value, fmt_value)
            fila += 1

        ws.write("D4", "Resumen de riesgos", fmt_section)
        ws.merge_range("D4:E4", "Resumen de riesgos", fmt_section)

        conteos = riesgos_df["Prioridad"].value_counts().to_dict() if not riesgos_df.empty else {}
        resumen_items = [
            ("Riesgos evaluados", len(riesgos_df)),
            ("Críticos", conteos.get("Crítico", 0)),
            ("Altos", conteos.get("Alto", 0)),
            ("Medios", conteos.get("Medio", 0)),
            ("Bajos", conteos.get("Bajo", 0)),
        ]
        rr = 5
        for label, value in resumen_items:
            ws.write(f"D{rr}", label, fmt_label)
            if label in priority_formats:
                ws.write(f"E{rr}", value, priority_formats[label])
            else:
                ws.write(f"E{rr}", value, fmt_center)
            rr += 1

        ws.write(f"A{fila+2}", "Mensaje clave", fmt_section)
        ws.merge_range(f"A{fila+2}:E{fila+2}", "Mensaje clave", fmt_section)
        ws.merge_range(
            f"A{fila+3}:E{fila+5}",
            "La herramienta no decide si conviene invertir. Ayuda a identificar, priorizar y tratar los riesgos asociados a la inversión antes y durante su ejecución.",
            workbook.add_format({
                "bg_color": light, "border": 1, "border_color": border,
                "text_wrap": True, "valign": "vcenter", "align": "left"
            })
        )

        # ---------------- RIESGOS ----------------
        riesgos_df.to_excel(writer, sheet_name="Riesgos", index=False, startrow=2)
        wr = writer.sheets["Riesgos"]
        wr.hide_gridlines(2)
        wr.merge_range(0, 0, 0, len(riesgos_df.columns)-1, "RIESGOS IDENTIFICADOS Y PRIORIZADOS", fmt_title)
        for col_num, col_name in enumerate(riesgos_df.columns):
            wr.write(2, col_num, col_name, fmt_header)

        widths = {
            "Código": 10, "Riesgo": 34, "Factor / origen": 23, "Causa": 38,
            "Evento": 40, "Consecuencia financiera": 42, "Probabilidad": 14,
            "Impacto": 12, "Nivel": 10, "Prioridad": 12
        }
        for idx, col in enumerate(riesgos_df.columns):
            wr.set_column(idx, idx, widths.get(col, 22))

        for row_idx in range(len(riesgos_df)):
            excel_row = row_idx + 3
            for col_idx, col in enumerate(riesgos_df.columns):
                value = riesgos_df.iloc[row_idx, col_idx]
                if col == "Prioridad":
                    wr.write(excel_row, col_idx, value, priority_formats.get(value, fmt_center))
                elif col in ["Probabilidad", "Impacto", "Nivel", "Código"]:
                    wr.write(excel_row, col_idx, value, fmt_center)
                else:
                    wr.write(excel_row, col_idx, value, fmt_wrap)

        wr.freeze_panes(3, 0)
        wr.autofilter(2, 0, max(2, len(riesgos_df)+2), len(riesgos_df.columns)-1)

        # ---------------- PLAN ----------------
        plan_df.to_excel(writer, sheet_name="Plan de acción", index=False, startrow=2)
        wp = writer.sheets["Plan de acción"]
        wp.hide_gridlines(2)
        wp.merge_range(0, 0, 0, len(plan_df.columns)-1, "PLAN DE TRATAMIENTO Y SEGUIMIENTO", fmt_title)
        for col_num, col_name in enumerate(plan_df.columns):
            wp.write(2, col_num, col_name, fmt_header)

        plan_widths = {
            "Código": 10, "Riesgo": 32, "Prioridad": 12, "Tratamiento": 55,
            "Responsable": 22, "Indicador": 42, "Meta / criterio de control": 42,
            "Frecuencia": 18, "Estado": 14
        }
        for idx, col in enumerate(plan_df.columns):
            wp.set_column(idx, idx, plan_widths.get(col, 22))

        for row_idx in range(len(plan_df)):
            excel_row = row_idx + 3
            for col_idx, col in enumerate(plan_df.columns):
                value = plan_df.iloc[row_idx, col_idx]
                if col == "Prioridad":
                    wp.write(excel_row, col_idx, value, priority_formats.get(value, fmt_center))
                elif col in ["Código", "Frecuencia", "Estado", "Responsable"]:
                    wp.write(excel_row, col_idx, value, fmt_center)
                else:
                    wp.write(excel_row, col_idx, value, fmt_wrap)

        wp.freeze_panes(3, 0)
        wp.autofilter(2, 0, max(2, len(plan_df)+2), len(plan_df.columns)-1)

        # ---------------- MATRIZ ----------------
        wm = workbook.add_worksheet("Matriz")
        writer.sheets["Matriz"] = wm
        wm.hide_gridlines(2)
        wm.merge_range("A1:G2", "MATRIZ 5 × 5 DE RIESGOS", fmt_title)
        wm.write("A4", "Probabilidad \\ Impacto", fmt_header)
        for imp in range(1, 6):
            wm.write(3, imp, imp, fmt_header)

        color_fmts = {
            "Bajo": workbook.add_format({"bg_color": green, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
            "Medio": workbook.add_format({"bg_color": yellow, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
            "Alto": workbook.add_format({"bg_color": orange, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
            "Crítico": workbook.add_format({"bg_color": red, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
        }

        posiciones = {}
        for _, r in riesgos_df.iterrows():
            posiciones.setdefault((int(r["Probabilidad"]), int(r["Impacto"])), []).append(str(r["Código"]))

        for row, p in enumerate(range(5, 0, -1), start=4):
            wm.write(row, 0, p, fmt_header)
            for imp in range(1, 6):
                nivel = p * imp
                prioridad = clasificar(nivel)
                contenido = "\n".join(posiciones.get((p, imp), []))
                wm.write(row, imp, contenido, color_fmts[prioridad])
                wm.set_row(row, 42)

        wm.set_column("A:A", 24)
        wm.set_column("B:F", 14)
        wm.write("A11", "Leyenda", fmt_section)
        leyenda = [("Bajo", green), ("Medio", yellow), ("Alto", orange), ("Crítico", red)]
        row = 11
        for nombre, col in leyenda:
            f = workbook.add_format({"bg_color": col, "border": 1, "bold": True, "align": "center"})
            wm.write(row, 0, nombre, f)
            row += 1

    output.seek(0)
    return output.getvalue()

# ============================================================
# CABECERA
# ============================================================
st.markdown("""
<div class="hero">
<h1>🧭 Antes de invertir: identificá y gestioná tus riesgos</h1>
<p><strong>Autodiagnóstico de riesgos asociados a decisiones de inversión para PyMEs</strong></p>
<p class="step">1. Tu inversión → 2. Detectar riesgos → 3. Evaluar → 4. Priorizar → 5. Tratar y hacer seguimiento</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
⚠️ <strong>Esta herramienta NO decide si tenés que invertir o no.</strong><br>
Te ayuda a reconocer qué riesgos puede generar la inversión, cuáles requieren más atención y qué acciones podés definir para gestionarlos.
</div>
""", unsafe_allow_html=True)

st.caption("Enfoque principal del proyecto: impacto financiero de los riesgos asociados a una inversión.")

# ============================================================
# 1. DATOS DE LA INVERSIÓN
# ============================================================
st.header("1. Datos de tu inversión")
st.caption("Esta información da contexto a la evaluación. Todavía no determina el nivel de riesgo.")

c1, c2 = st.columns(2)

with c1:
    empresa = st.text_input("Nombre de la empresa")
    rubro = st.selectbox("Rubro", RUBROS)
    if rubro == "Otro":
        rubro_otro = st.text_input("Especificá el rubro")
    else:
        rubro_otro = ""

    tipo_inversion = st.selectbox("Tipo de inversión", TIPOS_INVERSION)
    if tipo_inversion == "Otra":
        tipo_inversion_otro = st.text_area(
            "Especificá el tipo de inversión",
            placeholder="Ej.: adquisición de un vehículo especializado para distribución."
        )
    else:
        tipo_inversion_otro = ""

with c2:
    moneda = st.selectbox("Moneda", MONEDAS)
    monto = st.number_input("Monto estimado de la inversión", min_value=0.0, step=1000.0)

    objetivo = st.selectbox("Objetivo principal de la inversión", OBJETIVOS)
    if objetivo == "Otro":
        objetivo_otro = st.text_area(
            "Especificá el objetivo",
            placeholder="Ej.: reducir tiempos de entrega al cliente."
        )
    else:
        objetivo_otro = ""

    financiamiento = st.selectbox("Forma de financiamiento", FINANCIAMIENTO)
    if financiamiento == "Otro":
        financiamiento_otro = st.text_input("Especificá la forma de financiamiento")
    else:
        financiamiento_otro = ""

st.divider()

# ============================================================
# 2. DETECCIÓN
# ============================================================
st.header("2. Detección de riesgos")
st.write(
    "Respondé estas preguntas sobre la inversión. "
    "Si respondés **Sí** o **No sé** en determinadas situaciones, la herramienta marcará un riesgo para revisar."
)

respuestas = {}
for codigo, info in RIESGOS.items():
    respuestas[codigo] = st.radio(
        info["pregunta_deteccion"],
        ["Sí", "No", "No sé"],
        horizontal=True,
        key=f"det_{codigo}"
    )

riesgos_detectados = [
    codigo for codigo, info in RIESGOS.items()
    if respuestas[codigo] in info["disparadores"]
]

if riesgos_detectados:
    st.success(f"Se detectaron {len(riesgos_detectados)} riesgos para evaluar.")
else:
    st.info(
        "Con estas respuestas no se detectaron riesgos mediante este cuestionario. "
        "Esto no significa que la inversión esté libre de riesgos."
    )

st.divider()

# ============================================================
# 3. EVALUACIÓN
# ============================================================
st.header("3. Evaluación de los riesgos detectados")

evaluados = []

if not riesgos_detectados:
    st.info("No hay riesgos detectados para puntuar.")
else:
    for codigo in riesgos_detectados:
        info = RIESGOS[codigo]

        with st.expander(f"{codigo} · {info['nombre']}", expanded=True):
            st.markdown(
                f"""
                <div class="risk-note">
                <strong>Factor de origen:</strong> {info['factor']}<br>
                <strong>Causa:</strong> {info['causa']}<br>
                <strong>Evento:</strong> {info['evento']}<br>
                <strong>Consecuencia financiera:</strong> {info['consecuencia']}
                </div>
                """,
                unsafe_allow_html=True
            )

            colp, coli = st.columns(2)

            with colp:
                p_txt = st.selectbox(
                    "Probabilidad de que ocurra",
                    list(PROBABILIDAD.keys()),
                    key=f"prob_{codigo}"
                )
            with coli:
                i_txt = st.selectbox(
                    "Impacto si ocurre",
                    list(IMPACTO.keys()),
                    key=f"imp_{codigo}"
                )

            p = PROBABILIDAD[p_txt]
            i = IMPACTO[i_txt]
            nivel = p * i
            prioridad = clasificar(nivel)

            if nivel > 0:
                st.markdown(
                    f"""
                    <div style="padding:.7rem 1rem;border-radius:10px;
                    background:{color_prioridad(prioridad)};
                    font-weight:700;">
                    Nivel {nivel} · {prioridad}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.caption("Completá probabilidad e impacto para calcular el nivel.")

            evaluados.append({
                "Código": codigo,
                "Riesgo": info["nombre"],
                "Factor / origen": info["factor"],
                "Causa": info["causa"],
                "Evento": info["evento"],
                "Consecuencia financiera": info["consecuencia"],
                "Probabilidad": p,
                "Impacto": i,
                "Nivel": nivel,
                "Prioridad": prioridad,
            })

df_eval = pd.DataFrame(evaluados)
if not df_eval.empty:
    df_eval = df_eval[df_eval["Nivel"] > 0].copy()
    if not df_eval.empty:
        df_eval = df_eval.sort_values(["Nivel", "Impacto"], ascending=False)

st.divider()

# ============================================================
# 4. RESULTADOS + MATRIZ
# ============================================================
st.header("4. Resultados y matriz de riesgos")

if df_eval.empty:
    st.info("Completá la evaluación para generar la matriz.")
else:
    a, b, c, d = st.columns(4)
    a.metric("Críticos", int((df_eval["Prioridad"] == "Crítico").sum()))
    b.metric("Altos", int((df_eval["Prioridad"] == "Alto").sum()))
    c.metric("Medios", int((df_eval["Prioridad"] == "Medio").sum()))
    d.metric("Bajos", int((df_eval["Prioridad"] == "Bajo").sum()))

    st.markdown("### Matriz 5 × 5")
    st.markdown(matriz_html(df_eval), unsafe_allow_html=True)
    st.caption("Verde = Bajo · Amarillo = Medio · Naranja = Alto · Rojo = Crítico")

    st.markdown("### Riesgos priorizados")
    st.dataframe(
        df_eval[["Código", "Riesgo", "Factor / origen", "Probabilidad", "Impacto", "Nivel", "Prioridad"]],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ============================================================
# 5. PLAN DE ACCIÓN
# ============================================================
st.header("5. Plan de tratamiento y seguimiento")
st.write(
    "La herramienta propone un tratamiento inicial y un indicador práctico. "
    "Podés editarlos para adaptarlos a la realidad de la empresa."
)

plan = []

if df_eval.empty:
    st.info("Primero evaluá los riesgos para construir el plan.")
else:
    for _, row in df_eval.iterrows():
        codigo = row["Código"]
        info = RIESGOS[codigo]

        st.markdown(f"### {codigo} · {row['Riesgo']}")
        st.markdown(
            f"<div style='display:inline-block;padding:.35rem .65rem;border-radius:8px;"
            f"background:{color_prioridad(row['Prioridad'])};font-weight:700;'>"
            f"{row['Prioridad']} · Nivel {row['Nivel']}</div>",
            unsafe_allow_html=True
        )

        tratamiento = st.text_area(
            "Tratamiento propuesto",
            value=info["tratamiento"],
            key=f"trat_{codigo}"
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            responsable = st.selectbox(
                "Responsable",
                RESPONSABLES,
                key=f"resp_{codigo}"
            )
        with c2:
            frecuencia = st.selectbox(
                "Frecuencia de revisión",
                FRECUENCIAS,
                index=FRECUENCIAS.index(info["frecuencia"]) if info["frecuencia"] in FRECUENCIAS else 0,
                key=f"freq_{codigo}"
            )
        with c3:
            estado = st.selectbox(
                "Estado",
                ESTADOS,
                key=f"estado_{codigo}"
            )

        indicador = st.text_input(
            "Indicador de seguimiento",
            value=info["indicador"],
            key=f"ind_{codigo}"
        )

        meta = st.text_area(
            "Meta / criterio de control",
            value=info["meta"],
            key=f"meta_{codigo}"
        )

        plan.append({
            "Código": codigo,
            "Riesgo": row["Riesgo"],
            "Prioridad": row["Prioridad"],
            "Tratamiento": tratamiento,
            "Responsable": responsable,
            "Indicador": indicador,
            "Meta / criterio de control": meta,
            "Frecuencia": frecuencia,
            "Estado": estado,
        })

        st.divider()

df_plan = pd.DataFrame(plan)

# ============================================================
# 6. RESUMEN + EXCEL
# ============================================================
st.header("6. Resumen final")

tipo_final = tipo_inversion_otro.strip() if tipo_inversion == "Otra" and tipo_inversion_otro.strip() else tipo_inversion
objetivo_final = objetivo_otro.strip() if objetivo == "Otro" and objetivo_otro.strip() else objetivo
rubro_final = rubro_otro.strip() if rubro == "Otro" and rubro_otro.strip() else rubro
financiamiento_final = (
    financiamiento_otro.strip()
    if financiamiento == "Otro" and financiamiento_otro.strip()
    else financiamiento
)

simbolo = moneda_simbolo(moneda)

datos_inversion = {
    "Fecha": date.today().strftime("%d/%m/%Y"),
    "Empresa": empresa if empresa else "-",
    "Rubro": rubro_final,
    "Tipo de inversión": tipo_final,
    "Monto estimado": f"{simbolo} {monto:,.2f}",
    "Objetivo": objetivo_final,
    "Financiamiento": financiamiento_final,
}

if df_eval.empty:
    st.info("Completá la evaluación para generar el resumen final.")
else:
    st.markdown("### Datos de la inversión")
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Empresa:** {datos_inversion['Empresa']}")
    c1.write(f"**Rubro:** {datos_inversion['Rubro']}")
    c2.write(f"**Tipo:** {datos_inversion['Tipo de inversión']}")
    c2.write(f"**Objetivo:** {datos_inversion['Objetivo']}")
    c3.write(f"**Monto:** {datos_inversion['Monto estimado']}")
    c3.write(f"**Financiamiento:** {datos_inversion['Financiamiento']}")

    prioritarios = df_eval[df_eval["Prioridad"].isin(["Crítico", "Alto"])]
    if not prioritarios.empty:
        st.markdown("### Atención prioritaria")
        for _, r in prioritarios.iterrows():
            st.markdown(
                f"<div style='padding:.6rem .8rem;margin:.3rem 0;border-radius:8px;"
                f"background:{color_prioridad(r['Prioridad'])};'>"
                f"<strong>{r['Código']} · {r['Riesgo']}</strong> — "
                f"Nivel {r['Nivel']} · {r['Prioridad']}</div>",
                unsafe_allow_html=True
            )
    else:
        st.success("No se clasificaron riesgos como altos o críticos con la evaluación realizada.")

    st.markdown("### Plan consolidado")
    st.dataframe(df_plan, use_container_width=True, hide_index=True)

    excel = excel_bytes(datos_inversion, df_eval, df_plan)

    st.download_button(
        "📊 Descargar informe en Excel",
        data=excel,
        file_name="autodiagnostico_riesgos_inversion.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.divider()

if st.button("↺ Reiniciar herramienta"):
    st.session_state.clear()
    st.rerun()

st.caption(
    "Herramienta académica de autodiagnóstico. No determina si una inversión debe realizarse "
    "ni sustituye asesoramiento profesional. Desarrollada por estudiantes de Ingeniería en Logística · UTEC."
)
