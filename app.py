from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QGroupBox,
    QFormLayout,
    QProgressBar,
    QTextEdit,
    QStackedWidget,
)
from mundo import MundoCarrera
from agente import AgenteQueAprende


class VentanaEntrenador(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrenador Virtual IA — Agente que Aprende (UNAM)")
        self.resize(780, 580)

        self.mundo = None
        self.agente = None
        self.historial_fc = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._iteracion_simulacion)

        self.stack = QStackedWidget(self)
        layout_principal = QVBoxLayout(self)
        layout_principal.addWidget(self.stack)

        self._construir_pagina_config()
        self._construir_pagina_simulacion()
        self._construir_pagina_resumen()

    # ---------------- PÁGINA 1: CONFIGURACIÓN ----------------
    def _construir_pagina_config(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        titulo = QLabel("Configuración del Corredor y Meta de Entrenamiento")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(titulo)

        grupo = QGroupBox("Parámetros Fisiológicos y Objetivo")
        form = QFormLayout(grupo)

        self.input_edad = QSpinBox()
        self.input_edad.setRange(15, 80)
        self.input_edad.setValue(22)

        self.input_peso = QDoubleSpinBox()
        self.input_peso.setRange(40.0, 150.0)
        self.input_peso.setValue(70.0)
        self.input_peso.setSuffix(" kg")

        self.input_nivel = QComboBox()
        self.input_nivel.addItems(["Principiante", "Intermedio", "Avanzado"])
        self.input_nivel.setCurrentText("Intermedio")

        self.input_distancia = QDoubleSpinBox()
        self.input_distancia.setRange(1.0, 42.2)
        self.input_distancia.setValue(5.0)
        self.input_distancia.setSuffix(" km")

        self.input_tiempo = QDoubleSpinBox()
        self.input_tiempo.setRange(5.0, 240.0)
        self.input_tiempo.setValue(25.0)
        self.input_tiempo.setSuffix(" min")

        form.addRow("Edad:", self.input_edad)
        form.addRow("Peso:", self.input_peso)
        form.addRow("Nivel de experiencia:", self.input_nivel)
        form.addRow("Distancia meta:", self.input_distancia)
        form.addRow("Tiempo límite:", self.input_tiempo)
        layout.addWidget(grupo)

        btn_iniciar = QPushButton("Iniciar Entrenamiento con Agente que Aprende")
        btn_iniciar.setStyleSheet("font-size: 14px; padding: 10px; font-weight: bold;")
        btn_iniciar.clicked.connect(self._iniciar_sesion)
        layout.addWidget(btn_iniciar)
        layout.addStretch()

        self.stack.addWidget(pagina)

    # ---------------- PÁGINA 2: SIMULACIÓN EN VIVO ----------------
    def _construir_pagina_simulacion(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        # Panel de telemetría física
        grupo_telemetria = QGroupBox("Telemetría del Entorno y Corredor")
        form_tel = QFormLayout(grupo_telemetria)

        self.lbl_tiempo = QLabel("0.0 / 0.0 min")
        self.lbl_distancia = QLabel("0.00 / 0.00 km")
        self.lbl_fc = QLabel("72.0 bpm")
        self.lbl_pendiente = QLabel("0.0 %")
        self.lbl_ritmo = QLabel("6.00 min/km")

        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)

        form_tel.addRow("Tiempo:", self.lbl_tiempo)
        form_tel.addRow("Distancia:", self.lbl_distancia)
        form_tel.addRow("Frecuencia Cardíaca:", self.lbl_fc)
        form_tel.addRow("Pendiente Terreno:", self.lbl_pendiente)
        form_tel.addRow("Ritmo Actual:", self.lbl_ritmo)
        form_tel.addRow("Progreso Meta:", self.barra_progreso)
        layout.addWidget(grupo_telemetria)

        # Panel de Arquitectura de Agente que Aprende
        grupo_ia = QGroupBox("Estado Interno del Agente que Aprende (Russell & Norvig)")
        form_ia = QFormLayout(grupo_ia)

        self.lbl_accion = QLabel("-")
        self.lbl_accion.setStyleSheet("font-weight: bold; color: #0b5394;")
        self.lbl_modo = QLabel("-")
        self.lbl_critico = QLabel("-")
        self.lbl_aprendizaje = QLabel("-")

        form_ia.addRow("Elemento de Actuación:", self.lbl_accion)
        form_ia.addRow("Generador de Problemas:", self.lbl_modo)
        form_ia.addRow("Evaluación del Crítico:", self.lbl_critico)
        form_ia.addRow("Parámetros Aprendidos:", self.lbl_aprendizaje)
        layout.addWidget(grupo_ia)

        self.log_eventos = QTextEdit()
        self.log_eventos.setReadOnly(True)
        layout.addWidget(self.log_eventos)

        botones = QHBoxLayout()
        btn_detener = QPushButton("Finalizar Sesión Ahora")
        btn_detener.clicked.connect(self._finalizar_sesion)
        botones.addWidget(btn_detener)
        layout.addLayout(botones)

        self.stack.addWidget(pagina)

    # ---------------- PÁGINA 3: RESUMEN FINAL ----------------
    def _construir_pagina_resumen(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)

        titulo = QLabel("Resumen de Sesión y Consolidación del Aprendizaje")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(titulo)

        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setWordWrap(True)
        self.lbl_resumen.setStyleSheet("font-size: 13px; padding: 10px;")
        layout.addWidget(self.lbl_resumen)

        btn_volver = QPushButton("Nueva Sesión (Conservar Memoria Aprendida)")
        btn_volver.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        layout.addWidget(btn_volver)
        layout.addStretch()

        self.stack.addWidget(pagina)

    # ---------------- LÓGICA DE CONTROL ----------------
    def _iniciar_sesion(self):
        edad = self.input_edad.value()
        peso = self.input_peso.value()
        nivel = self.input_nivel.currentText()
        dist = self.input_distancia.value()
        tiempo = self.input_tiempo.value()

        self.mundo = MundoCarrera(edad, peso, nivel)
        self.agente = AgenteQueAprende(edad, peso, nivel, dist, tiempo)
        self.historial_fc = []

        self.log_eventos.clear()
        self.log_eventos.append(
            f"Sesión #{self.agente.sesiones_completadas + 1} iniciada | "
            f"Zona FC objetivo: [{self.agente.fc_obj_min:.1f}, {self.agente.fc_obj_max:.1f}] bpm | "
            f"Exploración ε={self.agente.epsilon:.2f}"
        )

        self.stack.setCurrentIndex(1)
        self.timer.start(350)  # 350 ms por paso de simulación

    def _iteracion_simulacion(self):
        percepcion = self.mundo.obtener_percepcion()
        decision = self.agente.decidir_accion(percepcion)
        nueva_percepcion = self.mundo.paso(decision["nuevo_ritmo"], dt_min=0.25)

        self.historial_fc.append(nueva_percepcion["fc"])

        # Actualizar interfaz
        self.lbl_tiempo.setText(f"{nueva_percepcion['tiempo']:.2f} / {self.agente.tiempo_meta:.1f} min")
        self.lbl_distancia.setText(f"{nueva_percepcion['distancia']:.2f} / {self.agente.distancia_meta:.2f} km")
        self.lbl_fc.setText(
            f"{nueva_percepcion['fc']:.1f} bpm (Ideal: {self.agente.fc_ideal:.1f} bpm)"
        )
        self.lbl_pendiente.setText(f"{nueva_percepcion['pendiente']:+.2f} %")
        self.lbl_ritmo.setText(f"{nueva_percepcion['ritmo']:.2f} min/km")

        progreso = int(min(100, (nueva_percepcion["distancia"] / self.agente.distancia_meta) * 100))
        self.barra_progreso.setValue(progreso)

        self.lbl_accion.setText(
            f"{decision['accion']} -> {decision['nuevo_ritmo']:.2f} min/km (U = {decision['utilidad']})"
        )
        self.lbl_modo.setText(decision["modo"])
        self.lbl_critico.setText(
            f"{decision['diagnostico_critico']} | Error pred. FC: {decision['error_modelo']:+.2f} bpm"
        )
        p = decision["pesos"]
        self.lbl_aprendizaje.setText(
            f"w_meta={p['meta']:.2f}, w_cardio={p['cardio']:.2f} | "
            f"Sensibilidad FC={decision['sensibilidad_fc']:.2f}"
        )

        self.log_eventos.append(
            f"[t={nueva_percepcion['tiempo']:.2f}m] FC={nueva_percepcion['fc']:.1f} | "
            f"Pend={nueva_percepcion['pendiente']:+.1f}% | {decision['accion']} ({decision['modo']})"
        )

        if (
            nueva_percepcion["distancia"] >= self.agente.distancia_meta
            or nueva_percepcion["tiempo"] >= self.agente.tiempo_meta
        ):
            self._finalizar_sesion()

    def _finalizar_sesion(self):
        self.timer.stop()
        percepcion = self.mundo.obtener_percepcion()
        fc_prom = sum(self.historial_fc) / max(1, len(self.historial_fc))

        score = self.agente.aprender_fin_sesion(
            percepcion["distancia"], percepcion["tiempo"], fc_prom
        )

        cumplio = percepcion["distancia"] >= (self.agente.distancia_meta * 0.98)
        estado_meta = "META CUMPLIDA" if cumplio else "META NO ALCANZADA"

        texto = (
            f"Resultado: {estado_meta}\n"
            f"Distancia recorrida: {percepcion['distancia']:.2f} km / {self.agente.distancia_meta:.2f} km\n"
            f"Tiempo total: {percepcion['tiempo']:.2f} min / {self.agente.tiempo_meta:.2f} min\n"
            f"Frecuencia cardíaca promedio: {fc_prom:.1f} bpm (Límite seguro: {self.agente.fc_obj_max:.1f} bpm)\n"
            f"Puntuación de desempeño de sesión: {score:.1f} / 100\n\n"
            f"--- Memoria Persistente Actualizada (memoria_agente.json) ---\n"
            f"Total de sesiones entrenadas: {self.agente.sesiones_completadas}\n"
            f"Pesos aprendidos: w_meta = {self.agente.pesos['meta']:.3f}, w_cardio = {self.agente.pesos['cardio']:.3f}\n"
            f"Sensibilidad cardíaca identificada: {self.agente.sensibilidad_fc_aprendida:.3f}\n"
            f"Nueva tasa de exploración (ε): {self.agente.epsilon:.3f}"
        )
        self.lbl_resumen.setText(texto)
        self.stack.setCurrentIndex(2)
