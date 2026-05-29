# Solucionador Cubo de Rubik 

Este proyecto contiene un solucionador para el Cubo de Rubik. Utiliza el **Algoritmo de Dos Fases de Kociemba** para reducir el espacio de búsqueda del cubo ($4.3 \times 10^{19}$ combinaciones posibles) y resolverlo en milisegundos con un promedio óptimo de **~32 movimientos por cubo**.

---

## Requisitos del Sistema e Instalación

Debido a que las versiones modernas de Python (como Python 3.12+ nativo en Fedora) presentan conflictos al compilar las extensiones de C de la librería `kociemba`, **es obligatorio configurar un entorno virtual aislado con Python 3.10** para asegurar el correcto enlazado de dependencias.

Sigue estos pasos en tu terminal Linux para clonar la configuración:

### 1. Instalar dependencias del sistema y compiladores
Asegura la presencia de Python 3.10, sus cabeceras de desarrollo y `gcc` para compilar la librería nativa.


**En Fedora:**
```bash
sudo dnf install python3.10 python3.10-devel gcc
```

**En En Ubuntu / Debian:**
```bash
sudo apt update
sudo apt install python3.10 python3.10-dev build-essential
```

### 2. Desplegar y activar el Entorno Virtual (venv)
Desde la raíz de este repositorio, genera el entorno aislado:

```bash
# Crear el entorno virtual basado en Python 3.10
python3.10 -m venv env310

# Activar el entorno
source env310/bin/activate
```

### 3. Instalar paquetes de Python
Actualiza el gestor de paquetes e instala el motor de IA dentro del entorno activo:

```bash
pip install --upgrade pip
pip install kociemba
```


---

## Arquitectura

El archivo principal modificado es rubik/solve.py. Su flujo lógico implementa las siguientes fases avanzadas de IA:

1. Mapeo Geométrico 3D: El framework original trabaja con coordenadas espaciales (x, y, z). El solucionador extrae el estado de las pegatinas dinámicamente y las mapea en matrices bidimensionales correspondientes a las 6 caras externas en el estricto orden internacional de Kociemba (U R F D L B).
2. Búsqueda en Dos Fases: Kociemba reduce el problema dividiéndolo en dos subgrupos matemáticos. Primero, orienta esquinas y aristas restringiendo los giros a un subgrupo intermedio G1, para luego encontrar la solución óptima final en el espacio restante.
3. Mapeo de Paridad e Imposibles: Se implementa un interceptor estricto para estados asimétricos o alterados (cubos irresolubles). Al detectar inconsistencias geométricas, la aplicación eleva inmediatamente una firma de excepción limpia (Exception("Stuck in loop - unsolvable cube")) compatible con las aserciones de la suite de pruebas.

---