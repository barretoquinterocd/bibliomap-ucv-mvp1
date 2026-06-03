# Flujo técnico inicial — BiblioMap UCV MVP 1.0

## Objetivo del flujo

El flujo técnico de BiblioMap UCV permite que un usuario introduzca un tema de investigación y el sistema consulte una fuente académica abierta, organice los resultados y los presente mediante mapa, tablas y brechas preliminares.

## Flujo general

Usuario escribe tema de investigación
↓
search_openalex.py busca publicaciones en OpenAlex
↓
clean_metadata.py limpia y normaliza los datos
↓
group_by_country.py agrupa resultados por país y continente
↓
generate_map.py genera el mapa bibliométrico
↓
generate_tables.py genera tablas de autores, instituciones y publicaciones
↓
gap_suggester.py sugiere brechas preliminares
↓
streamlit_app.py muestra todo en la interfaz

## Módulos del MVP

### 1. search_openalex.py

Función:
Consultar OpenAlex usando palabras clave introducidas por el usuario.

Entrada:
- Tema de investigación
- Palabras clave
- Periodo opcional

Salida:
- Lista de publicaciones con título, año, DOI, autores, instituciones, país y resumen si está disponible.

### 2. clean_metadata.py

Función:
Limpiar y normalizar los metadatos obtenidos.

Entrada:
- Datos crudos desde OpenAlex.

Proceso:
- Eliminar campos vacíos críticos.
- Normalizar nombres de países.
- Normalizar autores.
- Extraer instituciones.
- Organizar DOI/enlaces.

Salida:
- Dataset limpio.

### 3. group_by_country.py

Función:
Agrupar publicaciones por país y continente.

Entrada:
- Dataset limpio.

Salida:
- Tabla con número de publicaciones por país.
- Tabla con número de publicaciones por continente.

### 4. generate_map.py

Función:
Crear mapa mundial interactivo.

Entrada:
- Tabla por país.

Salida:
- Mapa bibliométrico mundial.

### 5. generate_tables.py

Función:
Crear tablas de consulta para el usuario.

Entrada:
- Dataset limpio.

Salida:
- Tabla de autores.
- Tabla de instituciones.
- Tabla de publicaciones.

### 6. gap_suggester.py

Función:
Sugerir brechas preliminares de investigación.

Entrada:
- Dataset limpio.
- Frecuencia de temas.
- Distribución geográfica.
- Producción por año.

Salida:
- Lista de posibles vacíos.
- Preguntas orientadoras.

### 7. streamlit_app.py

Función:
Mostrar la aplicación web.

Entrada:
- Tema escrito por el usuario.

Salida:
- Mapa.
- Tablas.
- Publicaciones.
- Brechas preliminares.
- Advertencias metodológicas.

## Advertencia metodológica

BiblioMap UCV ofrece orientación bibliométrica preliminar. Sus resultados dependen de la fuente consultada, los metadatos disponibles, los términos de búsqueda, el periodo seleccionado y los criterios aplicados. Las brechas sugeridas no son conclusiones definitivas, sino puntos de partida para la investigación humana.