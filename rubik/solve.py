"""Solucionador del cubo de Rubik.

La optimización principal de este archivo está en `_bfs()`: en lugar de
probar secuencias largas sobre el cubo completo, se resuelve cada pieza por
fases usando una búsqueda en anchura (BFS) sobre un estado ligero. Ese estado
solo guarda la posición y los colores de las piezas relevantes, lo que reduce
el costo de explorar movimientos y evita recalcular todo el cubo en cada paso.
"""

from collections import deque
from typing import Any

from rubik import cube
from rubik.maths import Point

DEBUG = False

FACE_MOVES = (
    "U", "Ui", "R", "Ri", "F", "Fi",
    "L", "Li", "D", "Di", "B", "Bi",
)

INVERSE_MOVE = {
    "U": "Ui", "Ui": "U",
    "R": "Ri", "Ri": "R",
    "F": "Fi", "Fi": "F",
    "L": "Li", "Li": "L",
    "D": "Di", "Di": "D",
    "B": "Bi", "Bi": "B",
}

MOVE_TABLE = {
    "L": ("x", -1, cube.ROT_YZ_CC),
    "Li": ("x", -1, cube.ROT_YZ_CW),
    "R": ("x", 1, cube.ROT_YZ_CW),
    "Ri": ("x", 1, cube.ROT_YZ_CC),
    "U": ("y", 1, cube.ROT_XZ_CW),
    "Ui": ("y", 1, cube.ROT_XZ_CC),
    "D": ("y", -1, cube.ROT_XZ_CC),
    "Di": ("y", -1, cube.ROT_XZ_CW),
    "F": ("z", 1, cube.ROT_XY_CW),
    "Fi": ("z", 1, cube.ROT_XY_CC),
    "B": ("z", -1, cube.ROT_XY_CC),
    "Bi": ("z", -1, cube.ROT_XY_CW),
}


class Solver:

    # El solver trabaja por fases: primero fija la cruz, luego esquinas,
    # aristas del medio y finalmente las piezas de la cara opuesta.
    # En cada fase se llama a BFS sobre un subconjunto pequeño del estado,
    # lo que permite encontrar secuencias cortas sin explorar movimientos
    # innecesarios para todo el cubo.

    def __init__(self, c):
        self.cube = c
        self.colors = c.colors()
        self.moves = []
        self.color_to_axis = {
            self.cube.left_color(): cube.LEFT,
            self.cube.right_color(): cube.RIGHT,
            self.cube.up_color(): cube.UP,
            self.cube.down_color(): cube.DOWN,
            self.cube.front_color(): cube.FRONT,
            self.cube.back_color(): cube.BACK,
        }

    def solve(self):
        if DEBUG:
            print(self.cube)

        protected = []
        for signature in self._cross_signatures():
            self._solve_piece(protected, signature, max_depth=self._phase_max_depth(0))
            protected.append(signature)

        for signature in self._front_corner_signatures():
            self._solve_piece(protected, signature, max_depth=self._phase_max_depth(1))
            protected.append(signature)

        for signature in self._middle_edge_signatures():
            self._solve_piece(protected, signature, max_depth=self._phase_max_depth(2))
            protected.append(signature)

        for signature in self._back_edge_signatures():
            self._solve_piece(protected, signature, max_depth=self._phase_max_depth(3))
            protected.append(signature)

        for signature in self._back_corner_signatures():
            self._solve_piece(protected, signature, max_depth=self._phase_max_depth(4))
            protected.append(signature)

        if DEBUG:
            print("Solved\n", self.cube)

    def move(self, move_str):
        self.moves.extend(move_str.split())
        self.cube.sequence(move_str)

    def _phase_max_depth(self, phase_index):
        return (8, 10, 12, 12, 14)[phase_index]

    def _cross_signatures(self):
        return [
            tuple(sorted((self.cube.front_color(), self.cube.left_color()))),
            tuple(sorted((self.cube.front_color(), self.cube.right_color()))),
            tuple(sorted((self.cube.front_color(), self.cube.up_color()))),
            tuple(sorted((self.cube.front_color(), self.cube.down_color()))),
        ]

    def _front_corner_signatures(self):
        return [
            tuple(sorted((self.cube.front_color(), self.cube.left_color(), self.cube.down_color()))),
            tuple(sorted((self.cube.front_color(), self.cube.left_color(), self.cube.up_color()))),
            tuple(sorted((self.cube.front_color(), self.cube.right_color(), self.cube.down_color()))),
            tuple(sorted((self.cube.front_color(), self.cube.right_color(), self.cube.up_color()))),
        ]

    def _middle_edge_signatures(self):
        return [
            tuple(sorted((self.cube.left_color(), self.cube.down_color()))),
            tuple(sorted((self.cube.left_color(), self.cube.up_color()))),
            tuple(sorted((self.cube.right_color(), self.cube.down_color()))),
            tuple(sorted((self.cube.right_color(), self.cube.up_color()))),
        ]

    def _back_edge_signatures(self):
        return [
            tuple(sorted((self.cube.back_color(), self.cube.left_color()))),
            tuple(sorted((self.cube.back_color(), self.cube.up_color()))),
            tuple(sorted((self.cube.back_color(), self.cube.right_color()))),
            tuple(sorted((self.cube.back_color(), self.cube.down_color()))),
        ]

    def _back_corner_signatures(self):
        return [
            tuple(sorted((self.cube.back_color(), self.cube.left_color(), self.cube.down_color()))),
            tuple(sorted((self.cube.back_color(), self.cube.left_color(), self.cube.up_color()))),
            tuple(sorted((self.cube.back_color(), self.cube.right_color(), self.cube.down_color()))),
            tuple(sorted((self.cube.back_color(), self.cube.right_color(), self.cube.up_color()))),
        ]

    def _solve_piece(self, protected_signatures, target_signature, max_depth):
        # Aquí se prepara el problema que resolverá BFS: se congelan las piezas
        # ya protegidas y la pieza objetivo, y después se busca la secuencia
        # mínima dentro de ese espacio reducido.
        tracked_signatures = list(protected_signatures) + [target_signature]
        goal_state = []
        for signature in tracked_signatures:
            if signature == target_signature:
                # store goal as lightweight key (pos tuple, colors tuple)
                p = self._goal_piece(signature)
                goal_state.append((tuple(p.pos), tuple(p.colors)))
            else:
                p = self.cube.find_piece(*signature)
                goal_state.append((tuple(p.pos), tuple(p.colors)))

        start_state = self._snapshot_state(tracked_signatures)
        sequence = self._bfs(start_state, goal_state, tracked_signatures, max_depth)
        if sequence is None:
            raise Exception("Stuck in loop - unsolvable cube\n" + str(self.cube))

        self.move(" ".join(sequence))

    def _bfs(self, start_state, goal_state, tracked_signatures, max_depth):
        # BFS explora primero las secuencias más cortas, así que sirve para
        # encontrar soluciones eficientes por fase. Además, trabajamos con un
        # estado ligero: ((x, y, z), (c0, c1, c2)) por pieza rastreada.
        start_key = self._state_key(start_state)
        goal_key = self._state_key(goal_state)
        if start_key == goal_key:
            return []

        queue: deque[tuple[Any, list[str], Any, str | None, str | None]] = deque(
            [(start_state, [], start_key, None, None)]
        )
        seen = {start_key}

        while queue:
            state, sequence, state_key, last_move, previous_move = queue.popleft()
            if state_key == goal_key:
                return sequence

            if len(sequence) >= max_depth:
                continue

            for move in FACE_MOVES:
                if last_move and INVERSE_MOVE[last_move] == move:
                    continue
                if (
                    previous_move is not None
                    and last_move is not None
                    and previous_move[0] == last_move[0] == move[0]
                ):
                    continue
                if not self._move_affects_state(state, move):
                    continue

                next_state = self._apply_move_to_state(state, move)
                next_key = self._state_key(next_state)
                if next_key in seen:
                    continue

                seen.add(next_key)
                queue.append((next_state, sequence + [move], next_key, move, last_move))

        return None

    def _snapshot_state(self, signatures):
        # Genera la representación compacta que consume BFS.
        result = []
        for signature in signatures:
            p = self.cube.find_piece(*signature)
            result.append((tuple(p.pos), tuple(p.colors)))
        return tuple(result)

    def _clone_piece(self, piece):
        # Conservado por compatibilidad; devuelve la misma forma compacta.
        return (tuple(piece.pos), tuple(piece.colors))

    def _state_key(self, state):
        # Si el estado ya está compactado, se usa directamente como llave.
        try:
            first = state[0]
        except Exception:
            return tuple(state)
        # Detecta si las entradas ya son (pos_tuple, colors_tuple).
        if isinstance(first, tuple) and len(first) == 2 and isinstance(first[0], tuple):
            return tuple(state)
        # En otro caso, se asume que contiene objetos tipo Piece.
        return tuple((tuple(piece.pos), tuple(piece.colors)) for piece in state)

    def _move_affects_state(self, state, move):
        axis_name, axis_value, _ = MOVE_TABLE[move]
        # Si ningún elemento del estado queda sobre la cara afectada, ese
        # movimiento no cambia la fase actual y se puede podar.
        axis_index = {'x': 0, 'y': 1, 'z': 2}[axis_name]
        for pos, colors in state:
            if pos[axis_index] == axis_value:
                return True
        return False

    def _apply_move_to_state(self, state, move):
        # Aplica el movimiento sobre el estado compacto, sin mover todo el cubo.
        axis_name, axis_value, matrix = MOVE_TABLE[move]
        axis_index = {'x': 0, 'y': 1, 'z': 2}[axis_name]
        next_state = []
        for pos_tuple, colors in state:
            before = Point(pos_tuple)
            if pos_tuple[axis_index] == axis_value:
                after = matrix * before
                # compute rot vector
                rot = after - before
                if not any(rot):
                    next_state.append((tuple(after), colors))
                    continue
                if rot.count(0) == 2:
                    rot = Point(rot.x + (matrix * rot).x,
                                rot.y + (matrix * rot).y,
                                rot.z + (matrix * rot).z)
                # find indices to swap
                idxs = [i for i, v in enumerate(rot) if v != 0]
                if len(idxs) == 1:
                    # should not happen, but keep colors same
                    next_colors = colors
                else:
                    i, j = idxs[0], idxs[1]
                    lst = list(colors)
                    lst[i], lst[j] = lst[j], lst[i]
                    next_colors = tuple(lst)
                next_state.append((tuple(after), next_colors))
            else:
                next_state.append((pos_tuple, colors))
        return tuple(next_state)

    def _goal_piece(self, signature):
        target_pos = Point(0, 0, 0)
        for color in signature:
            target_pos += self.color_to_axis[color]

        expected_colors = [None, None, None]
        if target_pos.x != 0:
            expected_colors[0] = self.cube.right_color() if target_pos.x > 0 else self.cube.left_color()
        if target_pos.y != 0:
            expected_colors[1] = self.cube.up_color() if target_pos.y > 0 else self.cube.down_color()
        if target_pos.z != 0:
            expected_colors[2] = self.cube.front_color() if target_pos.z > 0 else self.cube.back_color()

        return cube.Piece(pos=target_pos, colors=expected_colors)


if __name__ == '__main__':
    DEBUG = True
    c = cube.Cube("DLURRDFFUBBLDDRBRBLDLRBFRUULFBDDUFBRBBRFUDFLUDLUULFLFR")
    print("Solving:\n", c)
    orig = cube.Cube(c)
    solver = Solver(c)
    solver.solve()

    print(f"{len(solver.moves)} moves: {' '.join(solver.moves)}")

    check = cube.Cube(orig)
    check.sequence(" ".join(solver.moves))
    assert check.is_solved()