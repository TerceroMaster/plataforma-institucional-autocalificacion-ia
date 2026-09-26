import sqlite3

DB_NAME = "autograder_ujat.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS maestros
                 (id INTEGER PRIMARY KEY, nombre TEXT, matricula TEXT, division TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alumnos
                 (id INTEGER PRIMARY KEY, nombre TEXT, matricula TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS examenes_activos
                 (id INTEGER PRIMARY KEY, maestro TEXT, materia TEXT, codigo TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS entregas_examen
                 (id INTEGER PRIMARY KEY, codigo_examen TEXT, alumno TEXT, score INTEGER, evaluaciones TEXT)''')
    
    # Insert demo data if empty
    c.execute('SELECT COUNT(*) FROM maestros')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO maestros (nombre, matricula, division) VALUES (?, ?, ?)', ("Prof. Dr. Roberto", "M123", "DACB"))
        c.execute('INSERT INTO maestros (nombre, matricula, division) VALUES (?, ?, ?)', ("Dra. Maria Elena", "M124", "DACYTI"))
    
    c.execute('SELECT COUNT(*) FROM alumnos')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO alumnos (nombre, matricula) VALUES (?, ?)', ("Juan Pérez", "A001"))
        c.execute('INSERT INTO alumnos (nombre, matricula) VALUES (?, ?)', ("Ana Gómez", "A002"))
        
    conn.commit()
    conn.close()

def add_maestro(nombre, matricula, division):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO maestros (nombre, matricula, division) VALUES (?, ?, ?)', (nombre, matricula, division))
    conn.commit()
    conn.close()

def get_maestros():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT nombre, matricula, division FROM maestros')
    res = c.fetchall()
    conn.close()
    return res

def add_alumno(nombre, matricula):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # check if exists
    c.execute('SELECT COUNT(*) FROM alumnos WHERE matricula=?', (matricula,))
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO alumnos (nombre, matricula) VALUES (?, ?)', (nombre, matricula))
    conn.commit()
    conn.close()

def get_alumnos():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT nombre, matricula FROM alumnos')
    res = c.fetchall()
    conn.close()
    return res

def create_exam_session(maestro_nombre, materia, codigo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO examenes_activos (maestro, materia, codigo) VALUES (?, ?, ?)', (maestro_nombre, materia, codigo))
    conn.commit()
    conn.close()

def get_exam_by_code(codigo):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT maestro, materia FROM examenes_activos WHERE codigo=?', (codigo,))
    res = c.fetchone()
    conn.close()
    return res

def get_active_exam_by_teacher(maestro, materia):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT codigo FROM examenes_activos WHERE maestro=? AND materia=?', (maestro, materia))
    res = c.fetchone()
    conn.close()
    return res[0] if res else None

def add_entrega(codigo_examen, alumno, score, evaluaciones):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('INSERT INTO entregas_examen (codigo_examen, alumno, score, evaluaciones) VALUES (?, ?, ?, ?)', (codigo_examen, alumno, score, evaluaciones))
    conn.commit()
    conn.close()

def get_entregas_by_code(codigo_examen):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT alumno, score, evaluaciones FROM entregas_examen WHERE codigo_examen=?', (codigo_examen,))
    res = c.fetchall()
    conn.close()
    return res
