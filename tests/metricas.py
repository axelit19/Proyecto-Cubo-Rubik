import os
import random
import sys
import time
import tracemalloc


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from rubik.cube import Cube
from rubik.solve import Solver as BfsSolver
from rubik.solve_baseline import Solver as BaselineSolver
from rubik.optimize import optimize_moves

CUBOS_IMPOSIBLES = [
    "ORWOWGWYWGBGRGRBOBOWYGGBRRBYBRGOWOYGRYRBBGOOBYOYRYWYWW",
    "UUUUUUUUULLLFFFRRRBBBLLLFBFRRRBFBLLLFFFRRRBBBDDDDDDDDD",
    "UUBUUUUUULLLFFFRRRUBBLLLFFFRRRBBBLLLFFFRRRBBBDDDDDDDDD",
    "UUUUUUUUULLLFFFRRRBBBLLLFFFRRRBBBLLLFFFRRBRBBDDDDDDDDD",
    "UUUUUUUUULLLFFFRRRBBBLLFLFFRRRBBBLLLFFFRRRBBBDDDDDDDDD",
]

# Número de repeticiones por defecto: usar 1 para ejecutar cada cubo una vez (5 cubos total)
REPETICIONES = max(1, int(os.getenv("RUBIK_METRICAS_REPETICIONES", "1")))
NUMERO_CUBOS_VALIDOS = max(1, int(os.getenv("RUBIK_METRICAS_CUBOS_VALIDOS", "5")))
SEMILLA_METRICAS = int(os.getenv("RUBIK_METRICAS_SEED", "12345"))
MOVES = ["L", "R", "U", "D", "F", "B", "M", "E", "S"]
SOLVED_CUBE_STR = "OOOOOOOOOYYYWWWGGGBBBYYYWWWGGGBBBYYYWWWGGGBBBRRRRRRRRR"


def generar_cubo_valido_aleatorio(aleatorio):
    cubo = Cube(SOLVED_CUBE_STR)
    scramble_moves = " ".join(aleatorio.choices(MOVES, k=200))
    cubo.sequence(scramble_moves)
    return cubo.flat_str()


def generar_cubos_validos(cantidad=NUMERO_CUBOS_VALIDOS, semilla=SEMILLA_METRICAS):
    aleatorio = random.Random(semilla)
    return [generar_cubo_valido_aleatorio(aleatorio) for _ in range(cantidad)]


def medir_lote(solver_cls, aplicar_optimizacion=False):
    total_movimientos = 0
    total_cubos = 0
    peor_pico_bytes = 0
    tiempo_total = 0.0
    cubos_validos = generar_cubos_validos()

    for _ in range(REPETICIONES):
        for texto_cubo in cubos_validos:
            cubo = Cube(texto_cubo)
            solucionador = solver_cls(cubo)

            tracemalloc.start()
            inicio = time.perf_counter()
            solucionador.solve()
            movimientos = list(solucionador.moves)
            if aplicar_optimizacion:
                movimientos = optimize_moves(movimientos)
            duracion = time.perf_counter() - inicio
            _, pico_bytes = tracemalloc.get_traced_memory()
            tracemalloc.stop()

            if not cubo.is_solved():
                raise AssertionError("El cubo valido no quedo resuelto")

            if aplicar_optimizacion:
                verificacion = Cube(texto_cubo)
                verificacion.sequence(" ".join(movimientos))
                if not verificacion.is_solved():
                    raise AssertionError("La secuencia optimizada no resuelve el cubo")

            total_movimientos += len(movimientos)
            total_cubos += 1
            tiempo_total += duracion
            peor_pico_bytes = max(peor_pico_bytes, pico_bytes)

    return {
        "tiempo_total": tiempo_total,
        "tiempo_promedio": tiempo_total / total_cubos,
        "memoria_pico_kib": peor_pico_bytes / 1024.0,
        "movimientos_totales": total_movimientos,
        "cubos": total_cubos,
    }


def validar_cubos_imposibles(solver_cls):
    for texto_cubo in CUBOS_IMPOSIBLES:
        cubo = Cube(texto_cubo)
        solucionador = solver_cls(cubo)
        try:
            solucionador.solve()
        except Exception as error:
            if "Stuck in loop - unsolvable cube" not in str(error):
                raise AssertionError("El error no corresponde a un cubo imposible") from error
        else:
            raise AssertionError("Un cubo imposible fue resuelto por error")


def imprimir_reporte(nombre, metricas):
    print(f"{nombre}:")
    print(f"  Cubos procesados: {metricas['cubos']}")
    print(f"  Tiempo total: {metricas['tiempo_total'] * 1_000:.1f} milisegundos")
    print(f"  Tiempo promedio por cubo: {metricas['tiempo_promedio'] * 1_000:.1f} milisegundos")
    print(f"  Pico de memoria: {metricas['memoria_pico_kib']:.1f} KiB")
    print(f"  Movimientos totales: {metricas['movimientos_totales']}")


def medir_y_reportar(nombre, solver_cls, aplicar_optimizacion=False):
    print(f"Iniciando {nombre}...")
    metricas = medir_lote(solver_cls, aplicar_optimizacion=aplicar_optimizacion)
    imprimir_reporte(nombre, metricas)
    print(f"Terminado {nombre}")
    print()
    return metricas


def main():
    print("Metricas del solucionador Rubik")
    print(f"Repeticiones por conjunto: {REPETICIONES}")
    print(f"Semilla de cubos validos: {SEMILLA_METRICAS}")

    base = medir_y_reportar("Version base", BaselineSolver, aplicar_optimizacion=False)
    base_optimizada = medir_y_reportar("Version base optimizada", BaselineSolver, aplicar_optimizacion=True)
    bfs = medir_y_reportar("Version BFS", BfsSolver, aplicar_optimizacion=False)

    print("Comparacion:")
    print(f"  Ahorro de movimientos: {actual['movimientos_totales'] - optimizado['movimientos_totales']}")
    print(f"  Diferencia de tiempo total: {(optimizado['tiempo_total'] - actual['tiempo_total']) * 1_000:.1f} milisegundos")
    print(f"  Diferencia de memoria pico: {optimizado['memoria_pico_kib'] - actual['memoria_pico_kib']:.1f} KiB")
    print()
    validar_cubos_imposibles()
    print()
    if VALIDAR_IMPOSIBLES:
        validar_cubos_imposibles(BfsSolver)
        print()
        print("Correctitud:")
        print("  Los cubos validos se resuelven correctamente.")
        print("  Los cubos imposibles siguen detectandose como imposibles.")
    else:
        print("Correctitud:")
        print("  Validacion de cubos imposibles omitida para una corrida rapida.")


if __name__ == "__main__":
    main()