from datetime import datetime, date


class CalculadoraAgenda:
    """
    Clase encargada de calcular automáticamente la prioridad de los pendientes
    según la fecha de entrega, tipo de actividad, tipo de materia y horas estimadas.
    """

    def __init__(self):
        self.__peso_tipo_actividad = {
            "Lectura": 8,
            "Tarea": 15,
            "Práctica": 18,
            "Proyecto": 25,
            "Examen": 30
        }

        self.__peso_tipo_materia = {
            "Humanidades": 5,
            "Tronco común": 10,
            "Carrera": 15
        }

        self.__factor_tiempo_actividad = {
            "Lectura": 0.8,
            "Tarea": 1.0,
            "Práctica": 1.2,
            "Proyecto": 1.4,
            "Examen": 1.6
        }

        self.__factor_tiempo_materia = {
            "Humanidades": 1.0,
            "Tronco común": 1.15,
            "Carrera": 1.3
        }

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

        factor_actividad = self.__factor_tiempo_actividad.get(tipo_actividad, 1.0)
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

        puntaje_urgencia = self.calcular_urgencia(dias_restantes)
        puntaje_actividad = self.__peso_tipo_actividad.get(tipo_actividad, 15)
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