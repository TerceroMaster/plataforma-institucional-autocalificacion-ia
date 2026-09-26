# 🎓 UJAT Evaluador Automático Institucional

Un ecosistema institucional de vanguardia diseñado para la **Universidad Juárez Autónoma de Tabasco (UJAT)**. Esta plataforma permite a los docentes automatizar la evaluación de exámenes de preguntas abiertas y de opción múltiple mediante el uso de enjambres de Inteligencia Artificial (Agentes Cognitivos).

La plataforma estandariza las rúbricas de la universidad, garantizando que todos los alumnos sean calificados de manera justa, estandarizada y expedita, sin sobrecargar administrativamente a los profesores.

## ✨ Características Principales

*   **⚡ Calificación Inmediata y Escalable:** Los alumnos reciben su resultado en segundos tras enviar el examen. La plataforma puede evaluar a miles de alumnos de forma simultánea.
*   **👁️ Sistema Anti-Trampas Riguroso:** Monitoreo y detección automática de cambio de pestañas/ventanas; si el alumno intenta buscar en internet, el examen se suspende y envía una alerta al profesor.
*   **🎯 Alineación a Rúbricas Universitarias:** El profesor mantiene el control total; la IA respeta estrictamente los criterios docentes cargados en sus archivos (PDF/Word).
*   **📄 Expedientes Oficiales (PDF):** Generación automática de reportes institucionales con retroalimentación pedagógica individualizada, indicando exactamente en qué falló el estudiante y qué temas debe repasar.

## 🤖 Arquitectura Multi-Agente (LangGraph)

El sistema opera bajo un enjambre autónomo impulsado por **LangGraph**, modelos de **OpenAI** y telemetría de observabilidad de **LangSmith** para auditorías académicas.

1.  **🕵️ Agente Analista (Extractor Contextual):** Lee las respuestas del alumno y extrae meticulosamente cada concepto clave escrito, filtrando el "ruido" o texto de relleno.
2.  **⚖️ Agente Juez Evaluador (Zero-Shot Reasoner):** Cruza la rúbrica oficial del profesor con el análisis del Agente 1. No busca "palabras clave" exactas, sino que evalúa la **comprensión semántica** del alumno. Asigna los puntos justos.
3.  **👨‍🏫 Agente Pedagogo (Retroalimentador):** Toma la sentencia del Juez y redacta una explicación constructiva y empática para el alumno, indicando exactamente qué falló y recomendando los temas del programa educativo que debe volver a estudiar.
4.  **📈 Agente Analista de Patrones Grupales (Class Insights):** Identifica la tendencia general de conocimiento y los patrones de error sistemáticos de todo un salón para generar una *Alerta Académica* al maestro.

## 🛡️ Ética, Seguridad y Gobernanza (ISO/IEC 42001:2023)

La plataforma adopta los más altos estándares internacionales para el uso seguro y responsable de la Inteligencia Artificial, alineándose a la normativa **ISO/IEC 42001:2023**.

### Ciberseguridad y Prevención de Ataques
Para garantizar la integridad institucional, el sistema multi-agente está blindado contra vulnerabilidades de IA generativa:
*   **Prevención de Jailbreaking:** Filtros estrictos (*System Prompts* reforzados) que impiden a los alumnos insertar comandos ocultos para forzar un "10/10".
*   **Protección contra Prompt Injection:** El texto del alumno es procesado en una caja de arena lógica. El Agente Evaluador jamás obedece instrucciones contenidas en las respuestas.
*   **Privacidad de Datos:** La información de los estudiantes no se utiliza para entrenar modelos públicos.

## 📊 Observabilidad y Transparencia (White-box AI)

A diferencia de sistemas tradicionales donde la calificación es "mágica y opaca", nuestro sistema utiliza **LangSmith** para auditar cada microsegundo del pensamiento de los agentes (Rastreos, Latencia, Tokens y Costo Monetario). Esto garantiza la **Auditoría Académica** y la **Reproducibilidad Científica**.

## 🚀 Instalación y Despliegue Local

1.  Clona este repositorio.
2.  Navega a la carpeta principal (o a `autograder_ujat` dependiendo de tu estructura).
3.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    ```
4.  Crea un archivo `.env` en la raíz con tus llaves de acceso:
    ```env
    OPENAI_API_KEY="sk-proj-tu-llave-aqui"
    LANGCHAIN_API_KEY="lsv2_pt_tu-llave-aqui"
    LANGCHAIN_TRACING_V2="true"
    LANGCHAIN_PROJECT="autograder_ujat"
    ```
5.  Ejecuta la aplicación:
    ```bash
    streamlit run app.py
    ```

## 🛠️ Trabajos a Futuro

1.  Migración a PostgreSQL para escalabilidad en Producción Real.
2.  Dashboard de Analíticas para Directores de División.
3.  Descarga de Reportes y Actas en Excel para el SIAE.
4.  Generación Automática de Exámenes desde PDFs de clases.
5.  Detección Semántica de Plagio (Cross-Student) mediante Embeddings.
6.  Integración nativa con Microsoft Teams y Google Classroom vía LTI.
7.  Exámenes orales y multimodales (Speech-to-Text).
8.  Agente Tutor de Recuperación interactivo.
9.  Proctoring Biométrico Edge-AI.
10. Trazabilidad de Calificaciones vía Blockchain educativa.

---
**Desarrollado para la Universidad Juárez Autónoma de Tabasco (UJAT) - Legado Universitario.**
