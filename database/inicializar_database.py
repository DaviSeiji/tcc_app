import sqlite3
from pathlib import Path

# Caminho do banco de dados
db_path = Path(__file__).parent / "banco_cirurgias.db"

# Conecta (ou cria)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# ----------------------------
# TABELA: usuários
# ----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL
)
""")

# ----------------------------
# TABELA: salas
# ----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS salas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    nome TEXT NOT NULL,
    horario_seg TEXT,
    horario_sab TEXT,
    horario_dom TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# ----------------------------
# TABELA: cirurgias
# ----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS cirurgias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    plano TEXT NOT NULL,
    duracao_prevista INTEGER,
    duracao_real INTEGER,
    status TEXT DEFAULT 'pendente',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
)
""")

# ----------------------------
# TABELA: cirurgia_caracteristicas
# ----------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS cirurgia_caracteristicas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cirurgia_id INTEGER NOT NULL,
    opdur INTEGER,
    sex TEXT,
    bmi REAL,
    asa REAL,
    emop TEXT,
    department TEXT,
    optype TEXT,
    approach TEXT,
    position TEXT,
    ane_type TEXT,
    preop_htn TEXT,
    preop_dm TEXT,
    preop_pft TEXT,
    preop_hb REAL,
    preop_plt REAL,
    preop_pt REAL,
    preop_aptt REAL,
    preop_na REAL,
    preop_k REAL,
    preop_glucose REAL,
    preop_alb REAL,
    preop_got REAL,
    preop_gpt REAL,
    preop_bun REAL,
    preop_cr REAL,
    faixa_etaria TEXT,
    FOREIGN KEY (cirurgia_id) REFERENCES cirurgias(id)
)
""")

# Confirma e fecha
conn.commit()
conn.close()

print("✅ Banco de dados criado com sucesso!")
