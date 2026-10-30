# ============================================================
# MÓDULO: main.py
# ============================================================
"""main.py - Simulador de Funciones del Kernel (CLI).

Sistemas Operativos I - Universidad Mariano Gálvez de Guatemala.
Une los 5 componentes: procesos/Round Robin, memoria, semáforo,
deadlock y el menú interactivo con validación de entradas.
"""
import random


MAX_RAFAGA = 1000


def leer_entero(mensaje, minimo, maximo):
    """Lee un entero validado. Repite hasta que sea válido (robustez)."""
    while True:
        texto = input(mensaje).strip()
        try:
            valor = int(texto)
        except ValueError:
            print(f"  Entrada inválida: '{texto}' no es un número entero.")
            continue
        if valor < minimo or valor > maximo:
            print(f"  Fuera de rango: debe estar entre {minimo} y {maximo}.")
            continue
        return valor


def menu():
    print("\n" + "=" * 52)
    print("   SIMULADOR DEL KERNEL - SISTEMAS OPERATIVOS I")
    print("=" * 52)
    print(" 1. Crear proceso")
    print(" 2. Crear procesos aleatorios (prueba de estrés)")
    print(" 3. Ver tabla de procesos y cola de listos")
    print(" 4. Ver mapa de memoria RAM")
    print(f" 5. Ejecutar Round Robin (q = {QUANTUM})")
    print(" 6. Condición de carrera SIN semáforo")
    print(" 7. Condición de carrera CON semáforo")
    print(" 8. Forzar DEADLOCK")
    print(" 9. Detectar deadlock / ver recursos")
    print("10. Abortar un proceso (resolver deadlock)")
    print(" 0. Salir")


def main():
    memoria = Memoria()
    plan = Planificador(memoria)
    recursos = GestorRecursos()

    def liberar_recursos(pid):
        """Cuando un proceso termina o es abortado, libera sus recursos
        y reinserta en la cola de listos a quien estaba bloqueado por ellos."""
        for desbloqueado in recursos.liberar_proceso(pid):
            print(f"  P{desbloqueado} obtuvo el recurso que esperaba -> "
                  f"pasa a LISTO")
            plan.reinsertar(desbloqueado)

    plan.al_terminar = liberar_recursos

    while True:
        menu()
        try:
            opcion = input("Opción: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break

        try:
            if opcion == "1":
                tam = leer_entero(f"  Tamaño en memoria (1-{memoria.TOTAL_MB} MB): ",
                                  1, 10 ** 6)  # permite probar el rechazo OOM
                rafaga = leer_entero(f"  Ráfaga de CPU (1-{MAX_RAFAGA}): ", 1, MAX_RAFAGA)
                try:
                    plan.crear_proceso(tam, rafaga)
                except OutOfMemoryError as e:
                    print(f"  [ERROR] {e}  -> proceso RECHAZADO")

            elif opcion == "2":
                n = leer_entero("  ¿Cuántos procesos aleatorios? (1-50): ", 1, 50)
                for _ in range(n):
                    tam = random.randint(5, 40)
                    rafaga = random.randint(1, 15)
                    try:
                        plan.crear_proceso(tam, rafaga)
                    except OutOfMemoryError as e:
                        print(f"  [ERROR] {e}  -> proceso RECHAZADO")

            elif opcion == "3":
                plan.mostrar_procesos()

            elif opcion == "4":
                memoria.mostrar()

            elif opcion == "5":
                plan.ejecutar()

            elif opcion == "6":
                demo_condicion_carrera(usar_semaforo=False)

            elif opcion == "7":
                demo_condicion_carrera(usar_semaforo=True)

            elif opcion == "8":
                forzar_deadlock(plan, recursos)

            elif opcion == "9":
                recursos.mostrar()
                ciclo = recursos.detectar()
                if ciclo:
                    cadena = " -> ".join(f"P{p}" for p in ciclo) + f" -> P{ciclo[0]}"
                    print(f"\n  *** ¡ALERTA! DEADLOCK DETECTADO: {cadena} ***")
                    print("  Use la opción 10 para abortar uno de los procesos.")
                else:
                    print("\n  No hay deadlock.")

            elif opcion == "10":
                abortar(plan, recursos)

            elif opcion == "0":
                print("Fin de la simulación.")
                break
            else:
                print(f"  Opción '{opcion}' no válida. Elige un número del menú.")
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo...")
            break


def pedir_pid_activo(plan, mensaje, excluir=None):
    """Pide un PID y valida que exista y siga vivo."""
    activos = plan.activos()
    pid = leer_entero(mensaje, 1, 10 ** 9)
    if pid not in plan.procesos:
        print(f"  El proceso P{pid} no existe.")
        return None
    if pid not in activos:
        print(f"  P{pid} ya no está activo (estado {plan.procesos[pid].estado}).")
        return None
    if pid == excluir:
        print("  Debe ser un proceso distinto al anterior.")
        return None
    return pid


def forzar_deadlock(plan, recursos):
    if recursos.hay_recursos_en_uso():
        print("  Ya hay recursos en uso/espera. Resuelve el deadlock actual primero.")
        return
    if len(plan.activos()) < 2:
        print("  Se necesitan al menos 2 procesos activos. Crea más con la opción 1 o 2.")
        return
    plan.mostrar_procesos()
    a = pedir_pid_activo(plan, "  PID del Proceso A: ")
    if a is None:
        return
    b = pedir_pid_activo(plan, "  PID del Proceso B: ", excluir=a)
    if b is None:
        return
    print("\n=== Forzando espera circular ===")
    recursos.forzar_deadlock(a, b)
    plan.bloquear(a)
    plan.bloquear(b)
    print("\n  P{} y P{} quedaron BLOQUEADOS.".format(a, b))
    print("  Use la opción 9 para detectar el deadlock.")


def abortar(plan, recursos):
    activos = plan.activos()
    if not activos:
        print("  No hay procesos activos para abortar.")
        return
    ciclo = recursos.detectar()
    if ciclo:
        print("  Procesos en deadlock: " + ", ".join(f"P{p}" for p in ciclo))
    pid = pedir_pid_activo(plan, "  PID del proceso a abortar: ")
    if pid is None:
        return
    print(f"\n  Abortando P{pid}: se libera su memoria y sus recursos...")
    plan.abortar(pid)
    if ciclo and pid in ciclo and recursos.detectar() is None:
        print("  Deadlock RESUELTO: el ciclo de espera se rompió.")
    print("  Ejecuta Round Robin (opción 5) para que el proceso restante termine.")


if __name__ == "__main__":
    main()
