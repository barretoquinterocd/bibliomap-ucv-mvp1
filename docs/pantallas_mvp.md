# Pantallas iniciales — BiblioMap UCV MVP 1.0

## Objetivo general de la interfaz

La interfaz de BiblioMap UCV debe permitir que estudiantes, tesistas e investigadores introduzcan un tema de investigación y visualicen de forma sencilla la distribución geográfica, institucional, autoral y documental de la producción científica relacionada.

La herramienta debe ser clara, pedagógica, visual, ligera y orientadora.

---

# Pantalla 1 — Inicio

## Nombre de la pantalla

Inicio

## Propósito

Presentar la identidad de BiblioMap UCV, explicar brevemente para qué sirve y orientar al usuario sobre el tipo de análisis que puede realizar.

## Identidad inicial

Nombre de la plataforma:

**BiblioMap UCV**

Lema oficial:

**Mapea la ciencia, encuentra brechas, conecta con el mundo.**

Identidad de ecosistema:

**BiblioIntel — BIBLIometrólogo INTEligentizador**

Entidad impulsora:

**Laboratorio Estratégico de Gestión de la Innovación (LEGIN)**

Entidades vinculadas:

* Centro de Estudios de la Empresa y la Producción (CEAP).
* Facultad de Ciencias Económicas y Sociales de la Universidad Central de Venezuela (FACES UCV).
* Universidad Central de Venezuela (UCV).

## Elementos de la pantalla

* Logo principal de BiblioMap.
* Nombre de la plataforma: BiblioMap UCV.
* Lema: Mapea la ciencia, encuentra brechas, conecta con el mundo.
* Referencia al ecosistema BiblioIntel.
* Logo de LEGIN como entidad impulsora.
* Logos pequeños de CEAP, FACES UCV y UCV como entidades vinculadas.
* Breve explicación del propósito.
* Advertencia metodológica.
* Botón o sección para iniciar búsqueda.

## Texto sugerido

# BiblioMap UCV

**Mapea la ciencia, encuentra brechas, conecta con el mundo.**

BiblioMap UCV es una herramienta de orientación bibliométrica diseñada para ayudar a estudiantes e investigadores a explorar la producción científica mundial relacionada con un tema de investigación.

Permite visualizar países, instituciones, autores, publicaciones y posibles brechas preliminares a partir de fuentes académicas abiertas.

Forma parte del ecosistema BiblioIntel, entendido como BIBLIometrólogo INTEligentizador, e incorpora la identidad institucional de LEGIN como entidad impulsora del desarrollo.

Los resultados son orientadores y dependen de los términos de búsqueda, la fuente consultada, los metadatos disponibles y el periodo seleccionado.

---

# Pantalla 2 — Consulta bibliométrica

## Nombre de la pantalla

Buscar tema

## Propósito

Permitir que el usuario introduzca el tema de investigación que desea explorar.

## Elementos de entrada

* Tema de investigación.
* Palabras clave.
* Año inicial.
* Año final.
* Número máximo de resultados.
* Botón: Buscar.

## Campos sugeridos

Tema de investigación:

Ejemplo: inteligencia artificial y creatividad científica

Palabras clave:

Ejemplo: artificial intelligence, scientific creativity, knowledge production

Periodo:

Ejemplo: 2015–2026

Número máximo de resultados:

Ejemplo: 100

---

# Pantalla 3 — Mapa mundial bibliométrico

## Nombre de la pantalla

Mapa mundial

## Propósito

Mostrar la distribución geográfica de la producción científica relacionada con el tema consultado.

## Elementos visuales

* Mapa mundial por país.
* Intensidad de color según número de publicaciones.
* Tooltip al pasar el cursor:

  * País.
  * Número de publicaciones.
  * Instituciones detectadas.
  * Autores principales, si aplica.

## Interpretación esperada

El mapa permite observar qué regiones del mundo presentan mayor producción científica sobre el tema consultado.

---

# Pantalla 4 — Detalle por país, institución y continente

## Nombre de la pantalla

Detalle geográfico

## Propósito

Mostrar el desglose de los resultados por país, continente e institución.

## Elementos

* Tabla de países.
* Tabla de continentes.
* Tabla de instituciones.
* Número de publicaciones por país.
* Número de publicaciones por institución.
* Posible visualización de barras.

## Columnas sugeridas para la tabla de países

* País.
* Continente.
* Número de publicaciones.
* Instituciones principales.
* Autores principales.

## Columnas sugeridas para la tabla de instituciones

* Institución.
* País.
* Número de publicaciones.
* Autores asociados.

---

# Pantalla 5 — Investigadores

## Nombre de la pantalla

Investigadores detectados

## Propósito

Mostrar los autores e investigadores que aparecen vinculados al tema consultado.

## Elementos

* Tabla de autores.
* Afiliación institucional.
* País.
* Número de publicaciones detectadas.
* Lista breve de trabajos asociados.

## Columnas sugeridas

* Autor.
* Afiliación.
* País.
* Número de publicaciones.
* Títulos asociados.
* Enlace, si está disponible.

## Advertencia

La afiliación depende de los metadatos disponibles en la fuente consultada.

---

# Pantalla 6 — Publicaciones

## Nombre de la pantalla

Publicaciones relacionadas

## Propósito

Mostrar los documentos encontrados sobre el tema consultado.

## Elementos

* Tabla de publicaciones.
* Filtros por año, autor, país o institución.
* Enlace DOI o URL, cuando exista.
* Abstract, si está disponible.

## Columnas sugeridas

* Título.
* Año.
* Autores.
* Fuente o revista.
* DOI.
* País.
* Institución.
* Abstract disponible.

---

# Pantalla 7 — Brechas preliminares

## Nombre de la pantalla

Brechas y oportunidades

## Propósito

Sugerir posibles vacíos, oportunidades o rutas de investigación a partir del comportamiento preliminar de los datos.

## Elementos

* Temas poco desarrollados.
* Países o regiones con baja producción.
* Posibles conexiones entre temas.
* Preguntas orientadoras.
* Advertencia metodológica.

## Tipos de brechas preliminares

* Brecha geográfica.
* Brecha temática.
* Brecha temporal.
* Brecha institucional.
* Brecha de colaboración.
* Brecha de aplicación práctica.
* Brecha metodológica.

## Ejemplo de salida

Posible brecha geográfica:

Se observa baja producción en América Latina sobre el tema consultado, según la fuente analizada.

Posible pregunta:

¿Cómo se está abordando este tema en contextos universitarios latinoamericanos y qué oportunidades existen para nuevas investigaciones?

---

# Pantalla 8 — Aprender bibliometría

## Nombre de la pantalla

Aprender bibliometría

## Propósito

Ofrecer una sección pedagógica para que estudiantes comprendan los conceptos básicos usados por la herramienta.

## Conceptos a explicar

* Bibliometría.
* Bibliometrología.
* BiblioIntel.
* BiblioMap.
* Producción científica.
* Citas.
* Coautoría.
* Mapeo científico.
* Redes bibliométricas.
* Brecha de investigación.
* Fuente de datos.
* Limitaciones metodológicas.

## Texto sugerido

BiblioMap UCV no reemplaza al investigador. Su función es orientar, visualizar y apoyar la toma de decisiones iniciales en un proceso de investigación científica.

La interpretación final corresponde a la inteligencia humana del investigador, quien define el sentido, valida la evidencia y transforma los hallazgos en conocimiento nuevo.

---

# Menú lateral inicial de la aplicación

El menú lateral de Streamlit debe incluir:

1. Inicio
2. Buscar tema
3. Mapa mundial
4. Detalle geográfico
5. Investigadores
6. Publicaciones
7. Brechas preliminares
8. Aprender bibliometría

---

# Uso de logos en la interfaz

## Logo principal de la herramienta

El logo principal de la aplicación será el isologo de **BiblioMap**.

Debe aparecer en:

* Parte superior de la pantalla de inicio.
* Barra lateral o encabezado de navegación.
* Reportes exportados, cuando aplique.

## Logo del ecosistema

El logo de **BiblioIntel** debe aparecer como referencia del ecosistema mayor.

Debe mostrarse de forma secundaria, preferiblemente en:

* Barra lateral.
* Pie de página.
* Sección “Acerca de BiblioMap”.
* Documentación técnica.

## Logo LEGIN

El logo de **LEGIN** debe mantenerse tal cual, respetando su diseño original, incluyendo el texto **LEGIN** centrado en color negro dentro del símbolo.

Debe aparecer como entidad impulsora en:

* Pantalla de inicio.
* Barra lateral.
* Pie de página.
* Sección institucional.

## Logos de entidades vinculadas

Los logos de **CEAP**, **FACES UCV** y **UCV** deben aparecer en pequeño como entidades vinculadas o beneficiarias del aporte.

Ubicación recomendada:

* Parte inferior de la pantalla de inicio.
* Pie de página.
* Sección “Entidades vinculadas”.

## Regla visual

Los logos institucionales no deben competir con el logo funcional de BiblioMap.

La jerarquía visual será:

1. **BiblioMap** como herramienta principal.
2. **BiblioIntel** como ecosistema.
3. **LEGIN** como impulsor.
4. **CEAP**, **FACES UCV** y **UCV** como entidades vinculadas.

---

# Regla de diseño

La interfaz debe ser:

* Clara.
* Sencilla.
* En español.
* Pedagógica.
* Ligera.
* Visual.
* Sin exceso de tecnicismos.
* Orientada a estudiantes e investigadores noveles.

---

# Advertencia metodológica general

BiblioMap UCV ofrece resultados orientadores, no conclusiones definitivas. La cobertura depende de la fuente consultada, los metadatos disponibles, los términos usados, el periodo seleccionado y los criterios aplicados.

---

# Lema oficial

**Mapea la ciencia, encuentra brechas, conecta con el mundo.**
