import time
from rubik.cube import Cube
from rubik.solve import Solver

# Elegir un cubo de prueba (uno de los del test)
CUBE = "DLURRDFFUBBLDDRBRBLDLRBFRUULFBDDUFBRBBRFUDFLUDLUULFLFR"

if __name__ == '__main__':
    c = Cube(CUBE)
    orig = Cube(c)
    print("Estado inicial:\n", c)
    solver = Solver(c, use_kociemba=True)
    t0 = time.time()
    try:
        solver.solve()
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)
    t1 = time.time()
    print(f"Tiempo: {t1-t0:.3f}s")
    print(f"Movimientos ({len(solver.moves)}): {' '.join(solver.moves)}")
    check = Cube(orig)
    check.sequence(' '.join(solver.moves))
    print("¿resuelto?:", check.is_solved())

