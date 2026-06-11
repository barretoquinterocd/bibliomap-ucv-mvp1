# -*- coding: utf-8 -*-
"""
BiblioQuest
De la observacion al objetivo.

Modulo de diseno metodologico inicial para investigaciones bibliometricas /
bibliometrologicas dentro del ecosistema BiblioIntel.

Nota metodologica:
Basado en la metodologia HOMI: sinergia de los aportes intelectuales de
Hurtado de Barrera sobre formulacion holistica de objetivos de investigacion;
Ozturk, Kocaman y Kanbach sobre diseno de investigacion bibliometrica; y
Mirabal Gonzalez sobre I2E, A3D y 3S.

El paradigma inteligentizador se incorpora como marco conceptual propio en
desarrollo, orientado a la relacion humano-ciencia-IA-creatividad, con
trazabilidad, validacion humana y proyeccion transformadora del conocimiento.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import json
import re
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"

DEFAULT_JSON_PATH = PROCESSED_DIR / "biblioquest_protocol.json"
DEFAULT_MD_PATH = EXPORTS_DIR / "biblioquest_protocol.md"


HURTADO_LEVELS = {
    "perceptual": {
        "verbs": ["explorar", "describir"],
        "research_types": ["exploratoria", "descriptiva"],
        "description": "Nivel orientado a aproximarse, identificar o describir un evento de estudio.",
    },
    "aprehensivo": {
        "verbs": ["analizar", "comparar"],
        "research_types": ["analitica", "comparativa"],
        "description": "Nivel orientado a descomponer, relacionar o comparar componentes del evento de estudio.",
    },
    "comprensivo": {
        "verbs": ["explicar", "predecir", "proponer"],
        "research_types": ["explicativa", "predictiva", "proyectiva"],
        "description": "Nivel orientado a comprender relaciones, proyectar escenarios o formular propuestas.",
    },
    "integrativo": {
        "verbs": ["modificar", "confirmar", "evaluar"],
        "research_types": ["interactiva", "confirmatoria", "evaluativa"],
        "description": "Nivel orientado a intervenir, verificar o valorar resultados, procesos o propuestas.",
    },
}

TASK_ONLY_VERBS = [
    "buscar",
    "recolectar",
    "descargar",
    "hacer",
    "usar",
    "aplicar",
    "levantar",
    "copiar",
    "generar",
]


@dataclass
class BiblioQuestInput:
    researcher_name: str = ""
    project_title: str = ""
    tentative_topic: str = ""
    research_area: str = ""

    generative_situation: str = ""
    scientific_curiosity: str = ""
    cognitive_purpose: str = ""
    transformative_projection: str = ""

    study_event: str = ""
    unit_of_analysis: str = ""
    context: str = ""
    temporality: str = ""

    general_objective: str = ""
    specific_objectives: List[str] = None
    main_question: str = ""
    specific_questions: List[str] = None
    expected_results: str = ""

    bibliometric_justification: str = ""
    objective_question_data_analysis_fit: str = ""

    intorno: str = ""
    entorno: str = ""
    extorno: str = ""

    support: str = ""
    sustenance: str = ""
    sustainability: str = ""

    notes: str = ""

    def __post_init__(self) -> None:
        if self.specific_objectives is None:
            self.specific_objectives = []
        if self.specific_questions is None:
            self.specific_questions = []


def ensure_dirs() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def ensure_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [clean_text(item) for item in value if clean_text(item)]
    text = clean_text(value)
    if not text:
        return []
    parts = re.split(r"\n|;", text)
    return [clean_text(part) for part in parts if clean_text(part)]


def first_word(text: str) -> str:
    text = clean_text(text).lower()
    if not text:
        return ""
    return re.sub(r"[^a-záéíóúüñ]", "", text.split()[0])


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", clean_text(text)))


def detect_hurtado_level(objective: str) -> Dict[str, Any]:
    verb = first_word(objective)

    for level_name, payload in HURTADO_LEVELS.items():
        if verb in payload["verbs"]:
            return {
                "detected_verb": verb,
                "level": level_name,
                "suggested_research_types": payload["research_types"],
                "description": payload["description"],
                "status": "detected",
            }

    all_verbs = []
    for payload in HURTADO_LEVELS.values():
        all_verbs.extend(payload["verbs"])

    return {
        "detected_verb": verb,
        "level": "no_detectado",
        "suggested_research_types": [],
        "description": "No se detecto un verbo rector asociado a los niveles de objetivos usados por BiblioQuest.",
        "status": "review_required",
        "recommended_verbs": all_verbs,
    }


def validate_general_objective(objective: str) -> Dict[str, Any]:
    objective = clean_text(objective)
    checks = []
    recommendations = []
    score = 0

    if objective:
        checks.append({"criterion": "Existe objetivo general", "ok": True})
        score += 20
    else:
        checks.append({"criterion": "Existe objetivo general", "ok": False})
        recommendations.append("Redacta un objetivo general como logro cognitivo central de la investigacion.")

    if word_count(objective) >= 12:
        checks.append({"criterion": "Tiene desarrollo suficiente", "ok": True})
        score += 15
    else:
        checks.append({"criterion": "Tiene desarrollo suficiente", "ok": False})
        recommendations.append("Amplia el objetivo: debe incluir evento, unidad, contexto, temporalidad o finalidad cognitiva.")

    verb = first_word(objective)
    hurtado = detect_hurtado_level(objective)

    if hurtado["status"] == "detected":
        checks.append({"criterion": "Inicia con verbo cognitivo compatible con nivel de objetivo", "ok": True})
        score += 20
    else:
        checks.append({"criterion": "Inicia con verbo cognitivo compatible con nivel de objetivo", "ok": False})
        recommendations.append(
            "Considera iniciar con un verbo como analizar, describir, comparar, explicar, proponer o evaluar."
        )

    if verb in TASK_ONLY_VERBS:
        checks.append({"criterion": "No se limita a una actividad tecnica", "ok": False})
        recommendations.append(
            "El objetivo parece una tarea tecnica. Reformulalo como logro de conocimiento, no como accion operativa."
        )
    else:
        checks.append({"criterion": "No se limita a una actividad tecnica", "ok": True})
        score += 15

    event_terms = [
        "produccion",
        "estructura",
        "evolucion",
        "tendencia",
        "brecha",
        "campo",
        "red",
        "conocimiento",
        "literatura",
        "investigacion",
        "tematica",
        "cientifica",
    ]
    if any(term in objective.lower() for term in event_terms):
        checks.append({"criterion": "Sugiere evento de estudio bibliometrico", "ok": True})
        score += 10
    else:
        checks.append({"criterion": "Sugiere evento de estudio bibliometrico", "ok": False})
        recommendations.append(
            "Incluye con mayor claridad el evento de estudio: produccion cientifica, estructura tematica, redes, tendencias o brechas."
        )

    if re.search(r"\b(19|20)\d{2}\b", objective) or any(
        term in objective.lower() for term in ["periodo", "entre", "durante", "desde", "hasta"]
    ):
        checks.append({"criterion": "Incluye temporalidad o periodo", "ok": True})
        score += 10
    else:
        checks.append({"criterion": "Incluye temporalidad o periodo", "ok": False})
        recommendations.append("Agrega el periodo temporal de analisis o indica que sera delimitado en el protocolo.")

    if any(term in objective.lower() for term in ["para", "a fin de", "con el proposito de", "orientado a"]):
        checks.append({"criterion": "Declara finalidad cognitiva o uso esperado", "ok": True})
        score += 10
    else:
        checks.append({"criterion": "Declara finalidad cognitiva o uso esperado", "ok": False})
        recommendations.append("Agrega para que se analizara el campo: identificar tendencias, brechas, agenda futura o estructura.")

    if score >= 80:
        status = "solido"
    elif score >= 55:
        status = "requiere_ajustes"
    else:
        status = "debil"

    return {
        "score": score,
        "status": status,
        "detected_level": hurtado,
        "checks": checks,
        "recommendations": recommendations,
    }


def check_ozturk_fit(record: Dict[str, Any]) -> Dict[str, Any]:
    criteria = [
        ("Objetivo de investigacion declarado", record.get("general_objective", "")),
        ("Resultados esperados declarados", record.get("expected_results", "")),
        ("Pregunta principal declarada", record.get("main_question", "")),
        ("Preguntas especificas declaradas", record.get("specific_questions", [])),
        ("Justificacion del uso de bibliometria", record.get("bibliometric_justification", "")),
        ("Ajuste objetivo-pregunta-datos-analisis-interpretacion", record.get("objective_question_data_analysis_fit", "")),
    ]

    checks = []
    score = 0

    for criterion, value in criteria:
        ok = bool(value) and (not isinstance(value, list) or len(value) > 0)
        checks.append({"criterion": criterion, "ok": ok})
        if ok:
            score += 100 / len(criteria)

    score = round(score, 1)

    if score >= 85:
        status = "listo_para_bibliosearch"
    elif score >= 60:
        status = "requiere_ajustes_antes_de_buscar"
    else:
        status = "no_listo"

    recommendations = []
    if status != "listo_para_bibliosearch":
        recommendations.append(
            "Completa la alineacion entre objetivo, preguntas, resultados esperados, justificacion bibliometrica y plan de analisis."
        )

    return {
        "score": score,
        "status": status,
        "checks": checks,
        "recommendations": recommendations,
    }


def build_mirabal_i2e(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "intorno": clean_text(record.get("intorno", "")),
        "entorno": clean_text(record.get("entorno", "")),
        "extorno": clean_text(record.get("extorno", "")),
        "a3d": {
            "agil": "El protocolo debe permitir iteraciones rapidas entre objetivo, busqueda, corpus y lectura critica.",
            "digital": "El estudio se apoya en metadatos, bases academicas, software bibliometrico y trazabilidad digital.",
            "disruptiva": clean_text(record.get("transformative_projection", "")),
            "diferenciadora": "La diferenciacion dependera de la claridad del objetivo, la calidad del corpus y la interpretacion humana validada.",
        },
        "s3": {
            "soporte": clean_text(record.get("support", "")),
            "sustento": clean_text(record.get("sustenance", "")),
            "sostenimiento": clean_text(record.get("sustainability", "")),
        },
    }


def estimate_novelty_uncertainty(record: Dict[str, Any]) -> Dict[str, Any]:
    text = " ".join(
        [
            clean_text(record.get("generative_situation", "")),
            clean_text(record.get("scientific_curiosity", "")),
            clean_text(record.get("cognitive_purpose", "")),
            clean_text(record.get("transformative_projection", "")),
            clean_text(record.get("bibliometric_justification", "")),
            clean_text(record.get("extorno", "")),
        ]
    ).lower()

    novelty_signals = {
        "brecha_o_vacio": ["brecha", "vacio", "ausencia", "poco estudiado", "insuficiente"],
        "emergencia": ["emergente", "reciente", "nuevo", "actual", "tendencia"],
        "fragmentacion": ["fragmentado", "disperso", "desarticulado", "desconexion"],
        "region_o_contexto": ["latinoamerica", "venezuela", "sur global", "regional", "local"],
        "transformacion": ["transformar", "agenda", "propuesta", "innovacion", "creatividad", "inteligentizador"],
    }

    detected = []
    for signal, terms in novelty_signals.items():
        if any(term in text for term in terms):
            detected.append(signal)

    novelty_score = min(100, len(detected) * 20)

    missing_core = 0
    for field in ["general_objective", "main_question", "bibliometric_justification", "temporality"]:
        if not clean_text(record.get(field, "")):
            missing_core += 1

    uncertainty_score = min(100, 25 + missing_core * 18)

    if novelty_score >= 70:
        novelty_level = "alta"
    elif novelty_score >= 40:
        novelty_level = "media"
    else:
        novelty_level = "baja"

    if uncertainty_score >= 70:
        uncertainty_level = "alta"
    elif uncertainty_score >= 45:
        uncertainty_level = "moderada"
    else:
        uncertainty_level = "baja"

    return {
        "novelty_score": novelty_score,
        "novelty_level": novelty_level,
        "uncertainty_score": uncertainty_score,
        "uncertainty_level": uncertainty_level,
        "detected_signals": detected,
        "warning": (
            "La novedad cientifica no queda certificada por BiblioQuest. "
            "Esta estimacion es preliminar y debe validarse con busqueda sistematica, lectura critica y contraste experto."
        ),
    }


def build_objective_operationalization(record: Dict[str, Any]) -> List[Dict[str, str]]:
    objectives = ensure_list(record.get("specific_objectives", []))
    rows = []

    for idx, objective in enumerate(objectives, start=1):
        rows.append(
            {
                "objective_number": str(idx),
                "specific_objective": objective,
                "estimated_achievement": "Determinar evidencias e indicadores asociados al logro parcial del objetivo.",
                "vision": "Comprender como este objetivo contribuye al objetivo general.",
                "visualization": "Tabla, grafico, matriz, mapa o red segun corresponda.",
                "possible_evidence": "Metadatos bibliometricos, resultados descriptivos, redes, tendencias o lectura critica.",
            }
        )

    return rows


def build_biblioquest_record(input_data: BiblioQuestInput | Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(input_data, BiblioQuestInput):
        record = asdict(input_data)
    else:
        record = dict(input_data)

    record["specific_objectives"] = ensure_list(record.get("specific_objectives", []))
    record["specific_questions"] = ensure_list(record.get("specific_questions", []))
    record["created_at"] = datetime.now().isoformat(timespec="seconds")
    record["module"] = "BiblioQuest"
    record["slogan"] = "De la observacion al objetivo"
    record["methodological_note"] = (
        "Basado en la metodologia HOMI: sinergia de los aportes intelectuales de Hurtado de Barrera "
        "sobre formulacion holistica de objetivos de investigacion; Ozturk, Kocaman y Kanbach sobre "
        "diseno de investigacion bibliometrica; y Mirabal Gonzalez sobre I2E, A3D y 3S. "
        "El paradigma inteligentizador se incorpora como marco conceptual propio en desarrollo, "
        "sin referencia APA formal por ahora."
    )

    record["diagnostics"] = {
        "objective_validation": validate_general_objective(record.get("general_objective", "")),
        "ozturk_fit": check_ozturk_fit(record),
        "mirabal_i2e_a3d_s3": build_mirabal_i2e(record),
        "novelty_uncertainty": estimate_novelty_uncertainty(record),
        "objective_operationalization": build_objective_operationalization(record),
    }

    return record


def md_list(items: List[str]) -> str:
    if not items:
        return "- No especificado."
    return "\n".join([f"- {item}" for item in items])


def generate_protocol_markdown(record: Dict[str, Any]) -> str:
    diagnostics = record.get("diagnostics", {})
    obj_val = diagnostics.get("objective_validation", {})
    ozturk = diagnostics.get("ozturk_fit", {})
    novelty = diagnostics.get("novelty_uncertainty", {})
    i2e = diagnostics.get("mirabal_i2e_a3d_s3", {})
    operationalization = diagnostics.get("objective_operationalization", [])

    md = f"""# Ficha BiblioQuest

## De la observacion al objetivo

**Fecha:** {record.get("created_at", "")}  
**Investigador:** {record.get("researcher_name", "") or "No especificado"}  
**Proyecto:** {record.get("project_title", "") or "No especificado"}  
**Tema tentativo:** {record.get("tentative_topic", "") or "No especificado"}  
**Area:** {record.get("research_area", "") or "No especificado"}

---

## Nota metodologica

{record.get("methodological_note", "")}

---

## 1. Observacion inicial y situacion generadora

**Situacion generadora:**  
{record.get("generative_situation", "") or "No especificado."}

**Curiosidad cientifica:**  
{record.get("scientific_curiosity", "") or "No especificado."}

**Proposito cognitivo:**  
{record.get("cognitive_purpose", "") or "No especificado."}

**Proyeccion transformadora:**  
{record.get("transformative_projection", "") or "No especificado."}

---

## 2. Componentes metodologicos segun Hurtado

**Evento de estudio:** {record.get("study_event", "") or "No especificado"}  
**Unidad de analisis:** {record.get("unit_of_analysis", "") or "No especificado"}  
**Contexto:** {record.get("context", "") or "No especificado"}  
**Temporalidad:** {record.get("temporality", "") or "No especificado"}

---

## 3. Objetivo general

{record.get("general_objective", "") or "No especificado."}

**Validacion BiblioQuest:** {obj_val.get("status", "No evaluado")}  
**Puntaje:** {obj_val.get("score", "No evaluado")}/100  
**Nivel detectado segun Hurtado:** {obj_val.get("detected_level", {}).get("level", "No detectado")}  
**Verbo detectado:** {obj_val.get("detected_level", {}).get("detected_verb", "No detectado")}

### Recomendaciones sobre el objetivo

{md_list(obj_val.get("recommendations", []))}

---

## 4. Objetivos especificos

{md_list(record.get("specific_objectives", []))}

---

## 5. Pregunta principal

{record.get("main_question", "") or "No especificado."}

## 6. Preguntas especificas

{md_list(record.get("specific_questions", []))}

---

## 7. Resultados esperados

{record.get("expected_results", "") or "No especificado."}

---

## 8. Justificacion del uso de bibliometria

{record.get("bibliometric_justification", "") or "No especificado."}

---

## 9. Ajuste objetivo-pregunta-datos-analisis-interpretacion

{record.get("objective_question_data_analysis_fit", "") or "No especificado."}

**Estado de ajuste segun criterio bibliometrico:** {ozturk.get("status", "No evaluado")}  
**Puntaje de ajuste:** {ozturk.get("score", "No evaluado")}/100

### Recomendaciones de ajuste

{md_list(ozturk.get("recommendations", []))}

---

## 10. Lectura I2E segun Mirabal

**Intorno:**  
{i2e.get("intorno", "") or "No especificado."}

**Entorno:**  
{i2e.get("entorno", "") or "No especificado."}

**Extorno:**  
{i2e.get("extorno", "") or "No especificado."}

---

## 11. A3D y 3S

### A3D

- **Agil:** {i2e.get("a3d", {}).get("agil", "")}
- **Digital:** {i2e.get("a3d", {}).get("digital", "")}
- **Disruptiva:** {i2e.get("a3d", {}).get("disruptiva", "") or "No especificado."}
- **Diferenciadora:** {i2e.get("a3d", {}).get("diferenciadora", "")}

### 3S

- **Soporte:** {i2e.get("s3", {}).get("soporte", "") or "No especificado."}
- **Sustento:** {i2e.get("s3", {}).get("sustento", "") or "No especificado."}
- **Sostenimiento:** {i2e.get("s3", {}).get("sostenimiento", "") or "No especificado."}

---

## 12. Novedad potencial e incertidumbre

**Novedad potencial:** {novelty.get("novelty_level", "No evaluada")}  
**Puntaje de novedad:** {novelty.get("novelty_score", "No evaluado")}/100  
**Incertidumbre:** {novelty.get("uncertainty_level", "No evaluada")}  
**Puntaje de incertidumbre:** {novelty.get("uncertainty_score", "No evaluado")}/100  

**Senales detectadas:**  
{md_list(novelty.get("detected_signals", []))}

**Advertencia:**  
{novelty.get("warning", "")}

---

## 13. Operacionalizacion preliminar de objetivos

| Nº | Objetivo especifico | Estimacion | Vision | Visualizacion | Evidencia posible |
|---:|---|---|---|---|---|
"""

    if operationalization:
        for row in operationalization:
            md += (
                f"| {row['objective_number']} | {row['specific_objective']} | "
                f"{row['estimated_achievement']} | {row['vision']} | "
                f"{row['visualization']} | {row['possible_evidence']} |\n"
            )
    else:
        md += "| - | No especificado | - | - | - | - |\n"

    md += f"""

---

## 14. Comparacion entre proposito y objetivo general

**Proposito de investigacion:**  
{record.get("cognitive_purpose", "") or "No especificado."}

**Objetivo general de investigacion:**  
{record.get("general_objective", "") or "No especificado."}

**Lectura BiblioQuest:**  
El proposito expresa la intencion amplia y el horizonte de sentido de la investigacion. El objetivo general debe expresar el logro cognitivo central, delimitado y evaluable que orienta el metodo, los datos, el analisis y la interpretacion.

---

## 15. Recomendacion para BiblioSearch

- Usar el objetivo general y la pregunta principal como base para construir terminos nucleares.
- Derivar palabras clave desde el evento de estudio, la unidad de analisis, el contexto y la temporalidad.
- Traducir terminos principales al ingles cuando la fuente bibliografica lo requiera.
- Construir al menos tres versiones de busqueda: amplia, intermedia y precisa.
- Registrar cada version de busqueda para mantener trazabilidad.

---

## 16. Dictamen BiblioQuest

**Estado del objetivo:** {obj_val.get("status", "No evaluado")}  
**Estado del ajuste bibliometrico:** {ozturk.get("status", "No evaluado")}  
**Recomendacion general:** avanzar a BiblioSearch solo cuando objetivo, preguntas, resultados esperados y justificacion bibliometrica esten suficientemente alineados.

---

## Referencias metodologicas preliminares

Hurtado de Barrera, J. (2014). *Como formular objetivos de investigacion: Un acercamiento desde la investigacion holistica*. Quiron Ediciones.

Ozturk, O., Kocaman, R., & Kanbach, D. K. (2024). How to design bibliometric research: An overview and a framework proposal. *Review of Managerial Science, 18*(11), 3333-3361. https://doi.org/10.1007/s11846-024-00738-0

Mirabal Gonzalez, J. F. (s. f.). *El arbol para la innovacion: Transformando la empresa a la economia digital*. OEM.
"""
    return md


def save_protocol_json(record: Dict[str, Any], path: Path = DEFAULT_JSON_PATH) -> Path:
    ensure_dirs()
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def save_protocol_markdown(record: Dict[str, Any], path: Path = DEFAULT_MD_PATH) -> Path:
    ensure_dirs()
    md = generate_protocol_markdown(record)
    path.write_text(md, encoding="utf-8")
    return path


def generate_biblioquest_protocol(
    input_data: BiblioQuestInput | Dict[str, Any],
    json_path: Path = DEFAULT_JSON_PATH,
    md_path: Path = DEFAULT_MD_PATH,
) -> Dict[str, Any]:
    record = build_biblioquest_record(input_data)
    json_file = save_protocol_json(record, json_path)
    md_file = save_protocol_markdown(record, md_path)

    return {
        "record": record,
        "json_path": str(json_file),
        "markdown_path": str(md_file),
    }


def demo_input() -> BiblioQuestInput:
    return BiblioQuestInput(
        researcher_name="Investigador BiblioIntel",
        project_title="Protocolo inicial de investigacion bibliometrica",
        tentative_topic="Inteligencia artificial y creatividad cientifica",
        research_area="Gestion de investigacion y desarrollo",
        generative_situation=(
            "Se observa un crecimiento del debate academico sobre inteligencia artificial y creatividad, "
            "pero con posible dispersion conceptual, diferencias regionales y vacios sobre su aplicacion "
            "en la produccion de conocimiento cientifico."
        ),
        scientific_curiosity=(
            "Comprender como se ha configurado el campo y que tendencias, actores, regiones y brechas "
            "aparecen en la literatura cientifica."
        ),
        cognitive_purpose=(
            "Orientar una investigacion bibliometrica que permita comprender la estructura del campo "
            "y apoyar la construccion de una agenda futura."
        ),
        transformative_projection=(
            "Transformar la evidencia bibliometrica en rutas investigativas, preguntas emergentes "
            "y oportunidades de produccion cientifica."
        ),
        study_event="Produccion cientifica, estructura tematica, redes y brechas sobre inteligencia artificial y creatividad.",
        unit_of_analysis="Publicaciones cientificas, autores, instituciones, paises, fuentes, palabras clave y citas.",
        context="Literatura academica recuperada desde bases bibliograficas abiertas y/o indexadas.",
        temporality="2015-2026",
        general_objective=(
            "Analizar la estructura cientifica, tematica y evolutiva de la produccion academica sobre "
            "inteligencia artificial y creatividad durante el periodo 2015-2026, a fin de identificar "
            "tendencias, actores, brechas y oportunidades de investigacion futura."
        ),
        specific_objectives=[
            "Caracterizar la produccion cientifica recuperada por ano, fuente, tipo documental y citas.",
            "Identificar los principales autores, instituciones, paises y fuentes vinculados al campo.",
            "Analizar patrones tematicos y posibles redes de relacion entre terminos, autores y documentos.",
            "Detectar brechas preliminares, areas poco visibles y oportunidades de investigacion futura.",
        ],
        main_question=(
            "Como se estructura y evoluciona la produccion cientifica sobre inteligencia artificial y creatividad "
            "durante el periodo 2015-2026?"
        ),
        specific_questions=[
            "Cual es la evolucion temporal de la produccion cientifica del campo?",
            "Que autores, instituciones, paises y fuentes concentran mayor visibilidad?",
            "Que tendencias tematicas y patrones de relacion aparecen en los metadatos recuperados?",
            "Que brechas preliminares y oportunidades de investigacion futura pueden identificarse?",
        ],
        expected_results=(
            "Mapa preliminar del campo, indicadores de desempeno, tendencias, actores relevantes, "
            "brechas preliminares y agenda inicial de investigacion."
        ),
        bibliometric_justification=(
            "La bibliometria es pertinente porque permite analizar de manera estructurada la produccion cientifica, "
            "identificar patrones de crecimiento, actores, fuentes, citacion, tendencias tematicas y vacios de investigacion."
        ),
        objective_question_data_analysis_fit=(
            "El objetivo general se relaciona con preguntas sobre estructura, evolucion y brechas; estas preguntas "
            "requieren metadatos bibliograficos, analisis descriptivo, mapas, rankings, redes e interpretacion critica."
        ),
        intorno="Necesidad del investigador de formular un estado del arte riguroso y una agenda doctoral pertinente.",
        entorno="Produccion cientifica visible sobre IA, creatividad, conocimiento y educacion superior.",
        extorno="Aportes posibles desde cienciometria, gestion de I+D, filosofia de la ciencia y estudios sobre IA.",
        support="BiblioIntel, OpenAlex, repositorio GitHub, Streamlit, reportes reproducibles.",
        sustenance="Marco metodologico HOMI, bibliometria, bibliometrologia y paradigma inteligentizador.",
        sustainability="Vigilancia cientifica, actualizacion del corpus, mejora continua y validacion humana.",
    )


if __name__ == "__main__":
    result = generate_biblioquest_protocol(demo_input())
    print("BiblioQuest ejecutado correctamente.")
    print(f"JSON generado en: {result['json_path']}")
    print(f"Markdown generado en: {result['markdown_path']}")