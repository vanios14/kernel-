# kernel-
proyecto de kernel sistema operativos 
class PCB:
    def __init__(self, pid, tam_mb, rafaga):
        self.pid = pid
        self.estado = "NUEVO"   # NUEVO, LISTO, EJECUTANDO, BLOQUEADO, TERMINADO
        self.tam_mb = tam_mb
        self.rafaga_total = rafaga
        self.rafaga_restante = rafaga
