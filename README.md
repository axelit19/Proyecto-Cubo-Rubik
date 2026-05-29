![PyPI](https://img.shields.io/pypi/v/rubik-cube)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/rubik-cube)

### Optimización mediante BFS 

En esta implementación se incorpora una optimización clave basada en una
búsqueda en anchura (BFS) para resolver el cubo por fases. En lugar de
explorar movimientos sobre el cubo entero, el solucionador "congela" las
piezas ya resueltas y realiza una búsqueda limitada (por profundidad) sobre
un estado compacto que contiene únicamente la posición y los colores de las
piezas relevantes.

Puntos esenciales:

- Resolución por fases: se resuelven primero las piezas de la cruz, luego las
  esquinas frontales, las aristas del medio, las aristas traseras y las
  esquinas traseras. Cada fase protege las piezas ya colocadas.
- Estado compacto: `_snapshot_state()` crea una tupla de entradas
  `(pos_tuple, colors_tuple)` por pieza rastreada. Esta representación hace que
  comparar estados y aplicar movimientos sea muy barato.
- Búsqueda en anchura: `_bfs()` explora secuencias por orden de longitud, por
  lo que la primera solución encontrada es mínima en número de movimientos
  (dentro del límite de profundidad de la fase).
- Poda de movimientos: se eliminan movimientos que sean el inverso inmediato,
  movimientos que no afectan a las piezas rastreadas y se evitan expansiones
  redundantes sobre el mismo eje.

Esta estrategia reduce drásticamente el espacio de búsqueda necesario para
colocar cada pieza y, en conjunto, optimiza la secuencia final sin necesidad
de explorar combinaciones largas sobre todo el cubo.

### Ejemplo: trazado paso a paso de `_bfs()` para una pieza (ilustrativo)

Ejemplo sencillo y abstracto para mostrar la dinámica de `_bfs()`:

- Piezas rastreadas: [P1, P2]
- Estado inicial (start_state):
  - P1 -> pos=(1,0,0), colors=('R', None, None)
  - P2 -> pos=(0,1,0), colors=(None, 'W', None)
- Estado objetivo (goal_state):
  - P1 -> pos=(0,0,1), colors=(None, None, 'F')  # P1 en su lugar correcto
  - P2 -> pos=(0,1,0), colors=(None, 'W', None)  # P2 ya está en su sitio

Flujo resumido:

1) Cola inicial: Q = [ (start_state, []) ]
2) Expandir start_state -> generar movimientos válidos que afectan a P1/P2
   (ej.: `U`, `R`). Encolamos los estados resultantes con las secuencias
   `['U']`, `['R']`.
3) Desencolar el siguiente estado; si coincide con `goal_state` devolvemos la
   secuencia; si no, expandimos sus hijos (respetando `seen` y las podas) y
   repetimos hasta hallar la solución o alcanzar `max_depth`.

Diagrama ASCII simplificado:

```
[start_state]
     |
  expand movimientos válidos
     |
  +----+----+
  |         |
 [s1]      [s2]
  |\        |
  | \       |
  |  [s1a]  |
  |         |
  +-> match? -> si sí: devolver secuencia
```

Si la primera solución encontrada es `['R', 'U']`, BFS garantiza que no hay
otra solución más corta (en número de movimientos) dentro de la profundidad
permitida.
