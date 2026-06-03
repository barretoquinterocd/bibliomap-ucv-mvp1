# BiblioMap — MVP 1.0

**Mapea la ciencia, encuentra brechas, conecta con el mundo.**

BiblioMap es una herramienta académica de orientación bibliométrica desarrollada como recurso de apoyo para estudiantes, tesistas e investigadores que se encuentran construyendo antecedentes, estado del arte, marco teórico, marco contextual y brechas preliminares de investigación.

Forma parte del ecosistema **BiblioIntel**, entendido como **BIBLIOMETRÓLOGO INTELIGENTIZADOR**.

---

## 1. Propósito

BiblioMap permite realizar una exploración preliminar de literatura científica usando metadatos académicos abiertos. Su finalidad es apoyar la lectura inicial de un campo de investigación, identificar tendencias, autores, instituciones, países, publicaciones relevantes y posibles brechas preliminares.

La herramienta está pensada como apoyo pedagógico para espacios de formación universitaria, especialmente en procesos de elaboración del Capítulo 2 de trabajos de grado, tesis y proyectos de investigación.

---

## 2. Funciones del MVP 1.0

El MVP 1.0 permite:

- Consultar publicaciones académicas mediante OpenAlex.
- Recuperar metadatos bibliométricos básicos.
- Visualizar resultados preliminares.
- Agrupar producción científica por país.
- Visualizar un mapa mundial.
- Consultar detalle geográfico.
- Identificar investigadores detectados.
- Revisar publicaciones recuperadas.
- Detectar señales preliminares de brecha.
- Identificar tendencias de estudio.
- Identificar áreas poco visibles.
- Proponer oportunidades investigativas.
- Consultar una sección pedagógica para aprender bibliometría.
- Generar reporte preliminar en Markdown, HTML y PDF.

---

## 3. Advertencia metodológica

BiblioMap ofrece resultados orientadores, no conclusiones definitivas.

Los resultados dependen de:

- La fuente consultada.
- Los términos de búsqueda.
- El idioma utilizado.
- La cobertura de metadatos.
- El periodo seleccionado.
- El número máximo de registros recuperados.
- La calidad de autores, instituciones, países, DOI, fuentes y abstracts.

Toda señal de brecha, tendencia u oportunidad investigativa debe validarse mediante lectura crítica, revisión teórica y contraste con otras fuentes académicas.

---

## 4. Fuente de datos inicial

La fuente inicial del MVP 1.0 es **OpenAlex**, una base abierta de metadatos académicos.

---

## 5. Arquitectura del proyecto

```text
01_BiblioMap_UCV/
│
├── app/
│   └── streamlit_app.py
│
├── assets/
│   ├── images/
│   └── styles/
│       └── custom.css
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
│
├── docs/
│   ├── flujo_tecnico_mvp.md
│   ├── guia_integracion_FrameVR.md
│   ├── guia_rapida_instalacion.md
│   ├── pantallas_mvp.md
│   └── reglas_metodologicas_mvp.md
│
├── modules/
│   ├── clean_metadata.py
│   ├── gap_suggester.py
│   ├── generate_map.py
│   ├── generate_report.py
│   ├── generate_tables.py
│   ├── group_by_country.py
│   └── search_openalex.py
│
├── config.py
├── requirements.txt
├── README.md
└── .gitignore