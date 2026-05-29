from rubik.cube import BACK, DOWN, FRONT, LEFT, RIGHT, UP


def solve_cube(cube_obj):
    """Resuelve el cubo usando kociemba y devuelve una lista de movimientos.

    Esta lógica queda aislada fuera de `solve.py` para no ensuciar el flujo
    principal del solucionador BFS.
    """
    import kociemba

    color_to_face = {
        cube_obj.up_color(): 'U',
        cube_obj.right_color(): 'R',
        cube_obj.front_color(): 'F',
        cube_obj.down_color(): 'D',
        cube_obj.left_color(): 'L',
        cube_obj.back_color(): 'B',
    }

    face_specs = (
        (UP, 1, lambda p: (p.pos.z, p.pos.x)),
        (RIGHT, 0, lambda p: (-p.pos.y, -p.pos.z)),
        (FRONT, 2, lambda p: (-p.pos.y, p.pos.x)),
        (DOWN, 1, lambda p: (-p.pos.z, p.pos.x)),
        (LEFT, 0, lambda p: (-p.pos.y, p.pos.z)),
        (BACK, 2, lambda p: (-p.pos.y, -p.pos.x)),
    )

    facelets = []
    for axis, color_idx, key_fn in face_specs:
        for piece in sorted(cube_obj._face(axis), key=key_fn):
            facelets.append(color_to_face[piece.colors[color_idx]])

    converted = []
    for token in kociemba.solve(''.join(facelets)).split():
        face = token[0]
        if token.endswith('2'):
            converted.extend([face] * 2)
        elif token.endswith("'"):
            converted.append(face + 'i')
        else:
            converted.append(face)
    return converted

