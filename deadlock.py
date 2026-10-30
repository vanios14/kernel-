# ============================================================
# MÓDULO: deadlock.py
# ============================================================
"""deadlock.py - Recursos exclusivos, interbloqueo, detección y resolución."""


class GestorRecursos:
    """Dos recursos exclusivos (1 y 2).
    dueno[r]  -> pid que retiene el recurso r (o None)
    espera[p] -> recurso que el proceso p está solicitando y no obtuvo
    """

    def __init__(self):
        self.dueno = {1: None, 2: None}
        self.espera = {}

    def solicitar(self, pid, recurso):
        """True si se concede; False si el proceso queda esperando."""
        if self.dueno[recurso] is None:
            self.dueno[recurso] = pid
            return True
        if self.dueno[recurso] == pid:
            return True
        self.espera[pid] = recurso
        return False

    def hay_recursos_en_uso(self):
        return any(v is not None for v in self.dueno.values()) or bool(self.espera)

    def forzar_deadlock(self, pid_a, pid_b):
        """Crea la espera circular exigida:
        A retiene R1 y pide R2; B retiene R2 y pide R1."""
        print(f"  P{pid_a} solicita Recurso 1 -> "
              f"{'CONCEDIDO' if self.solicitar(pid_a, 1) else 'espera'}")
        print(f"  P{pid_b} solicita Recurso 2 -> "
              f"{'CONCEDIDO' if self.solicitar(pid_b, 2) else 'espera'}")
        print(f"  P{pid_a} solicita Recurso 2 -> "
              f"{'CONCEDIDO' if self.solicitar(pid_a, 2) else 'DENEGADO (lo tiene P' + str(pid_b) + '), se bloquea'}")
        print(f"  P{pid_b} solicita Recurso 1 -> "
              f"{'CONCEDIDO' if self.solicitar(pid_b, 1) else 'DENEGADO (lo tiene P' + str(pid_a) + '), se bloquea'}")

    def detectar(self):
        """Busca un ciclo en el grafo de espera. Devuelve la lista de PIDs
        involucrados o None si no hay deadlock."""
        for inicio in self.espera:
            visitados = [inicio]
            actual = inicio
            while actual in self.espera:
                retenedor = self.dueno[self.espera[actual]]
                if retenedor is None:
                    break
                if retenedor == inicio:
                    return visitados            # ciclo cerrado: DEADLOCK
                if retenedor in visitados:
                    break
                visitados.append(retenedor)
                actual = retenedor
        return None

    def liberar_proceso(self, pid):
        """Libera todo lo que tiene pid y cede los recursos a quien espera.
        Devuelve la lista de PIDs que quedaron desbloqueados."""
        self.espera.pop(pid, None)
        desbloqueados = []
        for r in (1, 2):
            if self.dueno[r] == pid:
                self.dueno[r] = None
                for esperando, rec in list(self.espera.items()):
                    if rec == r:
                        self.dueno[r] = esperando
                        del self.espera[esperando]
                        desbloqueados.append(esperando)
                        break
        return desbloqueados

    def mostrar(self):
        print("\n--- Estado de recursos ---")
        for r in (1, 2):
            d = self.dueno[r]
            print(f"  Recurso {r}: {'libre' if d is None else 'retenido por P' + str(d)}")
        for p, r in self.espera.items():
            print(f"  P{p} espera el Recurso {r}")
