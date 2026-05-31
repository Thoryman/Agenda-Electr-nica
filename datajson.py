# datajson.py
import json


class DataJson:
    """
    Clase encargada de manejar la lectura y escritura de archivos JSON
    para la agenda estudiantil.
    """

    def __init__(self, ruta_archivo: str = "agenda_local.json"):
        self.ruta_archivo = ruta_archivo
        self.data = self._cargardatos()

    def _estructura_vacia(self, usuario: str = "") -> dict:
        """
        Estructura base de la agenda.
        """

        return {
            "usuario": usuario,
            "clases": [],
            "pendientes": []
        }

    def _cargardatos(self) -> dict:
        """
        Carga datos desde el archivo local.
        Si no existe o está dañado, regresa una estructura vacía.
        """

        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                return self.validar_estructura(datos)

        except FileNotFoundError:
            return self._estructura_vacia()

        except json.JSONDecodeError:
            return self._estructura_vacia()

        except Exception:
            return self._estructura_vacia()

    def validar_estructura(self, datos: dict) -> dict:
        """
        Revisa que el JSON tenga las llaves necesarias.
        """

        if not isinstance(datos, dict):
            datos = self._estructura_vacia()

        if "usuario" not in datos:
            datos["usuario"] = ""

        if "clases" not in datos:
            datos["clases"] = []

        if "pendientes" not in datos:
            datos["pendientes"] = []

        return datos

    def crear_agenda_vacia(self, usuario: str) -> dict:
        """
        Crea una agenda desde cero para un usuario.
        """

        self.data = self._estructura_vacia(usuario)
        return self.data

    def guardar_datos(self, datos: dict) -> bool:
        """
        Guarda la agenda en el archivo local.
        """

        try:
            datos = self.validar_estructura(datos)

            with open(self.ruta_archivo, "w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=4, ensure_ascii=False)

            self.data = datos
            return True

        except Exception:
            return False

    def cargar_desde_archivo_subido(self, archivo_subido):
        """
        Carga una agenda desde un archivo JSON subido en Streamlit.
        """

        try:
            contenido = archivo_subido.read().decode("utf-8")
            datos = json.loads(contenido)
            datos = self.validar_estructura(datos)

            self.data = datos
            return datos, None

        except json.JSONDecodeError:
            return None, "El archivo no tiene formato JSON válido."

        except Exception as error:
            return None, f"No se pudo cargar el archivo: {error}"

    def convertir_a_json(self, datos: dict) -> str:
        """
        Convierte la agenda a texto JSON para poder descargarla.
        """

        datos = self.validar_estructura(datos)
        return json.dumps(datos, indent=4, ensure_ascii=False)