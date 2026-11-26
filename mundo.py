import random
import math


class MundoCarrera:
    """
    Simula el entorno físico (terreno con pendientes y ruido) y la respuesta
    fisiológica real del corredor.
    """
    def __init__(self, edad, peso, nivel):
        self.edad = edad
        self.peso = peso
        self.nivel = nivel

        # Parámetro fisiológico real (desconocido inicialmente por el agente)
        base_resistencia = {"Principiante": 0.85, "Intermedio": 1.0, "Avanzado": 1.20}
        self.resistencia_real = base_resistencia.get(nivel, 1.0) * random.uniform(0.92, 1.08)

        self.reset()

    def reset(self):
        self.tiempo = 0.0          # minutos
        self.distancia = 0.0       # km
        self.fc = 72.0             # bpm inicial en reposo activo
        self.ritmo_actual = 6.0    # min/km
        self.pendiente = 0.0       # % de inclinación
        self.fatiga_acumulada = 0.0

    def paso(self, nuevo_ritmo, dt_min=0.25):
        """
        Avanza la simulación dt_min minutos dada la acción (nuevo_ritmo)
        elegida por el agente.
        """
        self.ritmo_actual = nuevo_ritmo
        self.tiempo += dt_min

        # Distancia recorrida en este intervalo (km)
        velocidad_km_min = 1.0 / max(2.5, self.ritmo_actual)
        self.distancia += velocidad_km_min * dt_min

        # Evolución del terreno: colinas sinusoidales + ruido estocástico
        onda_terreno = 3.5 * math.sin(self.distancia * 2.2) + 1.8 * math.cos(self.distancia * 5.1)
        ruido = random.gauss(0.0, 0.8)
        self.pendiente = round(max(-6.0, min(10.0, onda_terreno + ruido)), 2)

        # Demanda metabólica y respuesta dinámica de frecuencia cardíaca
        esfuerzo_ritmo = (7.5 - self.ritmo_actual) * 14.5
        esfuerzo_pendiente = self.pendiente * 2.4
        self.fatiga_acumulada += max(0.0, (esfuerzo_ritmo + esfuerzo_pendiente) * 0.008 * dt_min)

        fc_objetivo_fisiologica = (
            85.0
            + (esfuerzo_ritmo + esfuerzo_pendiente) / self.resistencia_real
            + self.fatiga_acumulada
            + random.gauss(0.0, 1.5)
        )

        # Inercia cardíaca (primer orden)
        alpha = 0.35
        self.fc = self.fc + alpha * (fc_objetivo_fisiologica - self.fc)
        self.fc = max(65.0, min(205.0, self.fc))

        return self.obtener_percepcion()

    def obtener_percepcion(self):
        return {
            "tiempo": round(self.tiempo, 2),
            "distancia": round(self.distancia, 3),
            "fc": round(self.fc, 1),
            "ritmo": round(self.ritmo_actual, 2),
            "pendiente": self.pendiente,
            "fatiga": round(self.fatiga_acumulada, 2),
        }
