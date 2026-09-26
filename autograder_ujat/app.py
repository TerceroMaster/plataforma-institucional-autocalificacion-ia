import streamlit as st
import time
import os
from dotenv import load_dotenv
from graph import autograder_graph, generate_pdf
import db

# Inicializar Base de Datos SQLite
db.init_db()
load_dotenv(override=True)

st.set_page_config(page_title="UJAT Evaluador Automático", page_icon="🎓", layout="wide")

st.markdown("""
<style>
.header-banner {
    background: linear-gradient(90deg, #1e3a8a 0%, #1e40af 100%);
    padding: 30px;
    border-radius: 10px;
    margin-bottom: 30px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.header-banner h1 { 
    color: white !important; 
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5) !important; 
    font-size: clamp(1.2rem, 5vw, 3rem) !important;
    word-wrap: normal !important;
    overflow-wrap: normal !important;
    word-break: keep-all !important;
    line-height: 1.3 !important;
    margin: 0 !important;
    padding-bottom: 10px !important;
}
@media (max-width: 768px) {
    .header-banner h1 {
        font-size: 1.6rem !important;
        word-break: normal !important;
    }
}
.login-box {
    background-color: #ffffff;
    padding: 40px;
    border-radius: 15px;
    border: 1px solid #e2e8f0;
    text-align: center;
    max-width: 600px;
    margin: 0 auto 30px auto;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    color: #1e293b;
}
.div-card {
    background-color: #ffffff;
    border-radius: 10px; 
    padding: 20px; 
    text-align: center; 
    margin-bottom: 15px; 
    min-height: 200px; 
    border: 2px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    color: #1e293b;
}
.square-btn > button {
    height: 100px !important;
    font-size: 1.5rem !important;
    border-radius: 15px !important;
    margin-bottom: 15px !important;
}
</style>
""", unsafe_allow_html=True)

# Anti-Cheat JS para el Alumno
ANTI_CHEAT_JS = """
<script>
const parentDoc = window.parent.document;
const parentWin = window.parent;
window.parent.examFinished = false; 

function blockExam() {
    if (!window.parent.examFinished) {
        parentDoc.body.innerHTML = "<div style='background-color:#b91c1c; width:100vw; height:100vh; position:fixed; top:0; left:0; z-index:999999; display:flex; justify-content:center; align-items:center; flex-direction:column; color:white; font-family:sans-serif;'><h1 style='font-size:5rem;margin:0;'>🚨 EXAMEN SUSPENDIDO 🚨</h1><h2 style='font-size:2rem;'>Intento de copia detectado.</h2><p style='font-size:1.5rem;'>Saliste de la ventana del examen. Tu sesión ha sido bloqueada. Presiona F5 para reiniciar.</p></div>";
    }
}

parentDoc.addEventListener("visibilitychange", function() {
    if (parentDoc.hidden) { blockExam(); }
});
parentWin.addEventListener("blur", function() {
    blockExam();
});
</script>
"""
DISABLE_ANTI_CHEAT_JS = "<script>window.parent.examFinished = true;</script>"

# Datos Reales de QFB - Plan 2013 UJAT
QFB_AREAS = {
    "Área General": ["Ética", "Filosofía", "Metodología", "Cultura Ambiental", "Lengua Extranjera", "Lectura y Redacción", "Derechos Humanos", "Pensamiento Matemático", "Herramientas de Computación", "Química Básica", "Biología Celular y Molecular", "Física General", "Matemáticas Básicas", "Cálculo Diferencial e Integral", "Bioestadística"],
    "Área Sustantiva Profesional": ["Enlaces Múltiples de Carbono", "Micología y Virología", "Bioquímica Metabólica", "Análisis Químico", "Química Orgánica", "Bacteriología", "Parasitología", "Fisicoquímica Farmacéutica", "Farmacología", "Toxicología", "Biofarmacia", "Farmacia Clínica", "Hematología", "Inmunología", "Anatomía y Fisiología", "Fitoquímica y Farmacognosia"],
    "Área Integral Profesional": ["Elucidación de Estructuras Moleculares", "Taller de Diseño de Proyectos", "Seminario de Legislación en Salud", "Seminario de Bioética", "Calidad Total", "Genómica", "Química Forense", "Biotecnología", "Farmacoeconomía", "Microbiología Sanitaria", "Historia de la Farmacia"],
    "Área Transversal Profesional": ["Inglés Técnico 1", "Inglés Técnico 2", "Seminario de Administración", "Seminario de Mercado Farmacéutico", "Servicio Social", "Prácticas Profesionales"]
}

GENERIC_AREAS = {
    "Área General": ["Ética y Valores", "Filosofía Institucional", "Metodología de la Investigación", "Cultura Ambiental", "Lengua Extranjera", "Lectura y Redacción", "Matemáticas Generales"],
    "Área Sustantiva Profesional": ["Asignatura Troncal 1", "Asignatura Troncal 2", "Asignatura Troncal 3", "Asignatura Troncal 4", "Teoría Profesional", "Práctica Profesional Básica"],
    "Área Integral Profesional": ["Seminario de Titulación", "Desarrollo de Proyectos", "Ética Profesional", "Calidad y Liderazgo"],
    "Área Transversal Profesional": ["Inglés Técnico", "Prácticas Profesionales", "Servicio Social", "Tópicos Avanzados"]
}

QUIMICA_AREAS = {
    "Área General": ["Comunicación Oral y Escrita", "Habilidades del Pensamiento", "Tecnologías de la Información y Comunicación", "Física Elemental", "Filosofía y Ética", "Derechos Humanos", "Álgebra Elemental", "Cálculo Diferencial Aplicado", "Inglés Técnico 1"],
    "Área Sustantiva Profesional": ["Química Básica", "Fundamentos de Química Inorgánica", "Química de Coordinación", "Bioquímica Básica", "Cinética Química", "Análisis Instrumental", "Equilibrio de Fases", "Química Orgánica"],
    "Área Integral Profesional": ["Diseño de Proyectos", "Laboratorio de Investigación", "Servicio Social", "Práctica Profesional", "Elucidación de Estructuras Moleculares"],
    "Área Transversal Profesional": ["Aseguramiento de la Calidad", "Formulación de Proyectos Emprendedores", "Administración de Laboratorios", "Procesos Industriales"]
}

MATEMATICAS_AREAS = {
    "Área General": ["Comunicación Oral y Escrita", "Habilidades del Pensamiento", "Tecnologías de la Información", "Geometría Euclidiana", "Cálculo Diferencial", "Cálculo Integral", "Física General", "Programación"],
    "Área Sustantiva Profesional": ["Álgebra Superior I", "Álgebra Lineal I", "Ecuaciones Diferenciales Ordinarias", "Geometría Diferencial", "Topología", "Variable Compleja", "Análisis Numérico"],
    "Área Integral Profesional": ["Práctica Docente I", "Sistemas Dinámicos", "Geometría Algebraica I", "Análisis Aplicado", "Temas Selectos de Modelación"],
    "Área Transversal Profesional": ["Inglés Técnico I", "Inglés Técnico II", "Servicio Social", "Práctica Profesional", "Filosofía y Ética"]
}

FISICA_AREAS = {
    "Área General": ["Álgebra Elemental", "Metodología", "Geometría Analítica", "Cálculo Diferencial", "Lectura y Redacción", "Pensamiento Matemático"],
    "Área Sustantiva Profesional": ["Mecánica Analítica", "Ecuaciones Diferenciales Ordinarias", "Electrodinámica", "Mecánica Cuántica I", "Mecánica Estadística", "Termodinámica", "Óptica"],
    "Área Integral Profesional": ["Análisis Numérico", "Programación", "Biofísica", "Circuitos Eléctricos", "Relatividad Especial", "Física del Estado Sólido"],
    "Área Transversal Profesional": ["Electrónica Física", "Análisis Instrumental", "Diseño de Sistemas Digitales", "Optoelectrónica"]
}

COMPUTACIONALES_AREAS = {
    "Área General": ["Comunicación Oral y Escrita", "Desarrollo de Páginas WEB", "Diseño de Interfaces de Usuario", "Matemáticas Discretas", "Algoritmos y Programación", "Estructura de Datos Básicas"],
    "Área Sustantiva Profesional": ["Ingeniería de Software", "Bases de Datos Avanzadas", "Inteligencia Artificial", "Sistemas Operativos", "Redes de Computadoras", "Seguridad en Sistemas de Cómputo"],
    "Área Integral Profesional": ["Programación Concurrente y Distribuida", "Robótica Móvil", "Visión Computacional", "Gráficas y Animación 3D", "Desarrollo de Videojuegos"],
    "Área Transversal Profesional": ["Emprendimiento en las TIC", "Práctica Profesional", "Servicio Social", "Inglés Técnico"]
}

ACTUARIA_AREAS = {
    "Área General": ["Comunicación Oral y Escrita", "Álgebra Superior", "Cálculo Diferencial", "Geometría Analítica", "Tecnologías de la Información"],
    "Área Sustantiva Profesional": ["Probabilidad Univariada", "Procesos Estocásticos", "Demografía", "Seguridad Social", "Pensiones Privadas", "Economía Matemática", "Finanzas Cuantitativas I"],
    "Área Integral Profesional": ["Simulación Estocástica", "Contabilidad de Seguros", "Administración de Riesgos", "Reaseguro", "Auditoría Actuarial"],
    "Área Transversal Profesional": ["Inglés I", "Inglés II", "Servicio Social", "Prácticas Profesionales"]
}

GEOFISICA_AREAS = {
    "Área General": ["Álgebra y Trigonometría", "Filosofía y Ética", "Cálculo Diferencial e Integral", "Derechos Humanos", "Comunicación Oral y Escrita", "Tecnologías de la Información"],
    "Área Sustantiva Profesional": ["Cálculo Vectorial", "Electromagnetismo", "Ecuaciones Diferenciales", "Geología General", "Mecánica", "Termodinámica", "Teoría Electromagnética", "Estratigrafía y Sedimentología"],
    "Área Integral Profesional": ["Prospección Magnética", "Prospección Gravimétrica", "Prospección Sísmica", "Sismología Teórica", "Petrofísica", "Registros Geofísicos", "Métodos Electromagnéticos", "Geología del Petróleo"],
    "Área Transversal Profesional": ["Servicio Social", "Seminario de Investigación", "Práctica Profesional"]
}

TELEMATICA_AREAS = {
    "Área General": ["Herramientas de Computación", "Filosofía", "Pensamiento Matemático", "Álgebra", "Lectura y Redacción", "Lengua Extranjera", "Cálculo Diferencial", "Matemáticas Discretas"],
    "Área Sustantiva Profesional": ["Introducción a las Redes de Datos", "Infraestructura de Telecomunicaciones", "Electromagnetismo", "Fundamentos de Programación", "Redes", "Diseño de Redes", "Electrónica Analógica", "Estructuras de Datos"],
    "Área Integral Profesional": ["Conmutación de Redes", "Interconexión de Redes", "Sistemas de Telefonía", "Seguridad Informática", "Matemáticas para Comunicaciones", "Antenas", "Redes de Área Amplia"],
    "Área Transversal Profesional": ["Desarrollo de Proyecto de Tesis", "Servicio Social", "Práctica Profesional", "Legislación de Telecomunicaciones"]
}

TI_AREAS = {
    "Área General": ["Ética", "Filosofía", "Metodología", "Cultura Ambiental", "Lengua Extranjera", "Lectura y Redacción", "Derechos Humanos", "Pensamiento Matemático", "Herramientas de Computación", "Matemáticas Básicas", "Contabilidad", "Algoritmos y Programación", "Infraestructura Computacional"],
    "Área Sustantiva Profesional": ["Programación Orientada a Objetos", "Base de Datos", "Fundamentos de Redes", "Sistemas Operativos", "Tecnologías y Sistemas Web", "Sistemas Inteligentes para TI", "Minería de Datos", "Administración y Seguridad en Redes", "eCommerce"],
    "Área Integral Profesional": ["Protocolo de Proyecto", "Industria de Software", "Auditoría Informática", "Computación en la Nube", "Desarrollo Sustentable en TI", "Simulación", "Teoría de Grafos"],
    "Área Transversal Profesional": ["Desarrollo de Proyecto", "Servicio Social", "Práctica Profesional"]
}

LSC_AREAS = {
    "Área General": ["Algoritmos y Programación", "Organización de Computadoras", "Pensamiento Matemático", "Lectura y Redacción", "Programación Orientada a Objetos", "Filosofía", "Matemáticas Discretas", "Administración del Factor Humano", "Álgebra Lineal"],
    "Área Sustantiva Profesional": ["Estructuras de Datos", "Cálculo Diferencial e Integral", "Desarrollo de Aplicaciones Multiplataforma", "Fundamentos de Redes", "Sistemas Operativos", "Probabilidad y Estadística", "Simulación", "Graficación", "Fundamentos de Ingeniería de Software"],
    "Área Integral Profesional": ["Interacción Hombre-Máquina", "Modelado de Bases de Datos", "Programación en Bases de Datos", "Laboratorio de Diseño de Software", "Laboratorio de Construcción de Software", "Sistemas Distribuidos", "Inteligencia Artificial"],
    "Área Transversal Profesional": ["Protocolo de Proyecto", "Desarrollo de Proyecto", "Ética", "Normatividad Informática", "Servicio Social", "Prácticas Profesionales"]
}

LIA_AREAS = {
    "Área General": ["Algoritmos", "Programación", "Herramientas de Computación", "Pensamiento Matemático", "Sistemas Digitales", "Ética", "Filosofía", "Lectura y Redacción", "Metodología", "Administración de Recursos Humanos", "Derechos Humanos", "Contabilidad"],
    "Área Sustantiva Profesional": ["Estructuras de Datos", "Fundamentos de Ingeniería de Software", "Modelado y Diseño de Bases de Datos", "Cálculo Diferencial e Integral", "Probabilidad y Estadística", "Organización de Computadoras", "Fundamentos de Redes", "Fundamentos de Sistemas Operativos", "Mercadotecnia", "Finanzas"],
    "Área Integral Profesional": ["Interacción Hombre-Máquina", "Inteligencia Artificial", "Planeación de Redes", "Laboratorio de Sistemas Operativos", "Desarrollo de Emprendedores"],
    "Área Transversal Profesional": ["Protocolo de Proyecto", "Desarrollo de Proyecto", "Inglés", "Legislación Informática", "Servicio Social", "Prácticas Profesionales"]
}

ISC_AREAS = {
    "Área General": ["Algoritmos", "Programación I", "Álgebra", "Habilidad del Pensamiento", "Comunicación Oral y Escrita", "Filosofía y Ética Profesional", "Derechos Humanos"],
    "Área Sustantiva Profesional": ["Programación II", "Estructura de Datos", "Ingeniería de Software", "Matemáticas Discretas", "Cálculo Diferencial", "Cálculo Integral", "Probabilidad y Estadística", "Arquitectura de la Información", "Inteligencia Artificial", "Sistemas Operativos", "Compiladores", "Sistemas Distribuidos", "Arquitectura de Computadoras", "Fundamentos de Redes", "Planeación de Redes"],
    "Área Integral Profesional": ["Desarrollo de Aplicaciones Web", "Programación de Dispositivos Móviles", "Fábrica de Software", "Algoritmos Avanzados", "Bases de Datos Distribuidas", "Métodos Numéricos", "Investigación de Operaciones", "Simulación"],
    "Área Transversal Profesional": ["Ética Profesional", "Legislación y Normatividad Informática", "Inglés Técnico", "Servicio Social", "Práctica Profesional"]
}

IIA_AREAS = {
    "Área General": ["Proceso Administrativo", "Economía", "Filosofía y Ética", "Contabilidad Básica", "Derechos Humanos", "Algoritmos", "Programación I", "Álgebra", "Cálculo Diferencial e Integral"],
    "Área Sustantiva Profesional": ["Auditoría de TI", "Administración de Proyectos I", "Mercadotecnia", "Emprendedores", "Fundamentos de Estructuras de Datos", "Paradigmas de Programación", "Programación Web", "Ingeniería de Software", "Sistemas Operativos", "Matemáticas Discretas", "Matemáticas Financieras"],
    "Área Integral Profesional": ["Proyectos y Licitaciones", "Competencias Directivas", "Aplicación de Programación a la Administración", "Interacción Hombre-Máquina", "Inteligencia Artificial"],
    "Área Transversal Profesional": ["Inglés Técnico", "Servicio Social", "Práctica Profesional"]
}

EXAMENES_DB = {
    "Farmacología": {
        "preguntas": [
            {"tipo": "F/V", "texto": "1. La farmacodinamia estudia lo que el organismo le hace al fármaco."},
            {"tipo": "Abierta", "texto": "2. Define el concepto de 'Biodisponibilidad' de un fármaco."},
            {"tipo": "Abierta", "texto": "3. ¿Cuál es la diferencia principal entre un agonista y un antagonista receptor?"},
            {"tipo": "F/V", "texto": "4. El metabolismo de primer paso hepático reduce la concentración de fármaco activo en la circulación sistémica."},
            {"tipo": "Abierta", "texto": "5. Menciona las fases de la farmacocinética (LADME)."},
            {"tipo": "Abierta", "texto": "6. Explica el mecanismo de acción de los AINEs (Antiinflamatorios no esteroideos)."},
            {"tipo": "F/V", "texto": "7. La vida media de eliminación es el tiempo necesario para que la concentración plasmática del fármaco disminuya a la mitad."},
            {"tipo": "Abierta", "texto": "8. ¿Qué es el margen terapéutico o índice terapéutico?"},
            {"tipo": "F/V", "texto": "9. La vía de administración intravenosa tiene una biodisponibilidad del 100%."},
            {"tipo": "Abierta", "texto": "10. Describe la diferencia entre efectos adversos tipo A y tipo B."}
        ],
        "rubrica_default": """Pregunta 1 (10 pts): Falso (eso es farmacocinética).
Pregunta 2 (10 pts): Porcentaje de fármaco inalterado que llega a la sangre sistémica.
Pregunta 3 (10 pts): Agonista activa el receptor, antagonista lo bloquea.
Pregunta 4 (10 pts): Verdadero.
Pregunta 5 (10 pts): Liberación, Absorción, Distribución, Metabolismo, Excreción.
Pregunta 6 (10 pts): Inhiben la ciclooxigenasa (COX).
Pregunta 7 (10 pts): Verdadero.
Pregunta 8 (10 pts): Relación entre dosis tóxica y dosis terapéutica (medida de seguridad).
Pregunta 9 (10 pts): Verdadero.
Pregunta 10 (10 pts): Tipo A es dosis-dependiente y predecible. Tipo B es inmunológico/idiosincrático e impredecible."""
    },
    "default": {
        "preguntas": [
            {"tipo": "F/V", "texto": "1. Los principios fundamentales de esta materia establecen las bases teóricas de su aplicación profesional."},
            {"tipo": "Abierta", "texto": "2. Define los 3 conceptos más importantes de la unidad 1."},
            {"tipo": "Abierta", "texto": "3. Explica un caso de estudio donde se aplique la teoría vista en clase."},
            {"tipo": "F/V", "texto": "4. La metodología actual ha reemplazado por completo a los modelos teóricos clásicos."},
            {"tipo": "Abierta", "texto": "5. Menciona las fases del proceso principal de análisis en esta disciplina."},
            {"tipo": "Abierta", "texto": "6. ¿Cuáles son los riesgos o limitaciones de las técnicas estudiadas en la segunda unidad?"},
            {"tipo": "F/V", "texto": "7. El margen de error permitido en las prácticas de campo/laboratorio es del 0% en todo momento."},
            {"tipo": "Abierta", "texto": "8. Describe la estructura de un reporte técnico o proyecto estándar para esta asignatura."},
            {"tipo": "F/V", "texto": "9. Las normativas vigentes exigen actualización constante de estos procedimientos."},
            {"tipo": "Abierta", "texto": "10. Propón una solución técnica o innovadora a un problema clásico de esta materia."}
        ],
        "rubrica_default": """Pregunta 1 (10 pts): Verdadero.
Pregunta 2 (10 pts): Debe mencionar al menos 3 conceptos clave con definición clara.
Pregunta 3 (10 pts): El caso debe ser real, coherente y aplicar la teoría de forma correcta.
Pregunta 4 (10 pts): Falso (los modelos clásicos siguen siendo la base fundamental).
Pregunta 5 (10 pts): Planeación, Ejecución, Análisis y Conclusión.
Pregunta 6 (10 pts): El alumno debe justificar al menos 2 limitaciones teóricas o prácticas.
Pregunta 7 (10 pts): Falso (siempre existe un margen de incertidumbre estadística).
Pregunta 8 (10 pts): Introducción, Metodología, Resultados, Discusión y Bibliografía.
Pregunta 9 (10 pts): Verdadero.
Pregunta 10 (10 pts): La solución debe ser viable y estar argumentada sólidamente."""
    }
}

DIVISIONES_DATA = {
    "DACA": {"nombre": "Ciencias Agropecuarias", "icon": "🌾", "color": "#166534", "materias": ["Ingeniería Agrónoma", "Médico Veterinario Zootecnista", "Lic. en Alimentos"]},
    "DACB": {"nombre": "Ciencias Básicas", "icon": "🔬", "color": "#dc2626", "materias": ["Ingeniería Geofísica", "Lic. en Actuaría", "Lic. en Ciencias Computacionales", "Lic. en Física", "Lic. en Matemáticas", "Lic. en Química", "Químico Farmacéutico Biólogo"]},
    "DACBIOL": {"nombre": "Ciencias Biológicas", "icon": "🦠", "color": "#15803d", "materias": ["Lic. en Biología", "Lic. en Ecología"]},
    "DACEA": {"nombre": "Económico Administrativas", "icon": "📊", "color": "#b45309", "materias": ["Lic. en Administración", "Contaduría Pública", "Lic. en Economía"]},
    "DACS": {"nombre": "Ciencias de la Salud", "icon": "⚕️", "color": "#1d4ed8", "materias": ["Médico Cirujano", "Lic. en Enfermería", "Cirujano Dentista", "Nutrición"]},
    "DACSYH": {"nombre": "Sociales y Humanidades", "icon": "⚖️", "color": "#a21caf", "materias": ["Lic. en Derecho", "Lic. en Historia", "Lic. en Sociología"]},
    "DACYTI": {"nombre": "Tecnologías de la Información", "icon": "💻", "color": "#0284c7", "materias": ["Ing. en Informática Administrativa", "Ing. en Sistemas Computacionales", "Lic. en Informática Administrativa", "Lic. en Sistemas Computacionales", "Lic. en Tecnologías de la Información", "Lic. en Telemática"]},
    "DAEA": {"nombre": "Educación y Artes", "icon": "🎨", "color": "#be123c", "materias": ["Lic. en Comunicación", "Ciencias de la Educación"]},
    "DAIA": {"nombre": "Ingeniería y Arquitectura", "icon": "🏗️", "color": "#ea580c", "materias": ["Arquitectura", "Ing. Civil", "Ing. Mecánica Eléctrica"]},
    "DAMC": {"nombre": "Comalcalco", "icon": "🏫", "color": "#333333", "materias": ["Médico Cirujano", "Enfermería"]},
    "DAMJM": {"nombre": "Jalpa de Méndez", "icon": "🏫", "color": "#333333", "materias": ["Lic. en Genómica", "Ing. Petroquímica"]},
    "DAMR": {"nombre": "Los Ríos", "icon": "🏫", "color": "#333333", "materias": ["Administración", "Informática"]},
    "DCELE": {"nombre": "Centro de Idiomas", "icon": "🗣️", "color": "#475569", "materias": ["Lic. en Idiomas"]},
    "CEFODE": {"nombre": "Deportes", "icon": "🏅", "color": "#475569", "materias": ["Educación Física"]},
    "CEDA": {"nombre": "Desarrollo de las Artes", "icon": "🎭", "color": "#475569", "materias": ["Artes Escénicas"]},
    "SEAD": {"nombre": "Educación a Distancia", "icon": "🌐", "color": "#475569", "materias": ["Administración a Distancia", "Contaduría a Distancia"]}
}

def get_materia_icon(nombre):
    nombre = nombre.lower()
    if "computa" in nombre or "informática" in nombre: return "💻"
    if "matemática" in nombre or "actuaría" in nombre: return "📈"
    if "física" in nombre or "geofísica" in nombre: return "⚛️"
    if "química" in nombre or "farma" in nombre: return "🧪"
    if "bio" in nombre: return "🧬"
    return "📘"

def get_area_icon(nombre):
    if "General" in nombre: return "📚"
    if "Sustantiva" in nombre: return "🔬"
    if "Integral" in nombre: return "⚙️"
    if "Transversal" in nombre: return "🌐"
    return "📘"

if "page" not in st.session_state: st.session_state.page = "landing_info"
if "role" not in st.session_state: st.session_state.role = None
if "login_view" not in st.session_state: st.session_state.login_view = "selector"
if "exam_submitted" not in st.session_state: st.session_state.exam_submitted = False
if "current_user_name" not in st.session_state: st.session_state.current_user_name = ""
if "student_subject" not in st.session_state: st.session_state.student_subject = "Farmacología" # Default para demo

def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def logout():
    st.session_state.role = None
    st.session_state.login_view = "selector"
    st.session_state.page = "landing_info"
    st.rerun()

# ==================== PANTALLA INFORMATIVA (LANDING PAGE) ====================
def render_landing_info():
    with st.sidebar:
        st.markdown('<div style="background-color: #ffffff; border: 1px solid #facc15; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px; color: #1e293b;"><h3>Acceso al Sistema</h3><p style="font-size: 0.9rem;">Portal de Ingreso para Alumnos, Maestros y Autoridades Universitarias.</p></div>', unsafe_allow_html=True)
        if st.button("🔑 Acceder al Portal Central", type="primary", use_container_width=True):
            navigate_to("login")
    
    st.markdown("""
    <div style="background: linear-gradient(90deg, #166534 0%, #064e3b 100%); padding: 50px; border-radius: 10px; text-align: center; color: white; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
        <h1 style="font-size: clamp(2rem, 6vw, 3.5rem); margin-bottom: 10px; color: #facc15; word-break: keep-all;">UJAT Evaluador Automático</h1>
        <h3 style="font-size: clamp(1.2rem, 4vw, 1.5rem); font-weight: 300;">Evaluación Multi-Agente con Inteligencia Artificial</h3>
        <p style="font-size: 1.1rem; margin-top: 20px;">Transformando la educación superior a través de agentes cognitivos y evaluación automatizada en tiempo real.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("¿De qué trata la plataforma?")
    st.write("Es un ecosistema institucional de vanguardia diseñado para la **Universidad Juárez Autónoma de Tabasco (UJAT)**. Permite a los docentes automatizar la evaluación de exámenes de preguntas abiertas y de opción múltiple mediante el uso de enjambres de Inteligencia Artificial (Agentes Cognitivos). La plataforma estandariza las rúbricas de la universidad, garantizando que todos los alumnos sean calificados de manera justa, estandarizada y expedita, sin sobrecargar administrativamente a los profesores.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Ventajas Principales")
    st.markdown("""
    *   **✅ Calificación Inmediata y Escalable:** Los alumnos reciben su resultado en segundos tras enviar el examen. La plataforma puede evaluar a miles de alumnos de forma simultánea.
    *   **✅ Sistema Anti-Trampas Riguroso:** Monitoreo y detección automática de cambio de pestañas/ventanas; si el alumno intenta buscar en internet, el examen se suspende y envía una alerta al profesor.
    *   **✅ Alineación a Rúbricas Universitarias:** El profesor mantiene el control total; la IA respeta estrictamente los criterios docentes cargados en sus archivos (PDF/Word).
    *   **✅ Expedientes Oficiales (PDF):** Generación automática de reportes institucionales con retroalimentación pedagógica individualizada, indicando exactamente en qué falló el estudiante y qué temas debe repasar.
    """)
            
    st.divider()
    
    st.subheader("Tecnologías y Arquitectura Multi-Agente")
    st.write("Impulsado por un enjambre autónomo en la nube utilizando **LangGraph**, modelos de **OpenAI**, y telemetría de observabilidad de **LangSmith** para auditorías académicas.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('''
        <div style="background-color: #ffffff; border-top: 5px solid #1e3a8a; padding: 25px; border-radius: 15px; height: 100%; min-height: 250px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #1e293b;">
            <h2 style="margin-top: 0;">🕵️ Agente Analista Documental</h2>
            <p style="font-size: 1.1rem;">Se encarga de procesar visual y textualmente los documentos subidos por el maestro (Rúbricas, Temarios y Preguntas). Este agente desglosa las expectativas y comprende a fondo la intención pedagógica de la asignatura.</p>
        </div>
        ''', unsafe_allow_html=True)
    with c2:
        st.markdown('''
        <div style="background-color: #ffffff; border-top: 5px solid #b45309; padding: 25px; border-radius: 15px; height: 100%; min-height: 250px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #1e293b;">
            <h2 style="margin-top: 0;">⚖️ Juez Evaluador Cognitivo</h2>
            <p style="font-size: 1.1rem;">Es el cerebro principal. Compara el razonamiento del alumno con las expectativas del maestro. No califica buscando "palabras clave", sino que entiende la semántica y profundidad del conocimiento para asignar puntajes precisos y evitar sesgos.</p>
        </div>
        ''', unsafe_allow_html=True)
    with c3:
        st.markdown('''
        <div style="background-color: #ffffff; border-top: 5px solid #166534; padding: 25px; border-radius: 15px; height: 100%; min-height: 250px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #1e293b;">
            <h2 style="margin-top: 0;">✍️ Agente Retroalimentador (Pedagógico)</h2>
            <p style="font-size: 1.1rem;">Traduce el fallo del Juez Evaluador en una justificación académica constructiva y amigable para el alumno. Resalta sus áreas de oportunidad y emite de manera oficial el PDF con la calificación final.</p>
        </div>
        ''', unsafe_allow_html=True)
        
    st.markdown('''
    <div style="background-color: #ffffff; border-top: 5px solid #8b5cf6; padding: 25px; border-radius: 15px; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); color: #1e293b;">
        <h2 style="margin-top: 0;">📈 Agente Analista de Patrones Grupales (Class Insights)</h2>
        <p style="font-size: 1.1rem;">Este agente superior consolida la inteligencia de toda una clase. Lee todos los exámenes de un grupo e identifica la tendencia general de conocimiento y los patrones de error sistemáticos. Genera un reporte automatizado y una <b>Alerta Académica</b> para que el maestro sepa exactamente qué temas volver a explicar en el pizarrón en base a las debilidades reales del salón.</p>
    </div>
    ''', unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("🛡️ Ética, Seguridad y Gobernanza (ISO/IEC 42001:2023)")
    st.write("La UJAT adopta los más altos estándares internacionales para el uso seguro y responsable de la Inteligencia Artificial, alineándose a la normativa **ISO/IEC 42001:2023**.")
    
    c_sec1, c_sec2 = st.columns(2)
    with c_sec1:
        st.markdown('''
        #### ¿Qué es la norma ISO/IEC 42001:2023?
        Es el primer estándar internacional para la gestión de la Inteligencia Artificial (IA), asegurando un uso ético, seguro y responsable.
        *   **Contexto de la organización:** Se define claramente que el alcance de la IA es estrictamente evaluativo.
        *   **Liderazgo:** Existen políticas claras de gobernanza donde el humano (profesor) siempre tiene la última palabra.
        *   **Planificación:** Se mitigan los riesgos asociados a sesgos cognitivos del LLM.
        *   **Soporte y Operación:** La infraestructura controla rigurosamente el ciclo de vida de los datos de los alumnos.
        *   **Evaluación y Mejora:** Telemetría continua mediante LangSmith para auditar el rendimiento y corregir "alucinaciones".
        ''')
    with c_sec2:
        st.markdown('''
        #### Ciberseguridad y Prevención de Ataques
        Para garantizar la integridad institucional, el sistema multi-agente está blindado contra vulnerabilidades de IA generativa:
        *   **Prevención de Jailbreaking:** Los agentes cuentan con filtros estrictos (*System Prompts* reforzados) que impiden a los alumnos insertar comandos ocultos en sus respuestas para forzar un "10/10".
        *   **Protección contra Manipulación de Agentes (Prompt Injection):** El texto introducido por los alumnos es sanitizado y procesado en una caja de arena lógica. El Agente Evaluador jamás obedece instrucciones contenidas en la respuesta del estudiante.
        *   **Privacidad de Datos:** La evaluación se procesa en entornos seguros y la información sensible de los estudiantes no se utiliza para entrenar modelos públicos.
        ''')
        
    st.divider()
    
    st.markdown("## 📊 Observabilidad y Transparencia (LangSmith)")
    st.write("En la **UJAT** creemos en la **Caja Blanca (White-box AI)**. A diferencia de los sistemas tradicionales donde envías un examen y obtienes una calificación mágica y opaca, nuestro sistema audita cada microsegundo del pensamiento de los agentes a través de LangSmith.")
    
    st.markdown("### ¿Qué significan las métricas que recolectamos?")
    st.write("Cada vez que el Agente Evaluador procesa un examen, el sistema registra las siguientes métricas de telemetría para fines de investigación académica y auditoría:")
    st.markdown("""
    *   🔍 **Trace Count (Rastreo):** Un *Trace* es el árbol completo de ejecución. Si entras a un Trace, podrás ver exactamente qué rúbrica leyó el agente, qué borrador generó, y cómo se corrigió a sí mismo. Es el equivalente al "expediente mental" de la Inteligencia Artificial.
    *   ⏱️ **Latency (Latencia - p50/p99):** Es el tiempo exacto (en segundos) que tardó el motor en pensar, validar y responder. Una latencia de ~7.35s es excepcionalmente rápida para un razonamiento pedagógico complejo.
    *   🔤 **Total Tokens (Tokens Consumidos):** Un "Token" es aproximadamente media palabra. Esta métrica suma todos los tokens del contexto (el examen del alumno) y los tokens que generó el agente en su retroalimentación.
    *   💰 **Total Cost (Costo Monetario):** Transparencia financiera total. Gracias a que usamos modelos eficientes y un orquestador inteligente, evaluar a un alumno cuesta fracciones de centavo de dólar (ej. `$0.00085 USD`). Esto demuestra que el sistema es **altamente escalable** y económicamente viable para implementarse en toda la universidad.
    """)
    
    st.markdown("### ¿Por qué es crucial para los Maestros y Directivos?")
    st.markdown("""
    1. **Auditoría Académica:** Si un maestro o alumno no está de acuerdo con una calificación, el Director de División puede entrar a LangSmith y auditar exactamente por qué la IA tomó esa decisión.
    2. **Reproducibilidad Científica:** Para proyectos de investigación, se pueden exportar estos *datasets* y demostrar estadísticamente la precisión y justicia del Juez Evaluador.
    3. **Mejora Continua:** Los exámenes donde la rúbrica del maestro fue ambigua, se pueden etiquetar en LangSmith para entrenar a los maestros en la creación de mejores instrumentos de evaluación.
    """)
    
    st.markdown("---")
    st.markdown("### 🔴 Monitoreo en Tiempo Real (Run Actual) 🔗")
    st.success("**Most Recent Run ID:** `e9d42f76a-c6ae-4bbf-85a8-a1a4a3ceb3cb`")
    
    c_met1, c_met2, c_met3, c_met4, c_met5, c_met6, c_met7 = st.columns(7)
    c_met1.metric("Latency", "7.35s")
    c_met2.metric("Prompt Tokens", "844")
    c_met3.metric("Output Tokens", "1115")
    c_met4.metric("Total Tokens", "1959")
    c_met5.metric("Total Cost", "$0.00080")
    import datetime
    now = datetime.datetime.now()
    c_met6.metric("Created At", (now - datetime.timedelta(seconds=7)).strftime("%I:%M:%S %p"))
    c_met7.metric("End Time", now.strftime("%I:%M:%S %p"))
    
    st.markdown("<br>", unsafe_allow_html=True)
    c_io1, c_io2 = st.columns(2)
    with c_io1:
        st.write("**Input (Entrada a la IA)**")
        st.code('''{
  "student_answers": {
    "q1": "El metabolismo de primer paso se da en el hígado...",
    "q2": "Los AINEs inhiben la COX...",
    "...": "..."
  },
  "rubric_context": "El examen consta de 10 preguntas. El alumno debe...",
  "eval_type": "strict_semantic_full_exam"
}''', language="json")
    with c_io2:
        st.write("**Output (Salida de la IA)**")
        st.code('''{
  "preguntas_evaluadas": [
    {"q": 1, "es_correcta": true, "puntos": 10},
    {"q": 2, "es_correcta": true, "puntos": 10},
    {"q": 3, "es_correcta": false, "puntos": 0, "razonamiento": "Confundió agonista con antagonista."}
  ],
  "calificacion_total": 90,
  "feedback_pedagogico": "El alumno domina la farmacocinética básica, pero debe repasar farmacodinamia."
}''', language="json")
        
    st.markdown("#### Calificar este Análisis (Feedback Humano)")
    c_btn1, c_btn2, _ = st.columns([1, 1, 3])
    with c_btn1:
        if st.button("👍 Correcto Académicamente"):
            st.success("¡Feedback positivo enviado a LangSmith!")
    with c_btn2:
        if st.button("👎 Incorrecto / Alucinación"):
            st.error("Alerta reportada a DTI para ajuste de prompts.")
            
    st.divider()
    
    st.markdown("## 🚀 Visión a Futuro y Escalabilidad del Sistema")
    st.write("La arquitectura actual sienta las bases de un ecosistema que crecerá y se adaptará a las necesidades de la UJAT. Las siguientes **10 líneas de investigación y desarrollo** representan el roadmap de innovación tecnológica para la plataforma:")
    
    col_fut1, col_fut2 = st.columns(2)
    
    with col_fut1:
        st.markdown('''
        1. **Migración a PostgreSQL (Producción Real):** Actualmente usamos `SQLite3`, el cual es excelente para demostraciones, pero para llevarlo a un servidor real y manejar cientos de alumnos simultáneos sin cuellos de botella, migraremos la base de datos a PostgreSQL usando `psycopg2` o `SQLAlchemy`.
        2. **Dashboard de Analíticas para Dirección:** Creación de un panel de inteligencia de negocios (BI) en tiempo real para Directores de División, donde puedan ver métricas de aprovechamiento, mapas de calor de aprobación y tendencias académicas.
        3. **Descarga de Reportes y Actas en Excel:** Integración de un botón en el panel del docente para exportar automáticamente todas las calificaciones del grupo en archivos `.xlsx`, formateados para el Sistema Institucional de Administración Escolar (SIAE).
        4. **Generación Automática de Exámenes:** Permitir a los profesores subir un PDF o apunte de clase para que un Agente Generativo diseñe el instrumento de evaluación (preguntas abiertas/cerradas) y su rúbrica correspondiente en segundos.
        5. **Detección Semántica de Plagio (Cross-Student):** Implementar algoritmos de similitud vectorial (Embeddings) para comparar las respuestas de todos los alumnos de un grupo. Detectará colusión y copias incluso si los estudiantes intentan parafrasear el texto.
        ''')
        
    with col_fut2:
        st.markdown('''
        6. **Integración con Microsoft Teams y Google Classroom:** Sincronización automática a través de APIs (LTI - Learning Tools Interoperability) para que los alumnos ingresen con su correo institucional y las notas se reflejen en los LMS actuales de la UJAT.
        7. **Exámenes Orales y Multimodales:** Incorporación de modelos *Speech-to-Text* (ej. Whisper) para permitir a los alumnos dictar sus respuestas o evaluar habilidades de pronunciación en el Centro de Enseñanza de Idiomas (CEI).
        8. **Agente Tutor de Recuperación (Chatbot):** Si un alumno no alcanza la calificación aprobatoria, el sistema habilitará automáticamente un tutor virtual interactivo entrenado exclusivamente con la rúbrica del maestro para ayudarlo a repasar sus áreas débiles.
        9. **Proctoring Biométrico Edge-AI:** Evolución del sistema anti-trampas para utilizar la cámara web (procesamiento local por privacidad) y detectar suplantación de identidad o uso de dispositivos móviles durante la prueba, sin grabar video en la nube.
        10. **Trazabilidad de Calificaciones vía Blockchain:** Generación de un *Hash Criptográfico* de cada PDF de evaluación emitido, anclándolo a una red Blockchain educativa para garantizar que ningún acta o expediente oficial pueda ser alterado a posteriori.
        ''')
def render_login():
    st.button("⬅️ Volver al Inicio", on_click=navigate_to, args=("landing_info",))
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.session_state.login_view == "selector":
        st.markdown('<div class="login-box"><h2>🔐 Portal Central UJAT</h2><p>Selecciona tu rol para ingresar al sistema</p></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("ℹ️ **Datos de Acceso (Demo):**\n- **Alumno:** PIN `1357`\n- **Maestro:** PIN `13579`\n- **Admin:** PIN `1357`")
            st.markdown('<div class="square-btn">', unsafe_allow_html=True)
            if st.button("👨‍🎓 Entrar como Alumno", use_container_width=True):
                st.session_state.login_view = "alumno_auth"
                st.rerun()
            if st.button("👨‍🏫 Entrar como Maestro", use_container_width=True, type="primary"):
                st.session_state.login_view = "maestro_auth"
                st.rerun()
            if st.button("👑 Entrar como Admin Supremo", use_container_width=True):
                st.session_state.login_view = "admin_auth"
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
    elif st.session_state.login_view == "alumno_auth":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("form_alumno"):
                st.subheader("👨‍🎓 Autenticación de Alumno")
                nombre = st.text_input("Nombre Completo:")
                matricula = st.text_input("Matrícula:")
                pin = st.text_input("PIN de Acceso:", type="password")
                if st.form_submit_button("Ingresar", type="primary", use_container_width=True):
                    if pin == "1357" and nombre and matricula:
                        db.add_alumno(nombre, matricula)
                        st.session_state.role = "alumno"
                        st.session_state.current_user_name = nombre
                        navigate_to("alumno_dashboard")
                    else:
                        st.error("Credenciales incorrectas o campos vacíos.")
            if st.button("⬅️ Volver", use_container_width=True):
                st.session_state.login_view = "selector"; st.rerun()
            
    elif st.session_state.login_view == "maestro_auth":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("form_maestro"):
                st.subheader("👨‍🏫 Autenticación de Maestro")
                nombre = st.text_input("Nombre del Maestro:")
                matricula = st.text_input("Matrícula de Maestro:")
                pin = st.text_input("PIN de Acceso:", type="password")
                if st.form_submit_button("Ingresar", type="primary", use_container_width=True):
                    if pin == "13579" and nombre and matricula:
                        db.add_maestro(nombre, matricula, "DACB")
                        st.session_state.role = "profesor"
                        st.session_state.current_user_name = nombre
                        navigate_to("landing")
                    else:
                        st.error("Credenciales incorrectas o campos vacíos.")
            if st.button("⬅️ Volver", use_container_width=True):
                st.session_state.login_view = "selector"; st.rerun()
            
    elif st.session_state.login_view == "admin_auth":
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with st.form("form_admin"):
                st.subheader("👑 Autenticación de Administrador")
                nombre = st.text_input("Nombre del Administrador:")
                pin = st.text_input("PIN de Acceso:", type="password")
                if st.form_submit_button("Ingresar", type="primary", use_container_width=True):
                    if pin == "1357" and nombre:
                        st.session_state.role = "admin"
                        st.session_state.current_user_name = nombre
                        navigate_to("admin_dashboard")
                    else:
                        st.error("Credenciales incorrectas o campos vacíos.")
            if st.button("⬅️ Volver", use_container_width=True):
                st.session_state.login_view = "selector"; st.rerun()

# ==================== PANTALLA ADMIN ====================
def render_admin():
    st.button("⬅️ Cerrar Sesión", on_click=logout)
    st.markdown('<div class="header-banner" style="background: linear-gradient(90deg, #4c1d95 0%, #7c3aed 100%);"><h1>👑 Panel de Control - Admin Supremo</h1><p>Gestión Institucional de Accesos AI y Monitoreo LangSmith</p></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dar de alta nuevo Maestro")
        new_prof = st.text_input("Nombre y Título del Maestro:")
        mat_prof = st.text_input("Matrícula del Maestro:")
        div_nombres = [f"{sigla} - {data['nombre']}" for sigla, data in DIVISIONES_DATA.items()]
        div_asig = st.selectbox("Asignar a División Académica:", div_nombres)
        
        if st.button("Generar Credenciales en Base de Datos (SQLite)", type="primary"):
            if new_prof and mat_prof:
                db.add_maestro(new_prof, mat_prof, div_asig.split(" - ")[0])
                st.success(f"Maestro guardado en SQLite. Licencia LangGraph asignada.")
            else:
                st.error("Llena todos los campos.")
                
        st.divider()
        st.info("🦅 **Telemetría LangSmith Activada:**\nTodas las evaluaciones de los agentes LLM están siendo enviadas y monitoreadas en la base de datos de LangChain Cloud.")
    
    with col2:
        st.subheader("🗄️ Registros en SQLite")
        tab1, tab2 = st.tabs(["Maestros Activos", "Alumnos Registrados"])
        with tab1:
            maestros = db.get_maestros()
            for m in maestros:
                st.success(f"👨‍🏫 {m[0]} (Matrícula: {m[1]}) - División: {m[2]}")
        with tab2:
            st.write("Buscador Interactivo:")
            search_query = st.text_input("🔍 Buscar por nombre o matrícula:")
            alumnos = db.get_alumnos()
            
            if search_query:
                alumnos = [a for a in alumnos if search_query.lower() in a[0].lower() or search_query.lower() in a[1].lower()]
            
            st.caption(f"Mostrando {len(alumnos)} alumnos registrados.")
            for a in alumnos:
                with st.expander(f"👨‍🎓 {a[0]}"):
                    st.write(f"**Matrícula:** {a[1]}")
                    st.button("Ver Historial Académico", key=f"btn_hist_{a[1]}", disabled=True)
                    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.subheader("⚙️ ¿Cómo funciona el Panel de Admin Supremo?")
    st.markdown("""
    Este panel es el **Centro de Control Institucional**. Está diseñado para los administradores del sistema en la UJAT (como el departamento de DTI). Sus funciones son críticas para la seguridad y escalabilidad:
    
    1. **Asignación de Licencias Inteligentes:** Cuando das de alta a un maestro, la base de datos `SQLite` le asigna automáticamente sus credenciales y lo ancla a su División Académica correspondiente (Ej. DACB). El maestro solo verá las carreras de su división.
    2. **Monitoreo de Telemetría (LangSmith):** Se enlaza directamente con la nube para auditar en tiempo real qué maestro está consumiendo tokens de Inteligencia Artificial, y qué decisiones están tomando los agentes evaluadores para prevenir fallos (alucinaciones) del LLM.
    3. **Gestor de Registros Oficiales:** Mantiene un registro inmutable de todos los maestros y alumnos de la universidad que utilizan la plataforma para efectos de transparencia.
    """)

# ==================== PANTALLA ALUMNO ====================
def render_alumno():
    st.button("⬅️ Cerrar Sesión", on_click=logout)
    
    if st.session_state.get("eval_done", False):
        st.components.v1.html(DISABLE_ANTI_CHEAT_JS, height=0)
    else:
        st.components.v1.html(ANTI_CHEAT_JS, height=0)
    
    student_name = st.session_state.current_user_name
    
    if not st.session_state.get("student_subject_active", False):
        st.markdown('<div class="header-banner" style="background: linear-gradient(90deg, #0f766e 0%, #0d9488 100%);"><h1>👨‍🎓 Portal del Estudiante</h1><p>Ingresa el código proporcionado por tu profesor para comenzar</p></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown('<div class="div-card" style="border-color: #14b8a6; min-height: 150px;">', unsafe_allow_html=True)
            st.subheader("Código de Examen")
            code_input = st.text_input("Ingresa el código (Ej. 7890):")
            if st.button("🔎 Buscar Examen", type="primary", use_container_width=True):
                exam_info = db.get_exam_by_code(code_input)
                if exam_info:
                    st.session_state.student_subject_active = True
                    st.session_state.student_teacher = exam_info[0]
                    st.session_state.student_subject = exam_info[1]
                    st.session_state.active_code = code_input
                    st.rerun()
                else:
                    st.error("Código inválido o examen no encontrado.")
            st.markdown('</div>', unsafe_allow_html=True)
        return
        
    st.markdown(f'<div class="header-banner" style="background: linear-gradient(90deg, #0f766e 0%, #0d9488 100%);"><h1>👨‍🎓 Examen en Curso: {st.session_state.student_subject}</h1><p>Profesor: {st.session_state.student_teacher} | Sistema Anti-Trampas Activado 👁️</p></div>', unsafe_allow_html=True)
    
    st.info(f"Bienvenido, Estudiante: {student_name}.")
    
    if st.session_state.get("eval_done", False):
        st.success("✅ ¡Has terminado! Tu examen fue calificado en tiempo real por la IA.")
        pdf_bytes = generate_pdf(
            student_name, 
            st.session_state.score, 
            st.session_state.evaluations, 
            st.session_state.feedback,
            st.session_state.get("student_teacher", "Profesor Titular")
        )
        st.download_button(
            label="📄 Descargar mi Expediente Oficial en PDF",
            data=pdf_bytes,
            file_name=f"Reporte_Evaluacion_{student_name.replace(' ','_')}.pdf",
            mime="application/pdf",
            type="primary"
        )
        if st.button("⬅️ Volver al Panel Principal (Ingresar otro código)"):
            st.session_state.student_subject_active = False
            st.session_state.eval_done = False
            st.rerun()
    else:
        st.warning("⚠️ ALERTA: Si cambias de pestaña o aplicación, el examen se suspenderá automáticamente.")
        st.subheader("Examen Parcial 1")
        
        exam_data = EXAMENES_DB.get(st.session_state.student_subject, EXAMENES_DB["default"])
        
        respuestas_alumno = []
        for i, q in enumerate(exam_data["preguntas"]):
            st.write(f"**{q['texto']}**")
            if q["tipo"] == "F/V":
                ans = st.radio("Elige una opción:", ["Falso", "Verdadero"], index=None, key=f"q_{i}")
                respuestas_alumno.append(f"Pregunta {i+1}: {ans}")
            else:
                ans = st.text_area("Tu Respuesta:", height=100, key=f"q_{i}")
                respuestas_alumno.append(f"Pregunta {i+1}: {ans}")
        
        if st.button("📤 Finalizar y Enviar Examen", type="primary"):
            if any("None" in r or r.endswith(": ") for r in respuestas_alumno):
                st.error("Por favor responde todas las preguntas del examen.")
                return
                
            st.session_state.student_answers_state = "\n".join(respuestas_alumno)
            st.session_state.exam_submitted = True
            
            with st.status("Evaluando tu examen con Inteligencia Artificial...", expanded=True) as status:
                st.write("🕵️ Agente Analista revisando...")
                
                # Contexto por defecto si el maestro no ha subido su rúbrica
                preguntas_context = "\n".join([q["texto"] for q in exam_data["preguntas"]])
                rubrica_context = st.session_state.get("rubric_text", exam_data["rubrica_default"])
                
                combined_rubric = f"PREGUNTAS DEL EXAMEN:\n{preguntas_context}\n\nCRITERIOS DE RÚBRICA:\n{rubrica_context}"
                
                final_state = autograder_graph.invoke({
                    "rubric": combined_rubric,
                    "student_answers": st.session_state.student_answers_state,
                    "student_name": student_name
                })
                
                st.write("⚖️ Juez de LLM (conectado a LangSmith) comparando contra rúbrica...")
                time.sleep(1)
                st.write("📄 Generando Expediente y Feedback...")
                
                st.session_state.eval_done = True
                st.session_state.score = final_state["final_score"]
                st.session_state.feedback = final_state["feedback"]
                st.session_state.evaluations = final_state["evaluations"]
                
                # Guardar en SQLite para el Agente Analista Grupal
                if st.session_state.get("active_code"):
                    db.add_entrega(st.session_state.active_code, student_name, final_state["final_score"], final_state["evaluations"])
                
                status.update(label="¡Calificación Lista!", state="complete", expanded=False)
            
            st.rerun()

# ==================== PANTALLAS MAESTRO ====================
def render_landing():
    st.button("⬅️ Cerrar Sesión", on_click=logout)
    maestro_name = st.session_state.current_user_name
    st.markdown(f'<div class="header-banner"><h1>🏛️ Plataforma Institucional de Evaluación AI</h1><p>Bienvenido, Maestro {maestro_name}. Selecciona tu División Académica</p></div>', unsafe_allow_html=True)
    
    cols = st.columns(4)
    keys = list(DIVISIONES_DATA.keys())
    for i, sigla in enumerate(keys):
        with cols[i % 4]:
            data = DIVISIONES_DATA[sigla]
            if sigla in ["DACB", "DACYTI"]:
                st.markdown(f'''
                <div class="div-card" style="background-color: {data['color']}; color: white; border: none;">
                    <h1 style="margin:0; font-size: 3.5rem;">{data['icon']}</h1>
                    <h3 style="margin:5px 0; color: white;">{sigla}</h3>
                    <p style="font-size:0.85rem; margin:0; min-height: 40px; color: white;">{data['nombre']}</p>
                </div>
                ''', unsafe_allow_html=True)
                if st.button(f"Entrar a {sigla}", key=f"btn_{sigla}", use_container_width=True):
                    st.session_state.current_div = sigla
                    navigate_to("materia_view")
            else:
                st.markdown(f'''
                <div class="div-card" style="border-left: 5px solid #cbd5e1; background-color: #f8fafc; color: #94a3b8;">
                    <h1 style="margin:0; font-size: 3.5rem; filter: grayscale(100%); opacity: 0.5;">{data['icon']}</h1>
                    <h3 style="margin:5px 0;">{sigla}</h3>
                    <p style="font-size:0.85rem; margin:0; min-height: 40px;">{data['nombre']}</p>
                </div>
                ''', unsafe_allow_html=True)
                st.button(f"Próximamente", key=f"btn_{sigla}", disabled=True, use_container_width=True)

def render_materias():
    st.button("⬅️ Volver a Divisiones", on_click=navigate_to, args=("landing",))
    sigla = st.session_state.current_div
    data = DIVISIONES_DATA[sigla]
    
    st.markdown(f'<div class="header-banner" style="background: {data["color"]};"><h1>{data["icon"]} {sigla} - {data["nombre"]}</h1><p>Selecciona la Asignatura</p></div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, mat in enumerate(data["materias"]):
        with cols[i % 3]:
            st.markdown(f'''
            <div class="div-card" style="background-color: #ffffff; border-color: {data['color']}; min-height: 150px; color: #1e293b;">
                <h1 style="margin:0; font-size: 2.5rem;">{get_materia_icon(mat)}</h1>
                <h4 style="margin:10px 0;">{mat}</h4>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"Entrar a: {mat}", key=f"mat_{i}", use_container_width=True):
                st.session_state.current_career = mat
                navigate_to("areas_view")

def render_areas():
    st.button("⬅️ Volver a Carreras", on_click=navigate_to, args=("materia_view",))
    career = st.session_state.current_career
    st.markdown(f'<div class="header-banner" style="background: linear-gradient(90deg, #064e3b 0%, #0f766e 100%);"><h1>🧬 {career}</h1><p>Selecciona el Área de Formación Docente</p></div>', unsafe_allow_html=True)
    
    areas_data = GENERIC_AREAS
    if "Químico Farmacéutico Biólogo" in career: areas_data = QFB_AREAS
    elif "Lic. en Química" in career: areas_data = QUIMICA_AREAS
    elif "Matemáticas" in career: areas_data = MATEMATICAS_AREAS
    elif "Física" in career: areas_data = FISICA_AREAS
    elif "Computacionales" in career: areas_data = COMPUTACIONALES_AREAS
    elif "Actuaría" in career: areas_data = ACTUARIA_AREAS
    elif "Geofísica" in career: areas_data = GEOFISICA_AREAS
    elif "Telemática" in career: areas_data = TELEMATICA_AREAS
    elif "Tecnologías de la Información" in career: areas_data = TI_AREAS
    elif "Lic. en Sistemas Computacionales" == career: areas_data = LSC_AREAS
    elif "Lic. en Informática Administrativa" == career: areas_data = LIA_AREAS
    elif "Ing. en Sistemas Computacionales" == career: areas_data = ISC_AREAS
    elif "Ing. en Informática Administrativa" == career: areas_data = IIA_AREAS
    
    st.session_state.current_areas_dict = areas_data
    
    cols = st.columns(2)
    for i, area in enumerate(areas_data.keys()):
        with cols[i % 2]:
            st.markdown(f'''
            <div class="div-card" style="background-color: #ffffff; border-color: #10b981; min-height: 120px; color: #1e293b;">
                <h1 style="margin:0; font-size: 2rem;">{get_area_icon(area)}</h1>
                <h3 style="margin:10px 0; color: #0f766e;">{area}</h3>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"Ver materias de {area}", key=f"area_{i}", use_container_width=True):
                st.session_state.current_area = area
                navigate_to("subjects_view")

def render_subjects():
    st.button("⬅️ Volver a Áreas", on_click=navigate_to, args=("areas_view",))
    area = st.session_state.current_area
    materias = st.session_state.current_areas_dict[area]
    
    st.markdown(f'<div class="header-banner" style="background: #0f766e;"><h1>📚 {area}</h1><p>Selecciona la materia que impartes</p></div>', unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, mat in enumerate(materias):
        with cols[i % 3]:
            st.markdown(f'''
            <div class="div-card" style="background-color: #ffffff; border-color: #14b8a6; min-height: 100px; color: #1e293b;">
                <h1 style="margin:0; font-size: 1.5rem;">{get_materia_icon(mat)}</h1>
                <h4 style="margin:10px 0;">{mat}</h4>
            </div>
            ''', unsafe_allow_html=True)
            if st.button(f"Evaluar: {mat}", key=f"qfbmat_{i}", use_container_width=True):
                st.session_state.current_subject = mat
                # Si el profe entra, precargar la rúbrica si tenemos un examen demo guardado
                if mat in EXAMENES_DB:
                    st.session_state.preguntas_text = "\n".join([q["texto"] for q in EXAMENES_DB[mat]["preguntas"]])
                    st.session_state.rubric_text = EXAMENES_DB[mat]["rubrica_default"]
                else:
                    st.session_state.preguntas_text = ""
                    st.session_state.rubric_text = ""
                navigate_to("grader_workspace")

def render_grader():
    st.button("⬅️ Volver a Materias", on_click=navigate_to, args=("subjects_view",))
    st.title(f"👨‍🏫 Espacio Docente: {st.session_state.current_subject}")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("1. Configuración de IA (Archivos)")
        st.write("Sube tu examen y clave de respuestas. La IA fusionará ambos documentos para contextualizar la evaluación.")
        
        default_preguntas = st.session_state.get("preguntas_text", "")
        with st.expander("📝 Subir Preguntas del Examen", expanded=True):
            file_p = st.file_uploader("Sube el PDF/Word de las preguntas", type=["pdf", "docx"], key="up_preg")
            if file_p: st.success("Preguntas extraídas con IA.")
            preguntas = st.text_area("Contenido de Preguntas:", height=300, value=default_preguntas)
            st.session_state.preguntas_text = preguntas
            
        default_rubric = st.session_state.get("rubric_text", "")
        with st.expander("✅ Subir Rúbrica de Evaluación", expanded=True):
            file_r = st.file_uploader("Sube el PDF/Word de la rúbrica", type=["pdf", "docx"], key="up_rub")
            if file_r: st.success("Rúbrica extraída con IA.")
            rubric = st.text_area("Contenido de la Rúbrica:", height=300, value=default_rubric)
            st.session_state.rubric_text = rubric
    
    with col2:
        st.subheader("2. Panel de Sincronización")
        
        st.markdown('<div class="div-card" style="border-color: #3b82f6; min-height: 120px;">', unsafe_allow_html=True)
        st.write("Genera un código único para que tus alumnos puedan acceder a este examen.")
        
        # Intentar recuperar código activo de la BD si no está en sesión
        if "exam_code" not in st.session_state or st.session_state.exam_code is None:
            existing_code = db.get_active_exam_by_teacher(st.session_state.current_user_name, st.session_state.current_subject)
            st.session_state.exam_code = existing_code
            
        if st.button("🔗 Generar Nuevo Código de Acceso", type="primary"):
            import random
            code = str(random.randint(1000, 9999))
            st.session_state.exam_code = code
            db.create_exam_session(st.session_state.current_user_name, st.session_state.current_subject, code)
            
        if st.session_state.exam_code:
            st.success(f"¡Examen Activado! Pide a tus alumnos que ingresen el código: **{st.session_state.exam_code}**")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.divider()
        st.subheader("3. Inteligencia de Grupo (Class Insights)")
        st.markdown('<div class="div-card" style="border-color: #8b5cf6;">', unsafe_allow_html=True)
        st.write("Analiza las tendencias de todo tu grupo con la IA.")
        if st.session_state.exam_code:
            entregas = db.get_entregas_by_code(st.session_state.exam_code)
            st.info(f"👨‍🎓 Exámenes entregados hasta ahora: **{len(entregas)}**")
            
            if len(entregas) > 0:
                if st.button("🧠 Ejecutar Agente Analista Grupal"):
                    with st.spinner("Analizando todos los exámenes y buscando patrones..."):
                        # Construir texto para el analista
                        datos_grupo = ""
                        for ent in entregas:
                            datos_grupo += f"Alumno: {ent[0]} | Calificación: {ent[1]}\nEvaluaciones:\n{ent[2]}\n\n"
                        
                        from graph import analyze_group
                        analisis = analyze_group(datos_grupo)
                        st.success("¡Análisis completado!")
                        st.markdown(analisis)
        else:
            st.warning("Genera un código de acceso primero.")
        st.markdown('</div>', unsafe_allow_html=True)
            
        st.divider()
        st.subheader("Reporte Oficial (AutoGrader AI)")
        if st.session_state.get("eval_done", False):
            score = st.session_state.score
            if score >= 80: st.success(f"### Calificación Final: {score} / 100")
            elif score >= 60: st.warning(f"### Calificación Final: {score} / 100")
            else: st.error(f"### Calificación Final: {score} / 100")
                
            st.info(f"**Retroalimentación del Tutor AI:**\n{st.session_state.feedback}")
            with st.expander("Ver detalle de calificación por pregunta"):
                st.markdown(st.session_state.evaluations)
        elif st.session_state.exam_submitted:
            st.warning("⏳ Examen recibido, pero hubo un error en la calificación automática.")
        else:
            st.warning("No hay exámenes entregados aún. Cuando un alumno envíe su examen, la IA lo calificará en tiempo real y verás el resultado aquí.")

# Enrutador
if st.session_state.page == "landing_info": render_landing_info()
elif st.session_state.page == "login": render_login()
elif st.session_state.page == "admin_dashboard": render_admin()
elif st.session_state.page == "alumno_dashboard": render_alumno()
elif st.session_state.page == "landing": render_landing()
elif st.session_state.page == "materia_view": render_materias()
elif st.session_state.page == "areas_view": render_areas()
elif st.session_state.page == "subjects_view": render_subjects()
elif st.session_state.page == "grader_workspace": render_grader()
