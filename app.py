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
    background: #f4f6f8;
    color: #111111;
    border-left: 5px solid #667085;
    margin-bottom: 1.2rem;
}
.small {
    font-size: .9rem;
    opacity: .85;
}
.legend-box {
    padding: .8rem 1rem;
    border-radius: 10px;
    margin-bottom: .45rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# OPCIONES
# ============================================================
PROBABILIDAD = {
    "Elegir...": 0,
    "1 · Muy poco probable": 1,
    "2 · Poco probable": 2,
    "3 · Puede pasar": 3,
    "4 · Bastante probable": 4,
    "5 · Muy probable / ya pasó algo parecido": 5,
}

IMPACTO = {
    "Elegir...": 0,
    "1 · Casi no afectaría al negocio": 1,
    "2 · Complicaría un poco, pero se resolvería rápido": 2,
    "3 · Sería un problema importante": 3,
    "4 · Afectaría seriamente al negocio": 4,
    "5 · Podría poner en riesgo la continuidad de la empresa": 5,
}

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
    "Reducir costos",
    "Mejorar la productividad",
    "Mejorar la calidad",
    "Reemplazar equipos viejos",
    "Incorporar tecnología / automatización",
    "Expandirse a otra zona o mercado",
    "Abrir un nuevo punto de venta",
    "Diversificar productos o servicios",
    "Mejorar la seguridad o continuidad del negocio",
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
    "Cuando ocurra un cambio importante",
]

ESTADOS = [
    "Pendiente",
    "En curso",
    "Controlado",
    "Revisar",
]

# ============================================================
# RIESGOS CON LENGUAJE SIMPLE
# ============================================================
RIESGOS = {
    "R1": {
        "nombre": "Ventas menores a lo esperado",
        "pregunta_prob": "¿Qué tan probable es que después de hacer la inversión las ventas no aumenten tanto como esperás?",
        "pregunta_imp": "Si eso pasa, ¿qué tan grave sería para poder pagar los gastos del negocio o las obligaciones de la inversión?",
        "causa": "La inversión depende de que aumenten los ingresos.",
        "evento": "Las ventas adicionales son menores o llegan más tarde de lo esperado.",
        "consecuencia": "La empresa puede tener más dificultad para recuperar la inversión y mantener dinero disponible.",
        "tratamiento": "Fraccionar la inversión en etapas y/o validar la demanda antes de comprometer el monto total; diversificar canales de venta.",
        "indicador": "Ventas reales generadas por la inversión vs. ventas esperadas.",
        "como_medir": "Ejemplo: esperabas $200.000 y obtuviste $150.000.",
        "frecuencia": "Mensual",
    },
    "R2": {
        "nombre": "Gastos que no habías previsto",
        "pregunta_prob": "¿Qué tan probable es que aparezcan gastos que no habías tenido en cuenta, como instalación, arreglos, capacitación, mantenimiento o repuestos?",
        "pregunta_imp": "Si aparecen esos gastos, ¿qué tan difícil sería pagarlos sin afectar el funcionamiento normal de la empresa?",
        "causa": "No se contemplaron todos los gastos relacionados con la inversión.",
        "evento": "El costo total termina siendo mayor al pensado.",
        "consecuencia": "La empresa necesita más dinero del previsto o queda con menos dinero disponible.",
        "tratamiento": "Presupuestar con un margen de contingencia (10-15%) y cerrar cotizaciones a precio fijo con los proveedores.",
        "indicador": "Gasto previsto vs. gasto real.",
        "como_medir": "Ejemplo: previsto $500.000 / real $575.000.",
        "frecuencia": "Mensual",
    },
    "R3": {
        "nombre": "Falta de dinero disponible",
        "pregunta_prob": "Si la inversión tarda en dar resultados, ¿qué tan probable es que te falte dinero para pagar los gastos normales del negocio?",
        "pregunta_imp": "Si eso pasa, ¿qué tan grave sería para la empresa?",
        "causa": "La empresa tiene poco margen de dinero disponible durante la inversión.",
        "evento": "La inversión tarda más en generar resultados o aparecen gastos inesperados.",
        "consecuencia": "Puede faltar dinero para pagar gastos habituales u otras obligaciones.",
        "tratamiento": "Constituir un fondo de reserva antes de iniciar la inversión y/o gestionar una línea de crédito de respaldo.",
        "indicador": "Meses de gastos normales que podés cubrir con el dinero disponible.",
        "como_medir": "Ejemplo: tenés $300.000 disponibles y gastás $100.000 por mes = 3 meses.",
        "frecuencia": "Mensual",
    },
    "R4": {
        "nombre": "Problemas para pagar un préstamo",
        "pregunta_prob": "Si usás préstamo o crédito, ¿qué tan probable es que en algún mes te cueste pagar una cuota?",
        "pregunta_imp": "Si te atrasás con una cuota, ¿qué tan grave sería para el negocio?",
        "causa": "La inversión genera cuotas u obligaciones periódicas.",
        "evento": "En un mes complicado no hay dinero suficiente para pagar en fecha.",
        "consecuencia": "Pueden aparecer atrasos, recargos y más presión sobre el dinero disponible.",
        "tratamiento": "Elegir un esquema de cuotas acorde a la estacionalidad de ingresos; negociar plazos de gracia si es posible.",
        "indicador": "Cuotas pagadas en fecha / total de cuotas vencidas.",
        "como_medir": "Ejemplo: 12 cuotas vencidas / 12 pagadas en fecha = 100%.",
        "frecuencia": "Mensual",
    },
    "R5": {
        "nombre": "Suba del dólar",
        "pregunta_prob": "Si la máquina, compra o préstamo están en dólares, ¿qué tan probable es que una suba del dólar te complique?",
        "pregunta_imp": "Si el dólar sube, ¿qué tan grave sería el impacto en tus cuentas?",
        "causa": "La inversión tiene costos en dólares pero la empresa obtiene la mayor parte de sus ingresos en pesos.",
        "evento": "El dólar sube.",
        "consecuencia": "La cuota, deuda o costo de la inversión aumenta en pesos.",
        "tratamiento": "Tomar financiamiento en la misma moneda que los ingresos principales, o cubrir parcialmente el riesgo cambiario.",
        "indicador": "Valor en pesos de la cuota o deuda.",
        "como_medir": "Ejemplo: comparar cuánto costaba la cuota en pesos el mes pasado y cuánto cuesta ahora.",
        "frecuencia": "Mensual",
    },
    "R6": {
        "nombre": "Demora para empezar a usar la inversión",
        "pregunta_prob": "¿Qué tan probable es que un permiso, una instalación, una obra o un trámite demore más de lo pensado?",
        "pregunta_imp": "Si se demora, ¿qué tan grave sería tener el dinero invertido pero todavía no poder usarlo para generar ingresos?",
        "causa": "Todavía quedan permisos, instalaciones o pasos necesarios antes de poder usar la inversión.",
        "evento": "Uno o más de esos pasos se demora.",
        "consecuencia": "El dinero queda invertido, pero la empresa todavía no puede generar ingresos con esa inversión.",
        "tratamiento": "Iniciar en paralelo los trámites, permisos e instalaciones necesarios, con margen de tiempo en el cronograma.",
        "indicador": "Pasos completados / pasos necesarios.",
        "como_medir": "Ejemplo: 8 pasos necesarios / 6 completados = 75%.",
        "frecuencia": "Cuando ocurra un cambio importante",
    },
    "R7": {
        "nombre": "Dependencia de un proveedor, técnico o repuesto",
        "pregunta_prob": "¿Qué tan probable es que dependas de un proveedor, técnico o repuesto que sea difícil de reemplazar rápidamente?",
        "pregunta_imp": "Si ese proveedor, técnico o repuesto falla o demora, ¿qué tan grave sería para tu negocio?",
        "causa": "La empresa depende demasiado de una sola opción.",
        "evento": "El proveedor, técnico o repuesto no está disponible cuando se necesita.",
        "consecuencia": "La inversión puede quedar parada y generar pérdidas o demoras.",
        "tratamiento": "Buscar por lo menos una alternativa de proveedor, técnico o repuesto antes de necesitarla.",
        "indicador": "Cantidad de alternativas disponibles.",
        "como_medir": "Ejemplo: proveedor principal + 1 alternativa confirmada.",
        "frecuencia": "Trimestral",
    },
    "R8": {
        "nombre": "Falla de la máquina o equipo",
        "pregunta_prob": "¿Qué tan probable es que una falla de la máquina o equipo pueda detener una parte importante del trabajo?",
        "pregunta_imp": "Si la máquina queda parada, ¿qué tan grave sería para la producción o las ventas?",
        "causa": "La empresa depende del nuevo equipo para producir o prestar el servicio.",
        "evento": "La máquina o equipo falla.",
        "consecuencia": "Se detiene parte del trabajo y pueden perderse ventas o aumentar costos.",
        "tratamiento": "Definir mantenimiento, contacto técnico y los repuestos más importantes antes de que ocurra una falla.",
        "indicador": "Horas que la máquina estuvo parada por fallas.",
        "como_medir": "Ejemplo: agosto 12 h / septiembre 4 h.",
        "frecuencia": "Mensual",
    },
}

# ============================================================
# FUNCIONES
# ============================================================
def clasificar(nivel):
    # Rangos explícitos de la matriz 5x5:
    # Bajo 1-4 | Medio 5-9 | Alto 10-14 | Crítico 15-25
    if nivel <= 0:
        return "Sin evaluar"
    if nivel <= 4:
        return "Bajo"
    if nivel <= 9:
        return "Medio"
    if nivel <= 14:
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
            posiciones.setdefault(
                (int(row["Probabilidad"]), int(row["Impacto"])), []
            ).append(row["Código"])

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
            codigos = "<br>".join(posiciones.get((p, imp), []))
            html += (
                f'<td style="height:64px;padding:6px;border:1px solid #bbb;'
                f'background:{color_prioridad(prioridad)};color:#111;font-weight:700;">'
                f'{codigos}</td>'
            )
        html += "</tr>"

    html += "</table></div>"
    return html

def excel_bytes(datos, riesgos_df, plan_df):
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        wb = writer.book

        navy = "#1F4E78"
        blue = "#D9EAF7"
        green = "#D9EAD3"
        yellow = "#FFF2CC"
        orange = "#FCE5CD"
        red = "#F4CCCC"
        border = "#D0D5DD"

        title = wb.add_format({
            "bold": True, "font_size": 18, "font_color": "white",
            "bg_color": navy, "align": "center", "valign": "vcenter"
        })
        section = wb.add_format({
            "bold": True, "font_color": "white", "bg_color": navy,
            "align": "left", "valign": "vcenter"
        })
        label = wb.add_format({
            "bold": True, "bg_color": blue, "border": 1,
            "border_color": border
        })
        value = wb.add_format({
            "border": 1, "border_color": border,
            "text_wrap": True, "valign": "top"
        })
        header = wb.add_format({
            "bold": True, "font_color": "white", "bg_color": navy,
            "border": 1, "border_color": border,
            "align": "center", "valign": "vcenter",
            "text_wrap": True
        })
        center = wb.add_format({
            "border": 1, "border_color": border,
            "align": "center", "valign": "vcenter"
        })
        wrap = wb.add_format({
            "border": 1, "border_color": border,
            "text_wrap": True, "valign": "top"
        })

        pf = {
            "Bajo": wb.add_format({"bg_color": green, "border": 1, "align": "center"}),
            "Medio": wb.add_format({"bg_color": yellow, "border": 1, "align": "center"}),
            "Alto": wb.add_format({"bg_color": orange, "border": 1, "align": "center"}),
            "Crítico": wb.add_format({"bg_color": red, "border": 1, "align": "center", "bold": True}),
        }

        # RESUMEN
        ws = wb.add_worksheet("Resumen")
        writer.sheets["Resumen"] = ws
        ws.hide_gridlines(2)
        ws.set_column("A:A", 25)
        ws.set_column("B:B", 46)
        ws.set_column("D:D", 24)
        ws.set_column("E:E", 18)
        ws.merge_range("A1:E2", "ANTES DE INVERTIR · RESUMEN", title)

        ws.merge_range("A4:B4", "Datos de la inversión", section)
        fila = 5
        for k, v in datos.items():
            ws.write(f"A{fila}", k, label)
            ws.write(f"B{fila}", v, value)
            fila += 1

        ws.merge_range("D4:E4", "Resumen de riesgos", section)
        conteos = riesgos_df["Prioridad"].value_counts().to_dict()
        items = [
            ("Riesgos evaluados", len(riesgos_df)),
            ("Críticos", conteos.get("Crítico", 0)),
            ("Altos", conteos.get("Alto", 0)),
            ("Medios", conteos.get("Medio", 0)),
            ("Bajos", conteos.get("Bajo", 0)),
        ]
        rr = 5
        for k, v in items:
            ws.write(f"D{rr}", k, label)
            if k in pf:
                ws.write(f"E{rr}", v, pf[k])
            else:
                ws.write(f"E{rr}", v, center)
            rr += 1

        # RIESGOS
        riesgos_df.to_excel(writer, sheet_name="Riesgos", index=False, startrow=2)
        wr = writer.sheets["Riesgos"]
        wr.hide_gridlines(2)
        wr.merge_range(0, 0, 0, len(riesgos_df.columns)-1, "RIESGOS EVALUADOS", title)

        for c, col in enumerate(riesgos_df.columns):
            wr.write(2, c, col, header)

        widths = {
            "Código": 10,
            "Riesgo": 32,
            "Causa": 38,
            "Evento": 40,
            "Consecuencia": 42,
            "Probabilidad": 14,
            "Impacto": 12,
            "Nivel": 10,
            "Prioridad": 12,
        }

        for c, col in enumerate(riesgos_df.columns):
            wr.set_column(c, c, widths.get(col, 22))

        for r in range(len(riesgos_df)):
            er = r + 3
            for c, col in enumerate(riesgos_df.columns):
                val = riesgos_df.iloc[r, c]
                if col == "Prioridad":
                    wr.write(er, c, val, pf.get(val, center))
                elif col in ["Código", "Probabilidad", "Impacto", "Nivel"]:
                    wr.write(er, c, val, center)
                else:
                    wr.write(er, c, val, wrap)

        wr.freeze_panes(3, 0)
        wr.autofilter(2, 0, len(riesgos_df)+2, len(riesgos_df.columns)-1)

        # PLAN
        plan_df.to_excel(writer, sheet_name="Plan de acción", index=False, startrow=2)
        wp = writer.sheets["Plan de acción"]
        wp.hide_gridlines(2)
        wp.merge_range(0, 0, 0, len(plan_df.columns)-1, "PLAN DE ACCIÓN Y SEGUIMIENTO", title)

        for c, col in enumerate(plan_df.columns):
            wp.write(2, c, col, header)

        widths_plan = {
            "Código": 10,
            "Riesgo": 30,
            "Prioridad": 12,
            "Qué hacer": 58,
            "Responsable": 22,
            "Indicador": 42,
            "Cómo medirlo": 42,
            "Frecuencia": 18,
            "Estado": 14,
        }

        for c, col in enumerate(plan_df.columns):
            wp.set_column(c, c, widths_plan.get(col, 22))

        for r in range(len(plan_df)):
            er = r + 3
            for c, col in enumerate(plan_df.columns):
                val = plan_df.iloc[r, c]
                if col == "Prioridad":
                    wp.write(er, c, val, pf.get(val, center))
                elif col in ["Código", "Responsable", "Frecuencia", "Estado"]:
                    wp.write(er, c, val, center)
                else:
                    wp.write(er, c, val, wrap)

        wp.freeze_panes(3, 0)

        # MATRIZ
        wm = wb.add_worksheet("Matriz")
        writer.sheets["Matriz"] = wm
        wm.hide_gridlines(2)
        wm.merge_range("A1:F2", "MATRIZ 5 × 5 DE RIESGOS", title)

        wm.write("A4", "Prob. \\ Impacto", header)
        for i in range(1, 6):
            wm.write(3, i, i, header)

        cf = {
            "Bajo": wb.add_format({"bg_color": green, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
            "Medio": wb.add_format({"bg_color": yellow, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
            "Alto": wb.add_format({"bg_color": orange, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
            "Crítico": wb.add_format({"bg_color": red, "border": 1, "align": "center", "valign": "vcenter", "bold": True}),
        }

        posiciones = {}
        for _, row in riesgos_df.iterrows():
            posiciones.setdefault(
                (int(row["Probabilidad"]), int(row["Impacto"])), []
            ).append(str(row["Código"]))

        for row_idx, p in enumerate(range(5, 0, -1), start=4):
            wm.write(row_idx, 0, p, header)
            for imp in range(1, 6):
                nivel = p * imp
                prioridad = clasificar(nivel)
                contenido = "\n".join(posiciones.get((p, imp), []))
                wm.write(row_idx, imp, contenido, cf[prioridad])
                wm.set_row(row_idx, 42)

        wm.set_column("A:A", 24)
        wm.set_column("B:F", 14)

        wm.write("A11", "Leyenda", section)
        for idx, nombre in enumerate(["Bajo", "Medio", "Alto", "Crítico"], start=11):
            wm.write(idx, 0, nombre, cf[nombre])

    output.seek(0)
    return output.getvalue()

# ============================================================
# INICIO
# ============================================================
st.markdown("""
<div class="hero">
<h1>🧭 Antes de invertir: identificá y gestioná tus riesgos</h1>
<p><strong>Autodiagnóstico de riesgos asociados a una inversión para PyMEs</strong></p>
<p class="small">1. Tu inversión → 2. Evaluar riesgos → 3. Ver prioridades → 4. Definir qué hacer → 5. Hacer seguimiento</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
⚠️ <strong>Esta herramienta NO te dice si tenés que invertir o no.</strong><br>
Te ayuda a reconocer qué riesgos pueden aparecer con la inversión, cuáles son los más importantes y qué podés hacer para manejarlos.
</div>
""", unsafe_allow_html=True)

# ============================================================
# 1. DATOS DE LA INVERSIÓN
# ============================================================
st.header("1. Datos de tu inversión")
st.caption("Esto solo sirve para entender mejor la inversión que estás analizando.")

c1, c2 = st.columns(2)

with c1:
    empresa = st.text_input("Nombre de la empresa")

    rubro = st.selectbox("Rubro", RUBROS)
    rubro_otro = ""
    if rubro == "Otro":
        rubro_otro = st.text_input("Escribí el rubro")

    tipo_inversion = st.selectbox("Tipo de inversión", TIPOS_INVERSION)
    tipo_otro = ""
    if tipo_inversion == "Otra":
        tipo_otro = st.text_area(
            "Escribí qué inversión querés hacer",
            placeholder="Ej.: comprar un vehículo para reparto."
        )

with c2:
    moneda = st.selectbox("Moneda", MONEDAS)

    monto = st.number_input(
        "Monto estimado de la inversión",
        min_value=0.0,
        step=1000.0
    )

    objetivo = st.selectbox("Objetivo de la inversión", OBJETIVOS)
    objetivo_otro = ""
    if objetivo == "Otro":
        objetivo_otro = st.text_area(
            "Escribí el objetivo",
            placeholder="Ej.: reducir tiempos de entrega."
        )

    financiamiento = st.selectbox("Forma de financiamiento", FINANCIAMIENTO)
    financiamiento_otro = ""
    if financiamiento == "Otro":
        financiamiento_otro = st.text_input("Escribí cómo se financiará")

st.divider()

# ============================================================
# 2. AUTODIAGNÓSTICO
# ============================================================
st.header("2. Autodiagnóstico")
st.write(
    "Evaluá cada posible riesgo con dos preguntas: "
    "**qué tan probable es que pase** y **qué tan grave sería si pasa**."
)

evaluados = []

for codigo, info in RIESGOS.items():
    st.subheader(f"{codigo} · {info['nombre']}")

    c1, c2 = st.columns(2)

    with c1:
        p_txt = st.selectbox(
            info["pregunta_prob"],
            list(PROBABILIDAD.keys()),
            key=f"prob_{codigo}"
        )

    with c2:
        i_txt = st.selectbox(
            info["pregunta_imp"],
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
            background:{color_prioridad(prioridad)};color:#111;font-weight:700;">
            Nivel {nivel} · {prioridad}
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander("¿Qué significa este riesgo?"):
            st.write(f"**Causa:** {info['causa']}")
            st.write(f"**Qué puede pasar:** {info['evento']}")
            st.write(f"**Cómo puede afectar a la empresa:** {info['consecuencia']}")

    else:
        st.caption("Elegí probabilidad e impacto para calcular el nivel.")

    evaluados.append({
        "Código": codigo,
        "Riesgo": info["nombre"],
        "Causa": info["causa"],
        "Evento": info["evento"],
        "Consecuencia": info["consecuencia"],
        "Probabilidad": p,
        "Impacto": i,
        "Nivel": nivel,
        "Prioridad": prioridad,
    })

    st.divider()

df_eval = pd.DataFrame(evaluados)
df_eval = df_eval[df_eval["Nivel"] > 0].copy()

if not df_eval.empty:
    df_eval = df_eval.sort_values(
        ["Nivel", "Impacto"],
        ascending=False
    )

# ============================================================
# 3. MATRIZ
# ============================================================
st.header("3. Matriz de riesgos")

if df_eval.empty:
    st.info("Completá al menos un riesgo para generar la matriz.")
else:
    a, b, c, d = st.columns(4)
    a.metric("🔴 Críticos", int((df_eval["Prioridad"] == "Crítico").sum()))
    b.metric("🟠 Altos", int((df_eval["Prioridad"] == "Alto").sum()))
    c.metric("🟡 Medios", int((df_eval["Prioridad"] == "Medio").sum()))
    d.metric("🟢 Bajos", int((df_eval["Prioridad"] == "Bajo").sum()))

    st.markdown(matriz_html(df_eval), unsafe_allow_html=True)

    st.markdown("### ¿Qué significan los colores?")

    st.markdown(
        "<div class='legend-box' style='background:#D9EAD3;color:#111;'>"
        "🟢 BAJO · No requiere atención urgente, pero conviene controlarlo."
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='legend-box' style='background:#FFF2CC;color:#111;'>"
        "🟡 MEDIO · Necesita seguimiento y alguna acción preventiva."
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='legend-box' style='background:#FCE5CD;color:#111;'>"
        "🟠 ALTO · Requiere una acción concreta para reducirlo."
        "</div>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<div class='legend-box' style='background:#F4CCCC;color:#111;'>"
        "🔴 CRÍTICO · Necesita atención prioritaria porque puede afectar seriamente la inversión o la empresa."
        "</div>",
        unsafe_allow_html=True
    )

    st.caption("Rangos de la matriz: Bajo 1–4 · Medio 5–9 · Alto 10–14 · Crítico 15–25")

    st.markdown("### Orden de prioridad")
    st.dataframe(
        df_eval[
            ["Código", "Riesgo", "Probabilidad", "Impacto", "Nivel", "Prioridad"]
        ],
        use_container_width=True,
        hide_index=True
    )

st.divider()

# ============================================================
# 4. PLAN DE ACCIÓN
# ============================================================
st.header("4. Qué hacer con cada riesgo")
st.write(
    "La herramienta propone una acción preventiva para reducir la probabilidad o el impacto del riesgo, "
    "y un indicador separado para hacer seguimiento y detectar si el riesgo se está manifestando. "
    "Podés modificar ambos según tu empresa."
)

plan = []

if df_eval.empty:
    st.info("Primero completá la evaluación de riesgos.")
else:
    for _, row in df_eval.iterrows():
        codigo = row["Código"]
        info = RIESGOS[codigo]

        st.subheader(f"{codigo} · {row['Riesgo']}")

        st.markdown(
            f"<div style='display:inline-block;padding:.35rem .65rem;border-radius:8px;"
            f"background:{color_prioridad(row['Prioridad'])};color:#111;font-weight:700;'>"
            f"{row['Prioridad']} · Nivel {row['Nivel']}</div>",
            unsafe_allow_html=True
        )

        tratamiento = st.text_area(
            "¿Qué podés hacer para reducir este riesgo?",
            value=info["tratamiento"],
            key=f"trat_{codigo}"
        )

        indicador = st.text_input(
            "¿Qué vas a medir?",
            value=info["indicador"],
            key=f"ind_{codigo}"
        )

        como_medir = st.text_area(
            "¿Cómo se puede medir?",
            value=info["como_medir"],
            key=f"medir_{codigo}"
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            responsable = st.selectbox(
                "¿Quién se hace responsable?",
                RESPONSABLES,
                key=f"resp_{codigo}"
            )

        with c2:
            frecuencia = st.selectbox(
                "¿Cada cuánto se revisa?",
                FRECUENCIAS,
                index=FRECUENCIAS.index(info["frecuencia"])
                if info["frecuencia"] in FRECUENCIAS else 0,
                key=f"freq_{codigo}"
            )

        with c3:
            estado = st.selectbox(
                "Estado",
                ESTADOS,
                key=f"estado_{codigo}"
            )

        plan.append({
            "Código": codigo,
            "Riesgo": row["Riesgo"],
            "Prioridad": row["Prioridad"],
            "Qué hacer": tratamiento,
            "Responsable": responsable,
            "Indicador": indicador,
            "Cómo medirlo": como_medir,
            "Frecuencia": frecuencia,
            "Estado": estado,
        })

        st.divider()

df_plan = pd.DataFrame(plan)

# ============================================================
# 5. RESUMEN FINAL + EXCEL
# ============================================================
st.header("5. Resumen final")

rubro_final = rubro_otro.strip() if rubro == "Otro" and rubro_otro.strip() else rubro
tipo_final = tipo_otro.strip() if tipo_inversion == "Otra" and tipo_otro.strip() else tipo_inversion
objetivo_final = objetivo_otro.strip() if objetivo == "Otro" and objetivo_otro.strip() else objetivo
fin_final = financiamiento_otro.strip() if financiamiento == "Otro" and financiamiento_otro.strip() else financiamiento

simbolo = moneda_simbolo(moneda)

datos = {
    "Fecha": date.today().strftime("%d/%m/%Y"),
    "Empresa": empresa if empresa else "-",
    "Rubro": rubro_final,
    "Tipo de inversión": tipo_final,
    "Monto estimado": f"{simbolo} {monto:,.2f}",
    "Objetivo": objetivo_final,
    "Financiamiento": fin_final,
}

if df_eval.empty:
    st.info("Completá el autodiagnóstico para generar el resumen.")
else:
    c1, c2, c3 = st.columns(3)
    c1.write(f"**Empresa:** {datos['Empresa']}")
    c1.write(f"**Rubro:** {datos['Rubro']}")
    c2.write(f"**Tipo:** {datos['Tipo de inversión']}")
    c2.write(f"**Objetivo:** {datos['Objetivo']}")
    c3.write(f"**Monto:** {datos['Monto estimado']}")
    c3.write(f"**Financiamiento:** {datos['Financiamiento']}")

    prioritarios = df_eval[df_eval["Prioridad"].isin(["Crítico", "Alto"])]

    if not prioritarios.empty:
        st.markdown("### Riesgos que deberías atender primero")
        for _, row in prioritarios.iterrows():
            st.markdown(
                f"<div style='padding:.65rem .8rem;margin:.35rem 0;border-radius:8px;"
                f"background:{color_prioridad(row['Prioridad'])};color:#111;'>"
                f"<strong>{row['Código']} · {row['Riesgo']}</strong> — "
                f"Nivel {row['Nivel']} · {row['Prioridad']}</div>",
                unsafe_allow_html=True
            )
    else:
        st.success("No se clasificaron riesgos como altos o críticos.")

    st.markdown("### Plan de acción consolidado")
    st.dataframe(df_plan, use_container_width=True, hide_index=True)

    excel = excel_bytes(datos, df_eval, df_plan)

    st.download_button(
        "📊 Descargar resumen en Excel",
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
    "ni reemplaza asesoramiento profesional. Desarrollada por estudiantes de Ingeniería en Logística · UTEC."
)
