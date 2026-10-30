# ============================================================
# MÓDULO: semaforo.py
# ============================================================
"""semaforo.py - Semáforo binario y demostración de condición de carrera.

Se simula concurrencia con generadores: cada "proceso" cede el control
(yield) entre pasos de leer / calcular / escribir, así el planificador
intercala instrucciones y se reproduce la condición de carrera de forma
determinista (ideal para la bitácora de pruebas).
"""
from collections import deque



class SemaforoBinario:
    def __init__(self):
        self.valor = 1            # 1 = libre, 0 = ocupado
        self.espera = deque()     # cola de espera específica

    def wait(self, pcb):
        """Intenta entrar. True si entra; False si queda bloqueado en cola."""
        if self.valor == 1:
            self.valor = 0
            return True
        pcb.estado = BLOQUEADO
        self.espera.append(pcb)
        return False

    def signal(self):
        """Sale de la sección crítica. Si hay esperando, le cede el acceso."""
        if self.espera:
            siguiente = self.espera.popleft()
            siguiente.estado = LISTO      # el semáforo sigue en 0: pasa directo
            return siguiente
        self.valor = 1
        return None


class VariableCompartida:
    """Región crítica: la variable global compartida."""
    def __init__(self):
        self.valor = 0


def _tarea(pcb, comp, sem):
    """Cada tarea hace: valor = valor + 1 (en 3 pasos no atómicos)."""
    if sem is not None:
        if not sem.wait(pcb):
            print(f"  {pcb.pid}: wait() -> sección crítica OCUPADA, "
                  f"pasa a la cola de espera")
            while pcb.estado == BLOQUEADO:   # espera hasta que le hagan signal()
                yield
        print(f"  {pcb.pid}: wait() -> ENTRA a la sección crítica")
    pcb.estado = EJECUTANDO
    local = comp.valor
    print(f"  {pcb.pid}: LEE valor = {local}")
    yield
    local += 1
    print(f"  {pcb.pid}: CALCULA {local}")
    yield
    comp.valor = local
    print(f"  {pcb.pid}: ESCRIBE valor = {local}")
    yield
    if sem is not None:
        despertado = sem.signal()
        extra = f" (despierta a {despertado.pid})" if despertado else ""
        print(f"  {pcb.pid}: signal() -> sale de la sección crítica{extra}")
    pcb.estado = TERMINADO


def demo_condicion_carrera(usar_semaforo, n_procesos=3):
    """Ejecuta n procesos que incrementan la variable compartida en 1."""
    titulo = "CON semáforo" if usar_semaforo else "SIN semáforo"
    print(f"\n=== Condición de carrera {titulo} ({n_procesos} procesos) ===")
    comp = VariableCompartida()
    sem = SemaforoBinario() if usar_semaforo else None
    pcbs = [PCB(f"H{i + 1}", 0, 0) for i in range(n_procesos)]
    tareas = [_tarea(p, comp, sem) for p in pcbs]
    while tareas:                      # planificación intercalada (1 paso c/u)
        for t in list(tareas):
            try:
                next(t)
            except StopIteration:
                tareas.remove(t)
    esperado = n_procesos
    print(f"\n  Valor final = {comp.valor} | Valor esperado = {esperado}")
    if comp.valor == esperado:
        print("  RESULTADO: CORRECTO. La exclusión mutua evitó la condición de carrera.")
    else:
        print(f"  RESULTADO: INCORRECTO. Se perdieron {esperado - comp.valor} "
              f"actualizaciones (condición de carrera).")
