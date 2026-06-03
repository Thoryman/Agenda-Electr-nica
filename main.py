# Importamos las librerías necesarias y los módulos personalizados

# Librería streamlit para la interfaz gráfica
import streamlit as st

# Módulos personalizados para que funcione la agenda
from datajson import DataJson
from calculos import CalculadoraAgenda
from groq_client import GroqClient


# Configuración de la página
st.set_page_config(
    page_title="Agenda Inteligente Pythónica",
    page_icon="https://cdn-icons-png.flaticon.com/512/677/677388.png", # Logo de una agenda 
    layout="centered"
)

# Estados inciales del logging y la sesión
# Se usan para evitar que streamlit borre los datos cada vez que se actualiza el sitio
if "logueado" not in st.session_state:
    st.session_state.logueado = False

if "usuario" not in st.session_state:
    st.session_state.usuario = ""

if "agenda" not in st.session_state:
    st.session_state.agenda = None

if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = []

if "data_json" not in st.session_state:
    st.session_state.data_json = DataJson()

if "calculadora" not in st.session_state:
    st.session_state.calculadora = CalculadoraAgenda()

if "groq_client" not in st.session_state:
    try:
        st.session_state.groq_client = GroqClient()
        st.session_state.error_groq = None
    except Exception as error:
        st.session_state.groq_client = None
        st.session_state.error_groq = str(error)


# Funciones auxiliares para manejar la agenda y los pendientes
def obtener_pendientes_ordenados():
    """
    Analiza y ordena los pendientes.

    Se agrega un índice interno para poder eliminar correctamente
    aunque los pendientes estén ordenados por prioridad.
    """

    pendientes = st.session_state.agenda.get("pendientes", [])

    pendientes_con_indice = []

    for indice, pendiente in enumerate(pendientes):
        pendiente_temporal = pendiente.copy()
        pendiente_temporal["_indice_original"] = indice
        pendientes_con_indice.append(pendiente_temporal)

    return st.session_state.calculadora.ordenar_pendientes(pendientes_con_indice)


def obtener_agenda_analizada():
    """
    Crea una copia de la agenda con pendientes ya analizados.
    Esta copia se manda al asistente IA.
    """

    agenda_analizada = st.session_state.agenda.copy()
    agenda_analizada["pendientes"] = obtener_pendientes_ordenados()

    return agenda_analizada


def preparar_agenda_para_descarga():
    """
    Prepara la agenda para descargarla como JSON.
    Evita guardar datos internos como _indice_original.
    """

    agenda_limpia = st.session_state.agenda.copy()
    pendientes_limpios = []

    for pendiente in agenda_limpia.get("pendientes", []):
        pendiente_limpio = pendiente.copy()

        if "_indice_original" in pendiente_limpio:
            del pendiente_limpio["_indice_original"]

        pendientes_limpios.append(pendiente_limpio)

    agenda_limpia["pendientes"] = pendientes_limpios

    return agenda_limpia


def cerrar_agenda():
    st.session_state.agenda = None
    st.session_state.mensajes_chat = []

    if st.session_state.groq_client:
        st.session_state.groq_client.limpiar_historial()


def cerrar_sesion():
    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.agenda = None
    st.session_state.mensajes_chat = []

    if st.session_state.groq_client:
        st.session_state.groq_client.limpiar_historial()


# Título y bienvenida del programa
columna1, columna2 = st.columns([1, 3])
with columna1:
    st.image("https://covercero.com.mx/wp-content/uploads/2025/01/Zorros-Cetys-Logo.png", 
             width=100)
with columna2:
    st.title("Agenda Inteligente CETYS")
st.write("Esta agenda será tu amiga hasta en los peores momentos del parcial :)")
st.sidebar.title("Autores del proyecto")


# Información de los autores y agradecimientos
st.sidebar.write("- Felián Estrada - 39105")
st.sidebar.write("- Yamil Barajas - 39660")
st.sidebar.write("- Angel Barraza - 39118")
st.sidebar.write("- Profesor: Dario Landeros")
st.sidebar.write(" Mucha gracias, profesor. Después de tanto código y lágrimas, se logró :D")


# Simular inicio de sesión
if not st.session_state.logueado:
    st.subheader("Inicio de sesión")

    nombre = st.text_input("Escribe tu nombre:")

    if st.button("Entrar"):
        if nombre.strip():
            st.session_state.usuario = nombre.strip()
            st.session_state.logueado = True
            st.rerun()
        else:
            st.warning("Debes escribir un nombre para continuar, camarada.")

    st.stop()


st.write(f"Bienvenido, **{st.session_state.usuario}**.")


# Apartado para cargar o crear la agenda
if st.session_state.agenda is None:
    st.subheader("¿Cómo quieres iniciar tu agenda? 👀")

    opcion = st.radio(
        "Selecciona una opción:",
        [
            "Crear agenda desde cero",
            "Cargar agenda desde archivo .JSON"
        ]
    )

    if opcion == "Crear agenda desde cero":
        if st.button("Crear agenda"):
            st.session_state.agenda = st.session_state.data_json.crear_agenda_vacia(st.session_state.usuario)
            st.rerun()

    else:
        archivo_json = st.file_uploader(
            "Sube tu archivo JSON:",
            type=["json"]
        )

        if archivo_json is not None:
            agenda_cargada, error = st.session_state.data_json.cargar_desde_archivo_subido(archivo_json)

            if error:
                st.error(error)
            else:
                st.session_state.agenda = agenda_cargada

                if not st.session_state.agenda.get("usuario"):
                    st.session_state.agenda["usuario"] = st.session_state.usuario

                st.success("Agenda cargada correctamente :D.")
                st.rerun()

    st.stop()


agenda = st.session_state.agenda


# Secciones principales del programa, organizadas en tabs
tab_registrar, tab_resumen, tab_chat, tab_config = st.tabs(
    [
        "📝 Registrar",
        "📊 Resumen de agenda",
        "🤖 Chatbox",
        "⚙️ Configuración"
    ]
)


# Tab 1: Registrar pendientes en la agenda
with tab_registrar:
    st.subheader("Registrar pendiente")

    with st.form("form_pendiente"):
        materia = st.text_input("Materia")

        tipo_materia = st.selectbox(
            "Tipo de materia",
            ["Humanidades", "Tronco común", "Carrera"]
        )

        actividad = st.text_input("Actividad o pendiente")

        tipo_actividad = st.selectbox(
            "Tipo de actividad",
            ["Lectura", "Tarea", "Práctica", "Proyecto", "Examen"]
        )

        fecha = st.date_input("Fecha de entrega")

        horas_estimadas = st.number_input(
            "Horas estimadas que crees dedicarle",
            min_value=0.5,
            step=0.5
        )

        guardar = st.form_submit_button("Agregar pendiente")

        if guardar:
            if materia.strip() and actividad.strip():
                nuevo_pendiente = {
                    "materia": materia.strip(),
                    "tipo_materia": tipo_materia,
                    "actividad": actividad.strip(),
                    "tipo_actividad": tipo_actividad,
                    "fecha": str(fecha),
                    "horas_estimadas": horas_estimadas
                }

                agenda["pendientes"].append(nuevo_pendiente)
                st.session_state.agenda = agenda

                st.success("Pendiente agregado correctamente.")
                st.rerun()

            else:
                st.warning("Completa la materia y la actividad.")

    st.info("La prioridad no la eliges tú directamente. El programa la calcula usando la fecha, tipo de actividad, tipo de materia y horas estimadas.")


# Tab 2: Resumen de agenda y pendientes ordenados por prioridad
with tab_resumen:
    st.subheader("Resumen de agenda")

    pendientes = agenda.get("pendientes", [])

    if not pendientes:
        st.info("Todavía no hay pendientes registrados.")
    else:
        pendientes_ordenados = obtener_pendientes_ordenados()
        resumen = st.session_state.calculadora.obtener_resumen(pendientes)

        col1, col2, col3 = st.columns(3)

        col1.metric("Pendientes", resumen["total_pendientes"])
        col2.metric("Horas ajustadas", resumen["total_horas_ajustadas"])
        col3.metric("Prioridad alta", resumen["pendientes_prioridad_alta"])

        st.divider()

        st.write("### Pendientes ordenados por prioridad")

        for i, pendiente in enumerate(pendientes_ordenados, start=1):
            with st.container(border=True):
                st.write(f"### {i}. {pendiente.get('actividad', 'Sin actividad')}")

                st.write(f"**Materia:** {pendiente.get('materia', 'Sin materia')}")
                st.write(f"**Tipo de materia:** {pendiente.get('tipo_materia', 'No especificado')}")
                st.write(f"**Tipo de actividad:** {pendiente.get('tipo_actividad', 'No especificado')}")
                st.write(f"**Fecha de entrega:** {pendiente.get('fecha', 'Sin fecha')}")
                st.write(f"**Días restantes:** {pendiente.get('dias_restantes', 'No calculado')}")
                st.write(f"**Horas estimadas:** {pendiente.get('horas_estimadas', 'No especificadas')}")
                st.write(f"**Tiempo ajustado:** {pendiente.get('tiempo_ajustado', 'No calculado')} horas")
                st.write(f"**Carga:** {pendiente.get('carga', 'No calculada')}")
                st.write(f"**Prioridad calculada:** {pendiente.get('prioridad_calculada', 'No calculada')}")
                st.write(f"**Puntaje:** {pendiente.get('puntaje_prioridad', 'No calculado')}")

                if st.button("Eliminar pendiente", key=f"eliminar_{i}"):
                    indice_original = pendiente.get("_indice_original")

                    if indice_original is not None:
                        agenda["pendientes"].pop(indice_original)
                        st.session_state.agenda = agenda
                        st.rerun()


# Tab 3: Chatbox con IA para recomendaciones impulsadas por Groq
with tab_chat:
    st.subheader("Chatbox de agenda")
    
    columna1, columna2 = st.columns([0.4, 1])
    with columna1:
        st.write("Impulsado por:")
    with columna2:
        st.image("https://cdn.sanity.io/images/chol0sk5/production/ce0b2266373b3c9722b0bccb9a98441c26c89696-1200x630.png", width=100)

    if st.session_state.error_groq:
        st.error("No se pudo conectar con Groq ):")
        st.write(st.session_state.error_groq)
        st.info("Revisa que tu archivo .env tenga la variable GROQ_API_KEY.")
    else:
        st.write("Pregúntale cosas como: **¿Qué opinas de mi agenda?**, **¿qué hago primero?** o **¿cómo organizo mi semana?**")

        if st.button("Generar recomendación rápida"):
            agenda_analizada = obtener_agenda_analizada()

            respuesta = st.session_state.groq_client.recomendar_agenda(
                agenda_analizada
            )

            st.session_state.mensajes_chat.append(
                {
                    "role": "assistant",
                    "content": respuesta
                }
            )

            st.rerun()

        st.divider()

        for mensaje in st.session_state.mensajes_chat:
            with st.chat_message(mensaje["role"]):
                st.write(mensaje["content"])

        pregunta = st.chat_input("Pregúntame algo sobre tu agenda...")

        if pregunta:
            st.session_state.mensajes_chat.append(
                {
                    "role": "user",
                    "content": pregunta
                }
            )

            agenda_analizada = obtener_agenda_analizada()

            respuesta = st.session_state.groq_client.preguntar(
                mensaje_usuario=pregunta,
                agenda=agenda_analizada
            )

            st.session_state.mensajes_chat.append(
                {
                    "role": "assistant",
                    "content": respuesta
                }
            )

            st.rerun()

        if st.button("Limpiar conversación"):
            st.session_state.mensajes_chat = []

            if st.session_state.groq_client:
                st.session_state.groq_client.limpiar_historial()

            st.rerun()


#Tab 4: Configuración, descarga de agenda y cierre de sesión
with tab_config:
    st.subheader("Configuración")

    st.write("Desde aquí puedes descargar tu agenda o cerrar tu sesión.")

    agenda_para_descargar = preparar_agenda_para_descarga()

    agenda_json = st.session_state.data_json.convertir_a_json(
        agenda_para_descargar
    )

    nombre_archivo = f"agenda_{agenda.get('usuario', 'usuario').replace(' ', '_').lower()}.json"

    st.download_button(
        label="Descargar agenda en JSON",
        data=agenda_json,
        file_name=nombre_archivo,
        mime="application/json"
    )

    st.divider()

    if st.button("Cerrar agenda"):
        cerrar_agenda()
        st.rerun()

    if st.button("Cerrar sesión"):
        cerrar_sesion()
        st.rerun()
