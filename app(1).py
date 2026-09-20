import streamlit as st
import pandas as pd

st.set_page_config(page_title="Antes de invertir", page_icon="🧭", layout="wide")

probabilidad_opciones = {
    "Elegir...": 0,
    "No, para nada probable": 1,
    "Poco probable": 2,
    "Podría pasar": 3,
    "Bastante probable": 4,
    "Muy probable / ya está pasando": 5
}

impacto_opciones = {
    "Elegir...": 0,
    "No me afectaría casi nada": 1,
    "Me complicaría un poco, pero lo resolvería rápido": 2,
    "Sería un problema serio para el negocio": 3,
    "Pondría en riesgo el negocio por un tiempo": 4,
    "Pondría en riesgo la continuidad del negocio": 5
}

def clasificar_riesgo(valor):
    if valor == 0:
        return "Sin evaluar"
    if valor <= 6:
        return "Bajo"
    if valor <= 11:
        return "Medio"
    if valor <= 15:
        return "Alto"
    return "Crítico"

def evaluar_riesgo(titulo, pregunta_prob, pregunta_impacto, key, tratamiento, indicador):
    st.subheader(titulo)
    p_txt = st.selectbox(pregunta_prob, list(probabilidad_opciones.keys()), key=f"{key}_p")
    i_txt = st.selectbox(pregunta_impacto, list(impacto_opciones.keys()), key=f"{key}_i")

    p = probabilidad_opciones[p_txt]
    i = impacto_opciones[i_txt]
    nivel = p * i
    prioridad = clasificar_riesgo(nivel)

    if nivel:
        st.write(f"**Nivel {nivel} · {prioridad}**")
    else:
        st.caption("Todavía no evaluado")

    st.divider()

    return {
        "Riesgo": titulo,
        "Probabilidad": p,
        "Impacto": i,
        "Nivel": nivel,
        "Prioridad": prioridad,
        "Tratamiento sugerido": tratamiento,
        "Indicador sugerido": indicador
    }

st.title("🧭 Antes de invertir: identificá y gestioná tus riesgos")
st.caption("Herramienta de autodiagnóstico de riesgos financieros para PyMEs · ACIRN")

st.warning(
    "Esta herramienta NO te dice si tenés que invertir o no. "
    "Te ayuda a identificar qué riesgos vas a asumir y cómo manejarlos."
)

st.header("1. Datos de tu inversión")
st.caption("Esto solo da contexto. Todavía no evalúa ningún riesgo.")

c1, c2 = st.columns(2)

with c1:
    empresa = st.text_input("Nombre de la empresa")
    rubro = st.selectbox(
        "Rubro",
        ["Elegir...", "Panadería", "Gastronomía", "Supermercado / Minimercado",
         "Comercio", "Industria", "Taller / Servicios", "Otro"]
    )
    tipo_inversion = st.selectbox(
        "Tipo de inversión",
        ["Elegir...", "Compra de maquinaria", "Ampliación de capacidad",
         "Apertura de un nuevo local", "Incorporación de tecnología",
         "Mejora de infraestructura", "Otra"]
    )

with c2:
    monto = st.number_input("Monto estimado ($)", min_value=0.0, step=1000.0)
    objetivo = st.text_area("Objetivo de la inversión")
    financiamiento = st.selectbox(
        "Forma de financiamiento",
        ["Elegir...", "100% recursos propios", "Mixto (propio + préstamo)", "100% préstamo"]
    )

st.divider()

st.header("2. Autodiagnóstico")
st.write("Respondé cada pregunta con sentido común sobre tu negocio. No hace falta calcular nada.")

riesgos = []

riesgos.append(evaluar_riesgo(
    "Insuficiencia de liquidez",
    "¿Qué tan probable es que tus ventas no aumenten tanto como esperás después de esta inversión?",
    "Si tus ventas no aumentan como esperás, ¿qué tan grave sería para poder pagar tus gastos y cuotas?",
    "liquidez",
    "Definir un margen mínimo de liquidez y realizar seguimiento periódico del flujo de caja.",
    "Flujo de caja disponible / obligaciones mensuales"
))

riesgos.append(evaluar_riesgo(
    "Costos adicionales no previstos",
    "¿Qué tan probable es que aparezcan gastos que no tuviste en cuenta (instalación, mantenimiento, capacitación, etc.)?",
    "Si aparecen esos gastos extra, ¿qué tan grave sería tener que cubrirlos?",
    "costos",
    "Identificar costos indirectos y establecer una reserva para contingencias.",
    "Costo real acumulado vs. presupuesto inicial"
))

riesgos.append(evaluar_riesgo(
    "Dificultad para pagar el financiamiento",
    "¿Qué tan probable es que te cueste pagar alguna cuota del préstamo en un mes complicado?",
    "Si te atrasás con una cuota, ¿qué tan grave sería la consecuencia para tu negocio?",
    "financiamiento",
    "Revisar capacidad de pago y mantener un margen para cubrir obligaciones financieras.",
    "Cuotas financieras / ingresos mensuales"
))

riesgos.append(evaluar_riesgo(
    "Exposición al tipo de cambio",
    "Si tu deuda o el equipo están en dólares, ¿qué tan probable es que una suba del dólar te complique?",
    "Si el dólar sube fuerte, ¿qué tan grave sería el impacto en tus cuentas?",
    "cambio",
    "Revisar la exposición monetaria y monitorear la relación entre ingresos y obligaciones en moneda extranjera.",
    "Variación del tipo de cambio / valor de la obligación"
))

riesgos.append(evaluar_riesgo(
    "Demora en habilitación / puesta en marcha",
    "¿Qué tan probable es que se demore algún trámite, habilitación o instalación?",
    "Si se demora, ¿qué tan grave sería tener la plata invertida sin poder generar ingresos todavía?",
    "habilitacion",
    "Verificar requisitos y estado de habilitaciones antes de comprometer etapas críticas de la inversión.",
    "Estado del trámite / días de demora"
))

riesgos.append(evaluar_riesgo(
    "Dependencia de proveedores o técnicos",
    "¿Qué tan probable es que dependas de un proveedor, repuesto o técnico específico que podría fallar o demorar?",
    "Si eso pasa, ¿qué tan grave sería quedarte sin ese insumo o servicio?",
    "proveedores",
    "Identificar alternativas de proveedores, repuestos y asistencia técnica.",
    "Cantidad de proveedores alternativos disponibles"
))

st.divider()

st.header("3. Resultados: matriz de riesgos")

df = pd.DataFrame(riesgos)
df_eval = df[df["Nivel"] > 0].copy()

if df_eval.empty:
    st.info("Todavía no hay riesgos evaluados.")
else:
    df_eval = df_eval.sort_values("Nivel", ascending=False)

    a, b, c, d = st.columns(4)
    a.metric("Críticos", int((df_eval["Prioridad"] == "Crítico").sum()))
    b.metric("Altos", int((df_eval["Prioridad"] == "Alto").sum()))
    c.metric("Medios", int((df_eval["Prioridad"] == "Medio").sum()))
    d.metric("Bajos", int((df_eval["Prioridad"] == "Bajo").sum()))

    st.dataframe(
        df_eval[["Riesgo", "Probabilidad", "Impacto", "Nivel", "Prioridad"]],
        use_container_width=True,
        hide_index=True
    )

    st.markdown("**Escala:** Bajo 1–6 · Medio 7–11 · Alto 12–15 · Crítico 16–25")

st.divider()

st.header("4. Plan de acción")
plan = []

responsables = ["Elegir...", "Propietario/a", "Administración", "Responsable financiero",
                "Encargado/a del proyecto", "Otro"]
frecuencias = ["Elegir...", "Semanal", "Mensual", "Trimestral"]

if df_eval.empty:
    st.info("Primero evaluá al menos un riesgo.")
else:
    for idx, fila in df_eval.iterrows():
        st.subheader(fila["Riesgo"])
        st.write(f"**Prioridad:** {fila['Prioridad']}")

        tratamiento = st.text_area(
            "Tratamiento",
            value=fila["Tratamiento sugerido"],
            key=f"trat_{idx}"
        )

        c1, c2 = st.columns(2)
        with c1:
            responsable = st.selectbox("Responsable", responsables, key=f"resp_{idx}")
        with c2:
            frecuencia = st.selectbox("Frecuencia", frecuencias, key=f"freq_{idx}")

        indicador = st.text_input(
            "Indicador",
            value=fila["Indicador sugerido"],
            key=f"ind_{idx}"
        )

        plan.append({
            "Riesgo": fila["Riesgo"],
            "Prioridad": fila["Prioridad"],
            "Tratamiento": tratamiento,
            "Responsable": responsable,
            "Indicador": indicador,
            "Frecuencia": frecuencia
        })

st.divider()

st.header("5. Resumen final")

if not df_eval.empty:
    st.write(f"**Empresa:** {empresa or '-'}")
    st.write(f"**Rubro:** {rubro}")
    st.write(f"**Tipo de inversión:** {tipo_inversion}")
    st.write(f"**Monto estimado:** ${monto:,.0f}")
    st.write(f"**Objetivo:** {objetivo or '-'}")
    st.write(f"**Financiamiento:** {financiamiento}")

    st.subheader("Riesgos priorizados")
    st.dataframe(
        df_eval[["Riesgo", "Probabilidad", "Impacto", "Nivel", "Prioridad"]],
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Plan de tratamiento")
    st.dataframe(pd.DataFrame(plan), use_container_width=True, hide_index=True)

    resumen = f'''ANTES DE INVERTIR - AUTODIAGNÓSTICO DE RIESGOS

Empresa: {empresa}
Rubro: {rubro}
Tipo de inversión: {tipo_inversion}
Monto estimado: ${monto:,.0f}
Objetivo: {objetivo}
Financiamiento: {financiamiento}

RIESGOS
'''

    for _, r in df_eval.iterrows():
        resumen += f"\n- {r['Riesgo']}: P={r['Probabilidad']} | I={r['Impacto']} | Nivel={r['Nivel']} | {r['Prioridad']}"

    resumen += "\n\nPLAN DE ACCIÓN\n"

    for item in plan:
        resumen += (
            f"\nRiesgo: {item['Riesgo']}"
            f"\nPrioridad: {item['Prioridad']}"
            f"\nTratamiento: {item['Tratamiento']}"
            f"\nResponsable: {item['Responsable']}"
            f"\nIndicador: {item['Indicador']}"
            f"\nFrecuencia: {item['Frecuencia']}\n"
        )

    st.download_button(
        "📋 Descargar resumen",
        data=resumen,
        file_name="autodiagnostico_riesgos.txt",
        mime="text/plain"
    )

st.divider()

if st.button("↺ Reiniciar herramienta"):
    st.session_state.clear()
    st.rerun()

st.caption(
    "Herramienta académica de autodiagnóstico. No reemplaza asesoramiento profesional. "
    "Desarrollada por estudiantes de Ingeniería en Logística · UTEC."
)
