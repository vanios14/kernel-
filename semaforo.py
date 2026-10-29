from collections import deque

class SemaforoBinario:
    def __init__(self):
        self.valor = 1
        self.espera = deque()

    def wait(self, pcb):
        if self.valor == 1:
            self.valor = 0
            return True              # entra a la sección crítica
        pcb.estado = "BLOQUEADO"
        self.espera.append(pcb)
        return False

    def signal(self):
        if self.espera:
            sig = self.espera.popleft()   # despierta al siguiente
            sig.estado = "LISTO"
            return sig
        self.valor = 1
