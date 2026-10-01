# Conciliador de Facturas y Retenciones

Prototipo full-stack para la conciliación automática de facturas y registros contables.

El sistema permite cargar dos archivos CSV, aplicar reglas de validación contable y tributaria, identificar inconsistencias y consultar los resultados desde una interfaz web.

## Tecnologías utilizadas

### Backend
- Python 3.13.3
- FastAPI 0.142.2
- Uvicorn 0.54.0
- python-multipart 0.0.32
- pytest 9.1.1

### Frontend
- Angular CLI 21.2.24
- Node.js 22.15.0
- TypeScript
- HTML
- CSS

## Estructura del proyecto

```text
analista-prueba/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── services/
│   │   ├── __init__.py
│   │   └── conciliacion.py
│   └── tests/
│       └── test_conciliacion.py
│
├── data/
│   ├── facturas.csv
│   └── contabilidad.csv
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── presentacion/
└── README.md

## Requisitos

Para ejecutar el proyecto se requiere:

- Python 3.13 o compatible.
- Node.js 22.x.
- npm.
- Angular CLI 21.x.

## Ejecución del backend

1. Abrir una terminal y ubicarse en la carpeta del backend:

```powershell
cd backend

## Crear el entorno virtual

python -m venv venv

## Activar el entorno virtual en Windows

.\venv\Scripts\Activate.ps1

## Instalar dependencias

pip install -r requirements.txt

## Ejecutar el servidor

uvicorn main:app --reload

## La API estará disponible en 

http://127.0.0.1:8000

## La documentación interactiva de FastAPI estará disponible en

http://127.0.0.1:8000/docs

## Ejecución del frontend

1. Abrir otra terminal y ubicarse en la carpeta del frontend:

```powershell
cd frontend

## Instalar dependencias

npm install --legacy-peer-deps

## Ejecutar la aplicación

ng serve

## La aplicación estará disponible en 

http://localhost:4200

### ¿Por qué usar `--legacy-peer-deps`?

Porque fue necesario durante la instalación de las dependencias de este proyecto debido a un conflicto de dependencias de npm.


## Funcionamiento

El usuario debe cargar dos archivos CSV:

1. `facturas.csv`
2. `contabilidad.csv`

Al iniciar la conciliación, el backend realiza las siguientes validaciones:

1. Valida que los archivos tengan extensión `.csv`.
2. Valida que los archivos contengan las columnas requeridas.
3. Lee los registros de ambos archivos.
4. Identifica facturas duplicadas.
5. Busca los registros contables asociados a cada factura.
6. Valida el valor del IVA.
7. Valida el total esperado de la factura.
8. Identifica facturas sin registro contable.
9. Identifica registros contables en estado `Pendiente`.
10. Devuelve un resumen y el detalle de los resultados.

El frontend muestra el resultado de la conciliación y permite filtrar las facturas por estado.


## Reglas de conciliación

### Validación del IVA

El IVA esperado se calcula mediante la siguiente fórmula:

IVA esperado = base gravable × tarifa de IVA

El valor calculado se compara con el valor de IVA registrado en la factura.

La validación se considera correcta cuando la diferencia absoluta entre ambos valores es menor o igual a $0,01.

### Validación del total de la factura

El total esperado se calcula mediante la siguiente fórmula:

Total esperado = base gravable + IVA - valor de retención

El resultado se compara con el total registrado en la factura.

La validación se considera correcta cuando la diferencia absoluta entre ambos valores es menor o igual a $0,01.

### Duplicados

Se identifican facturas que tienen el mismo `id_factura` más de una vez en el archivo de facturas.

También se identifican múltiples registros contables asociados al mismo `id_factura`.

### Registro contable

Una factura se marca como inconsistente cuando:

- No tiene registro contable.
- Tiene un registro contable en estado `Pendiente`.
- Tiene múltiples registros contables asociados.

### Campos obligatorios

El backend valida que estén presentes las columnas requeridas en cada archivo.

También identifica campos obligatorios que estén vacíos dentro de los registros.


## Respuesta de la API

El endpoint `POST /api/conciliar` devuelve un resumen general y el detalle de los resultados de cada factura.

Ejemplo del resumen:

```json
{
  "resumen": {
    "total_facturas": 50,
    "correctas": 28,
    "inconsistencias": 22
  }
}
```

Cada resultado del detalle incluye:

* ID de la factura.
* Estado de la conciliación.
* Causas de inconsistencia.
* IVA esperado y registrado.
* Diferencia de IVA.
* Total esperado y registrado.
* Diferencia del total.
* Estado del registro contable.

El frontend consume esta respuesta mediante una solicitud HTTP al backend y presenta la información en una tabla.

Además, permite filtrar los resultados por estado:

* `Todos`
* `Correcta`
* `Con inconsistencia`

## Manejo de errores

El sistema contempla validaciones básicas para evitar el procesamiento de archivos inválidos.

### Backend

El backend devuelve errores HTTP cuando:

* El archivo no tiene extensión `.csv`.
* El archivo está vacío o no contiene encabezados.
* Faltan columnas requeridas.
* No existen registros en el archivo.
* Un campo numérico contiene un valor inválido.
* Ocurre un error durante el procesamiento de los archivos.

Los errores de validación se devuelven con código HTTP `400` y un mensaje descriptivo.

Los errores inesperados durante el procesamiento se devuelven con código HTTP `500`.

### Frontend

El frontend muestra mensajes de error cuando:

* No se han seleccionado ambos archivos.
* El backend rechaza alguno de los archivos.
* No es posible conectarse con el backend.
* Ocurre un error durante la conciliación.

Mientras se procesa la información, la interfaz muestra un estado de carga para informar al usuario que la operación está en curso.

## Pruebas

El backend cuenta con pruebas automatizadas utilizando `pytest`.

Las pruebas cubren:

* Cálculo del IVA esperado.
* Validación de un IVA correcto.
* Detección de un IVA incorrecto.
* Validación de un total incorrecto.
* Detección de facturas duplicadas.
* Validación de columnas requeridas en los archivos CSV.
* Ejecución completa del proceso de conciliación.

Para ejecutar las pruebas, ubicarse en la carpeta `backend` con el entorno virtual activo y ejecutar:

```powershell
pytest
```

Resultado de las pruebas realizadas:

```text
7 passed
```


## Supuestos y limitaciones

Para el desarrollo del prototipo se asumieron las siguientes condiciones:

* Los archivos de entrada utilizan codificación UTF-8 y formato CSV.
* Los identificadores de factura (`id_factura`) son la llave utilizada para relacionar las facturas con los registros contables.
* Una factura con más de un registro contable asociado se considera inconsistente por posible duplicidad.
* Un registro contable en estado `Pendiente` se considera una inconsistencia para efectos de la conciliación.
* La validación del total se realiza utilizando la fórmula definida en las reglas del ejercicio: base gravable + IVA - retención.
* No se realiza una validación adicional de la distribución de los valores entre las cuentas contables de débito y crédito.
* No se realizan validaciones tributarias adicionales diferentes a las solicitadas para el ejercicio.
* El prototipo procesa los archivos en memoria y no utiliza una base de datos persistente.
* Los resultados no se almacenan después de finalizar la ejecución.
* La aplicación está diseñada como un prototipo funcional y no contempla autenticación, autorización ni despliegue en un ambiente productivo.


## Declaración de uso de inteligencia artificial

Durante el desarrollo de esta prueba técnica se utilizó inteligencia artificial como herramienta de apoyo para:

* Resolver dudas puntuales sobre sintaxis y configuración de Python, FastAPI y Angular.
* Revisar y mejorar la estructura del código.
* Identificar posibles errores durante el desarrollo y las pruebas.
* Apoyar la redacción y organización de la documentación.
* Sugerir alternativas de implementación y buenas prácticas.

La lógica de negocio, las reglas de conciliación, la integración de los componentes, las pruebas y la validación de los resultados fueron revisadas y ejecutadas durante el desarrollo del prototipo.

La inteligencia artificial se utilizó como herramienta de asistencia y consulta, manteniendo la responsabilidad sobre las decisiones de implementación y los resultados entregados.
