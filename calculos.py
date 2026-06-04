from datetime import datetime, date


class TipoActividad:
    """
    Clase base para representar un tipo de actividad.
    Esta clase permite aplicar herencia y polimorfismo.
    """

    def obtener_peso(self) -> int:
        return 15

    def obtener_factor_tiempo(self) -> float:
        return 1.0


class Lectura(TipoActividad):
    """
    Subclase para actividades de lectura.
    """

    def obtener_peso(self) -> int:
        return 8

    def obtener_factor_tiempo(self) -> float:
        return 0.8


class Tarea(TipoActividad):
    """
    Subclase para actividades tipo tarea.
    """

    def obtener_peso(self) -> int:
        return 15

    def obtener_factor_tiempo(self) -> float:
        return 1.0


class Practica(TipoActividad):
    """
    Subclase para actividades tipo práctica.
    """

    def obtener_peso(self) -> int:
        return 18

    def obtener_factor_tiempo(self) -> float:
        return 1.2


class Proyecto(TipoActividad):
    """
    Subclase para actividades tipo proyecto.
    """

    def obtener_peso(self) -> int:
        return 25

    def obtener_factor_tiempo(self) -> float:
        return 1.4


class Examen(TipoActividad):
    """
    Subclase para actividades tipo examen.
    """

    def obtener_peso(self) -> int:
        return 30

    def obtener_factor_tiempo(self) -> float:
        return 1.6


class CalculadoraAgenda:
    """
    Clase encargada de calcular automáticamente la prioridad de los pendientes
    según la fecha de entrega, tipo de actividad, tipo de materia y horas estimadas.

    Esta clase usa objetos de tipo actividad para aplicar herencia y polimorfismo.
    """

    def __init__(self):
        self.__peso_tipo_materia = {
            "Humanidades": 5,
            "Tronco común": 10,
            "Carrera": 15
        }

        self.__factor_tiempo_materia = {
            "Humanidades": 1.0,
            "Tronco común": 1.15,
            "Carrera": 1.3
        }

    def __crear_tipo_actividad(self, tipo_actividad: str) -> TipoActividad:
        """
        Crea un objeto según el tipo de actividad.
        Aquí se aplica herencia porque cada tipo viene de TipoActividad.
        También se aplica polimorfismo porque todos tienen los mismos métodos,
        pero cada subclase responde diferente.
        """

        if tipo_actividad == "Lectura":
            return Lectura()
        elif tipo_actividad == "Tarea":
            return Tarea()
        elif tipo_actividad == "Práctica":
            return Practica()
        elif tipo_actividad == "Proyecto":
            return Proyecto()
        elif tipo_actividad == "Examen":
            return Examen()
        else:
            return Tarea()

    def calcular_dias_restantes(self, fecha_entrega: str) -> int:
        """
        Calcula los días restantes para la entrega.
        Si la fecha ya pasó o es hoy, regresa 0.
        Si la fecha no es válida, regresa 999.
        """

        try:
            fecha = datetime.strptime(fecha_entrega, "%Y-%m-%d").date()
            hoy = date.today()

            dias = (fecha - hoy).days

            if dias < 0:
                return 0

            return dias

        except Exception:
            return 999

    def calcular_urgencia(self, dias_restantes: int) -> int:
        """
        Calcula el puntaje de urgencia según los días restantes.
        """

        if dias_restantes == 999:
            return 0
        elif dias_restantes == 0:
            return 100
        elif dias_restantes <= 1:
            return 90
        elif dias_restantes <= 3:
            return 75
        elif dias_restantes <= 7:
            return 55
        elif dias_restantes <= 14:
            return 35
        else:
            return 20

    def estimar_tiempo_ajustado(self, pendiente: dict) -> float:
        """
        Estima el tiempo real aproximado usando las horas base,
        el tipo de actividad y el tipo de materia.
        """

        horas_base = float(pendiente.get("horas_estimadas", 1))
        tipo_actividad = pendiente.get("tipo_actividad", "Tarea")
        tipo_materia = pendiente.get("tipo_materia", "Tronco común")

        actividad = self.__crear_tipo_actividad(tipo_actividad)

        factor_actividad = actividad.obtener_factor_tiempo()
        factor_materia = self.__factor_tiempo_materia.get(tipo_materia, 1.15)

        tiempo_ajustado = horas_base * factor_actividad * factor_materia

        return round(tiempo_ajustado, 2)

    def clasificar_carga(self, tiempo_ajustado: float) -> str:
        """
        Clasifica la carga de trabajo según el tiempo ajustado.
        """

        if tiempo_ajustado <= 1.5:
            return "Ligera"
        elif tiempo_ajustado <= 3:
            return "Moderada"
        elif tiempo_ajustado <= 5:
            return "Pesada"
        else:
            return "Muy pesada"

    def calcular_puntaje(self, pendiente: dict) -> float:
        """
        Calcula el puntaje total del pendiente.
        Entre mayor sea el puntaje, más prioridad tiene.
        """

        tipo_actividad = pendiente.get("tipo_actividad", "Tarea")
        tipo_materia = pendiente.get("tipo_materia", "Tronco común")
        fecha = pendiente.get("fecha", "")
        horas_estimadas = float(pendiente.get("horas_estimadas", 1))

        dias_restantes = self.calcular_dias_restantes(fecha)

        actividad = self.__crear_tipo_actividad(tipo_actividad)

        puntaje_urgencia = self.calcular_urgencia(dias_restantes)
        puntaje_actividad = actividad.obtener_peso()
        puntaje_materia = self.__peso_tipo_materia.get(tipo_materia, 10)

        # Se limita el efecto de las horas para que no domine todo el cálculo.
        puntaje_horas = min(horas_estimadas * 5, 30)

        puntaje_total = (
            puntaje_urgencia
            + puntaje_actividad
            + puntaje_materia
            + puntaje_horas
        )

        return round(puntaje_total, 2)

    def clasificar_prioridad(self, puntaje: float) -> str:
        """
        Convierte el puntaje en prioridad alta, media o baja.
        """

        if puntaje >= 120:
            return "Alta"
        elif puntaje >= 80:
            return "Media"
        else:
            return "Baja"

    def analizar_pendiente(self, pendiente: dict) -> dict:
        """
        Analiza un pendiente y le agrega los resultados calculados.
        """

        dias_restantes = self.calcular_dias_restantes(pendiente.get("fecha", ""))
        tiempo_ajustado = self.estimar_tiempo_ajustado(pendiente)
        puntaje = self.calcular_puntaje(pendiente)
        prioridad = self.clasificar_prioridad(puntaje)
        carga = self.clasificar_carga(tiempo_ajustado)

        pendiente_analizado = pendiente.copy()

        pendiente_analizado["dias_restantes"] = dias_restantes
        pendiente_analizado["tiempo_ajustado"] = tiempo_ajustado
        pendiente_analizado["puntaje_prioridad"] = puntaje
        pendiente_analizado["prioridad_calculada"] = prioridad
        pendiente_analizado["carga"] = carga

        return pendiente_analizado

    def analizar_pendientes(self, pendientes: list) -> list:
        """
        Analiza todos los pendientes.
        """

        pendientes_analizados = []

        for pendiente in pendientes:
            pendientes_analizados.append(self.analizar_pendiente(pendiente))

        return pendientes_analizados

    def ordenar_pendientes(self, pendientes: list) -> list:
        """
        Ordena los pendientes de mayor a menor prioridad.
        """

        pendientes_analizados = self.analizar_pendientes(pendientes)

        return sorted(
            pendientes_analizados,
            key=lambda pendiente: pendiente["puntaje_prioridad"],
            reverse=True
        )

    def obtener_resumen(self, pendientes: list) -> dict:
        """
        Genera un resumen general de la agenda.
        """

        pendientes_analizados = self.analizar_pendientes(pendientes)

        total_pendientes = len(pendientes_analizados)
        total_horas = sum(p["tiempo_ajustado"] for p in pendientes_analizados)

        prioridad_alta = 0

        for pendiente in pendientes_analizados:
            if pendiente["prioridad_calculada"] == "Alta":
                prioridad_alta += 1

        return {
            "total_pendientes": total_pendientes,
            "total_horas_ajustadas": round(total_horas, 2),
            "pendientes_prioridad_alta": prioridad_alta
        }