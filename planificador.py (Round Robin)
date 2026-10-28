from collections import deque
QUANTUM = 3

class Planificador:
    def __init__(self, memoria):
        self.cola = deque()
        self.memoria = memoria
        self.reloj = 0

    def ejecutar(self):
        while self.cola:
            p = self.cola.popleft()
            p.estado = "EJECUTANDO"
            t = min(QUANTUM, p.rafaga_restante)
            p.rafaga_restante -= t
            self.reloj += t
            print(f"[t={self.reloj}] P{p.pid} ejecutó {t} u. Restante: {p.rafaga_restante}")
            if p.rafaga_restante == 0:
                p.estado = "TERMINADO"
                self.memoria.liberar(p.pid)
            else:
                p.estado = "LISTO"
                print(f"  Cambio de contexto: P{p.pid} vuelve a la cola")
                self.cola.append(p)
