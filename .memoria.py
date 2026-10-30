# ============================================================
# MÓDULO: memoria.py
# ============================================================
"""memoria.py - Administrador de Memoria (RAM de 100 MB).

Estrategia: Asignación CONTIGUA DINÁMICA con First-Fit.
La RAM es una lista de bloques (inicio, tamaño, dueño). Al crear un
proceso se busca el primer hueco libre suficientemente grande y se
parte. Al terminar, el bloque se libera y se fusiona con huecos vecinos.
Si no hay espacio se lanza OutOfMemoryError y el proceso es rechazado.
"""


class OutOfMemoryError(Exception):
    """Error de desbordamiento de memoria (Out of Memory)."""


class Memoria:
    TOTAL_MB = 100

    def __init__(self):
        # Un solo bloque libre que abarca toda la RAM
        self.bloques = [{"inicio": 0, "tam": self.TOTAL_MB, "pid": None}]

    def libre_total(self):
        return sum(b["tam"] for b in self.bloques if b["pid"] is None)

    def usada(self):
        return self.TOTAL_MB - self.libre_total()

    def asignar(self, pid, tam_mb):
        """Reserva tam_mb MB para el proceso pid (First-Fit)."""
        if tam_mb <= 0:
            raise ValueError("El tamaño debe ser mayor que 0 MB.")
        for i, b in enumerate(self.bloques):
            if b["pid"] is None and b["tam"] >= tam_mb:
                resto = b["tam"] - tam_mb
                b["tam"], b["pid"] = tam_mb, pid
                if resto > 0:  # el sobrante queda como un nuevo hueco libre
                    self.bloques.insert(i + 1, {"inicio": b["inicio"] + tam_mb,
                                                "tam": resto, "pid": None})
                return b["inicio"]
        # Si llegamos aquí no hubo hueco: distinguimos la causa para el reporte
        if tam_mb > self.libre_total():
            causa = f"memoria insuficiente (libres {self.libre_total()} MB)"
        else:
            causa = (f"fragmentación externa (libres {self.libre_total()} MB "
                     f"pero no contiguos)")
        raise OutOfMemoryError(f"Out of Memory: P{pid} solicita {tam_mb} MB -> {causa}")

    def liberar(self, pid):
        """Libera la memoria del proceso y fusiona huecos adyacentes."""
        for b in self.bloques:
            if b["pid"] == pid:
                b["pid"] = None
        # Coalescencia: unir huecos libres consecutivos
        i = 0
        while i < len(self.bloques) - 1:
            a, b = self.bloques[i], self.bloques[i + 1]
            if a["pid"] is None and b["pid"] is None:
                a["tam"] += b["tam"]
                del self.bloques[i + 1]
            else:
                i += 1

    def mostrar(self):
        """Imprime el mapa de memoria con una barra visual."""
        print(f"\n--- Mapa de RAM ({self.usada()}/{self.TOTAL_MB} MB usados) ---")
        for b in self.bloques:
            dueno = f"P{b['pid']}" if b["pid"] is not None else "LIBRE"
            print(f"  [{b['inicio']:>3} - {b['inicio'] + b['tam'] - 1:>3}] "
                  f"{b['tam']:>3} MB  {dueno}")
        barra = ""
        for b in self.bloques:
            simbolo = "." if b["pid"] is None else str(b["pid"] % 10)
            barra += simbolo * max(1, round(b["tam"] / 2))
        print(f"  |{barra}|  (cada caracter ~2 MB, '.' = libre)")
