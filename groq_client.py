from openai import OpenAI


class GroqClient:
    """
    Cliente para usar Groq como chatbot dentro de una agenda estudiantil.

    La API key se recibe desde main.py, por medio de Streamlit.
    """

    def __init__(self, api_key: str):
        if api_key:
            self.__api_key = api_key.strip()
        else:
            raise ValueError("No se recibió una API key de Groq.")

        self.__cliente = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=self.__api_key
        )

        self.__modelo = "llama-3.3-70b-versatile"
        self.__historial = []

        self.__system_prompt = """
        Eres un asistente académico dentro de una aplicación de agenda estudiantil.

        Tu trabajo principal es ayudar al usuario a analizar su agenda, pendientes,
        tareas, clases, horarios, proyectos, exámenes, tiempos de entrega,
        dificultad de actividades y prioridades.

        Puedes responder como chatbot, pero debes priorizar siempre el contexto
        de la agenda del estudiante.

        Cuando el usuario pregunte cosas como:
        - ¿Qué opinas de mi agenda?
        - ¿Qué hago primero?
        - ¿Cómo organizo mi semana?
        - ¿Estoy muy cargado?
        - ¿Qué pendiente debería priorizar?
        debes revisar la agenda proporcionada y dar una recomendación clara.

        Si el usuario pregunta algo que no tiene relación con la agenda,
        responde de forma breve y amable. Después redirige la conversación
        hacia la organización académica.

        No inventes actividades, fechas, clases ni pendientes.
        Si falta información, dilo claramente.
        """

    def __construir_contexto_agenda(self, agenda) -> str:
        """
        Convierte la agenda del usuario en texto para que la IA pueda leerla.
        """

        if not agenda:
            return "El usuario todavía no tiene actividades registradas en su agenda."

        if isinstance(agenda, str):
            return agenda

        if isinstance(agenda, list):
            texto = "Agenda actual del usuario:\n"

            for i, actividad in enumerate(agenda, start=1):
                texto += f"\nActividad {i}:\n"

                if isinstance(actividad, dict):
                    for clave, valor in actividad.items():
                        texto += f"- {clave}: {valor}\n"
                else:
                    texto += f"- {actividad}\n"

            return texto

        if isinstance(agenda, dict):
            texto = "Agenda actual del usuario:\n"

            for clave, valor in agenda.items():
                texto += f"\n{clave}:\n"

                if isinstance(valor, list):
                    for i, elemento in enumerate(valor, start=1):
                        texto += f"  {i}. {elemento}\n"
                else:
                    texto += f"  {valor}\n"

            return texto

        return str(agenda)

    def __construir_mensajes(self, mensaje_usuario: str, agenda=None) -> list:
        """
        Construye los mensajes que se enviarán al modelo.
        """

        contexto_agenda = self.__construir_contexto_agenda(agenda)

        mensajes = [
            {
                "role": "system",
                "content": self.__system_prompt
            },
            {
                "role": "system",
                "content": contexto_agenda
            }
        ]

        mensajes.extend(self.__historial)

        mensajes.append(
            {
                "role": "user",
                "content": mensaje_usuario
            }
        )

        return mensajes

    def preguntar(self, mensaje_usuario: str, agenda=None) -> str:
        """
        Envía una pregunta al chatbot de Groq y devuelve la respuesta.
        """

        if not mensaje_usuario or not mensaje_usuario.strip():
            return "Escribe una pregunta para poder ayudarte con tu agenda."

        try:
            mensajes = self.__construir_mensajes(mensaje_usuario, agenda)

            respuesta = self.__cliente.chat.completions.create(
                model=self.__modelo,
                messages=mensajes,
                temperature=0.4,
                max_completion_tokens=450
            )

            texto_respuesta = respuesta.choices[0].message.content

            self.__historial.append(
                {
                    "role": "user",
                    "content": mensaje_usuario
                }
            )

            self.__historial.append(
                {
                    "role": "assistant",
                    "content": texto_respuesta
                }
            )

            self.__limitar_historial()

            return texto_respuesta

        except Exception as error:
            return f"No pude generar una respuesta en este momento. Error: {error}"

    def recomendar_agenda(self, agenda) -> str:
        """
        Genera una recomendación automática de la agenda.
        Ideal para usar con un botón en Streamlit.
        """

        mensaje = """
        Analiza mi agenda actual y dime:
        1. Qué actividad debería hacer primero.
        2. Por qué debería empezar con esa.
        3. Un consejo breve para organizarme mejor.
        """

        return self.preguntar(mensaje, agenda)

    def __limitar_historial(self):
        """
        Limita el historial para evitar enviar demasiados mensajes a la API.
        """

        limite = 12

        if len(self.__historial) > limite:
            self.__historial = self.__historial[-limite:]

    def limpiar_historial(self):
        """
        Limpia el historial del chatbot.
        """

        self.__historial = []

    def obtener_historial(self):
        """
        Devuelve una copia del historial.
        """

        return self.__historial.copy()

    def obtener_modelo(self):
        """
        Devuelve el modelo usado.
        """

        return self.__modelo

    def __str__(self):
        return f"GroqClient | modelo: {self.__modelo} | mensajes: {len(self.__historial)}"
