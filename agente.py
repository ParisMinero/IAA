import json
import os
import random


class AgenteQueAprende:
    """
    Agente que Aprende (Nivel máximo de arquitectura según Russell & Norvig):
    1. Elemento de Actuación: Evalúa utilidad esperada y elige ritmo.
    2. Crítico: Evalúa el error de predicción fisiológica y el desempeño real.
    3. Elemento de Aprendizaje: Actualiza el modelo interno de sensibilidad cardíaca
       y ajusta los pesos de la función de utilidad (w_meta, w_cardio, w_fatiga).
    4. Generador de Problemas: Exploración controlada (epsilon-greedy) para descubrir
       mejores políticas de ritmo.
    """
    ARCHIVO_MEMORIA = "memoria_agente.json"

    def __init__(self, edad, peso, nivel, distancia_meta, tiempo_meta):
        self.edad = edad
        self.peso = peso
        self.nivel = nivel
        self.distancia_meta = distancia_meta
        self.tiempo_meta = tiempo_meta

        # Ecuación de Tanaka
        self.fc_max = 208.0 - (0.7 * self.edad)
        factores = {
            "Principiante": (0.65, 0.75),
            "Intermedio": (0.70, 0.82),
            "Avanzado": (0.75, 0.88),
        }
        f_min, f_max = factores.get(nivel, (0.70, 0.80))
        self.fc_obj_min = self.fc_max * f_min
        self.fc_obj_max = self.fc_max * f_max
        self.fc_ideal = (self.fc_obj_min + self.fc_obj_max) / 2.0

        # Estado de memoria previa para el Crítico
        self.ultima_prediccion_fc = None
        self.ultima_accion = None
        self.ultimo_ritmo_base = None
        self.ultima_pendiente = 0.0

        # Carga conocimiento aprendido de sesiones anteriores o inicializar
        self._cargar_memoria()

    def _cargar_memoria(self):
        if os.path.exists(self.ARCHIVO_MEMORIA):
            try:
                with open(self.ARCHIVO_MEMORIA, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.sesiones_completadas = data.get("sesiones_completadas", 0)
                self.pesos = data.get("pesos", {"meta": 1.0, "cardio": 1.0, "terreno": 1.0})
                self.sensibilidad_fc_aprendida = data.get("sensibilidad_fc", 12.0)
                self.epsilon = max(0.05, 0.25 * (0.85 ** self.sesiones_completadas))
                self.historial_recompensas = data.get("historial_recompensas", [])
                return
            except Exception:
                pass

        # Parámetros iniciales sin experiencia previa
        self.sesiones_completadas = 0
        self.pesos = {"meta": 1.0, "cardio": 1.0, "terreno": 1.0}
        self.sensibilidad_fc_aprendida = 12.0  
        self.epsilon = 0.25                    
        self.historial_recompensas = []

    def guardar_memoria(self):
        data = {
            "sesiones_completadas": self.sesiones_completadas,
            "pesos": {k: round(v, 4) for k, v in self.pesos.items()},
            "sensibilidad_fc": round(self.sensibilidad_fc_aprendida, 4),
            "epsilon": round(self.epsilon, 4),
            "historial_recompensas": self.historial_recompensas[-20:],
        }
        with open(self.ARCHIVO_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # MÓDULO 2: CRÍTICO (Evaluación de desempeño y predicción)

    def critico_evaluar(self, percepcion_actual):
        """
        Compara la FC real observada contra la FC predicha en el paso anterior
        y calcula una señal de recompensa/penalización inmediata.
        """
        fc_real = percepcion_actual["fc"]
        error_modelo = 0.0

        if self.ultima_prediccion_fc is not None:
            error_modelo = fc_real - self.ultima_prediccion_fc

        # Estándar de desempeño del crítico
        if fc_real > self.fc_obj_max:
            recompensa = -2.0 * (fc_real - self.fc_obj_max)
            diagnostico = "Sobreesfuerzo detectado: aumentando prioridad cardíaca"
        elif fc_real < self.fc_obj_min:
            recompensa = -0.8 * (self.fc_obj_min - fc_real)
            diagnostico = "Sub-entrenamiento: ajustando prioridad de meta"
        else:
            recompensa = +10.0
            diagnostico = "Zona aeróbica óptima: reforzando política actual"

        return recompensa, error_modelo, diagnostico


    # MÓDULO 3: ELEMENTO DE APRENDIZAJE (Actualización online)

    def aprender_paso(self, percepcion_actual, tasa_aprendizaje=0.04):
        """
        Actualiza:
        1) El modelo interno del entorno (sensibilidad_fc_aprendida).
        2) Los pesos de la función de utilidad (w_meta, w_cardio).
        """
        recompensa, error_modelo, diagnostico = self.critico_evaluar(percepcion_actual)

        # 1. Aprendizaje del modelo interno (identificación de sistema en línea)
        if self.ultima_prediccion_fc is not None and self.ultimo_ritmo_base is not None:
            delta_ritmo = self.ultimo_ritmo_base - percepcion_actual["ritmo"]
            if abs(delta_ritmo) > 0.05:
                # Gradiente estocástico sobre el error de predicción de FC
                ajuste = tasa_aprendizaje * error_modelo * (1.0 if delta_ritmo > 0 else -1.0)
                self.sensibilidad_fc_aprendida = max(
                    5.0, min(25.0, self.sensibilidad_fc_aprendida + ajuste)
                )

        # 2. Aprendizaje de preferencias / pesos de utilidad
        fc_real = percepcion_actual["fc"]
        if fc_real > self.fc_obj_max:
            self.pesos["cardio"] = min(2.5, self.pesos["cardio"] + tasa_aprendizaje)
            self.pesos["meta"] = max(0.5, self.pesos["meta"] - tasa_aprendizaje * 0.5)
        elif fc_real < self.fc_obj_min:
            self.pesos["meta"] = min(2.5, self.pesos["meta"] + tasa_aprendizaje)
            self.pesos["cardio"] = max(0.5, self.pesos["cardio"] - tasa_aprendizaje * 0.3)

        return recompensa, error_modelo, diagnostico

    def aprender_fin_sesion(self, distancia_final, tiempo_final, fc_promedio):
        """
        Consolidación episódica al terminar la carrera y reducción de exploración.
        """
        cumplio_distancia = distancia_final >= (self.distancia_meta * 0.98)
        fc_segura = fc_promedio <= self.fc_obj_max

        score_sesion = (distancia_final / max(0.1, self.distancia_meta)) * 100.0
        if not fc_segura:
            score_sesion -= 25.0

        # Ajuste episódico según éxito global
        if not cumplio_distancia and fc_segura:
            self.pesos["meta"] = min(2.5, self.pesos["meta"] + 0.08)
        elif not fc_segura:
            self.pesos["cardio"] = min(2.5, self.pesos["cardio"] + 0.10)

        self.sesiones_completadas += 1
        self.epsilon = max(0.05, self.epsilon * 0.85)
        self.historial_recompensas.append(round(score_sesion, 1))
        self.guardar_memoria()
        return score_sesion

    # MÓDULO 1 & 4: ACTUACIÓN (Utilidad) + GENERADOR DE PROBLEMAS

    def calcular_utilidad(self, fc_estimada, ritmo_propuesto, ritmo_requerido, pendiente):
        error_fc = abs(fc_estimada - self.fc_ideal)
        penalizacion_fc = (error_fc / self.fc_max) * 100.0 * self.pesos["cardio"]
        if fc_estimada > self.fc_obj_max:
            penalizacion_fc *= 2.2

        diff_ritmo = abs(ritmo_propuesto - ritmo_requerido)
        penalizacion_meta = diff_ritmo * 15.0 * self.pesos["meta"]

        penalizacion_terreno = (
            max(0.0, pendiente) * (1.0 / max(0.1, ritmo_propuesto)) * 5.0 * self.pesos["terreno"]
        )

        return 100.0 - (penalizacion_fc + penalizacion_meta + penalizacion_terreno)

    def decidir_accion(self, percepcion):
        recompensa, error_modelo, diagnostico = self.aprender_paso(percepcion)

        fc_actual = percepcion["fc"]
        pendiente = percepcion["pendiente"]
        ritmo_actual = percepcion["ritmo"]
        dist_restante = max(0.01, self.distancia_meta - percepcion["distancia"])
        tiempo_restante = max(0.01, self.tiempo_meta - percepcion["tiempo"])
        ritmo_requerido = tiempo_restante / dist_restante

        acciones_posibles = [
            ("Acelerar fuertemente", ritmo_actual - 0.35),
            ("Acelerar ligeramente", ritmo_actual - 0.15),
            ("Mantener ritmo", ritmo_actual),
            ("Reducir ligeramente", ritmo_actual + 0.20),
            ("Recuperar / Bajar ritmo", ritmo_actual + 0.45),
        ]

        evaluaciones = []
        for nombre, nuevo_ritmo in acciones_posibles:
            nuevo_ritmo = round(max(3.2, min(8.5, nuevo_ritmo)), 2)
            # Predicción usando el parámetro aprendido (sensibilidad_fc_aprendida)
            delta_fc = (ritmo_actual - nuevo_ritmo) * (self.sensibilidad_fc_aprendida * 0.4) + (
                pendiente * 1.6
            )
            fc_predicha = fc_actual + delta_fc
            u = self.calcular_utilidad(fc_predicha, nuevo_ritmo, ritmo_requerido, pendiente)
            evaluaciones.append((nombre, nuevo_ritmo, u, fc_predicha))

        # MÓDULO 4: GENERADOR DE PROBLEMAS (Exploración epsilon-greedy)
        modo = "Explotación (Utilidad Máxima)"
        if random.random() < self.epsilon and fc_actual < (self.fc_obj_max - 5):
            elegida = random.choice(evaluaciones)
            modo = f"Exploración (ε={self.epsilon:.2f})"
        else:
            elegida = max(evaluaciones, key=lambda x: x[2])

        nombre_acc, ritmo_elegido, util_elegida, fc_pred = elegida

        # Guardar estado para que el Crítico evalúe en el siguiente ciclo
        self.ultima_prediccion_fc = fc_pred
        self.ultima_accion = nombre_acc
        self.ultimo_ritmo_base = ritmo_actual
        self.ultima_pendiente = pendiente

        return {
            "accion": nombre_acc,
            "nuevo_ritmo": ritmo_elegido,
            "utilidad": round(util_elegida, 2),
            "modo": modo,
            "diagnostico_critico": diagnostico,
            "error_modelo": round(error_modelo, 2),
            "pesos": dict(self.pesos),
            "sensibilidad_fc": round(self.sensibilidad_fc_aprendida, 2),
            "sesiones": self.sesiones_completadas,
        }
