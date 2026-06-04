# Agenda Inteligente CETYS

Agenda Inteligente CETYS es una aplicación desarrollada en Python con Streamlit que permite a estudiantes de CETYS Universidad registrar pendientes académicos, calcular automáticamente su prioridad y recibir recomendaciones mediante inteligencia artificial usando Groq.

El proyecto fue desarrollado por parte de estudiante en la materia Lenguajes de Programación Orientada a Objetos, con el propósito de aplicar los pilares de la POO, manejo de archivos .json, consumo de servicios externos y diseño modular.

Para gente externa de CETYS, sería un agrado que puedan probar nuestra aplicación :D

## Autores

- Felián Estrada - 39105
- Yamil Barajas - 39660
- Angel Barraza - 39118

Profesor: Dario Landeros

## Funciones principales de la aplicación

- Inicio de sesión simulado.
- Creación de agenda desde cero.
- Carga de agenda desde archivo JSON.
- Registro de pendientes académicos.
- Cálculo automático de prioridad.
- Estimación de tiempo ajustado.
- Clasificación de carga de trabajo.
- Ordenamiento de pendientes de mayor a menor prioridad.
- Chatbox con inteligencia artificial usando Groq.
- Descarga de la agenda en formato JSON.
- Interfaz gráfica web desarrollada con Streamlit.

## Tecnologías utilizadas

- Python
- Streamlit
- OpenAI SDK compatible con Groq
- JSON
- Groq API

## Instalación y ejecución del programa
-   El archivo "requirements.txt" contiene las librerías externas de Python para
    poder hacer funcionar el proyecto desde una máquina local. Instalar con el comando "pip install -r requirements.txt" desde una terminal de consola, en la misma carpeta donde está descargado el proyecto.
-   Para ejecutar el programa en local, se necesita tener todos los módulos
    instalados en un mismo fichero y las librerías del proyecto.
-   En una pestaña de consola ejecutar el comando "streamlit run main.py" para
    que el programa se ejecute localmente.
-   En caso de querer correrlo en línea, copiar y pegar la siguiente dirección
    web: https://agendaelectronica.streamlit.app/
