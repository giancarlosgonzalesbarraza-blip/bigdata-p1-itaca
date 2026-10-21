# Proyecto 1 · Analítica académica ITACA (origen XML)

## Descripción y objetivo

Este proyecto tiene como objetivo extraer y procesar datos académicos procedentes de la plataforma **ITACA**, utilizando archivos **XML** como fuente de datos.

Los datos corresponden a diferentes aspectos del ámbito académico, como:

- Alumnos
- Contenidos
- Calificaciones
- Cursos

El proyecto transforma estos datos mediante un proceso de **ingesta, almacenamiento, limpieza y procesamiento**, con el objetivo de generar información útil para su posterior análisis.

Finalmente, los datos procesados se utilizarán para crear un **dashboard interactivo** que permita visualizar indicadores académicos y facilitar el análisis del rendimiento de los alumnos.

## Arquitectura

```mermaid
graph LR
    A[Fuente XML<br/>ITACA] --> B[Ingesta]
    B --> C[Almacenamiento<br/>MongoDB]
    C --> D[Procesamiento<br/>Limpieza y cálculo]
    D --> E[Visualización<br/>Dashboard + modelo predictivo]
```

## Fuentes de datos

Los datos de origen proceden de la plataforma **ITACA** y se entregan mediante **exportación en formato XML**. El mecanismo de acceso consiste en descargar el archivo comprimido **`Datos Análisis Académico XML`**, que contiene un subdirectorio por tabla con un archivo XML en su interior, para cada una de las tablas del modelo relacional de origen utilizadas en este proyecto: **Alumnos**, **Contenidos**, **Calificaciones** y **Cursos**.

La exportación constituye un *snapshot* puntual del sistema académico: los archivos XML se descargan y se incorporan directamente al proceso de **ingesta**, sin conexión adicional a la base de datos relacional de origen.

A continuación se documentan, para cada tabla, el mecanismo de acceso, los campos disponibles y la frecuencia de actualización esperada.

### Alumnos

- **Mecanismo de acceso:** fichero XML correspondiente a la tabla `Alumnos`, incluido en el ZIP `Datos Análisis Académico XML`.
- **Frecuencia de actualización esperada:** anual, con la matriculación del curso académico (con posibles regeneraciones puntuales por altas, bajas o cambios de grupo).

| Campo   | Tipo   | Descripción                     |
|---------|--------|---------------------------------|
| Anyo    | string | Año académico                   |
| NIA     | int    | Número de Identificación Alumno |
| Curso   | string | Curso al que pertenece          |
| PrimSeg | string | Primaria o Secundaria           |
| Ciclo   | string | Ciclo formativo                 |
| Grado   | string | Grado académico                 |
| Familia | string | Familia profesional             |
| Turno   | string | Turno (mañana, tarde, etc.)     |
| Grupo   | string | Grupo al que pertenece          |

### Contenidos

- **Mecanismo de acceso:** fichero XML correspondiente a la tabla `Contenidos`, incluido en el ZIP `Datos Análisis Académico XML`.
- **Frecuencia de actualización esperada:** anual, al inicio del curso académico, cuando cambia la oferta de módulos.

| Campo         | Tipo   |       Descripción      |
|---------------|--------|------------------------|
| Anyo          | string | Año académico          |
| Curso         | string | Curso al que pertenece |
| Modulo        | string | Código del módulo      |
| Nombre_Modulo | string | Nombre del módulo      |

### Calificaciones

- **Mecanismo de acceso:** fichero XML correspondiente a la tabla `Calificaciones`, incluido en el ZIP `Datos Análisis Académico XML`.
- **Frecuencia de actualización esperada:** varias veces por curso académico, tras cada corte de evaluación (una exportación por evaluación cerrada).

| Campo      | Tipo   | Descripción                     |
|------------|--------|---------------------------------|
| Anyo       | string | Año académico                   |
| NIA        | int    | Número de Identificación Alumno |
| Curso      | string | Curso al que pertenece          |
| Modulo     | string | Código del módulo               |
| Nota       | float  | Nota obtenida                   |
| Evaluacion | string | Evaluación correspondiente      |

### Cursos

- **Mecanismo de acceso:** fichero XML correspondiente a la tabla `Cursos`, incluido en el ZIP `Datos Análisis Académico XML`.
- **Frecuencia de actualización esperada:** anual o bajo demanda, según cambios en la estructura académica (jerarquía de cursos).

| Campo      | Tipo   | Descripción                        |
|------------|--------|------------------------------------|
| Anyo       | string | Año académico                      |
| Codigo     | string | Código del curso                   |
| Nombre_Cas | string | Nombre del curso en castellano     |
| Nombre_Val | string | Nombre del curso en valenciano     |
| Padre      | string | Código del curso padre (jerarquía) |

> **Nota:** al publicarse una nueva versión de la exportación, la ingesta deberá procesar de nuevo el ZIP completo, ya que los cuatro XML forman parte del mismo snapshot del sistema origen.
