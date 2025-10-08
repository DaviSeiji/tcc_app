import sqlite3
import os

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

    @staticmethod
    def listar_todos():
        conn = Usuario.conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, nome, email FROM usuarios")
        rows = cur.fetchall()
        conn.close()
        return [Usuario(id=r[0], nome=r[1], email=r[2]) for r in rows]

    def atualizar(self):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute("""
            UPDATE usuarios
            SET nome = ?, email = ?, senha = ?
            WHERE id = ?
        """, (self.nome, self.email, self.senha, self.id))
        conn.commit()
        conn.close()
        
    def deletar(self):
        conn = self.conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = ?", (self.id,))
        conn.commit()
        conn.close()
