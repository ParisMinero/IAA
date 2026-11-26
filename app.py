from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath, QFont, QLinearGradient
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QFrame,
    QFormLayout,
    QProgressBar,
    QTextEdit,
    QStackedWidget,
    QSizePolicy,
)
from mundo import MundoCarrera
from agente import AgenteQueAprende


ESTILO_GLOBAL = """
QWidget {
    background-color: #0f172a;
    color: #f8fafc;
    font-family: 'Segoe UI', 'Ubuntu', 'Noto Sans', sans-serif;
    font-size: 13px;
}
QFrame#Tarjeta {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
}
QFrame#Tarjeta QLabel {
    background-color: transparent;
}
QFrame#TarjetaKPI {
    background-color: #1e293b;
    border: 1px solid #334155;
    border-radius: 10px;
}
QFrame#TarjetaKPI QLabel {
    background-color: transparent;
}
QLabel#TituloPrincipal {
    font-size: 22px;
    font-weight: 700;
    color: #f8fafc;
}
QLabel#Subtitulo {
    font-size: 13px;
    color: #94a3b8;
}
QLabel#SeccionTitulo {
    font-size: 14px;
    font-weight: 700;
    color: #38bdf8;
    letter-spacing: 0.5px;
}
QLabel#KPITitulo {
    font-size: 11px;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
}
QLabel#KPIValor {
    font-size: 20px;
    font-weight: 700;
    color: #f8fafc;
}
QLabel#KPISub {
    font-size: 11px;
    color: #64748b;
}
QSpinBox, QDoubleSpinBox, QComboBox {
    background-color: #0f172a;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 28px 6px 10px;
    color: #f8fafc;
    font-size: 13px;
    min-height: 24px;
}
QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {
    border: 1px solid #38bdf8;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 24px;
    background-color: #334155;
    border-left: 1px solid #475569;
    border-top-right-radius: 6px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 24px;
    background-color: #334155;
    border-left: 1px solid #475569;
    border-bottom-right-radius: 6px;
}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
    background-color: #475569;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
    width: 0px;
    height: 0px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid #f8fafc;
}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
    width: 0px;
    height: 0px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #f8fafc;
}
QComboBox::drop-down {
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 26px;
    background-color: #334155;
    border-left: 1px solid #475569;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}
QComboBox::down-arrow {
    width: 0px;
    height: 0px;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #f8fafc;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    color: #f8fafc;
    selection-background-color: #0284c7;
}
QPushButton#BtnPrimario {
    background-color: #10b981;
    color: #064e3b;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 12px 20px;
}
QPushButton#BtnPrimario:hover {
    background-color: #34d399;
}
QPushButton#BtnPrimario:pressed {
    background-color: #059669;
}
QPushButton#BtnPeligro {
    background-color: #ef4444;
    color: #ffffff;
    font-size: 13px;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 10px 18px;
}
QPushButton#BtnPeligro:hover {
    background-color: #f87171;
}
QProgressBar {
    background-color: #0f172a;
    border: 1px solid #334155;
    border-radius: 7px;
    height: 14px;
    text-align: center;
    color: #f8fafc;
    font-size: 11px;
    font-weight: 700;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0284c7, stop:1 #10b981);
    border-radius: 6px;
}
QTextEdit {
    background-color: #0b1120;
    border: 1px solid #334155;
    border-radius: 8px;
    padding: 8px;
    font-family: 'Consolas', 'Ubuntu Mono', monospace;
    font-size: 12px;
    color: #cbd5e1;
}
"""

class GraficaTelemetria(QWidget):
    """Widget personalizado que dibuja en tiempo real la FC, la zona objetivo y la pendiente."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(165)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.datos_fc = []
        self.datos_pendiente = []
        self.fc_min_obj = 130.0
        self.fc_max_obj = 160.0

    def reiniciar(self, fc_min_obj, fc_max_obj):
        self.datos_fc = []
        self.datos_pendiente = []
        self.fc_min_obj = fc_min_obj
        self.fc_max_obj = fc_max_obj
        self.update()

    def agregar_punto(self, fc, pendiente):
        self.datos_fc.append(fc)
        self.datos_pendiente.append(pendiente)
        if len(self.datos_fc) > 80:
            self.datos_fc.pop(0)
            self.datos_pendiente.pop(0)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(6, 6, -6, -6)
        # Fondo de gráfica
        painter.setPen(QPen(QColor("#334155"), 1))
        painter.setBrush(QColor("#0b1120"))
        painter.drawRoundedRect(rect, 8, 8)

        w = rect.width() - 24
        h = rect.height() - 28
        x0 = rect.left() + 12
        y0 = rect.top() + 18

        y_min, y_max = 60.0, 205.0

        def map_y_fc(val):
            norm = (val - y_min) / (y_max - y_min)
            norm = max(0.0, min(1.0, norm))
            return y0 + h - (norm * h)

        # Banda verde de zona aeróbica segura
        y_top_zona = map_y_fc(self.fc_max_obj)
        y_bot_zona = map_y_fc(self.fc_min_obj)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(16, 185, 129, 32))
        painter.drawRect(int(x0), int(y_top_zona), int(w), int(max(2, y_bot_zona - y_top_zona)))

        # Líneas límite de zona objetivo
        pen_limite = QPen(QColor("#10b981"), 1, Qt.DashLine)
        painter.setPen(pen_limite)
        painter.drawLine(int(x0), int(y_top_zona), int(x0 + w), int(y_top_zona))
        painter.drawLine(int(x0), int(y_bot_zona), int(x0 + w), int(y_bot_zona))

        # Leyenda superior
        painter.setFont(QFont("Sans", 9))
        painter.setPen(QColor("#34d399"))
        painter.drawText(
            int(x0),
            int(rect.top() + 13),
            f"Zona Objetivo: {self.fc_min_obj:.0f}–{self.fc_max_obj:.0f} bpm",
        )
        painter.setPen(QColor("#f43f5e"))
        painter.drawText(int(x0 + w - 195), int(rect.top() + 13), "— FC (bpm)   --- Pendiente (%)")

        if len(self.datos_fc) < 2:
            painter.setPen(QColor("#64748b"))
            painter.drawText(rect, Qt.AlignCenter, "Esperando telemetría de carrera...")
            return

        paso_x = w / max(1, len(self.datos_fc) - 1)

        # Curva de pendiente (escalada de -6..10% a la altura del panel)
        path_pend = QPainterPath()
        for i, p in enumerate(self.datos_pendiente):
            px = x0 + i * paso_x
            norm_p = (p + 6.0) / 16.0
            py = y0 + h - (max(0.0, min(1.0, norm_p)) * h)
            if i == 0:
                path_pend.moveTo(px, py)
            else:
                path_pend.lineTo(px, py)
        painter.setPen(QPen(QColor("#38bdf8"), 1.5, Qt.DotLine))
        painter.drawPath(path_pend)

        # Curva de Frecuencia Cardíaca
        path_fc = QPainterPath()
        for i, fc in enumerate(self.datos_fc):
            px = x0 + i * paso_x
            py = map_y_fc(fc)
            if i == 0:
                path_fc.moveTo(px, py)
            else:
                path_fc.lineTo(px, py)

        painter.setPen(QPen(QColor("#f43f5e"), 2.5))
        painter.drawPath(path_fc)


class VentanaEntrenador(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrenador Virtual IA — Agente que Aprende (UNAM)")
        self.resize(900, 680)
        self.setStyleSheet(ESTILO_GLOBAL)

        self.mundo = None
        self.agente = None
        self.historial_fc = []

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._iteracion_simulacion)

        self.stack = QStackedWidget(self)
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(16, 16, 16, 16)
        layout_principal.addWidget(self.stack)

        self._construir_pagina_config()
        self._construir_pagina_simulacion()
        self._construir_pagina_resumen()

    def _crear_tarjeta(self, object_name="Tarjeta"):
        frame = QFrame()
        frame.setObjectName(object_name)
        return frame

    def _crear_kpi(self, titulo, valor_inicial, sub_inicial=""):
        card = self._crear_tarjeta("TarjetaKPI")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(2)

        lbl_t = QLabel(titulo)
        lbl_t.setObjectName("KPITitulo")
        lbl_v = QLabel(valor_inicial)
        lbl_v.setObjectName("KPIValor")
        lbl_s = QLabel(sub_inicial)
        lbl_s.setObjectName("KPISub")

        lay.addWidget(lbl_t)
        lay.addWidget(lbl_v)
        lay.addWidget(lbl_s)
        return card, lbl_v, lbl_s

    # ---------------- PÁGINA 1: CONFIGURACIÓN ----------------
    def _construir_pagina_config(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(16)

        header = QVBoxLayout()
        titulo = QLabel("Entrenador Virtual de Carrera IA")
        titulo.setObjectName("TituloPrincipal")
        subtitulo = QLabel(
            "Arquitectura de Agente que Aprende (Russell & Norvig) con anclaje fisiológico de Tanaka"
        )
        subtitulo.setObjectName("Subtitulo")
        header.addWidget(titulo)
        header.addWidget(subtitulo)
        layout.addLayout(header)

        tarjeta_form = self._crear_tarjeta()
        lay_tarjeta = QVBoxLayout(tarjeta_form)
        lay_tarjeta.setContentsMargins(20, 20, 20, 20)
        lay_tarjeta.setSpacing(14)

        lbl_sec = QLabel("PERFIL FISIOLÓGICO Y META DE SESIÓN")
        lbl_sec.setObjectName("SeccionTitulo")
        lay_tarjeta.addWidget(lbl_sec)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft)

        self.input_edad = QSpinBox()
        self.input_edad.setRange(15, 80)
        self.input_edad.setValue(22)
        self.input_edad.setSuffix(" años")

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

        form.addRow("Edad del corredor:", self.input_edad)
        form.addRow("Peso corporal:", self.input_peso)
        form.addRow("Nivel de experiencia:", self.input_nivel)
        form.addRow("Distancia objetivo:", self.input_distancia)
        form.addRow("Tiempo límite:", self.input_tiempo)
        lay_tarjeta.addLayout(form)

        layout.addWidget(tarjeta_form)

        btn_iniciar = QPushButton("▶  Iniciar Entrenamiento Inteligente")
        btn_iniciar.setObjectName("BtnPrimario")
        btn_iniciar.setCursor(Qt.PointingHandCursor)
        btn_iniciar.clicked.connect(self._iniciar_sesion)
        layout.addWidget(btn_iniciar)
        layout.addStretch()

        self.stack.addWidget(pagina)

    # ---------------- PÁGINA 2: SIMULACIÓN EN VIVO ----------------
    def _construir_pagina_simulacion(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(12)

        # Barra superior con título de sesión y botón detener
        top_bar = QHBoxLayout()
        self.lbl_titulo_sesion = QLabel("Sesión Activa")
        self.lbl_titulo_sesion.setObjectName("TituloPrincipal")
        top_bar.addWidget(self.lbl_titulo_sesion)
        top_bar.addStretch()

        btn_detener = QPushButton("■  Finalizar Sesión")
        btn_detener.setObjectName("BtnPeligro")
        btn_detener.setCursor(Qt.PointingHandCursor)
        btn_detener.clicked.connect(self._finalizar_sesion)
        top_bar.addWidget(btn_detener)
        layout.addLayout(top_bar)

        # Fila de 5 tarjetas KPI
        grid_kpi = QGridLayout()
        grid_kpi.setSpacing(10)

        c1, self.lbl_tiempo, self.sub_tiempo = self._crear_kpi("Tiempo", "0.0 min", "Meta: 0.0 min")
        c2, self.lbl_distancia, self.sub_distancia = self._crear_kpi("Distancia", "0.00 km", "Meta: 0.00 km")
        c3, self.lbl_fc, self.sub_fc = self._crear_kpi("Frec. Cardíaca", "72.0 bpm", "Ideal: -- bpm")
        c4, self.lbl_ritmo, self.sub_ritmo = self._crear_kpi("Ritmo Actual", "6.00 min/km", "Objetivo dinámico")
        c5, self.lbl_pendiente, self.sub_pendiente = self._crear_kpi("Terreno", "+0.0 %", "Inclinación actual")

        grid_kpi.addWidget(c1, 0, 0)
        grid_kpi.addWidget(c2, 0, 1)
        grid_kpi.addWidget(c3, 0, 2)
        grid_kpi.addWidget(c4, 0, 3)
        grid_kpi.addWidget(c5, 0, 4)
        layout.addLayout(grid_kpi)

        # Barra de progreso
        self.barra_progreso = QProgressBar()
        self.barra_progreso.setRange(0, 100)
        self.barra_progreso.setFormat("Progreso de Meta: %p%")
        layout.addWidget(self.barra_progreso)

        # Gráfica en tiempo real
        self.grafica = GraficaTelemetria()
        layout.addWidget(self.grafica)

        # Tarjeta de los 4 módulos del Agente que Aprende
        tarjeta_ia = self._crear_tarjeta()
        lay_ia = QVBoxLayout(tarjeta_ia)
        lay_ia.setContentsMargins(14, 12, 14, 12)
        lay_ia.setSpacing(8)

        lbl_ia_sec = QLabel("ARQUITECTURA INTERNA DEL AGENTE QUE APRENDE")
        lbl_ia_sec.setObjectName("SeccionTitulo")
        lay_ia.addWidget(lbl_ia_sec)

        grid_ia = QGridLayout()
        grid_ia.setSpacing(8)

        self.lbl_accion = QLabel("-")
        self.lbl_accion.setStyleSheet("font-weight: 700; color: #34d399; font-size: 13px;")
        self.lbl_modo = QLabel("-")
        self.lbl_modo.setStyleSheet("color: #38bdf8; font-weight: 600;")
        self.lbl_critico = QLabel("-")
        self.lbl_critico.setStyleSheet("color: #fbbf24;")
        self.lbl_aprendizaje = QLabel("-")
        self.lbl_aprendizaje.setStyleSheet("color: #c084fc; font-weight: 600;")

        grid_ia.addWidget(QLabel("1. Actuación (Utilidad):"), 0, 0)
        grid_ia.addWidget(self.lbl_accion, 0, 1)
        grid_ia.addWidget(QLabel("4. Generador Problemas:"), 0, 2)
        grid_ia.addWidget(self.lbl_modo, 0, 3)
        grid_ia.addWidget(QLabel("2. Crítico:"), 1, 0)
        grid_ia.addWidget(self.lbl_critico, 1, 1)
        grid_ia.addWidget(QLabel("3. Aprendizaje:"), 1, 2)
        grid_ia.addWidget(self.lbl_aprendizaje, 1, 3)
        lay_ia.addLayout(grid_ia)

        layout.addWidget(tarjeta_ia)

        # Bitácora compacta
        self.log_eventos = QTextEdit()
        self.log_eventos.setReadOnly(True)
        self.log_eventos.setMaximumHeight(110)
        layout.addWidget(self.log_eventos)

        self.stack.addWidget(pagina)

    # ---------------- PÁGINA 3: RESUMEN FINAL ----------------
    def _construir_pagina_resumen(self):
        pagina = QWidget()
        layout = QVBoxLayout(pagina)
        layout.setSpacing(16)

        self.lbl_titulo_resumen = QLabel("Resumen de Sesión y Consolidación del Aprendizaje")
        self.lbl_titulo_resumen.setObjectName("TituloPrincipal")
        layout.addWidget(self.lbl_titulo_resumen)

        # KPIs finales
        grid_res = QGridLayout()
        grid_res.setSpacing(12)
        r1, self.res_estado, self.res_sub_estado = self._crear_kpi("Resultado", "-", "")
        r2, self.res_dist, self.res_sub_dist = self._crear_kpi("Distancia Lograda", "-", "")
        r3, self.res_fc, self.res_sub_fc = self._crear_kpi("FC Promedio", "-", "")
        r4, self.res_score, self.res_sub_score = self._crear_kpi("Puntuación IA", "-", "")
        grid_res.addWidget(r1, 0, 0)
        grid_res.addWidget(r2, 0, 1)
        grid_res.addWidget(r3, 0, 2)
        grid_res.addWidget(r4, 0, 3)
        layout.addLayout(grid_res)

        # Tarjeta de memoria persistente
        tarjeta_mem = self._crear_tarjeta()
        lay_mem = QVBoxLayout(tarjeta_mem)
        lay_mem.setContentsMargins(18, 16, 18, 16)
        lay_mem.setSpacing(8)

        lbl_mem_t = QLabel("MEMORIA PERSISTENTE ACTUALIZADA (memoria_agente.json)")
        lbl_mem_t.setObjectName("SeccionTitulo")
        lay_mem.addWidget(lbl_mem_t)

        self.lbl_resumen = QLabel("")
        self.lbl_resumen.setWordWrap(True)
        self.lbl_resumen.setStyleSheet("font-size: 13px; line-height: 1.5; color: #e2e8f0;")
        lay_mem.addWidget(self.lbl_resumen)
        layout.addWidget(tarjeta_mem)

        btn_volver = QPushButton("↻  Nueva Sesión (Conservar Memoria Aprendida)")
        btn_volver.setObjectName("BtnPrimario")
        btn_volver.setCursor(Qt.PointingHandCursor)
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

        self.lbl_titulo_sesion.setText(
            f"Sesión #{self.agente.sesiones_completadas + 1} • Perfil {nivel} ({edad} años)"
        )
        self.sub_tiempo.setText(f"Límite: {tiempo:.1f} min")
        self.sub_distancia.setText(f"Meta: {dist:.2f} km")
        self.sub_fc.setText(
            f"Segura: {self.agente.fc_obj_min:.0f}–{self.agente.fc_obj_max:.0f} bpm"
        )

        self.grafica.reiniciar(self.agente.fc_obj_min, self.agente.fc_obj_max)
        self.log_eventos.clear()
        self.log_eventos.append(
            f"▶ Sesión #{self.agente.sesiones_completadas + 1} iniciada | "
            f"Zona FC: [{self.agente.fc_obj_min:.1f}, {self.agente.fc_obj_max:.1f}] bpm | "
            f"Exploración ε={self.agente.epsilon:.2f}"
        )

        self.stack.setCurrentIndex(1)
        self.timer.start(350)

    def _iteracion_simulacion(self):
        percepcion = self.mundo.obtener_percepcion()
        decision = self.agente.decidir_accion(percepcion)
        nueva_percepcion = self.mundo.paso(decision["nuevo_ritmo"], dt_min=0.25)

        fc_actual = nueva_percepcion["fc"]
        self.historial_fc.append(fc_actual)
        self.grafica.agregar_punto(fc_actual, nueva_percepcion["pendiente"])

        # Actualizar tarjetas KPI
        self.lbl_tiempo.setText(f"{nueva_percepcion['tiempo']:.2f} min")
        self.lbl_distancia.setText(f"{nueva_percepcion['distancia']:.2f} km")
        self.lbl_fc.setText(f"{fc_actual:.1f} bpm")
        self.lbl_ritmo.setText(f"{nueva_percepcion['ritmo']:.2f} min/km")
        self.lbl_pendiente.setText(f"{nueva_percepcion['pendiente']:+.2f} %")

        # Color dinámico de FC según zona aeróbica
        if fc_actual > self.agente.fc_obj_max:
            self.lbl_fc.setStyleSheet("font-size: 20px; font-weight: 700; color: #f43f5e;")
        elif fc_actual < self.agente.fc_obj_min:
            self.lbl_fc.setStyleSheet("font-size: 20px; font-weight: 700; color: #38bdf8;")
        else:
            self.lbl_fc.setStyleSheet("font-size: 20px; font-weight: 700; color: #10b981;")

        progreso = int(min(100, (nueva_percepcion["distancia"] / self.agente.distancia_meta) * 100))
        self.barra_progreso.setValue(progreso)

        self.lbl_accion.setText(
            f"{decision['accion']} → {decision['nuevo_ritmo']:.2f} min/km (U={decision['utilidad']})"
        )
        self.lbl_modo.setText(decision["modo"])
        self.lbl_critico.setText(
            f"{decision['diagnostico_critico']} (err={decision['error_modelo']:+.1f})"
        )
        p = decision["pesos"]
        self.lbl_aprendizaje.setText(
            f"w_meta={p['meta']:.2f} | w_cardio={p['cardio']:.2f} | S_fc={decision['sensibilidad_fc']:.2f}"
        )

        self.log_eventos.append(
            f"[t={nueva_percepcion['tiempo']:05.2f}m] FC={fc_actual:5.1f} bpm | "
            f"Pend={nueva_percepcion['pendiente']:+5.1f}% | {decision['accion']} ({decision['modo']})"
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
        if cumplio:
            self.res_estado.setText("CUMPLIDA")
            self.res_estado.setStyleSheet("font-size: 20px; font-weight: 700; color: #10b981;")
            self.res_sub_estado.setText("Objetivo alcanzado")
        else:
            self.res_estado.setText("INCOMPLETA")
            self.res_estado.setStyleSheet("font-size: 20px; font-weight: 700; color: #f59e0b;")
            self.res_sub_estado.setText("Tiempo agotado")

        self.res_dist.setText(f"{percepcion['distancia']:.2f} km")
        self.res_sub_dist.setText(f"de {self.agente.distancia_meta:.2f} km meta")

        self.res_fc.setText(f"{fc_prom:.1f} bpm")
        self.res_sub_fc.setText(f"Límite: {self.agente.fc_obj_max:.1f} bpm")

        self.res_score.setText(f"{score:.1f} / 100")
        self.res_sub_score.setText("Evaluación del Crítico")

        texto = (
            f"• Total de sesiones entrenadas acumuladas: {self.agente.sesiones_completadas}\n"
            f"• Pesos de utilidad aprendidos: w_meta = {self.agente.pesos['meta']:.3f}  |  "
            f"w_cardio = {self.agente.pesos['cardio']:.3f}\n"
            f"• Sensibilidad cardíaca calibrada del corredor: {self.agente.sensibilidad_fc_aprendida:.3f} bpm/u\n"
            f"• Nueva tasa de exploración del Generador de Problemas (ε): {self.agente.epsilon:.3f}\n"
            f"• Tiempo total registrado: {percepcion['tiempo']:.2f} min / {self.agente.tiempo_meta:.2f} min"
        )
        self.lbl_resumen.setText(texto)
        self.stack.setCurrentIndex(2)