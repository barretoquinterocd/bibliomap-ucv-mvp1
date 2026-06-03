# BiblioMap UCV — MVP 1.0

**Mapea la ciencia, encuentra brechas, conecta con el mundo.**

## 1. ¿Qué es BiblioMap UCV?

BiblioMap UCV es una herramienta informática de orientación bibliométrica diseñada para apoyar a estudiantes, tesistas e investigadores en la exploración inicial de la producción científica mundial relacionada con un tema de investigación.

Forma parte del ecosistema **BiblioIntel**, entendido como **BIBLIometrólogo INTEligentizador**: un sistema bibliometrológico inteligentizador orientado a medir, mapear, interpretar y transformar evidencia científica en conocimiento útil, preguntas de investigación, brechas preliminares y rutas creaductivas.

BiblioMap UCV no sustituye al investigador humano ni pretende ofrecer conclusiones definitivas. Su función es orientar, visualizar, conectar y apoyar la fase inicial de exploración científica.

## 2. Propósito social

BiblioMap UCV nace como una herramienta de apoyo para la Universidad Central de Venezuela, con el propósito de contribuir a la democratización del acceso a la orientación científica.

Su finalidad es ayudar a que estudiantes e investigadores puedan conectarse con la producción científica global, identificar autores, instituciones, países, publicaciones y posibles vacíos de investigación.

La herramienta busca fortalecer la cultura de consulta científica, bibliometría, metodología de investigación y gestión del conocimiento, especialmente en contextos universitarios con limitaciones de acceso a recursos especializados.

## 3. Lema

**BiblioMap UCV: mapea la ciencia, encuentra brechas, conecta con el mundo.**

## 4. Identidad visual e institucional

BiblioMap UCV forma parte del ecosistema BiblioIntel, entendido como **BIBLIometrólogo INTEligentizador**.

La identidad visual del proyecto se organiza en tres niveles:

1. **BiblioIntel**: ecosistema general de bibliometrología inteligentizadora.
2. **BiblioMap**: herramienta visual, educativa y geográfica para mapear producción científica.
3. **LEGIN**: entidad impulsora del desarrollo desde el Laboratorio Estratégico de Gestión de la Innovación.

Además, BiblioMap UCV incorporará en pequeño los logos de las entidades vinculadas o beneficiarias del aporte:

* Centro de Estudios de la Empresa y la Producción (CEAP).
* Facultad de Ciencias Económicas y Sociales de la Universidad Central de Venezuela (FACES UCV).
* Universidad Central de Venezuela (UCV).

La incorporación de estos logos se realizará en la interfaz como elementos de respaldo institucional, sin interferir con las funciones bibliométricas de la herramienta.

La relación institucional queda definida así:

```text
BiblioIntel = ecosistema conceptual y tecnológico.
BiblioMap = herramienta informática aplicada.
LEGIN = laboratorio impulsor.
CEAP / FACES UCV / UCV = entidades vinculadas o beneficiarias.
```

El logo de **LEGIN** debe mantenerse tal cual en la interfaz, respetando su composición original, incluyendo la palabra **LEGIN** centrada en color negro dentro del símbolo.

## 5. Fundamento metodológico

BiblioMap UCV se inspira en el enfoque de investigación bibliométrica propuesto por **Oğuzhan Öztürk, Rıdvan Kocaman y Dominik K. Kanbach**, quienes plantean que una investigación bibliométrica rigurosa debe articular:

* Objetivo de investigación.
* Recolección de datos.
* Análisis y visualización.
* Interpretación de hallazgos y resultados.

La herramienta no busca sustituir una investigación bibliométrica completa, sino apoyar una primera fase de exploración, orientación y aprendizaje.

En versiones futuras, BiblioIntel Creaductivo ampliará este enfoque hacia una herramienta más completa de diseño, análisis, interpretación, vigilancia y formulación de agendas de investigación bibliométrica.

## 6. Fundamento inteligentizador

BiblioMap UCV se apoya en la siguiente fórmula rectora:

```text
Humano define sentido.
Software procesa evidencia.
IA amplifica interpretación.
Inteligencia Humana profundiza el conocimiento.
IA + IH creaduccen.
La creatividad transforma resultados en conocimiento nuevo.
```

Desde esta perspectiva, BiblioMap UCV no se limita a mostrar datos. Su objetivo es ofrecer una experiencia de orientación científica que permita al usuario observar el campo, reconocer actores, identificar tendencias preliminares y formular nuevas preguntas de investigación.

## 7. ¿Qué permite hacer el MVP 1.0?

La versión MVP 1.0 permitirá:

* Ingresar un tema de investigación.
* Consultar una fuente académica abierta.
* Recuperar publicaciones relacionadas.
* Agrupar resultados por país.
* Visualizar un mapa mundial de producción científica.
* Mostrar autores detectados.
* Mostrar instituciones detectadas.
* Mostrar publicaciones relacionadas.
* Sugerir brechas preliminares de investigación.

## 8. Fuente de datos inicial

La fuente de datos inicial prevista para el MVP 1.0 será **OpenAlex** u otra fuente académica abierta compatible.

Los resultados dependerán de:

* Cobertura de la fuente.
* Calidad de los metadatos.
* Términos de búsqueda.
* Periodo seleccionado.
* Número máximo de resultados.
* Criterios aplicados.

## 9. Alcance del MVP 1.0

El MVP 1.0 tendrá un alcance preliminar y educativo.

Incluye:

* Consulta temática.
* Mapa mundial.
* Tabla de países.
* Tabla de autores.
* Tabla de instituciones.
* Tabla de publicaciones.
* Brechas preliminares.

No incluye todavía:

* Investigación bibliométrica completa.
* Co-citación avanzada.
* Acoplamiento bibliográfico avanzado.
* Análisis de redes completo.
* Revisión sistemática de literatura.
* Validación definitiva de brechas.
* Integración formal con Scopus o Web of Science.

## 10. Advertencia metodológica

BiblioMap UCV ofrece resultados orientadores, no conclusiones definitivas.

La cobertura depende de:

* Fuente consultada.
* Metadatos disponibles.
* Términos de búsqueda.
* Periodo seleccionado.
* Número máximo de resultados.
* Criterios aplicados.

La interpretación final corresponde al investigador humano.

La herramienta no debe afirmar que un tema no existe, que nadie lo investiga o que una brecha está definitivamente comprobada. Debe expresar sus resultados como observaciones preliminares según la fuente, periodo y criterios utilizados.

## 11. Estructura inicial del proyecto

```text
01_BiblioMap_UCV/
│
├── app/
│   └── streamlit_app.py
│
├── assets/
│   ├── images/
│   │   ├── logo_legin.png
│   │   ├── logo_bibliomap.png
│   │   ├── logo_bibliointel.png
│   │   ├── logo_ceap.png
│   │   ├── logo_faces_ucv.png
│   │   └── logo_ucv.png
│   │
│   └── styles/
│       └── custom.css
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── exports/
│
├── modules/
│   ├── search_openalex.py
│   ├── clean_metadata.py
│   ├── group_by_country.py
│   ├── generate_map.py
│   ├── generate_tables.py
│   └── gap_suggester.py
│
├── docs/
│   ├── README.md
│   ├── flujo_tecnico_mvp.md
│   ├── pantallas_mvp.md
│   └── reglas_metodologicas_mvp.md
│
├── requirements.txt
└── config.py
```

## 12. Módulos previstos

### search_openalex.py

Consulta publicaciones científicas relacionadas con el tema introducido por el usuario.

### clean_metadata.py

Limpia y normaliza los metadatos recuperados.

### group_by_country.py

Agrupa publicaciones por país y continente.

### generate_map.py

Genera el mapa mundial bibliométrico.

### generate_tables.py

Genera tablas de autores, instituciones y publicaciones.

### gap_suggester.py

Sugiere brechas preliminares de investigación.

### streamlit_app.py

Integra la interfaz visual de la aplicación.

## 13. Logos y archivos gráficos

Los logos del proyecto deben guardarse en la carpeta:

```text
assets/images/
```

Con los siguientes nombres exactos:

```text
logo_legin.png
logo_bibliomap.png
logo_bibliointel.png
logo_ceap.png
logo_faces_ucv.png
logo_ucv.png
```

El uso previsto de cada logo será:

```text
logo_bibliomap.png = logo principal de la herramienta.
logo_bibliointel.png = logo del ecosistema mayor.
logo_legin.png = logo de la entidad impulsora.
logo_ceap.png = logo de entidad vinculada.
logo_faces_ucv.png = logo de entidad vinculada.
logo_ucv.png = logo institucional universitario.
```

## 14. Instalación prevista

Desde la carpeta `01_BiblioMap_UCV`, se instalarán las dependencias con:

```bash
pip install -r requirements.txt
```

## 15. Ejecución prevista

Una vez desarrollado el MVP, la aplicación se ejecutará con:

```bash
streamlit run app/streamlit_app.py
```

## 16. Estado del proyecto

Estado actual:

**Fase 0 — Diseño inicial y preparación documental.**

Próximas fases:

1. Crear interfaz inicial en Streamlit.
2. Mostrar identidad visual e institucional.
3. Crear módulo de búsqueda en OpenAlex.
4. Crear limpieza básica de metadatos.
5. Crear agrupación por país.
6. Crear mapa mundial.
7. Crear tablas bibliométricas.
8. Crear sugeridor de brechas.
9. Integrar todo en Streamlit.

## 17. Principio rector

BiblioMap UCV no reemplaza al investigador.

Su función es orientar, visualizar, conectar y apoyar la fase inicial de exploración científica para que la inteligencia humana pueda profundizar, validar y creaducir conocimiento nuevo.

**BiblioMap UCV mapea la ciencia, encuentra brechas y conecta con el mundo.**
