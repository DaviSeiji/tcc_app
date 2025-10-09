import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/banco_cirurgias.db')

class Usuario:
    def __init__(self, id=None, nome=None, email=None, senha=None):
        self.id = id
        self.nome = nome
        self.email = email
        self.senha = senha

    @staticmethod
    def conectar():
        return sqlite3.connect(DB_PATH)

    def salvar(self):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO usuarios (nome, email, senha)
            VALUES (?, ?, ?)
        """, (self.nome, self.email, self.senha))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_email(email):
        conn = Usuario.conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, email, senha FROM usuarios WHERE email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        if row:
            return Usuario(*row)
        return None

    def set_password(self, senha):
        self.senha = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha, senha)

    @staticmethod
    def autenticar(email, senha):
        usuario = Usuario.buscar_por_email(email)
        if usuario and check_password_hash(usuario.senha, senha):
            return usuario
        return None
