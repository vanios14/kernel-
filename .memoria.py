class Memoria:
    TOTAL = 100
    def __init__(self):
        self.usada = 0
        self.asignaciones = {}          # pid -> MB

    def asignar(self, pcb):
        if pcb.tam_mb <= 0 or pcb.tam_mb > self.TOTAL - self.usada:
            raise MemoryError(f"Out of Memory: P{pcb.pid} pide {pcb.tam_mb} MB, libres {self.TOTAL - self.usada}")
        self.usada += pcb.tam_mb
        self.asignaciones[pcb.pid] = pcb.tam_mb

    def liberar(self, pid):
        self.usada -= self.asignaciones.pop(pid, 0)
