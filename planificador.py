# ============================================================
# MÓDULO: planificador.py
# ============================================================
"""planificador.py - Planificador de procesos Round Robin (quantum = 3)."""
from collections import deque


QUANTUM = 3  # Quantum fijo exigido por el enunciado


class Planificador:
    def __init__(self, memoria):
        self.memoria = memoria
        self.procesos = {}          # pid -> PCB (todos, incluso terminados)
        self.cola = deque()         # cola de listos (FIFO)
        self.reloj = 0              # reloj global simulado
        self._sig_pid = 1
        self.al_terminar = None     # callback opcional (liberar recursos)

    # ------------------------------------------------------------------
    def crear_proceso(self, tam_mb, rafaga):
        """Crea un PCB y valida la RAM. Si no cabe, lo rechaza (OOM)."""
        pid = self._sig_pid
        self._sig_pid += 1
        pcb = PCB(pid, tam_mb, rafaga)
        pcb.llegada = self.reloj
        self.procesos[pid] = pcb
        try:
            inicio = self.memoria.asignar(pid, tam_mb)
        except OutOfMemoryError:
            pcb.estado = RECHAZADO
            raise
        pcb.estado = LISTO
        self.cola.append(pcb)
        print(f"  [OK] P{pid} creado: {tam_mb} MB (dir {inicio}), ráfaga {rafaga}")
        return pcb

    # ------------------------------------------------------------------
    def ejecutar(self):
        """Ejecuta Round Robin hasta vaciar la cola de listos."""
        if not self.cola:
            print("  La cola de listos está vacía. Crea procesos primero.")
            return
        print(f"\n=== Round Robin (quantum = {QUANTUM}) ===")
        gantt = []
        terminados = []
        while self.cola:
            p = self.cola.popleft()
            p.estado = EJECUTANDO
            tiempo = min(QUANTUM, p.rafaga_restante)
            inicio = self.reloj
            p.rafaga_restante -= tiempo
            self.reloj += tiempo
            gantt.append((p.pid, inicio, self.reloj))
            print(f"  [t={inicio:>3}->{self.reloj:>3}] P{p.pid} ejecuta {tiempo} u. "
                  f"| restante: {p.rafaga_restante}")
            if p.rafaga_restante == 0:
                p.fin = self.reloj
                print(f"      P{p.pid} TERMINÓ; se libera su memoria.")
                self._finalizar(p, TERMINADO)
                terminados.append(p)
            else:
                # Quantum agotado: cambio de contexto simulado
                p.estado = LISTO
                self.cola.append(p)
                print(f"      Quantum agotado -> CAMBIO DE CONTEXTO: "
                      f"P{p.pid} vuelve al final de la cola")
        self._mostrar_gantt(gantt)
        self._mostrar_metricas(terminados)
        bloqueados = [p.pid for p in self.procesos.values() if p.estado == BLOQUEADO]
        if bloqueados:
            print(f"  Aviso: siguen BLOQUEADOS (no planificables): "
                  f"{', '.join('P' + str(b) for b in bloqueados)}")

    # ------------------------------------------------------------------
    def _finalizar(self, pcb, estado):
        """Libera memoria, marca estado final y avisa al gestor de recursos."""
        self.memoria.liberar(pcb.pid)
        pcb.estado = estado
        if self.al_terminar:
            self.al_terminar(pcb.pid)

    def bloquear(self, pid):
        """Saca un proceso de la cola de listos y lo marca BLOQUEADO."""
        pcb = self.procesos[pid]
        if pcb in self.cola:
            self.cola.remove(pcb)
        pcb.estado = BLOQUEADO

    def reinsertar(self, pid):
        """Devuelve un proceso desbloqueado a la cola de listos."""
        pcb = self.procesos[pid]
        pcb.estado = LISTO
        self.cola.append(pcb)

    def abortar(self, pid):
        """Mata un proceso: lo saca de la cola, libera RAM y recursos."""
        pcb = self.procesos[pid]
        if pcb in self.cola:
            self.cola.remove(pcb)
        self._finalizar(pcb, ABORTADO)

    def activos(self):
        """PIDs de procesos vivos (listos, ejecutando o bloqueados)."""
        return [p.pid for p in self.procesos.values()
                if p.estado in (LISTO, EJECUTANDO, BLOQUEADO)]

    # ------------------------------------------------------------------
    def mostrar_procesos(self):
        print("\n--- Tabla de procesos (PCB) ---")
        if not self.procesos:
            print("  (sin procesos)")
            return
        print(f"  {'PID':>4} {'ESTADO':<11} {'MEM(MB)':>8} {'TOTAL':>6} {'RESTANTE':>9}")
        for p in self.procesos.values():
            print(f"  {p.pid:>4} {p.estado:<11} {p.tam_mb:>8} "
                  f"{p.rafaga_total:>6} {p.rafaga_restante:>9}")
        cola = " -> ".join(f"P{p.pid}" for p in self.cola) or "(vacía)"
        print(f"  Cola de listos: {cola}")

    @staticmethod
    def _mostrar_gantt(gantt):
        print("\n  Diagrama de Gantt:")
        linea1 = "  |"
        linea2 = "  0"
        for pid, ini, fin in gantt:
            ancho = max(4, (fin - ini) * 2)
            linea1 += f"P{pid}".center(ancho) + "|"
            linea2 += str(fin).rjust(ancho + 1)
        print(linea1)
        print(linea2)

    @staticmethod
    def _mostrar_metricas(terminados):
        """Tiempo de retorno = fin - llegada; espera = retorno - ráfaga total."""
        if not terminados:
            return
        print("\n  Métricas (tiempo de espera = fin - llegada - ráfaga total):")
        print(f"  {'PID':>4} {'LLEGADA':>8} {'RÁFAGA':>7} {'FIN':>5} {'ESPERA':>7} {'RETORNO':>8}")
        esperas, retornos = [], []
        for p in terminados:
            retorno = p.fin - p.llegada
            espera = retorno - p.rafaga_total
            esperas.append(espera)
            retornos.append(retorno)
            print(f"  {p.pid:>4} {p.llegada:>8} {p.rafaga_total:>7} {p.fin:>5} "
                  f"{espera:>7} {retorno:>8}")
        print(f"  Espera promedio: {sum(esperas) / len(esperas):.2f} | "
              f"Retorno promedio: {sum(retornos) / len(retornos):.2f}")
